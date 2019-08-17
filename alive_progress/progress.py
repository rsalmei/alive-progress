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
def alive_bar(total=None, title=None, force_tty=False, manual=False, **options):
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
    ... with alive_bar(<total>) as bar:
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
        force_tty (bool): runs animations even without a tty (pycharm terminal for example)
        manual (bool): set to manage progress manually
        **options: custom configuration options, see config_handler for details

    """
    config = config_handler(**options)
    if total and total <= 0:
        total = None

    def to_elapsed():
        return timedelta(seconds=int(run.elapsed)) if run.elapsed >= 60 else \
            '{:.1f}s'.format(run.elapsed) if end else '{}s'.format(int(run.elapsed))

    def clear_traces():
        sys.__stdout__.write('\033[2K\r')

    def run():
        player = spinner_player(config.spinner())
        while thread:
            event.wait()
            alive_repr(next(player))
            time.sleep(1. / fps())

    def alive_repr(spin=''):
        update_data()

        line = '{} {}{}{} in {} {} {}'.format(
            bar_repr(run.percent, end), spin, spin and ' ' or '',
            monitor(), to_elapsed(), run.stats(), run.text or title or ''
        )

        line_len = len(line)
        with print_lock:
            if line_len < run.last_line_len:
                clear_traces()
            sys.__stdout__.write(line + (spin and '\r' or '\n'))
            sys.__stdout__.flush()

        run.last_line_len = line_len

    if manual:
        def bar(perc, text=None):
            run.percent = float(perc)
            if text is not None:
                run.text = str(text)
            return run.percent
    else:
        def bar(text=None):
            run.count += 1
            if text is not None:
                run.text = str(text)
            return run.count

    def print_hook(part):
        if part != '\n':
            print_buffer.extend([u for x in part.splitlines(True) for u in (x, None)][:-1])
        else:
            header = 'on {}: '.format(run.count)
            nested = (line or ' ' * len(header) for line in print_buffer)
            with print_lock:
                clear_traces()
                sys.__stdout__.write('{}{}\n'.format(header, ''.join(nested)))
            print_buffer[:] = []

    print_buffer = []
    print_hook.write = print_hook
    print_hook.flush = lambda: None
    print_lock = threading.Lock()

    def start_monitoring(offset=0.):
        sys.stdout = print_hook
        event.set()
        run.init = time.time() - offset

    def stop_monitoring(clear):
        if clear:
            event.clear()
        sys.stdout = sys.__stdout__
        return time.time() - run.init

    event = threading.Event()
    if sys.stdout.isatty() or force_tty:
        @contextmanager
        def pause_monitoring():
            offset = stop_monitoring(True)
            alive_repr()
            yield
            start_monitoring(offset)

        bar.pause = pause_monitoring
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def update_data():
        update_hook()
        run.elapsed = time.time() - run.init
        run.rate = current() / run.elapsed if run.elapsed else 0.
        run.eta_text = eta_text()

    if total or manual:  # we can track progress and therefore eta.
        bar_repr = config.bar(config.length)
        stats = lambda: '({:.1{}}/s, eta: {})'.format(run.rate, format_spec, run.eta_text)

        def eta_text():
            if run.rate:
                eta = (logic_total - current()) / run.rate
                if eta >= 0:
                    return '{:.0f}s'.format(eta) if eta < 60 \
                        else timedelta(seconds=int(eta) + 1)
            return '?'
    else:  # unknown progress.
        bar_repr = config.unknown(config.length, config.bar)
        eta_text = lambda: None
        stats = lambda: '({:.1f}/s)'.format(run.rate)
    stats_end = lambda: '({:.2{}}/s)'.format(run.rate, format_spec)

    if manual and not total:  # there's only a percentage indication.
        logic_total, format_spec, current = 1., '%', lambda: run.percent
        fps = lambda: max(math.log10(run.rate) * 10. + 40, 2.) if run.rate else 10.
    else:  # there's items being processed.
        logic_total, format_spec, current = total, 'f', lambda: run.count
        fps = lambda: max(math.log10(run.rate) * 10., 2.) if run.rate else 10.

    if total:
        if manual:
            def update_hook():
                run.count = int(math.ceil(run.percent * total))
        else:
            def update_hook():
                run.percent = run.count / total

        monitor = lambda: '{}{}/{} [{:.0%}]'.format(
            '(!) ' if end and run.count != total else '', run.count, total, run.percent
        )
    elif manual:
        update_hook = lambda: None
        monitor = lambda: '{}{:.0%}'.format(
            '(!) ' if end and run.percent != 1. else '', run.percent
        )
    else:
        def update_hook():
            if end:
                run.percent = 1.

        monitor = lambda: '{}'.format(run.count)

    end, run.text, run.eta_text, run.stats = False, '', '', stats
    run.count, run.last_line_len = 0, 0
    run.percent, run.rate, run.init, run.elapsed = 0., 0., 0., 0.
    start_monitoring()
    try:
        yield bar
    except BaseException:
        # makes visible the point where an exception is thrown.
        sys.__stdout__.write('\n')
        raise
    finally:
        thread = None
        stop_monitoring(False)

    end, run.text, run.stats = True, '', stats_end
    alive_repr()
