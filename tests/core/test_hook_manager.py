import logging
import sys
from contextlib import contextmanager
from threading import Condition
from unittest import mock

import click
import pytest

from alive_progress.core.hook_manager import buffered_hook_manager
from alive_progress.utils.terminal import get_term


@contextmanager
def install_hook(hook_manager=None):
    if hook_manager is None:
        hook_manager = hook('nice {}! ')
    hook_manager.install()
    yield
    hook_manager.uninstall()


def hook(header):
    return buffered_hook_manager(header, lambda: 35, 0, Condition(), get_term())


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
    with install_hook():
        print(out)
    assert capsys.readouterr().out == expected


def test_hook_manager_captures_bytes_stdout(print_data, capsys):
    out, expected = print_data
    with install_hook():
        click.echo(out)
    assert capsys.readouterr().out == expected


# I couldn't make this work yet, there's some weird interaction
# between my hook and the pytest one...
def _hook_manager_captures_logging(capsys):
    import sys
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger('?name?')

    with install_hook():
        logger.error('oops')
    assert capsys.readouterr().err == 'nice! ERROR:?name?:oops\n'


def test_hook_manager_captures_multiple_lines(capsys):
    with install_hook():
        print('ok1\nok2')
    assert capsys.readouterr().out == 'nice 35! ok1\n         ok2\n'


def test_hook_manager_can_be_disabled(capsys):
    with install_hook(hook('')):
        print('ok')
    assert capsys.readouterr().out == 'ok\n'


def test_hook_manager_flush(capsys):
    hook_manager = hook('')
    with install_hook(hook_manager):
        print('ok', end='')
        assert capsys.readouterr().out == ''
        hook_manager.flush_buffers()
        assert capsys.readouterr().out == 'ok\n'

    # after used, the buffers should be empty
    hook_manager.flush_buffers()
    assert capsys.readouterr().out == ''


def test_hook_manager_do_clear_line_on_stdout():
    term = get_term()
    hook_manager = buffered_hook_manager('', None, 0, Condition(), term)
    m_clear = mock.Mock()
    with install_hook(hook_manager), mock.patch.dict(term.__dict__, clear_line=m_clear):
        print('some')
    m_clear.assert_called()


def test_hook_manager_do_not_flicker_screen_when_logging():
    logging.basicConfig()
    logger = logging.getLogger()

    term = get_term()
    hook_manager = buffered_hook_manager('', None, 0, Condition(), term)
    m_clear = mock.Mock()
    with install_hook(hook_manager), mock.patch.dict(term.__dict__, clear_line=m_clear):
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
    hook_manager = hook('')
    with mock.patch('logging.StreamHandler.setStream') as mock_set_stream:
        hook_manager.install()
    mock_set_stream.assert_has_calls(tuple(mock.call(mock.ANY) for _ in handlers))


def test_uninstall(handlers):
    hook_manager = hook('')
    hook_manager.install()
    with mock.patch('logging.StreamHandler.setStream') as mock_set_stream:
        hook_manager.uninstall()
    mock_set_stream.assert_has_calls(tuple(mock.call(mock.ANY) for _ in handlers))
