import random
import re
import time
from collections import OrderedDict
from enum import Enum
from shutil import get_terminal_size

from .internal import BARS, SPINNERS, THEMES
from ..animations.spinners import compound_spinner_factory, scrolling_spinner_factory
from ..animations.utils import spinner_player
from ..core.configuration import config_handler
from ..core.utils import hide_cursor, show_cursor

Show = Enum('Show', 'SPINNERS BARS THEMES')


def showtime(show=Show.SPINNERS, *, fps=None, length=None, pattern=None):
    """Start a show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second refresh rate
        show (Show): chooses which show will run
        length (int): the bar length, as in configuration options
        pattern (Pattern): to filter objects displayed
    """
    show_funcs = {
        Show.SPINNERS: show_spinners,
        Show.BARS: show_bars,
        Show.THEMES: show_themes,
    }
    show_funcs[show](fps=fps, length=length, pattern=pattern)


def show_spinners(*, fps=None, length=None, pattern=None):
    """Start a spinner show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        length (int): the bar length, as in configuration options
        pattern (Pattern): to filter objects displayed
    """
    selected = _filter(SPINNERS, pattern)
    max_natural = max(map(lambda x: x.natural, selected.values())) + 2
    max_name_length = max(map(lambda x: len(x), selected)) + 2
    prepared_gen = OrderedDict((f'{k:^{max_name_length}}', _spinner_gen(s, max_natural))
                               for k, s in selected.items())
    displaying, line_pattern = 'spinners and their unknown bars', '{1}|{2}| {0} |{3}|'
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, length)


def show_bars(*, fps=None, length=None, pattern=None):
    """Start a bar show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        length (int): the bar length, as in configuration options
        pattern (Pattern): to filter objects displayed
    """
    selected = _filter(BARS, pattern)
    max_name_length = max(map(lambda x: len(x), selected)) + 2
    prepared_gen = OrderedDict((f'{k:>{max_name_length}}', _bar_gen(b))
                               for k, b in selected.items())
    displaying, line_pattern = 'bars, with their underflow and overflow states', '{0} {1}'
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, length)


def show_themes(*, fps=None, length=None, pattern=None):
    """Start a theme show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        length (int): the bar length, as in configuration options
        pattern (Pattern): to filter objects displayed
    """
    selected = _filter(THEMES, pattern)
    themes = {k: config_handler(**v) for k, v in selected.items()}
    max_natural = max(x.spinner.natural for x in themes.values())
    max_name_length = max(map(lambda x: len(x), selected)) + 2
    prepared_gen = OrderedDict((f'{k:>{max_name_length}}', _theme_gen(c, max_natural))
                               for k, c in themes.items())
    displaying, line_pattern = 'themes and their bar, spinner and unknown bar', '{0} {1} {2}{3} {4}'
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, length)


def _filter(source, pattern):
    p = re.compile(pattern or '')
    selected = {k: v for k, v in source.items() if p.search(k)}
    if not selected:
        raise ValueError(f'Nothing was selected with pattern "{pattern}".')
    return selected


def _showtime_gen(fps, prepared_gen, displaying, line_pattern, length=None):
    logo_player, info_player = spinner_player(SPINNERS['waves']()), None
    info_spinners = compound_spinner_factory(
        scrolling_spinner_factory(f'showing: preconfigured {displaying}', right=False),
        scrolling_spinner_factory('and you can create your own styles, enjoy :)', right=False),
        alongside=False
    )

    # initialize generators, sending fps and config params (list is discarded).
    fps, config = min(60., max(2., float(fps or 15.))), config_handler(length=length)
    [(next(gen), gen.send((fps, config.length))) for gen in prepared_gen.values()]

    start, sleep, frame, i, last_info_cols = time.perf_counter(), 1. / fps, 0, 0, 0
    start, current = start - sleep, start  # simulates the first frame took exactly "sleep" ms.
    hide_cursor()
    try:
        while True:
            term_cols, term_lines = get_terminal_size()

            fps_monitor = f'fps: {frame / (current - start):.2f} (goal: {fps:.1f})'
            info_cols = term_cols - len(fps_monitor) - 1
            if info_cols != last_info_cols:
                info_player = spinner_player(info_spinners(max(10, info_cols)))
                last_info_cols = info_cols

            title = f'\rWelcome to alive-progress! {next(logo_player)}'
            info = f'{fps_monitor} {next(info_player)}'
            print(title[:term_cols])
            print(info[:term_cols], end='')

            for i, (name, gen) in enumerate(prepared_gen.items(), 3):
                data = next(gen)  # must consume data even if will not use it, to keep in sync.
                if i > term_lines:
                    break
                print('\n' + line_pattern.format(name, *data)[:term_cols], end='')

            frame += 1
            current = time.perf_counter()
            time.sleep(max(0., start + frame * sleep - current))
            print(f'\033[{i - 1}A', end='\r')  # ANSI escape sequence for Cursor Up.
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()


def _bar_gen(bar_factory):
    fps, length = yield
    total = int(length * 1.9)
    bar = bar_factory(length)
    while True:
        # standard use cases, increment till completion, underflow and overflow.
        for t in total, int(total * .6), int(total + 1):
            for pos in range(t):
                percent = float(pos) / total
                yield bar(percent),
            # generates a small pause in movement between cases, based on fps.
            percent = float(t) / total
            for _ in range(int(fps * 2)):
                yield bar(percent, end=True),

        # advanced use cases, which do not go only forward.
        for t in [1. - float(x) / total for x in range(total)], \
                 [random.random() for _ in range(total)]:
            for percent in t:
                yield bar(percent),


def _spinner_gen(spinner_factory, max_natural):
    fps, length = yield
    blanks = ' ' * (max_natural - spinner_factory.natural)
    player = spinner_player(spinner_factory())
    unknown = spinner_player(spinner_factory(length))
    while True:
        yield blanks, next(player), next(unknown)


def _theme_gen(config, max_natural):
    fps, length = yield
    bar = _bar_gen(config.bar)
    next(bar), bar.send((fps, length))  # initialize generator
    blanks = ' ' * (max_natural - config.spinner.natural)
    player = spinner_player(config.spinner())
    unknown = config.unknown(length)
    while True:
        yield next(bar)[0], next(player), blanks, unknown()
