import logging
import sys
from collections import defaultdict
from functools import partial
from itertools import chain, islice, repeat
from logging import StreamHandler
from types import SimpleNamespace

from ..utils.terminal import clear_line


def buffered_hook_manager(header_template, get_pos, cond_refresh):
    """Create and maintain a buffered hook manager, used for instrumenting print
    statements and logging.

    Args:
        header_template (): the template for enriching output
        get_pos (Callable[..., Any]): the container to retrieve the current position
        cond_refresh: Condition object to force a refresh when printing

    Returns:
        a closure with several functions

    """

    def flush_buffers():
        for stream, buffer in buffers.items():
            flush(stream)

    def flush(stream):
        if buffers[stream]:
            write(stream, '\n')
            stream.flush()

    def write(stream, part):
        buffer = buffers[stream]
        if part != '\n':
            # this will generate a sequence of lines interspersed with None, which will later
            # be rendered as the indent filler to align additional lines under the same header.
            gen = chain.from_iterable(zip(repeat(None), part.splitlines(True)))
            buffer.extend(islice(gen, 1, None))
        else:
            header = get_header()
            with cond_refresh:
                nested = ''.join(line or ' ' * len(header) for line in buffer)
                if stream in base:
                    # this avoids potential flickering, since now the stream can also be
                    # files from logging, and thus not needing to clear the screen...
                    clear_line()
                stream.write(f'{header}{nested.strip()}\n')
                stream.flush()
                cond_refresh.notify()
                buffer[:] = []

    def get_hook_for(handler):
        if handler.stream:  # supports FileHandlers with delay=true.
            handler.stream.flush()
        return SimpleNamespace(write=partial(write, handler.stream),
                               flush=partial(flush, handler.stream),
                               isatty=sys.__stdout__.isatty)

    def install():
        root = logging.root
        # modify all stream handlers, including their subclasses.
        before_handlers.update({h: _set_stream(h, get_hook_for(h))  # noqa
                                for h in root.handlers if isinstance(h, StreamHandler)})
        sys.stdout, sys.stderr = (get_hook_for(SimpleNamespace(stream=x)) for x in base)

    def uninstall():
        flush_buffers()
        buffers.clear()
        sys.stdout, sys.stderr = base

        [_set_stream(handler, original_stream)
         for handler, original_stream in before_handlers.items()]
        before_handlers.clear()

    # internal data.
    buffers = defaultdict(list)
    get_header = (lambda: header_template.format(get_pos())) if header_template else lambda: ''
    base = sys.stdout, sys.stderr  # needed for tests.
    before_handlers = {}

    # external interface.
    hook_manager = SimpleNamespace(
        flush_buffers=flush_buffers,
        install=install,
        uninstall=uninstall,
    )

    return hook_manager


if sys.version_info >= (3, 7):  # pragma: no cover
    def _set_stream(handler, stream):
        return handler.setStream(stream)
else:  # pragma: no cover
    def _set_stream(handler, stream):
        # from python 3.7 implementation.
        result = handler.stream
        handler.acquire()
        try:
            handler.flush()
            handler.stream = stream
        finally:
            handler.release()
        return result
