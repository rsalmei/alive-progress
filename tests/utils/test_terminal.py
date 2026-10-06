import io
import sys
from types import SimpleNamespace

from alive_progress.utils.terminal import get_term


def test_imported_ipython_without_shell_keeps_terminal_controls(monkeypatch):
    monkeypatch.setitem(sys.modules, 'IPython', SimpleNamespace(get_ipython=lambda: None))
    output = io.StringIO()
    term = get_term(output, force_tty=True)
    term.hide_cursor()
    term.show_cursor()
    assert output.getvalue() == '\x1b[?25l\x1b[?25h'


def test_notebook_shell_keeps_its_cursor_behavior(monkeypatch):
    shell = type('ZMQInteractiveShell', (), {})()
    monkeypatch.setitem(sys.modules, 'IPython', SimpleNamespace(get_ipython=lambda: shell))
    output = io.StringIO()
    term = get_term(output, force_tty=True)
    term.hide_cursor()
    term.show_cursor()
    assert output.getvalue() == ''


def test_terminal_ipython_shell_keeps_terminal_controls(monkeypatch):
    shell = type('TerminalInteractiveShell', (), {})()
    monkeypatch.setitem(sys.modules, 'IPython', SimpleNamespace(get_ipython=lambda: shell))
    output = io.StringIO()
    term = get_term(output, force_tty=True)
    term.hide_cursor()
    assert output.getvalue() == '\x1b[?25l'
