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


@pytest.mark.parametrize('before,after', [(None, 'next item'), ('current item', None)])
@pytest.mark.parametrize('dual_line', [True, False])
def test_text_change_during_render(before, after, dual_line, monkeypatch):
    import io

    from alive_progress.core import progress
    from alive_progress.utils import terminal

    output = io.StringIO()
    term = terminal.get_term(output, force_tty=True, cols=200)
    term.interactive = False  # Drive frames explicitly rather than depend on thread timing.
    monkeypatch.setattr(terminal, 'get_term', lambda *args: term)
    config = config_handler(file=output, dual_line=dual_line, enrich_print=False)

    with __alive_bar(config, 2, _testing=True, _sampling=True) as state:
        state['set_text'](before)
        output.seek(0)
        output.truncate()
        print_cells = progress.print_cells

        def change_text_after_cells(*args):
            result = print_cells(*args)
            # The main thread can update text while the renderer writes a frame.
            state['set_text'](after)
            return result

        with monkeypatch.context() as patch:
            patch.setattr(progress, 'print_cells', change_text_after_cells)
            state['alive_repr'](term)

        frame = output.getvalue()
        assert frame.count('\n') == int(dual_line and bool(before))
        assert frame.count(term.cursor_up_1.sequence) == int(dual_line and bool(before))
        if before:
            assert before in frame
        if after:
            assert after not in frame

        output.seek(0)
        output.truncate()
        state['alive_repr'](term)
        frame = output.getvalue()
        assert frame.count('\n') == int(dual_line and bool(after))
        assert frame.count(term.cursor_up_1.sequence) == int(dual_line and bool(after))
        if after:
            assert after in frame


@pytest.mark.parametrize('receipt_text', [True, False])
def test_dual_line_receipt_cursor(receipt_text, monkeypatch):
    import io

    from alive_progress.utils import terminal

    output = io.StringIO()
    term = terminal.get_term(output, force_tty=True, cols=200)
    term.interactive = False
    monkeypatch.setattr(terminal, 'get_term', lambda *args: term)
    config = config_handler(file=output, dual_line=True, receipt_text=receipt_text)

    with __alive_bar(config, 1, _testing=True) as bar:
        bar.text = 'finished item'
        bar()

    receipt = output.getvalue()
    assert ('finished item' in receipt) == receipt_text
    assert receipt.count('\n') == 1 + receipt_text
    assert term.cursor_up_1.sequence not in receipt
