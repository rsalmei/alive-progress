import logging
import sys
from contextlib import contextmanager
from threading import Condition
from unittest import mock

import click
import pytest

from alive_progress.core.hook_manager import buffered_hook_manager
from alive_progress.utils.terminal import FULL, VOID


@contextmanager
def hook(hook_manager):
    hook_manager.install()
    yield
    hook_manager.uninstall()


@pytest.fixture(params=[
    ('ok', 'nice 35! ok\n'),
    ('ok  ', 'nice 35! ok\n'),
    ('  ok', 'nice 35!   ok\n'),
    ('  ok  ', 'nice 35!   ok\n'),
])
def print_data(request):
    yield request.param


def test_hook_manager_captures_stdout(print_data, capsys):
    out, expected = print_data
    hook_manager = buffered_hook_manager('nice {}! ', lambda: 35, Condition(), FULL)
    with hook(hook_manager):
        print(out)
    assert capsys.readouterr().out == expected


def test_hook_manager_captures_bytes_stdout(print_data, capsys):
    out, expected = print_data
    hook_manager = buffered_hook_manager('nice {}! ', lambda: 35, Condition(), FULL)
    with hook(hook_manager):
        click.echo(out)
    assert capsys.readouterr().out == expected


# I couldn't make this work yet, there's some weird interaction
# between my hook and the pytest one...
def _hook_manager_captures_logging(capsys):
    import sys
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger('?name?')

    hook_manager = buffered_hook_manager('nice {}! ', lambda: 35, Condition(), FULL)
    with hook(hook_manager):
        logger.error('oops')
    assert capsys.readouterr().err == 'nice 35! ERROR:?name?:oops\n'


def test_hook_manager_captures_multiple_lines(capsys):
    hook_manager = buffered_hook_manager('nice {}! ', lambda: 35, Condition(), FULL)
    with hook(hook_manager):
        print('ok1\nok2')
    assert capsys.readouterr().out == 'nice 35! ok1\n         ok2\n'


def test_hook_manager_can_be_disabled(capsys):
    hook_manager = buffered_hook_manager('', None, Condition(), FULL)
    with hook(hook_manager):
        print('ok')
    assert capsys.readouterr().out == 'ok\n'


def test_hook_manager_flush(capsys):
    hook_manager = buffered_hook_manager('', None, Condition(), FULL)
    with hook(hook_manager):
        print('ok', end='')
        assert capsys.readouterr().out == ''
        hook_manager.flush_buffers()
        assert capsys.readouterr().out == 'ok\n'

    # after used, the buffers should be empty
    hook_manager.flush_buffers()
    assert capsys.readouterr().out == ''


def test_hook_manager_do_clear_line_on_stdout():
    hook_manager = buffered_hook_manager('', None, Condition(), VOID)
    m_clear = mock.Mock()
    with hook(hook_manager), mock.patch.dict(VOID.__dict__, clear_line=m_clear):
        print('some')
    m_clear.assert_called()


def test_hook_manager_do_not_flicker_screen_when_logging():
    logging.basicConfig()
    logger = logging.getLogger()

    hook_manager = buffered_hook_manager('', None, Condition(), VOID)
    m_clear = mock.Mock()
    with hook(hook_manager), mock.patch.dict(VOID.__dict__, clear_line=m_clear):
        logger.error('oops')
    m_clear.assert_not_called()


@pytest.fixture
def handlers():
    handlers = (logging.StreamHandler(sys.stderr),
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/dev/null', delay=True))
    [logging.root.addHandler(h) for h in handlers]
    yield handlers
    [logging.root.removeHandler(h) for h in handlers]


def test_install(handlers):
    hook_manager = buffered_hook_manager('', None, Condition(), FULL)
    with mock.patch('alive_progress.core.hook_manager._set_stream') as mock_set_stream:
        hook_manager.install()
    mock_set_stream.assert_has_calls(tuple(mock.call(h, mock.ANY) for h in handlers))


def test_uninstall(handlers):
    hook_manager = buffered_hook_manager('', None, Condition(), FULL)
    with mock.patch('alive_progress.core.hook_manager._set_stream') as mock_set_stream:
        hook_manager.install()
        hook_manager.uninstall()
    mock_set_stream.assert_has_calls(tuple(mock.call(h, mock.ANY) for h in handlers))
