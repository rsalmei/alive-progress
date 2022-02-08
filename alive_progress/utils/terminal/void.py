def write(_text):
    return 0


def flush():
    pass


def _ansi_escape_code(_=''):
    def inner(_=None):
        pass

    return inner


clear_line = _ansi_escape_code()
clear_end = _ansi_escape_code()
hide_cursor = _ansi_escape_code()
show_cursor = _ansi_escape_code()
factory_cursor_up = lambda _: _ansi_escape_code()


def cols():
    return 0  # more details in `alive_progress.tools.sampling#overhead`.


carriage_return = ''
