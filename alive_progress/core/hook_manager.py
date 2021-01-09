import sys
import threading
from collections import defaultdict
from functools import partial
from itertools import chain, islice, repeat
from types import SimpleNamespace

from ..utils.terminal import clear_traces


def buffered_hook_manager(header_template, get_pos):
    """Create and maintain a buffered hook manager, used for instrumenting print
    statements and logging.

    Args:
        header_template (): the template for enriching output
        get_pos (Callable[..., Any]): the container to retrieve the current position

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
            with lock:
                nested = ''.join(line or ' ' * len(header) for line in buffer)
                if stream == base_stdout:
                    # this avoids potential flickering, since now the stream can also be
                    # files from logging, and thus not needing to clear the screen...
                    clear_traces()
                stream.write(f'{header}{nested.strip()}\n')
                stream.flush()
                buffer[:] = []

    def get_hook_for(stream):
        stream.flush()
        if stream == sys.stderr:  # this stream also goes to screen, which can mess with stdout.
            stream = base_stdout
        # generates multiple hooks, one for each stream.
        return SimpleNamespace(write=partial(write, stream),
                               flush=partial(flush, stream),
                               isatty=sys.__stdout__.isatty)

    # internal data.
    buffers = defaultdict(list)
    lock = threading.Lock()
    get_header = (lambda: header_template.format(get_pos())) if header_template else lambda: ''
    base_stdout = sys.stdout  # needed for tests.

    # external interface.
    hook_manager = SimpleNamespace(
        lock=lock,
        flush_buffers=flush_buffers,
        get_hook_for=get_hook_for,
    )

    return hook_manager
