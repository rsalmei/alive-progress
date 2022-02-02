import math
import threading
import time
from contextlib import contextmanager

from .calibration import calibrated_fps, custom_fps
from .configuration import config_handler
from .hook_manager import buffered_hook_manager, passthrough_hook_manager
from ..utils.cells import combine_cells, fix_cells, print_cells, to_cells
from ..utils.terminal import VOID
from ..utils.timing import elapsed_text, eta_text, gen_simple_exponential_smoothing_eta


def alive_bar(total=None, *, calibrate=None, **options):
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
        calibrate (float): maximum theoretical throughput to calibrate animation speed
        **options: custom configuration options, which override the global configuration:
            title (Optional[str]): an optional, always visible bar title
            length (int): the number of characters to render the animated progress bar
            spinner (Union[None, str, object]): the spinner style to be rendered next to the bar
                accepts a predefined spinner name, a custom spinner factory, or None
            bar (Union[None, str, object]): the bar style to be rendered in known modes
                accepts a predefined bar name, a custom bar factory, or None
            unknown (Union[str, object]): the bar style to be rendered in the unknown mode
                accepts a predefined spinner name, or a custom spinner factory (cannot be None)
            theme (str): a set of matching spinner, bar and unknown
                accepts a predefined theme name
            force_tty (Optional[int|bool]): forces a specific kind of terminal:
                False -> disables animations, keeping only the the final receipt
                True -> enables animations, and auto-detects Jupyter Notebooks!
                None (default) -> auto select, according to the terminal/Jupyter
            disable (bool): if True, completely disables all output, do not install hooks
            manual (bool): set to manually control the bar position
            enrich_print (bool): enriches print() and logging messages with the bar position
            receipt (bool): prints the nice final receipt, disables if False
            receipt_text (bool): set to repeat the last text message in the final receipt
            monitor (bool): set to display the monitor widget `123/100 [123%]`
            stats (bool): set to display the stats widget `(123.4/s eta: 12s)`
            elapsed (bool): set to display the elapsed time widget `in 12s`
            title_length (int): fixes the title lengths, or 0 for unlimited
                title will be truncated if longer, and a cool ellipsis "…" will appear at the end
            spinner_length (int): forces the spinner length, or `0` for its natural one
            refresh_secs (int): forces the refresh period to this, `0` is the reactive visual feedback

    """
    config = config_handler(**options)
    return __alive_bar(config, total, calibrate=calibrate)


@contextmanager
def __alive_bar(config, total=None, *, calibrate=None, _cond=threading.Condition):
    """Actual alive_bar handler, that exposes internal functions for configuration of
    both normal operation and overhead estimation."""

    if total is not None:
        if not isinstance(total, int):
            raise TypeError(f"integer argument expected, got '{type(total).__name__}'.")
        if total <= 0:
            total = None

    def run(spinner_player):
        with cond_refresh:
            while thread:
                event_renderer.wait()
                alive_repr(next(spinner_player))
                cond_refresh.wait(1. / fps(run.rate))

    def alive_repr(spin=None):
        run.elapsed = time.perf_counter() - run.init
        run.rate = current() / run.elapsed

        fragments = (run.title, bar_repr(run.percent), spin, monitor(),
                     elapsed(), stats(), run.text)

        run.last_len = print_cells(fragments, term.cols(), run.last_len, _term=term)
        term.flush()

    def set_text(text=None):
        run.text = to_cells(None if text is None else str(text))

    def set_title(title=None):
        run.title = _render_title(config, None if title is None else str(title))

    if config.manual:
        def bar_handle(percent):  # for manual progress modes.
            hook_manager.flush_buffers()
            run.percent = max(0., float(percent))
            update_hook()
    else:
        def bar_handle(count=1):  # for counting progress modes.
            hook_manager.flush_buffers()
            run.count += max(0, int(count))
            update_hook()

    def start_monitoring(offset=0.):
        term.hide_cursor()
        hook_manager.install()
        bar._handle = bar_handle
        run.init = time.perf_counter() - offset
        event_renderer.set()

    def stop_monitoring():
        term.show_cursor()
        hook_manager.uninstall()
        bar._handle = None
        return time.perf_counter() - run.init

    @contextmanager
    def pause_monitoring():
        event_renderer.clear()
        offset = stop_monitoring()
        alive_repr()
        term.write('\n')
        term.flush()
        try:
            yield
        finally:
            start_monitoring(offset)

    if total or not config.manual:  # we can count items.
        logic_total, current = total, lambda: run.count
        rate_spec, factor, header = 'f', 1.e6, 'on {:d}: '
    else:  # there's only a manual percentage.
        logic_total, current = 1., lambda: run.percent
        rate_spec, factor, header = '%', 1., 'on {:.1%}: '

    if config.refresh_secs:
        fps = custom_fps(config.refresh_secs)
    else:
        fps = calibrated_fps(calibrate or factor)

    __alive_bar._alive_repr = alive_repr  # sampling mode.
    bar_repr, run.last_len, run.elapsed = _create_bars(config), 0, 0.
    run.count, run.percent, run.rate, run.init, run.text, run.title = 0, 0., 0., 0., None, None
    bar = __AliveBarHandle(pause_monitoring, current, set_title, set_text)
    thread, event_renderer, cond_refresh = None, threading.Event(), _cond()

    if config.disable:
        term, hook_manager = VOID, passthrough_hook_manager()
    else:
        term = config.force_tty
        hook_manager = buffered_hook_manager(
            header if config.enrich_print else '', current, cond_refresh, term)

    if term.interactive:
        thread = threading.Thread(target=run, args=(_create_spinner_player(config),))
        thread.daemon = True
        thread.start()

    if total or config.manual:  # we can track progress and therefore eta.
        gen_eta = gen_simple_exponential_smoothing_eta(.5, logic_total)
        gen_eta.send(None)

        def stats():
            eta = eta_text(gen_eta.send((current(), run.rate)))
            return f'({run.rate:.1{rate_spec}}/s, eta: {eta})'
    else:  # unknown progress.
        bar_repr = bar_repr.unknown

        def stats():
            return f'({run.rate:.1f}/s)'

    def stats_end():
        return f'({run.rate:.2{rate_spec}}/s)'

    def elapsed():
        return f'in {elapsed_text(run.elapsed, False)}'

    def elapsed_end():
        return f'in {elapsed_text(run.elapsed, True)}'

    if total:
        if config.manual:
            def update_hook():
                run.count = math.ceil(run.percent * total)
        else:
            def update_hook():
                run.percent = run.count / total

        def monitor_run():
            return f'{run.count}/{total} [{run.percent:.0%}]'

        def monitor_end():
            warning = '(!) ' if run.count != total else ''
            return f'{warning}{monitor_run()}'
    else:
        def update_hook():
            pass

        if config.manual:
            def monitor_run():
                return f'{run.percent:.0%}'

            def monitor_end():
                warning = '(!) ' if run.percent != 1. else ''
                return f'{warning}{monitor_run()}'
        else:
            def monitor_run():
                return f'{run.count}'

            monitor_end = monitor_run

    monitor = monitor_run
    if not config.monitor:
        monitor = monitor_end = _noop
    if not config.stats:
        stats = stats_end = _noop
    if not config.elapsed:
        elapsed = elapsed_end = _noop

    set_text()
    set_title()
    start_monitoring()
    try:
        yield bar
    finally:
        stop_monitoring()
        if thread:  # lets the internal thread terminate gracefully.
            local_copy, thread = thread, None
            local_copy.join()

    if config.receipt:  # prints the nice but optional final receipt.
        elapsed, stats, monitor, bar_repr = elapsed_end, stats_end, monitor_end, bar_repr.end
        if not config.receipt_text:
            run.text = ''
        alive_repr()
        term.write('\n')
    else:
        term.clear_line()
    term.flush()


class _GatedProperty:
    def __set_name__(self, owner, name):
        self.prop = f'_{name}'

    # noinspection PyProtectedMember
    def __get__(self, obj, objtype=None):
        if obj._handle:
            return getattr(obj, self.prop)
        return _noop

    def __set__(self, obj, value):
        raise AttributeError(f"Can't set {self.prop}")


class _GatedAssignProperty(_GatedProperty):
    # noinspection PyProtectedMember
    def __set__(self, obj, value):
        if obj._handle:
            getattr(obj, self.prop)(value)


class __AliveBarHandle:
    pause = _GatedProperty()
    current = _GatedProperty()
    text = _GatedAssignProperty()
    title = _GatedAssignProperty()

    def __init__(self, pause, get_current, set_title, set_text):
        self._handle, self._pause, self._current = None, pause, get_current
        self._title, self._text = set_title, set_text

    # this enables to exchange the __call__ implementation.
    def __call__(self, *args, **kwargs):
        if self._handle:
            self._handle(*args, **kwargs)


def _create_bars(config):
    bar = config.bar
    if bar is None:
        obj = _noop
        obj.unknown, obj.end = obj, obj
        return obj
    return bar(config.length, config.unknown)


def _create_spinner_player(config):
    spinner = config.spinner
    if spinner is None:
        from itertools import repeat
        return repeat('')
    from ..animations.utils import spinner_player
    return spinner_player(spinner(config.spinner_length))


def _render_title(config, title=None):
    title, length = to_cells(title or config.title or ''), config.title_length
    if not length:
        return title

    len_title = len(title)
    if len_title <= length:
        # fixed left align implementation for now, there may be more in the future, like
        # other alignments, variable with a maximum size, and even scrolling and bouncing.
        return combine_cells(title, (' ',) * (length - len_title))

    if length == 1:
        return '…'

    return combine_cells(fix_cells(title[:length - 1]), ('…',))


def _noop(*_args, **_kwargs):  # pragma: no cover
    pass


def alive_it(it, total=None, *, calibrate=None, **options):
    """New iterator adapter in 2.0, which makes it simpler to monitor any processing.

    Simply wrap your iterable with `alive_it`, and process your items normally!
    >>> from alive_progress import alive_it
    ... import time
    ... items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ... for item in alive_it(items):
    ...     time.sleep(.5)  # process item.

    And the bar will just work, it's that simple!

    All `alive_bar` parameters apply as usual, except `total` (which is smarter: if not supplied
    it will be inferred from the iterable using len or length_hint), and `manual` (which can't
    be used in this mode at all).
    To force unknown mode, even when the total would be available, send `total=0`.

    If you want to use other alive_bar's more advanced features, like for instance setting
    situational text messages, you can assign it to a variable!

    >>> from alive_progress import alive_it
    ... bar = alive_it(items):
    ... for item in bar:
    ...     bar.text(f'Wow, it works! Item: {item}')
    ...     # process item.

    Args:
        it (iterable): the input iterable to be processed
        total: same as alive_bar
        calibrate: same as alive_bar
        options: same as alive_bar

    See Also:
        alive_bar

    Returns:
        Generator

    """
    config = config_handler(**options)
    if config.manual:
        raise UserWarning("Manual mode can't be used in iterator adapter.")

    if total is None and hasattr(it, '__len__'):
        total = len(it)
    it = iter(it)
    if total is None and hasattr(it, '__length_hint__'):
        total = it.__length_hint__()
    return __AliveBarIteratorAdapter(it, __alive_bar(config, total, calibrate=calibrate))


class __AliveBarIteratorAdapter:
    def __init__(self, it, inner_bar):
        self._it, self._inner_bar = it, inner_bar

    def __iter__(self):
        if '_inner_bar' not in self.__dict__:  # this iterator has already exhausted.
            return

        with self._inner_bar as self._bar:
            del self._inner_bar
            for item in self._it:
                yield item
                self._bar()

    def __call__(self, *args, **kwargs):
        raise UserWarning('The bar position is controlled automatically with `alive_it`.')

    def __getattr__(self, item):
        # makes this adapter work as the real bar.
        return getattr(self._bar, item)
