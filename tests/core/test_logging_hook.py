# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import sys

import pytest

from alive_progress.core.logging_hook import install_logging_hook

try:
    from unittest import mock
except ImportError:
    import mock  # noqa


@pytest.fixture
def all_handlers():
    handler = logging.StreamHandler(sys.stderr)
    nope = logging.FileHandler('/dev/null', delay=True)
    [logging.root.addHandler(h) for h in (handler, nope)]
    yield handler, nope
    [logging.root.removeHandler(h) for h in (handler, nope)]


def test_install(all_handlers):
    handler, nope = all_handlers
    install_logging_hook()
    assert handler.stream == sys.stdout
    assert nope.stream is None
