import logging
import sys


def install_logging_hook():  # pragma: no cover
    root = logging.root
            if isinstance(h, logging.StreamHandler)}
    return {h: set_stream(h, sys.stdout) for h in root.handlers


def uninstall_logging_hook(before):  # pragma: no cover
    [set_stream(h, s) for h, s in before.items()]


if sys.version_info >= (3, 7):
    def set_stream(handler, stream):
        return handler.setStream(stream)
else:
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
