# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from contextlib import contextmanager

import math
import threading
import time
from datetime import timedelta

from .configuration import config_handler
from .spinners import spinner_player


@contextmanager
def alive_bar(total=None, title=None, **options):
    """An alive progress bar to keep track of lengthy operations.
    It has a spinner indicator, time elapsed, throughput and eta.
    When the operation finishes, a receipt is displayed with statistics.

    If the code was being executed in a headless environment, ie without a
    connected tty, all features of the alive progress bar will be disabled
    but the final receipt.

    Another cool feature is that it tracks the actual count in regard of the
    expected count. It will look different if you send more (or less) than
    expected.

    Also, the bar installs a hook in the system print function, which cleans
    any garbage mix-up of texts, allowing you to print() while using the bar.

    And finally, it also do not show anything like `eta: 1584s`, it will nicely
    show `eta: 0:26:24` as you would expect (but anything less than a minute
    is indeed `eta: 42s`). :)

    Use it like this:

    >>> from alive_progress import alive_bar
    ... with alive_bar(total=<length>) as bar:
    ...     for item in <iterable>:
    ...         # process item
    ...         bar()  # makes the bar go forward

    The `bar()` call is what makes the bar go forward. You can call it always,
    or you can choose when to call it, depending on what you want to monitor.

    While in a progress bar context, you have two ways to output messages:
      - call `bar('text')`, which besides incrementing the counter, also
      sets/overwrites an inline message within the bar;
      - call `print('text')`, which prints an enriched message that includes
      the current position of the progress bar, effectively leaving behind a
      log and continuing the progress bar below it.
    Both methods always clear the line appropriately to remove any garbage of
    previous messages on screen.

    If the bar is over or underused, it will warn you!
    To test all supported scenarios, you can do this:
    >>> for x in 3000, 4000, 2000, 0:
    ...    with alive_bar(x) as bar:
    ...        for i in range(3000):
    ...            time.sleep(.002)
    ...            bar()
    Expected results are these (but you have to see them in motion!):
[========================================] 3000/3000 [100%] in 7.4s (408.09/s)
[==============================!         ] (!) 3000/4000 [75%] in 7.3s (408.90/s)
[========================================x (!) 3000/2000 [150%] in 7.4s (408.11/s)
[========================================] 3000 in 7.4s (407.54/s)

    Args:
        total (Optional[int]): the total expected count
        title (Optional[str]): the title, will be printed whenever there's no custom message
        **options: custom configuration options, see config_handler for details

    """
    config = config_handler(**options)
    if total and total <= 0:
        total = None

    def to_elapsed(secs):
        return timedelta(seconds=int(secs)) if secs >= 60 else \
            '{:.1f}s'.format(secs) if end else '{}s'.format(int(secs))

    def clear_traces():
        sys.__stdout__.write('\033[2K\r')

    def __tick():
        last_line_len, player = 0, spinner_player(config.spinner())
        while thread:
            event.wait()
            fps, last_line_len = __alive_repr(last_line_len, spin=next(player))
            time.sleep(1. / fps)

    def __alive_repr(last_line_len, spin=''):
        init, pos, text = init_pos_text
        elapsed = time.time() - init
        rate = pos / elapsed if elapsed else 0

        eta_text = '?'
        if total and rate:
            eta = (total - pos) / rate
            if eta >= 0:
                eta_text = '{:.0f}s'.format(eta) if eta < 60 \
                    else timedelta(seconds=int(eta) + 1)

        text, stats_ = ('', stats_end) if end else (text, stats)
        percent = percent_fn(pos)
        line = '{} {}{}{} in {} {} {}'.format(
            bar_repr(percent, end), spin, spin and ' ' or '', monitor(percent, pos),
            to_elapsed(elapsed), stats_(rate, eta_text), text or title or ''
        )

        line_len = len(line)
        with print_lock:
            if line_len < last_line_len:
                clear_traces()
            sys.__stdout__.write(line + (spin and '\r' or '\n'))
            sys.__stdout__.flush()

        fps = (math.log10(rate) * 10 if rate >= 1.3 else 2) if pos else 10
        return fps, line_len

    def tracker(text=None):
        init_pos_text[1] += 1
        if text is not None:
            init_pos_text[2] = str(text)
        return init_pos_text[1]

    def print_hook(part):
        if part != '\n':
            print_buffer.extend([u for x in part.splitlines(True) for u in (x, None)][:-1])
        else:
            header = 'on {}: '.format(init_pos_text[1])
            nested = map(lambda x: x or ' ' * len(header), print_buffer)
            with print_lock:
                clear_traces()
                sys.__stdout__.write('{}{}\n'.format(header, ''.join(nested)))
            print_buffer[:] = []

    print_buffer = []
    alive_bar.write = print_hook

    def start_monitoring():
        sys.stdout = alive_bar
        event.set()

    def stop_monitoring(clear):
        if clear:
            event.clear()
        sys.stdout = sys.__stdout__

    if sys.stdout.isatty():
        @contextmanager
        def pause_monitoring():
            stop_monitoring(True)
            offset = time.time() - init_pos_text[0]
            __alive_repr(1e6)
            yield
            init_pos_text[0] = time.time() - offset
            start_monitoring()

        tracker.pause = pause_monitoring
        event = threading.Event()
        print_lock = threading.Lock()
        thread = threading.Thread(target=__tick)
        thread.daemon = True
        thread.start()

    if total:
        bar_repr = config.bar(config.length)
        percent_fn = lambda x: x / total
        monitor = lambda percent, pos: '{}{}/{} [{:.0%}]'.format(
            '(!) ' if end and pos != total else '', pos, total, percent
        )
        stats = lambda rate, eta: '({:.1f}/s, eta: {})'.format(rate, eta)
    else:
        bar_repr = config.unknown(config.length, config.bar)
        percent_fn = lambda x: 1.
        monitor = lambda percent, pos: '{}'.format(pos)
        stats = lambda rate, eta: '({:.1f}/s)'.format(rate)
    stats_end = lambda rate, eta: '({:.2f}/s)'.format(rate)

    end = False
    init_pos_text = [time.time(), 0, '']
    start_monitoring()
    try:
        yield tracker
    except:
        # makes visible the point where an exception is thrown.
        sys.__stdout__.write('\n')
        raise
    finally:
        thread = None
        stop_monitoring(False)

    end = True
    __alive_repr(1e6)
