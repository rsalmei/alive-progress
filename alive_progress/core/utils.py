from ..utils.cells import combine_cells, fix_cells, to_cells


def render_title(title, length):
    title = to_cells(title)
    if not length:
        return title

    len_title = len(title)
    if len_title <= length:
        # fixed left align implementation for now, there may be more in the future, like
        # other alignments, variable with a maximum size, and even scrolling and bouncing.
        return combine_cells(title, (' ',) * (length - len_title))

    if length == 1:
        return '…'

    return combine_cells(fix_cells(title[:length - 1]), ('…',))
