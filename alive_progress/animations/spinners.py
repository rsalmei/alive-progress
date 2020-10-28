import math
from itertools import chain

from .spinner_compiler import compiler_controller
from .utils import combinations, overlay_sliding_window, spinner_player, split_options, \
    spread_weighted, static_sliding_window
from ..utils.cells import combine_cells, fix_cells, mark_graphemes, strip_marks, \
    to_cells


def frame_spinner_factory(*frames):
    """Create a factory of a spinner that delivers frames in sequence, split by cycles.
    Supports unicode grapheme clusters and emoji chars (those that has length one but when on
    screen occupies two cells). Enjoy! 😜

    Args:
        frames (Union[str, Tuple[str, ...]): the frames to be displayed, split by cycles
            if sent only a string, it is interpreted as frames of a single char each.

    Returns:
        a styled spinner factory

    Examples:
        To define one cycle:
        >>> frame_spinner_factory(('cool',))  # only one frame.
        >>> frame_spinner_factory(('ooo', '---'))  # two frames.
        >>> frame_spinner_factory('|/_')  # three frames of one char each, same as below.
        >>> frame_spinner_factory(('|', '/', '_'))

        To define two cycles:
        >>> frame_spinner_factory(('super',), ('cool',))  # only one frame.
        >>> frame_spinner_factory(('ooo', '-'), ('vvv', '^'))  # two frames.
        >>> frame_spinner_factory('|/_', '▁▄█')  # three frames, same as below.
        >>> frame_spinner_factory(('|', '/', '_'), ('▁', '▄', '█'))

        Mix and match at will:
        >>> frame_spinner_factory(('oo', '-'), 'cool', ('it', 'is', 'alive!'))

    """
    # shortcut for single char animations.
    frames = (tuple(cycle) if isinstance(cycle, str) else cycle for cycle in frames)

    # support for unicode grapheme clusters and emoji chars.
    frames = tuple(tuple(to_cells(frame) for frame in cycle) for cycle in frames)

    @compiler_controller(natural=max(len(frame) for cycle in frames for frame in cycle))
    def inner_spinner_factory(actual_length=None):
        actual_length = actual_length or inner_spinner_factory.natural
        max_ratio = math.ceil(actual_length / min(len(frame) for cycle in frames
                                                  for frame in cycle))

        def frame_data(cycle):
            for frame in cycle:
                # differently sized frames and repeat support.
                yield (frame * max_ratio)[:actual_length]

        return (frame_data(cycle) for cycle in frames)

    return inner_spinner_factory


def scrolling_spinner_factory(chars, length=None, block=None, background=None, *,
                              right=True, hide=True, wrap=True, overlay=False):
    """Create a factory of a spinner that scrolls characters from one side to
    the other, configurable with various constraints.
    Supports unicode grapheme clusters and emoji chars, those that has length one but when on
    screen occupies two cells.

    Args:
        chars (str): the characters to be scrolled, either together or split in blocks
        length (Optional[int]): the natural length that should be used in the style
        block (Optional[int]): if defined, split chars in blocks with this size
        background (Optional[str]): the pattern to be used besides or underneath the animations
        right (bool): the scroll direction to animate
        hide (bool): controls whether the animation goes out of the borders or stays inside
        wrap (bool): makes the animation wrap borders or stop when not hiding.
        overlay (bool): fixes the background in place if overlay, scrolls it otherwise

    Returns:
        a styled spinner factory

    """
    chars = to_cells(chars)

    @compiler_controller(natural=length or len(chars))
    def inner_spinner_factory(actual_length=None):
        actual_length = actual_length or inner_spinner_factory.natural
        ratio = actual_length / inner_spinner_factory.natural

        initial, block_size = 0, math.ceil((block or 0) * ratio) or len(chars)
        if hide:
            gap = actual_length
        else:
            gap = max(0, actual_length - block_size)
            if right:
                initial = -block_size if block else abs(actual_length - block_size)

        if block:
            get_block = lambda g: fix_cells((mark_graphemes(g) * block_size)[:block_size])
            contents = map(get_block, strip_marks(reversed(chars) if right else chars))
        else:
            contents = (chars,)

        window_impl = overlay_sliding_window if overlay else static_sliding_window
        infinite_ribbon = window_impl(to_cells(background or ' '),
                                      gap, contents, actual_length, right, initial)

        def frame_data():
            for i, fill in zip(range(gap + block_size), infinite_ribbon):
                if i <= size:
                    yield fill

        size = gap + block_size if wrap or hide else abs(actual_length - block_size)
        cycles = len(tuple(strip_marks(chars))) if block else 1
        return (frame_data() for _ in range(cycles))

    return inner_spinner_factory


def bouncing_spinner_factory(chars, length=None, block=None, background=None, *,
                             right=True, hide=True, overlay=False):
    """Create a factory of a spinner that scrolls characters from one side to
    the other and bounce back, configurable with various constraints.
    Supports unicode grapheme clusters and emoji chars, those that has length one but when on
    screen occupies two cells.

    Args:
        chars (Union[str, Tuple[str, str]]): the characters to be scrolled, either
            together or split in blocks. Also accepts a tuple of two strings,
            which are used one in each direction.
        length (Optional[int]): the natural length that should be used in the style
        block (Union[int, Tuple[int, int], None]): if defined, split chars in blocks
        background (Optional[str]): the pattern to be used besides or underneath the animations
        right (bool): the scroll direction to start the animation
        hide (bool): controls whether the animation goes out of the borders or stays inside
        overlay (bool): fixes the background in place if overlay, scrolls it otherwise

    Returns:
        a styled spinner factory

    """
    chars_1, chars_2 = split_options(chars)
    block_1, block_2 = split_options(block)
    scroll_1 = scrolling_spinner_factory(chars_1, length, block_1, background, right=right,
                                         hide=hide, wrap=False, overlay=overlay)
    scroll_2 = scrolling_spinner_factory(chars_2, length, block_2, background, right=not right,
                                         hide=hide, wrap=False, overlay=overlay)
    return sequential_spinner_factory(scroll_1, scroll_2)












    Args:

    Returns:
        a styled spinner factory

    """

        else:





def delayed_spinner_factory(spinner_factory, copies, offset=1):
    """Create a factory of a spinner that combines itself several times alongside,
    with an increasing iteration offset on each one.

    Args:
        spinner_factory (a spinner): the source spinner
        copies (int): the number of copies
        offset (int): the offset to be applied incrementally to each copy

    Returns:
        a styled spinner factory

    """

    # this spinner is not actually a spinner, it is more a helper factory method.
    # it does not define an inner_spinner, only creates a compound spinner internally.
    def inner_factory(length_actual=None):
        # it needed to have two levels to wait for the length_actual, since this
        # argument can change the number of copies.
        copies_actual = math.ceil(length_actual / spinner_factory.natural) \
            if length_actual else copies
        result = compound_spinner_factory(*((spinner_factory,) * copies_actual))(length_actual)
        for i, s in enumerate(result.players):  # noqa
            for _ in range(i * offset):
                next(s)
        return result

    inner_factory.natural = spinner_factory.natural * copies
    return inner_factory
