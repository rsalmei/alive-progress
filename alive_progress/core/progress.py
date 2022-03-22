import math
import threading
import time
from contextlib import contextmanager

from .calibration import calibrated_fps, custom_fps
from .configuration import config_handler
from .hook_manager import buffered_hook_manager, passthrough_hook_manager
from ..utils import terminal
from ..utils.cells import combine_cells, fix_cells, print_cells, to_cells
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
            monitor (bool|str): configures the monitor widget `152/200 [76%]`
                send a string with `{count}`, `{total}` and `{percent}` to customize it
            elapsed (bool|str): configures the elapsed time widget `in 12s`
                send a string with `{elapsed}` to customize it
            stats (bool|str): configures the stats widget `(123.4/s, eta: 12s)`
                send a string with `{rate}` and `{eta}` to customize it
            monitor_end (bool|str): configures the monitor widget within final receipt
                same as monitor, the default format is dynamic, it inherits monitor's one
            elapsed_end (bool|str): configures the elapsed time widget within final receipt
                same as elapsed, the default format is dynamic, it inherits elapsed's one
            stats_end (bool|str): configures the stats widget within final receipt
                send a string with `{rate}` to customize it (no relation to stats)
            title_length (int): fixes the title lengths, or 0 for unlimited
                title will be truncated if longer, and a cool ellipsis "…" will appear at the end
            spinner_length (int): forces the spinner length, or `0` for its natural one
            refresh_secs (int): forces the refresh period, `0` for the reactive visual feedback
            ctrl_c (bool): if False, disables CTRL+C (captures it)
            dual_line (bool): if True, places the text below the bar

    """
    config = config_handler(**options)
    return __alive_bar(config, total, calibrate=calibrate)


@contextmanager
def __alive_bar(config, total=None, *, calibrate=None, _cond=threading.Condition, _sampling=False):
    """Actual alive_bar handler, that exposes internal functions for configuration of
    both normal operation and overhead estimation."""

    if total is not None:
        if not isinstance(total, int):
            raise TypeError(f"integer argument expected, got '{type(total).__name__}'.")
        if total <= 0:
            total = None

    def run(spinner_player, spinner_suffix):
        with cond_refresh:
            while thread:
                event_renderer.wait()
                alive_repr(next(spinner_player), spinner_suffix)
                cond_refresh.wait(1. / fps(run.rate))

    def alive_repr(spinner=None, spinner_suffix=None):
        run.elapsed = time.perf_counter() - run.init
        run.rate = current() / run.elapsed

        fragments = (run.title, bar_repr(run.percent), bar_suffix, spinner, spinner_suffix,
                     monitor(), elapsed(), stats(), *run.text)

        run.last_len = print_cells(fragments, term.cols(), run.last_len, _term=term)
        term.write(run.suffix)
        term.flush()

    def set_text(text=None):
        if text and config.dual_line:
            run.text, run.suffix = ('\n', to_cells(str(text))), term.cursor_up_1.sequence
        else:
            run.text, run.suffix = (to_cells(None if text is None else str(text)),), ''  # 1-tuple.

    def set_title(title=None):
        run.title = _render_title(config, None if title is None else str(title))
        if run.title:
            run.title += (' ',)  # space separator for print_cells.

    if config.manual:
        def bar_handle(percent):  # for manual progress modes.
            hook_manager.flush_buffers()
            run.percent = max(0., float(percent))
            update_hook()
    else:
        def bar_handle(count=1):  # for counting progress modes.
            hook_manager.flush_buffers()
            run.count += max(1, int(count))
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

    run.last_len, run.elapsed, run.count, run.percent = 0, 0., 0, 0.
    run.rate, run.init, run.text, run.title, run.suffix = 0., 0., None, None, None
    thread, event_renderer, cond_refresh = None, threading.Event(), _cond()
    bar_repr, bar_suffix = _create_bars(config)

    if config.disable:
        term, hook_manager = terminal.VOID, passthrough_hook_manager()
    else:
        term = config.force_tty
        hook_manager = buffered_hook_manager(
            header if config.enrich_print else '', current, cond_refresh, term)

    if term.interactive:
        thread = threading.Thread(target=run, args=_create_spinner_player(config))
        thread.daemon = True
        thread.start()

    def monitor_run(f):
        return f.format(count=run.count, total=total, percent=run.percent)

    def monitor_end(f):
        warning = '(!) ' if current() != logic_total else ''
        return f'{warning}{monitor_run(f)}'

    def elapsed_run(f):
        return f.format(elapsed=elapsed_text(run.elapsed, False))

    def elapsed_end(f):
        return f.format(elapsed=elapsed_text(run.elapsed, True))

    if total or config.manual:  # we can track progress and therefore eta.
        def stats_run(f):
            eta = eta_text(gen_eta.send((current(), run.rate)))
            return f.format(rate=run.rate, rate_spec=rate_spec, eta=eta)

        gen_eta = gen_simple_exponential_smoothing_eta(.5, logic_total)
        gen_eta.send(None)
        stats_default = '({rate:.1{rate_spec}}/s, eta: {eta})'
    else:  # unknown progress.
        def stats_run(f):
            return f.format(rate=run.rate, eta='?')

        bar_repr = bar_repr.unknown
        stats_default = '({rate:.1f}/s)'

    def stats_end(f):
        return f.format(rate=run.rate, rate_spec=rate_spec)

    stats_end_default = '({rate:.2{rate_spec}}/s)'

    if total:
        if config.manual:
            def update_hook():
                run.count = math.ceil(run.percent * total)
        else:
            def update_hook():
                run.percent = run.count / total

        monitor_default = '{count}/{total} [{percent:.0%}]'
    else:
        def update_hook():
            pass

        if config.manual:
            monitor_default = '{percent:.0%}'
        else:
            monitor_default = '{count}'
    elapsed_default = 'in {elapsed}'

    monitor = _Widget(monitor_run, config.monitor, monitor_default)
    monitor_end = _Widget(monitor_end, config.monitor_end, monitor.f[:-1])  # space separator.
    elapsed = _Widget(elapsed_run, config.elapsed, elapsed_default)
    elapsed_end = _Widget(elapsed_end, config.elapsed_end, elapsed.f[:-1])  # space separator.
    stats = _Widget(stats_run, config.stats, stats_default)
    stats_end = _Widget(stats_end, config.stats_end, stats_end_default if stats.f[:-1] else '')

    ctrl_c, bar = False, __AliveBarHandle(pause_monitoring, current, set_title, set_text)
    set_text(), set_title()
    start_monitoring()
    try:
        yield bar if not _sampling else locals()
    except KeyboardInterrupt:
        ctrl_c = True
        if config.ctrl_c:
            raise
    finally:
        stop_monitoring()
        if thread:  # lets the internal thread terminate gracefully.
            local_copy, thread = thread, None
            local_copy.join()

        # guarantees last_len is already set...
        if ctrl_c and term.cols() - run.last_len < 2:
            term.cursor_up_1()  # try to not duplicate last line when terminal prints "^C".

        if config.receipt:  # prints the nice but optional final receipt.
            elapsed, stats, monitor = elapsed_end, stats_end, monitor_end
            bar_repr, run.suffix = bar_repr.end, ''
            if not config.receipt_text:
                set_text()
            term.clear_end_screen()
            alive_repr()
            term.write('\n')
        else:
            term.clear_line()
        term.flush()


class _Widget:  # pragma: no cover
    def __init__(self, func, value, default):
        self.func = func
        if isinstance(value, str):
            self.f = value
        elif value:
            self.f = default
        else:
            self.f = ''

        if self.f:
            self.f += ' '  # space separator for print_cells.

    def __call__(self):
        return self.func(self.f)


class _GatedProperty:  # pragma: no cover
    def __set_name__(self, owner, name):
        self.prop = f'_{name}'

    # noinspection PyProtectedMember
    def __get__(self, obj, objtype=None):
        if obj._handle:
            return getattr(obj, self.prop)
        return _noop

    def __set__(self, obj, value):
        raise AttributeError(f"Can't set {self.prop}")


class _GatedAssignProperty(_GatedProperty):  # pragma: no cover
    # noinspection PyProtectedMember
    def __set__(self, obj, value):
        if obj._handle:
            getattr(obj, self.prop)(value)


class __AliveBarHandle:  # pragma: no cover
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


def _noop(*_args, **_kwargs):  # pragma: no cover
    pass


def _create_bars(config):  # pragma: no cover
    bar = config.bar
    if bar is None:
        def obj(*_args, **_kwargs):
            pass

        obj.unknown, obj.end = obj, obj
        return obj, ''

    return bar(config.length, config.unknown), ' '


def _create_spinner_player(config):  # pragma: no cover
    spinner = config.spinner
    if spinner is None:
        from itertools import repeat
        return repeat(''), ''

    from ..animations.utils import spinner_player
    return spinner_player(spinner(config.spinner_length)), ' '


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
        return ('…',)

    return combine_cells(fix_cells(title[:length - 1]), ('…',))


def alive_it(it, total=None, *, finalize=None, calibrate=None, **options):
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
    situational text messages, you can assign it to a variable! And send a `finalize` closure
    to set the final receipt title and/or text!

    >>> from alive_progress import alive_it
    ... bar = alive_it(items):
    ... for item in bar:
    ...     bar.text(f'Wow, it works! Item: {item}')
    ...     # process item.

    Args:
        it (iterable): the input iterable to be processed
        total: same as alive_bar
        finalize: a function to be called when the bar is going to finalize
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
    return __AliveBarIteratorAdapter(it, finalize, __alive_bar(config, total, calibrate=calibrate))


class __AliveBarIteratorAdapter:
    def __init__(self, it, finalize, inner_bar):
        self._it, self._finalize, self._inner_bar = it, finalize, inner_bar

    def __iter__(self):
        if '_bar' in self.__dict__:  # this iterator has already initiated.
            return

        with self._inner_bar as self._bar:
            del self._inner_bar
            for item in self._it:
                yield item
                self._bar()
            if self._finalize:
                self._finalize(self._bar)

    def __call__(self, *args, **kwargs):
        raise UserWarning('The bar position is controlled automatically with `alive_it`.')

    def __getattr__(self, item):
        # makes this adapter work as the real bar.
        return getattr(self._bar, item)

    def __setattr__(self, key, value):
        # makes this adapter work as the real bar.
        if '_bar' in self.__dict__:
            return setattr(self._bar, key, value)
        return super().__setattr__(key, value)
