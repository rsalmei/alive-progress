# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict

from .configuration import config_handler
from .spinners import spinner_player
from .styles import BARS, SPINNERS


def showtime(fps=15, spinners=True, **options):
    def bar_gen(bar_factory, end):
        total = int(config.length * 4)
        bar = bar_factory(config.length)
        while True:
            for t in total, int(total * .6), int(total + 1):
                for pos in range(t):
                    percent = float(pos) / total
                    yield bar(percent), '\n'
                if end:
                    percent = float(t) / total
                    for pos in range(int(fps * 2)):
                        yield bar(percent, end=True), '\n'

    def spinner_gen(name, spinner_factory, unknown_factory):
        blanks = ' ' * (longest - spinner_lengths[name])
        player = spinner_player(spinner_factory())
        unknown = bar_gen(unknown_factory, False)
        while True:
            yield blanks, next(player), next(unknown)[0]

    config = config_handler(**options)

    if spinners:
        spinner_lengths = {k: v[0].natural for k, v in SPINNERS.items()}
        longest = max(spinner_lengths.values()) + 2
        max_name_length = max(map(lambda x: len(x), SPINNERS.keys())) + 2
        prepared_gen = OrderedDict(('{:^{}}'.format(k, max_name_length), spinner_gen(k, s, u))
                                   for k, (s, u) in SPINNERS.items())
        displaying, line_pattern = 'spinners (and equivalent unknown bars)', '{1}|{2}| {0} {3}'
        total_lines = 1 + len(prepared_gen)
    else:
        max_name_length = max(map(lambda x: len(x), BARS.keys())) + 2
        prepared_gen = OrderedDict(('{:>{}}'.format(k, max_name_length), bar_gen(b, True))
                                   for k, b in BARS.items())
        displaying, line_pattern = 'bars', '{0} {1}{2}'
        total_lines = 1 + len(prepared_gen) * 2

    sleep = 1. / fps
    print('\nalive-progress bars, enjoy :)')
    print('==========================')
    print('fps:', fps, '(sleep: {:.3f}s)'.format(sleep))
    print('\npreconfigured {}:'.format(displaying))

    import time
    try:
        while True:
            for name, gens in prepared_gen.items():
                print(line_pattern.format(name, *next(gens)))

            time.sleep(sleep)
            print('\033[{}A'.format(total_lines))
    except KeyboardInterrupt:
        pass


def show_chars(line=64):
    def pos():
        return i * line + 32

    for i in range(185):
        print(pos(), end=': ')
        for j in range(line):
            print(chr(pos() + j), end=' ')
        print()
