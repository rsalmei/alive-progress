import sys

import pytest

from alive_progress.core.progress import __alive_bar, __AliveBarIteratorAdapter
from alive_progress.core.configuration import config_handler

DATA = {
    # enrich_print, total, manual, scale
    (True, True, False, True): 'on 1234: half\n[===] 2.5kU/2.5kU [100%] in 1.2s (9.88kU/s)',
    (True, True, False, False): 'on 1234: half\n[===] 2468U/2468U [100%] in 1.2s (9876.54U/s)',
    (True, True, True, True): 'on 1234: half\n[===] 100% [2.5kU/2.5kU] in 1.2s (9.88kU/s)',
    (True, True, True, False): 'on 1234: half\n[===] 100% [2468U/2468U] in 1.2s (9876.54U/s)',
    (True, False, False, True): 'on 1234: half\n[===] 2.5kU in 1.2s (9.88kU/s)',
    (True, False, False, False): 'on 1234: half\n[===] 2468U in 1.2s (9876.54U/s)',
    (True, False, True, True): 'on 50.0%: half\n[===] 100% in 1.2s (9.88k%U/s)',
    (True, False, True, False): 'on 50.0%: half\n[===] 100% in 1.2s (9876.54%U/s)',
    (False, True, False, True): 'half\n[===] 2.5kU/2.5kU [100%] in 1.2s (9.88kU/s)',
    (False, True, False, False): 'half\n[===] 2468U/2468U [100%] in 1.2s (9876.54U/s)',
    (False, True, True, True): 'half\n[===] 100% [2.5kU/2.5kU] in 1.2s (9.88kU/s)',
    (False, True, True, False): 'half\n[===] 100% [2468U/2468U] in 1.2s (9876.54U/s)',
    (False, False, False, True): 'half\n[===] 2.5kU in 1.2s (9.88kU/s)',
    (False, False, False, False): 'half\n[===] 2468U in 1.2s (9876.54U/s)',
    (False, False, True, True): 'half\n[===] 100% in 1.2s (9.88k%U/s)',
    (False, False, True, False): 'half\n[===] 100% in 1.2s (9876.54%U/s)',
}


@pytest.fixture(params=[True, False])
def enrich_print(request):
    yield request.param


@pytest.fixture(params=[True, False])
def total(request):
    yield request.param


@pytest.fixture(params=[True, False])
def manual(request):
    yield request.param


@pytest.fixture(params=[True, False])
def scale(request):
    yield request.param


def test_progress_bar(enrich_print, total, manual, scale, capsys):
    def alive_bar_case(total_num):
        with __alive_bar(config, total_num, _testing=True) as bar:
            for i in range(n):
                if i == n // 2:
                    print('half')  # this is not a debug, it's part of the test.
                bar((i + 1) / n if manual else 1)

    n = 2468
    config = config_handler(enrich_print=enrich_print, manual=manual, scale=scale,
                            length=3, bar='classic', force_tty=False, unit='U', file=sys.stdout)

    alive_bar_case(n if total else None)
    assert capsys.readouterr().out.strip() == DATA[enrich_print, total, manual, scale]


def test_progress_it(enrich_print, total, scale, capsys):
    def alive_it_case(total_num):
        for i in __AliveBarIteratorAdapter(range(n), None,
                                           __alive_bar(config, total_num, _testing=True)):
            if i == n // 2:
                print('half')  # this is not a debug, it's part of the test.

    n = 2468
    config = config_handler(enrich_print=enrich_print, scale=scale,
                            length=3, bar='classic', force_tty=False, unit='U', file=sys.stdout)

    alive_it_case(n if total else None)
    assert capsys.readouterr().out.strip() == DATA[enrich_print, total, False, scale]
