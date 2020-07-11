# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import sys

import pytest

from alive_progress.core.logging_hook import install_logging_hook, uninstall_logging_hook


@pytest.fixture
def all_handlers():
    handler = logging.StreamHandler(sys.stderr)
    nope = logging.FileHandler('/dev/null', delay=True)
    [logging.root.addHandler(h) for h in (handler, nope)]
    yield handler, nope
    [logging.root.removeHandler(h) for h in (handler, nope)]


def test_install(all_handlers):
    handler, nope = all_handlers
    changed = install_logging_hook()
    assert handler.stream == sys.stdout
    assert nope.stream is None
    assert changed == {handler: sys.stderr}


def test_uninstall(all_handlers):
    handler, _ = all_handlers
    uninstall_logging_hook({handler: sys.stderr})
    assert handler.stream == sys.stderr
