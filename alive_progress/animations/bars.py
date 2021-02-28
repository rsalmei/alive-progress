import math

from .utils import bordered, extract_fill_graphemes, fix_signature, spinner_player
from ..utils.cells import VS_15, combine_cells, fix_cells, is_wide, join_cells, mark_graphemes, \
    split_graphemes, strip_marks, to_cells


def bar_factory(chars=None, *, tip=None, background=None, borders=None, errors=None):
    """Create a factory of a bar with the given styling parameters.
    Supports unicode grapheme clusters and emoji chars (those that has length one but when on
    screen occupies two cells). Enjoy! 😜

    Args:
        chars (Optional[str]): the sequence of increasing glyphs to fill the bar; it can be
            None for a transparent fill.
        tip (Optional[str): the tip in front of the bar, which are also considered for the 100%
            (this means the tip smoothly enters and exits the frame to get to 100%); it can be
            None, unless chars is also None.
        background (Optional[str]): the pattern to be used underneath the bar
        borders (Optional[Union[str, Tuple[str, str]]): the pattern or patterns to be used
            before and after the bar.
        errors (Optional[Union[str, Tuple[str, str]]): the pattern or patterns to be used
            when an underflow or overflow occurs.

    Returns:
        a styled bar factory

    """
    def inner_bar_factory(length, spinner_factory=None):
        if chars:
            def fill_style(complete, filling):  # chars fill.
                fill = (chars[-1],) * complete
                if filling:
                    fill = fill + (chars[filling - 1],)
                return mark_graphemes(fill)  # convert to cells.
        else:
            def fill_style(complete, filling):  # invisible fill.
                return fix_cells(padding[:complete + bool(filling)])

        def running(fill):
            return None, (fix_cells(padding[len(fill) + len_tip:]),)  # this is a 1-tuple.

        def ended(fill):
            border = None if len(fill) + len(underflow) <= length else underflow
            texts = *(() if border else (underflow,)), blanks
            return border, texts

        @bordered(borders, '||')
        def draw_known(apply_state, percent):
            virtual_fill = round(virtual_length * max(0., min(1., percent)))
            fill = fill_style(*divmod(virtual_fill, num_graphemes))
            border, texts = apply_state(fill)
            border = overflow if percent > 1. else None if percent == 1. else border
            return fix_cells(combine_cells(fill, tip, *texts)[len_tip:length + len_tip]), border

        if spinner_factory:
            @bordered(borders, '||')
            def draw_unknown(_percent=None):
                return next(player), None

            player = spinner_player(spinner_factory(length))
        else:
            draw_unknown = None

        padding = (' ',) * len_tip + background * math.ceil((length + len_tip) / len(background))
        virtual_length, blanks = num_graphemes * (length + len_tip), (' ',) * length
        if chars and is_wide(chars[-1]):
            virtual_length /= 2

        return draw_known, running, ended, draw_unknown

    if not chars and not tip:
        raise ValueError('tip is mandatory for transparent bars')
    chars = split_graphemes(chars or '')  # the only one not yet marked.
    tip, background = (to_cells(x) for x in (tip, background or ' '))
    underflow, overflow = extract_fill_graphemes(errors, (f'⚠{VS_15}', f'✗{VS_15}'))
    num_graphemes, len_tip = len(chars) or 1, len(tip)
    return inner_bar_factory
