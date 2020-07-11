# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import sys


def install_logging_hook():
    root = logging.root
    return {h: set_stream(h, sys.stdout) for h in root.handlers  # noqa
            if h.__class__ == logging.StreamHandler}  # want only this, not its subclasses.


def uninstall_logging_hook(before):
    [set_stream(h, s) for h, s in before.items()]


if sys.version_info >= (3, 7):
    def set_stream(handler, stream):
        return handler.setStream(stream)
else:  # pragma: no cover
    def set_stream(handler, stream):
        # from python 3.7 implementation.
        result = handler.stream
        handler.acquire()
        try:
            handler.flush()
            handler.stream = stream
        finally:
            handler.release()
        return result
