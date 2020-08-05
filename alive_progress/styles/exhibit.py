import random
import re
import time
from collections import OrderedDict

from .internal import BARS, SPINNERS
from ..animations.utils import spinner_player
from ..core.configuration import config_handler
from ..core.utils import hide_cursor, show_cursor


def showtime(fps=None, spinners=True, length=None, pattern=None):
    """Start a show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        spinners (bool): shows spinners if True, or bars otherwise
        options (dict): configuration options
        pattern (Pattern): to filter objects displayed
    """
    if spinners:
        show_spinners(fps, **options)
    else:
        show_bars(fps, **options)


def show_spinners(fps=None, length=None, pattern=None):
    """Start a spinner show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        options (dict): configuration options
        pattern (Pattern): to filter objects displayed
    """
    displaying, line_pattern = 'spinners, with their unknown bar renditions', '{1}|{2}| {0} {3}'
    total_lines = 1 + len(prepared_gen)
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, total_lines, **options)
    selected = _filter(SPINNERS, pattern)
    max_natural = max(map(lambda x: x.natural, selected.values())) + 2
    max_name_length = max(map(lambda x: len(x), selected)) + 2
    prepared_gen = OrderedDict((f'{k:^{max_name_length}}', _spinner_gen(s, max_natural))
                               for k, s in selected.items())


def show_bars(fps=None, length=None, pattern=None):
    """Start a bar show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        options (dict): configuration options
        pattern (Pattern): to filter objects displayed
    """
    selected = _filter(BARS, pattern)
    max_name_length = max(map(lambda x: len(x), selected)) + 2
    prepared_gen = OrderedDict((f'{k:>{max_name_length}}', _bar_gen(b))
                               for k, b in selected.items())
    """
    displaying, line_pattern = 'bars', '{0} {1}{2}'
    total_lines = 1 + 2 * len(prepared_gen)
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, total_lines, **options)


    fps = min(300., max(2., float(fps or 15.)))  # since one can't set the total, max_fps is higher.
    sleep, config = 1. / fps, config_handler(**options)
def _filter(source, pattern):
    p = re.compile(pattern or '')
    selected = {k: v for k, v in source.items() if p.search(k)}
    if not selected:
        raise ValueError(f'Nothing was selected with pattern "{pattern}".')
    return selected

    print('Welcome to alive-progress, enjoy! (ctrl+c to stop :)')
    print('=================================')
    print('showing: preconfigured {}'.format(displaying))
    print('--> remember you can create your own!\n')

    # initialize the generators, sending fps and config params (list comprehension is discarded).
    [(next(gen), gen.send((fps, config))) for gen in prepared_gen.values()]

    timer = time.perf_counter if sys.version_info >= (3, 3) else time.time

    total_lines += 1  # frames per second indicator.
    up_command = '\033[{}A'.format(total_lines)  # ANSI escape sequence for Cursor Up.
    start, frame = timer(), 0
def _showtime_gen(fps, prepared_gen, displaying, line_pattern, total_lines, length=None):
    start, current = start - sleep, start  # simulates the first frame took exactly "sleep" ms.
    hide_cursor()
    try:
        while True:
            print('fps: {:.2f} (goal: {:.1f})  '  # the blanks at the end remove artifacts.
                  .format(frame / (current - start), fps))

            for name, gen in prepared_gen.items():
                print(line_pattern.format(name, *next(gen)))

            frame += 1
            current = timer()
            time.sleep(max(0., start + frame * sleep - current))
            print(up_command)
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
                yield bar(percent), '\n'
            # generates a small pause in movement between cases, based on fps.
            percent = float(t) / total
            for _ in range(int(fps * 2)):
                yield bar(percent, end=True), '\n'

        # advanced use cases, which do not go only forward.
        for t in [1. - float(x) / total for x in range(total)], \
                 [random.random() for _ in range(total)]:
            for percent in t:
                yield bar(percent), '\n'


def _spinner_gen(spinner_factory, max_natural):
    fps, length = yield
    blanks = ' ' * (max_natural - spinner_factory.natural)
    player = spinner_player(spinner_factory())
    unknown = spinner_player(spinner_factory(length))
    while True:
        yield blanks, next(player), next(unknown)


def print_chars(line_length=32, max_char=0x10000):
    """Print all chars in your terminal, to help you find that cool one to put in your
    customized spinner or bar. Also useful to determine which ones your terminal do support.

    Args:
        line_length (int): the desired characters per line
        max_char (int): the last character in the unicode table to show
            this goes up to 0x10ffff, but after the default value it seems to return
            only question marks, increase it if would like to see more.
    """
    max_char = min(0x10ffff, max(0, max_char))
    for i in range(32, max_char + line_length, line_length):
        print(f'0x{i:05x}', end=': ')
        for j in range(line_length):
            try:
                print(chr(i + j), end=' ')
            except UnicodeEncodeError:
                print('?', end=' ')
        print()
