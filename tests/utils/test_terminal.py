import io

from alive_progress.utils.terminal import non_tty, tty


def test_tty_progress_writes_osc_9_4_sequence():
    output = io.StringIO()
    term = tty.new(output, 80)

    term.progress(1, 42)

    assert output.getvalue() == '\x1b]9;4;1;42\x07'


def test_non_tty_progress_is_suppressed():
    output = io.StringIO()
    term = non_tty.get_from(tty.new(output, 80))

    term.progress(1, 42)

    assert output.getvalue() == ''
