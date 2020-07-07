# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import sys
import time
from collections import OrderedDict

from .internal import BARS, SPINNERS
from ..animations.utils import spinner_player
from ..core.configuration import config_handler


def showtime(fps=None, spinners=True, **options):
    """Start a show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        spinners (bool): shows spinners if True, or bars otherwise
        options (dict): configuration options
    """
    if spinners:
        show_spinners(fps, **options)
    else:
        show_bars(fps, **options)


def show_spinners(fps=None, **options):
    """Start a spinner show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        options (dict): configuration options
    """
    max_name_length = max(map(lambda x: len(x), SPINNERS.keys())) + 2
    prepared_gen = OrderedDict(('{:^{}}'.format(k, max_name_length), _spinner_gen(k, s, u))
                               for k, (s, u) in SPINNERS.items())
    displaying, line_pattern = 'spinners, with their unknown bar renditions', '{1}|{2}| {0} {3}'
    total_lines = 1 + len(prepared_gen)
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, total_lines, **options)


def show_bars(fps=None, **options):
    """Start a bar show, rendering all styles simultaneously in your screen.

    Args:
        fps (float): the desired frames per second rendition
        options (dict): configuration options
    """
    max_name_length = max(map(lambda x: len(x), BARS.keys())) + 2
    prepared_gen = OrderedDict(('{:>{}}'.format(k, max_name_length), _bar_gen(b))
                               for k, b in BARS.items())
    displaying, line_pattern = 'bars', '{0} {1}{2}'
    total_lines = 1 + 2 * len(prepared_gen)
    _showtime_gen(fps, prepared_gen, displaying, line_pattern, total_lines, **options)


def _showtime_gen(fps, prepared_gen, displaying, line_pattern, total_lines, **options):
    fps = min(300., max(2., float(fps or 15.)))  # since one can't set the total, max_fps is higher.
    sleep, config = 1. / fps, config_handler(**options)

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
    start, current = start - sleep, start  # simulates the first frame took exactly "sleep" ms.
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


def _bar_gen(bar_factory):
    fps, config = yield
    total = int(config.length * 2)
    bar = bar_factory(config.length)
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


def _spinner_gen(key, spinner_factory, unknown_factory):
    fps, config = yield
    spinner_lengths = {k: v[0].natural for k, v in SPINNERS.items()}
    longest = max(spinner_lengths.values()) + 2
    blanks = ' ' * (longest - spinner_lengths[key])
    player = spinner_player(spinner_factory())
    unknown = unknown_factory(config.length)
    while True:
        yield blanks, next(player), unknown()


def print_chars(line_length=32, max_char=0x2e80):
    """Print all chars in your terminal, to help you find that cool one to put in your
    customized spinner or bar. Also useful to determine which ones your terminal support.

    Args:
        line_length (int): the desired characters per line
        max_char (int): the last character in the unicode table to show
            this goes up to 0x10ffff, but after the default value, it seems to return
            only japanese ideograms, increase this if would like to see them.
    """
    char = chr if sys.version_info >= (3,) else unichr  # noqa
    max_char = min(0x10ffff, max(0, max_char))
    num_lines = int(max_char / line_length)
    for i in map(lambda x: x * line_length + 32, range(num_lines)):
        print(hex(i), end=': ')
        for j in range(line_length):
            print(char(i + j), end=' ')
        print()
