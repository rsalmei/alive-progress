# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import math
import sys
import threading
import time
from contextlib import contextmanager
from itertools import chain, islice, repeat

from .timming import gen_simple_exponential_smoothing_eta, to_elapsed_text, to_eta_text
from .utils import clear_traces, hide_cursor, sanitize_text, show_cursor, terminal_columns
from ..animations.utils import spinner_player
from ..configuration import config_handler


@contextmanager
def alive_bar(total=None, title=None, calibrate=None, **options):
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
    >>> for x in 1000, 1500, 700, 0:
    ...    with alive_bar(x) as bar:
    ...        for i in range(1000):
    ...            time.sleep(.005)
    ...            bar()
    Expected results are these (but you have to see them in motion!):
[========================================] 3000/3000 [100%] in 7.4s (408.09/s)
[==============================!         ] (!) 3000/4000 [75%] in 7.3s (408.90/s)
[========================================x (!) 3000/2000 [150%] in 7.4s (408.11/s)
[========================================] 3000 in 7.4s (407.54/s)

    Args:
        total (Optional[int]): the total expected count
        title (Optional[str]): the title, will be printed whenever there's no custom message
        calibrate (int): maximum theoretical throughput to calibrate animation speed
            (cannot be in the global configuration because it depends on the current mode)
        **options: custom configuration options, which override the global configuration:
            length (int): number of characters to render the animated progress bar
            spinner (Union[str | object]): spinner name in alive_progress.SPINNERS or custom
            bar (Union[str | object]): bar name in alive_progress.BARS or custom
            unknown (Union[str | object]): spinner name in alive_progress.SPINNERS or custom
            theme (str): theme name in alive_progress.THEMES
            force_tty (bool): runs animations even without a tty (pycharm terminal for example)
            manual (bool): set to manually control percentage

    """
    if total is not None:
        if not isinstance(total, int):
            raise TypeError("integer argument expected, got '{}'.".format(type(total).__name__))
        if total <= 0:
            total = None
    config = config_handler(**options)

    def run():
        player = spinner_player(config.spinner())
        while thread:
            release_thread.wait()
            alive_repr(next(player))
            time.sleep(1. / fps())

    def alive_repr(spin=''):
        update_hook()
        elapsed = time.time() - run.init
        run.rate = current() / elapsed if elapsed else 0.

        line = '{} {}{}{} in {} {} {}'.format(
            bar_repr(run.percent, end), spin, spin and ' ' or '', monitor(),
            to_elapsed_text(elapsed, end), run.stats(), run.text or title or ''
        )

        line_len, cols = len(line), terminal_columns()
        with print_lock:
            if line_len < run.last_line_len:
                clear_traces()
            sys.__stdout__.write(line[:cols] + (spin and '\r' or '\n'))
            sys.__stdout__.flush()

        run.last_line_len = line_len

    def flush_buffer():
        if print_buffer:
            print()

    if config.manual:
        def bar(perc=None, text=None):
            if perc is not None:
                flush_buffer()
                run.percent = float(perc)
            if text is not None:
                run.text = sanitize_text(text)
            return run.percent
    else:
        def bar(text=None, incr=1):
            if incr > 0:
                flush_buffer()
                run.count += int(incr)
            if text is not None:
                run.text = sanitize_text(text)
            return run.count

    def print_hook(part):
        if part != '\n':
            # this will generate a sequence of lines interspersed with None, which will later
            # be rendered as the indent filler to align additional lines under the same header.
            gen = chain.from_iterable(zip(repeat(None), part.splitlines(True)))
            print_buffer.extend(islice(gen, 1, None))
        else:
            header = header_template.format(run.count)
            nested = ''.join(line or ' ' * len(header) for line in print_buffer)
            with print_lock:
                clear_traces()
                sys.__stdout__.write('{}{}\n'.format(header, nested))
            print_buffer[:] = []

    print_buffer, print_lock = [], threading.Lock()
    header_template = 'on {}: ' if config.enrich_print else ''
    print_hook.write = print_hook
    print_hook.flush = lambda: None
    print_hook.isatty = sys.__stdout__.isatty

    def start_monitoring(offset=0.):
        hide_cursor()
        sys.stdout = print_hook
        release_thread.set()
        run.init = time.time() - offset

    def stop_monitoring():
        show_cursor()
        sys.stdout = sys.__stdout__
        return time.time() - run.init

    thread, release_thread = None, threading.Event()
    if sys.stdout.isatty() or config.force_tty:
        @contextmanager
        def pause_monitoring():
            release_thread.clear()
            offset = stop_monitoring()
            alive_repr()
            yield
            start_monitoring(offset)

        bar.pause = pause_monitoring
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    if total or not config.manual:  # we can count items.
        logic_total, rate_spec, factor, current = total, 'f', 1.e6, lambda: run.count  # noqa
    else:  # there's only a manual percentage.
        logic_total, rate_spec, factor, current = 1., '%', 1., lambda: run.percent  # noqa

    if total or config.manual:  # we can track progress and therefore eta.
        spec = '({{:.1{}}}/s, eta: {{}})'.format(rate_spec)
        gen_eta = gen_simple_exponential_smoothing_eta(.5, logic_total)
        gen_eta.send(None)
        stats = lambda: spec.format(run.rate, to_eta_text(gen_eta.send((current(), run.rate))))
        bar_repr = config.bar(config.length)
    else:  # unknown progress.
        eta_text = lambda: None  # noqa
        bar_repr = config.unknown(config.length, config.bar)
        stats = lambda: '({:.1f}/s)'.format(run.rate)  # noqa
    stats_end = lambda: '({:.2{}}/s)'.format(run.rate, rate_spec)  # noqa

    # calibration of the dynamic fps engine.
    # I've started with the equation y = log10(x + m) * k + n, where:
    #   y is the desired fps, m and n are horizontal and vertical translation,
    #   k is a calibration factor, computed from some user input c (see readme for details).
    # considering minfps and maxfps as given constants, I came to:
    #   fps = log10(x + 1) * k + minfps, which must be equal to maxfps for x = c,
    # so the factor k = (maxfps - minfps) / log10(c + 1), and
    #   fps = log10(x + 1) * (maxfps - minfps) / log10(c + 1) + minfps
    # neat! ;)
    min_fps, max_fps = 2., 60.
    calibrate = max(0., calibrate or factor)
    adjust_log_curve = 100. / min(calibrate, 100.)  # adjust curve for small numbers
    factor = (max_fps - min_fps) / math.log10((calibrate * adjust_log_curve) + 1.)

    def fps():
        if run.rate <= 0:
            return 10.  # bootstrap speed
        if run.rate < calibrate:
            return math.log10((run.rate * adjust_log_curve) + 1.) * factor + min_fps
        return max_fps

    end, run.text, run.eta_text, run.stats = False, '', '', stats
    run.count, run.last_line_len = 0, 0
    run.percent, run.rate, run.init = 0., 0., 0.

    if total:
        if config.manual:
            def update_hook():
                run.count = int(math.ceil(run.percent * total))
        else:
            def update_hook():
                run.percent = run.count / total

        monitor = lambda: '{}{}/{} [{:.0%}]'.format(  # noqa
            '(!) ' if end and run.count != total else '', run.count, total, run.percent
        )
    elif config.manual:
        update_hook = lambda: None  # noqa
        monitor = lambda: '{}{:.0%}'.format(  # noqa
            '(!) ' if end and run.percent != 1. else '', run.percent
        )
    else:
        run.percent = 1.
        update_hook = lambda: None  # noqa
        monitor = lambda: '{}'.format(run.count)  # noqa

    start_monitoring()
    try:
        yield bar
    finally:
        flush_buffer()
        stop_monitoring()
        if thread:
            local_copy = thread
            thread = None  # lets the internal thread terminate gracefully.
            local_copy.join()

        end, run.text, run.stats = True, '', stats_end
        alive_repr()
