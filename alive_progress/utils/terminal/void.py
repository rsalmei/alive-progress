def write(_text):
    return 0


def flush():
    pass


def _emit_ansi_escape(_=''):
    def inner(_=None):
        pass

    return inner


clear_line = _emit_ansi_escape()
clear_end = _emit_ansi_escape()
hide_cursor = _emit_ansi_escape()
show_cursor = _emit_ansi_escape()
factory_cursor_up = lambda _: _emit_ansi_escape()


def cols():
    return 0  # more details in `alive_progress.tools.sampling#overhead`.


carriage_return = ''
