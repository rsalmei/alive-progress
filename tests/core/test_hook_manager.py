import sys
from contextlib import redirect_stdout
from unittest import mock

from alive_progress.core.hook_manager import buffered_hook_manager


def test_hook_manager_prints_header(capsys):
    hook_manager = buffered_hook_manager('nice {}! ', lambda: 35)
    with redirect_stdout(hook_manager.get_hook_for(sys.stdout)), \
         mock.patch('alive_progress.core.hook_manager.clear_traces') as mock_clear:
        print('ok')
    mock_clear.assert_any_call()
    assert capsys.readouterr().out == 'nice 35! ok\n'


def test_hook_manager_indents_multiple_lines(capsys):
    hook_manager = buffered_hook_manager('nice {}! ', lambda: 35)
    with redirect_stdout(hook_manager.get_hook_for(sys.stdout)), \
         mock.patch('alive_progress.core.hook_manager.clear_traces') as mock_clear:
        print('ok\nok')
    mock_clear.assert_any_call()
    assert capsys.readouterr().out == 'nice 35! ok\n         ok\n'


def test_hook_manager_dont_flicker_screen():
    hook_manager = buffered_hook_manager('', lambda: 35)
    with redirect_stdout(hook_manager.get_hook_for(sys.stderr)), \
         mock.patch('alive_progress.core.hook_manager.clear_traces') as mock_clear:
        print('some')
    mock_clear.assert_not_called()


def test_hook_manager_prints_clean(capsys):
    def no_current():
        raise ValueError

    hook_manager = buffered_hook_manager('', no_current)
    with redirect_stdout(hook_manager.get_hook_for(sys.stdout)):
        print('ok')
    assert capsys.readouterr().out == 'ok\n'


def test_hook_manager_flush(capsys):
    hook_manager = buffered_hook_manager('', None)
    with redirect_stdout(hook_manager.get_hook_for(sys.stdout)):
        print('ok', end='')
        assert capsys.readouterr().out == ''
        hook_manager.flush_buffers()
        assert capsys.readouterr().out == 'ok\n'

    # after used, the buffers should be empty
    hook_manager.flush_buffers()
    assert capsys.readouterr().out == ''


def test_hook_manager_get_hook():
    hook_manager = buffered_hook_manager('', None)
    hook = hook_manager.get_hook_for(sys.stdout)
    assert all(hasattr(hook, x) for x in ('write', 'flush', 'isatty'))
