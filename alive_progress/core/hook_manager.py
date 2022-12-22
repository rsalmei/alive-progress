import logging
import sys
from collections import defaultdict
from itertools import chain, islice, repeat
from logging import StreamHandler
from types import SimpleNamespace

# support for click.echo, which calls `write` with bytes instead of str.
ENCODING = sys.getdefaultencoding()


def buffered_hook_manager(header_template, get_pos, cond_refresh, term):
    """Create and maintain a buffered hook manager, used for instrumenting print
    statements and logging.

    Args:
        header_template (): the template for enriching output
        get_pos (Callable[..., Any]): the container to retrieve the current position
        cond_refresh: Condition object to force a refresh when printing
        term: the current terminal

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
        if isinstance(part, bytes):
            part = part.decode(ENCODING)

        buffer = buffers[stream]
        if part != '\n':
            # this will generate a sequence of lines interspersed with None, which will later
            # be rendered as the indent filler to align additional lines under the same header.
            gen = chain.from_iterable(zip(repeat(None), part.splitlines(True)))
            buffer.extend(islice(gen, 1, None))
        else:
            header = get_header()
            spacer = ' ' * len(header)
            nested = ''.join(line or spacer for line in buffer)
            text = f'{header}{nested.rstrip()}\n'
            with cond_refresh:
                if stream in base:  # pragma: no cover
                    term.clear_line()
                    term.clear_end_screen()
                stream.write(text)
                stream.flush()
                cond_refresh.notify()
                buffer[:] = []

    # better hook impl, which works even when nested, since __hash__ will be forwarded.
    class Hook:
        def __init__(self, stream):
            self.__stream = stream

        def write(self, part):
            return write(self.__stream, part)

        def flush(self):
            return flush(self.__stream)

        def __getattr__(self, item):
            return getattr(self.__stream, item)

    def get_hook_for(handler):
        if handler.stream:  # supports FileHandlers with delay=true.
            handler.stream.flush()
        return Hook(handler.stream)

    def install():
        def get_all_loggers():
            yield logging.root
            yield from (logging.getLogger(name) for name in logging.root.manager.loggerDict)

        # account for reused handlers within loggers.
        handlers = set(h for logger in get_all_loggers()
                       for h in logger.handlers if isinstance(h, StreamHandler))
        # modify all stream handlers, including their subclasses.
        before_handlers.update({h: h.setStream(get_hook_for(h)) for h in handlers})
        sys.stdout, sys.stderr = (get_hook_for(SimpleNamespace(stream=x)) for x in base)

    def uninstall():
        flush_buffers()
        buffers.clear()
        sys.stdout, sys.stderr = base

        [handler.setStream(original_stream)
         for handler, original_stream in before_handlers.items()]
        before_handlers.clear()

        # did the number of logging handlers change??
        # if yes, it probably means logging was initialized within alive_bar context,
        # and thus there can be an instrumented stdout or stderr within handlers,
        # which causes a TypeError: unhashable type: 'types.SimpleNamespace'...
        # or simply a logger **reuses** a handler...

    # internal data.
    buffers = defaultdict(list)
    get_header = gen_header(header_template, get_pos) if header_template else null_header
    base = sys.stdout, sys.stderr  # needed for tests.
    before_handlers = {}

    # external interface.
    hook_manager = SimpleNamespace(
        flush_buffers=flush_buffers,
        install=install,
        uninstall=uninstall,
    )

    return hook_manager


def passthrough_hook_manager():  # pragma: no cover
    passthrough_hook_manager.flush_buffers = __noop
    passthrough_hook_manager.install = __noop
    passthrough_hook_manager.uninstall = __noop
    return passthrough_hook_manager


def __noop():  # pragma: no cover
    pass


def gen_header(header_template, get_pos):  # pragma: no cover
    def inner():
        return header_template.format(get_pos())

    return inner


def null_header():  # pragma: no cover
    return ''
