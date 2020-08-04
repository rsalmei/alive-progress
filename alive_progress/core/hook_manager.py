import sys
import threading
from collections import defaultdict
from functools import partial
from itertools import chain, islice, repeat
from types import SimpleNamespace

from .utils import clear_traces


def create_print_hook(header_template, get_pos):
    """Creates and maintain a buffered hook manager, used for instrumenting print
    statements and logging.

    Args:
        header_template (): the template for enriching output
        get_pos (Callable[..., Any]): the container to retrieve the current position

    Returns:
        a closure with several functions

    """

    def flush_buffer():
        if print_buffer:
            print()

    def print_hook(part):
        if part != '\n':
            # this will generate a sequence of lines interspersed with None, which will later
            # be rendered as the indent filler to align additional lines under the same header.
            gen = chain.from_iterable(zip(repeat(None), part.splitlines(True)))
            print_buffer.extend(islice(gen, 1, None))
        else:
            header = header_template.format(run.count)
            nested = ''.join(line or ' ' * len(header) for line in print_buffer)
            with print_lock:
                clear_traces()
                sys.__stdout__.write('{}{}\n'.format(header, nested))
            print_buffer[:] = []


    # internal data.
    print_buffer = []
    print_lock = threading.Lock()

    # external interface.
    print_hook.write = print_hook
    print_hook.flush = lambda: None
    print_hook.isatty = sys.__stdout__.isatty

    return print_hook
