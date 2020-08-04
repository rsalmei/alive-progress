import logging
import sys
from unittest import mock

import pytest

from alive_progress.core.logging_hook import install_logging_hooks, uninstall_logging_hooks


@pytest.fixture
def handlers():
    handlers = (logging.StreamHandler(sys.stderr),
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/dev/null', delay=True))
    [logging.root.addHandler(h) for h in handlers]
    yield {handler: handler.stream for handler in handlers}
    [logging.root.removeHandler(h) for h in handlers]


def test_install(handlers):
    hook_manager = mock.Mock()
    hook_manager.get_hook_for.side_effect = lambda s: s
    with mock.patch('alive_progress.core.logging_hook.set_stream') as mock_set_stream:
        mock_set_stream.side_effect = lambda h, s: s
        changed = install_logging_hooks(hook_manager)

    assert handlers == {k: v for k, v in changed.items() if k in handlers}  # pytest has one.
    hook_manager.get_hook_for.assert_has_calls(tuple(mock.call(x) for x in handlers.values()),
                                               any_order=True)
    mock_set_stream.assert_has_calls(tuple(mock.call(h, s) for h, s in handlers.items()),
                                     any_order=True)


def test_uninstall(handlers):
    with mock.patch('alive_progress.core.logging_hook.set_stream') as mock_set_stream:
        uninstall_logging_hooks(handlers)
    mock_set_stream.assert_has_calls(mock.call(h, s) for h, s in handlers.items())
