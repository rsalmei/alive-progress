import math
import sys
import threading
import time
from contextlib import contextmanager
from shutil import get_terminal_size

from .calibration import calibrated_fps
from .configuration import config_handler
from .hook_manager import buffered_hook_manager
from .logging_hook import install_logging_hooks, uninstall_logging_hooks
from .timing import gen_simple_exponential_smoothing_eta, to_elapsed_text, to_eta_text
from .utils import clear_traces, hide_cursor, render_title, sanitize_text_marking_wide_chars, \
    show_cursor
from ..animations.utils import spinner_player


@contextmanager
def alive_bar(total=None, title=None, *, calibrate=None, **options):
    """An alive progress bar to keep track of lengthy operations.
    It has a spinner indicator, elapsed time, throughput and ETA.
    When the operation finishes, a receipt is displayed with statistics.

    If the code is executed in a headless environment, ie without a
    connected tty, all features are disabled but the final receipt.

    Another cool feature is that it tracks the actual count in regard of the
    expected count. So it will look different if you send more (or less) than
    expected.

    Also, the bar installs a hook in the system print function that cleans
    any garbage out of the terminal, allowing you to print() effortlessly
    while using the bar.

    Use it like this:

    >>> from alive_progress import alive_bar
    ... with alive_bar(123, 'Title') as bar:  # <-- expected total and bar title
    ...     for item in <iterable>:
    ...         # process item
    ...         bar()  # makes the bar go forward

    The `bar()` method should be called whenever you want the bar to go forward.
    You usually call it in every iteration, but you could do it only when some
    criteria match, depending on what you want to monitor.

    While in a progress bar context, you have two ways to output messages:
      - the usual Python `print()` statement, which will properly clean the line,
        print an enriched message (including the current bar position) and
        continue the bar right below it;
      - the `bar.text('message')` call, which sets a situational message right within
        the bar, usually to display something about the items being processed or the
        phase the processing is in.

    If the bar is over or underused, it will warn you!
    To test all supported scenarios, you can do this:
    >>> for x in 1000, 1500, 700, 0:
    ...    with alive_bar(x) as bar:
    ...        for i in range(1000):
    ...            time.sleep(.005)
    ...            bar()
    Expected results are these (but you have to see them in motion!):
|████████████████████████████████████████| 1000/1000 [100%] in 6.0s (167.93/s)
|██████████████████████████▋⚠            | (!) 1000/1500 [67%] in 6.0s (167.57/s)
|████████████████████████████████████████✗ (!) 1000/700 [143%] in 6.0s (167.96/s)
|████████████████████████████████████████| 1000 in 5.8s (171.91/s)

    Args:
        total (Optional[int]): the total expected count
        title (Optional[str]): the title, will be printed whenever there's no custom message
        calibrate (int): maximum theoretical throughput to calibrate animation speed
            (cannot be in the global configuration because it depends on the current mode)
        **options: custom configuration options, which override the global configuration:
            length (int): number of characters to render the animated progress bar
            spinner (Union[str, object]): the spinner to be used in all renditions
                it's a predefined name in `show_spinners()`, or a custom spinner
            bar (Union[str, object]): bar to be used in definite and both manual modes
                it's a predefined name in `show_bars()`, or a custom bar
            unknown (Union[str, object]): bar to be used in unknown mode (whole bar is a spinner)
                it's a predefined name in `show_spinners()`, or a custom spinner
            theme (str): theme name in alive_progress.THEMES
            force_tty (bool): runs animations even without a tty (pycharm terminal for example)
            manual (bool): set to manually control percentage
            enrich_print (bool): includes the bar position in print() and logging messages
            title_length (int): fixed title length, or 0 for unlimited

    """
    if total is not None:
        if not isinstance(total, int):
            raise TypeError(f"integer argument expected, got '{type(total).__name__}'.")
        if total <= 0:
            total = None
    config = config_handler(**options)

    def run(spinner):
        player = spinner_player(spinner)
        while thread:
            release_thread.wait()
            alive_repr(next(player))
            time.sleep(1. / fps(run.rate))

    def alive_repr(spin=''):
        elapsed = time.perf_counter() - run.init
        run.rate = current() / elapsed if elapsed else 0.

        line = ' '.join(filter(None, (
            title, bar_repr(run.percent, end), spin, monitor(), 'in',
            to_elapsed_text(elapsed, end), stats(), run.text)))

        line_len, (cols, _) = len(line), get_terminal_size()
        with hook_manager.lock:
            if line_len < run.last_line_len:
                clear_traces()
            sys.__stdout__.write(line[:cols] + (spin and '\r' or '\n'))
            sys.__stdout__.flush()

        run.last_line_len = line_len

    def set_text(message):
        run.text = sanitize_text_marking_wide_chars(message)

    if config.manual:
        def bar_handle(percent, *, relative=False):
            """Bar handle for manual (bounded and unbounded) modes.
            Default is absolute positioning.
            """
            hook_manager.flush_buffers()
            percent = float(percent)
            if relative:
                percent += run.percent
            run.percent = max(0., percent)
            update_hook()
    else:
        def bar_handle(count=1, *, relative=True):
            """Bar handle for definite and unknown modes.
            Default is relative positioning.
            """
            hook_manager.flush_buffers()
            count = int(count)
            if relative:
                count += run.count
            run.count = max(0, count)
            update_hook()

    def start_monitoring(offset=0.):
        hide_cursor()
        sys.stdout = hook_manager.get_hook_for(sys.stdout)
        run.before_handlers = install_logging_hooks(hook_manager)
        release_thread.set()
        run.init = time.perf_counter() - offset

    def stop_monitoring():
        show_cursor()
        sys.stdout = sys.__stdout__
        uninstall_logging_hooks(run.before_handlers)  # noqa
        return time.perf_counter() - run.init

    thread, release_thread = None, threading.Event()
    if sys.stdout.isatty() or config.force_tty:
        @contextmanager
        def pause_monitoring():
            release_thread.clear()
            offset = stop_monitoring()
            alive_repr()
            yield
            start_monitoring(offset)

        bar_handle.pause = pause_monitoring
        thread = threading.Thread(target=run, args=(config.spinner(),))
        thread.daemon = True
        thread.start()

    if total or not config.manual:  # we can count items.
        logic_total, current = total, lambda: run.count
        rate_spec, factor, print_template = 'f', 1.e6, 'on {:d}: '
    else:  # there's only a manual percentage.
        logic_total, current = 1., lambda: run.percent
        rate_spec, factor, print_template = '%', 1., 'on {:.1%}: '

    known, unknown = (impl(config.length) for impl in (config.bar, config.unknown))
    bar_handle.text, bar_handle.current = set_text, current
    if total or config.manual:  # we can track progress and therefore eta.
        bar_repr = known
        gen_eta = gen_simple_exponential_smoothing_eta(.5, logic_total)
        gen_eta.send(None)

        def stats():
            eta = to_eta_text(gen_eta.send((current(), run.rate)))
            return f'({run.rate:.1{rate_spec}}/s, eta: {eta})'
    else:  # unknown progress.
        bar_repr = unknown

        def stats():
            return f'({run.rate:.1f}/s)'

    def stats_end():
        return f'({run.rate:.2{rate_spec}}/s)'

    end, run.text, run.last_line_len = False, '', 0
    run.count, run.percent, run.rate, run.init = 0, 0., 0., 0.

    if total:
        if config.manual:
            def update_hook():
                run.count = math.ceil(run.percent * total)
        else:
            def update_hook():
                run.percent = run.count / total

        def monitor():
            warning = '(!) ' if end and run.count != total else ''
            return f'{warning}{run.count}/{total} [{run.percent:.0%}]'
    else:
        def update_hook():
            pass

        if config.manual:
            def monitor():
                warning = '(!) ' if end and run.percent != 1. else ''
                return f'{warning}{run.percent:.0%}'
        else:
            def monitor():
                return f'{run.count}'

    title = render_title(title, config.title_length)
    fps = calibrated_fps(calibrate or factor)
    hook_manager = buffered_hook_manager(print_template if config.enrich_print else '', current)
    start_monitoring()
    try:
        yield bar_handle
    finally:
        hook_manager.flush_buffers()
        stop_monitoring()
        if thread:
            local_copy = thread
            thread = None  # lets the internal thread terminate gracefully.
            local_copy.join()

    # prints the nice final receipt.
    if bar_repr is unknown:
        bar_repr, run.percent = known, 1.
    end, stats = True, stats_end
    if not config.show_receipt_text:
        run.text = ''
    alive_repr()
