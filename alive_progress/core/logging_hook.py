import logging
import sys


def install_logging_hooks(hook_manager):
    root = logging.root
    # modify all stream handlers, including their subclasses.
    return {handler: set_stream(handler, hook_manager.get_hook_for(handler.stream))
            for handler in root.handlers
            if isinstance(handler, logging.StreamHandler)}


def uninstall_logging_hooks(before):
    [set_stream(handler, original_stream)
     for handler, original_stream in before.items()]


if sys.version_info >= (3, 7):  # pragma: no cover
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
