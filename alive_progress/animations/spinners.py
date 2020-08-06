import math
from itertools import accumulate

from .utils import overlay_sliding_window_factory, repeating, spinner_player, \
    static_sliding_window_factory


def frame_spinner_factory(*frames):
    """Create a factory of a spinner that delivers frames in sequence.

    Args:
        frames (str): the frames to be displayed
            if sent only one, it is interpreted as frames of one char each.

    Returns:
        a styled spinner factory

    """

    def inner_factory(length_actual=None):
        @repeating(length_actual)
        def inner_spinner():
            yield from frames

        inner_spinner.cycles = len(frames)
        return inner_spinner

    if len(frames) == 1:
        frames = frames[0]

    inner_factory.natural = len(frames[0])
    return inner_factory


def scrolling_spinner_factory(chars, length=None, block=None, background=None,
                              right=True, hiding=True, overlay=False):
    """Create a factory of a spinner that scrolls characters from one side to
    the other, configurable with various constraints.

    Args:
        chars (str): the characters to be scrolled, either together or split in blocks
        length (Optional[int]): the natural length that should be used in the style
        block (Optional[int]): if defined, split chars in blocks with this size
        background (Optional[str]): the pattern to be used besides or underneath the animations
        right (bool): the scroll direction to animate
        hiding (bool): controls whether the animation goes outside the borders or stays inside
        overlay (bool): fixes the background in place if overlay, scrolls it otherwise

    Returns:
        a styled spinner factory

    """

    def inner_factory(length_actual=None):
        if block and not (length_actual or length):  # pragma: no cover
            raise ValueError('length must be set with block')

        ratio = float(length_actual) / length if length and length_actual else 1
        length_actual = length_actual or inner_factory.natural

        def inner_spinner():
            for _ in range(inner_spinner.cycles):
                yield next(infinite_ribbon)

        initial, block_size = 0, int((block or 0) * ratio) or len(chars)
        if hiding:
            gap = length_actual
        else:
            gap = max(0, length_actual - block_size)
            if right:
                initial = -block_size if block else abs(length_actual - block_size)

        if block:
            contents = map(lambda c: c * block_size, reversed(chars) if right else chars)
        else:
            contents = (chars,)

        window_impl = overlay_sliding_window_factory if overlay else static_sliding_window_factory
        infinite_ribbon = window_impl(background, gap, contents, length_actual, step, initial)

        inner_spinner.cycles = gap + block_size
        return inner_spinner

    step = -1 if right else 1
    background = background or ' '

    inner_factory.natural = length or len(chars)
    return inner_factory


def bouncing_spinner_factory(chars, length=None, block=None, background=None,
                             hiding=True, is_text=False, overlay=False):
    """Create a factory of a spinner that scrolls characters from one side to
    the other and bounce back, configurable with various constraints.

    Args:
        chars (Union[str, Tuple[str, str]]): the characters to be scrolled, either
            together or split in blocks. Also accepts a tuple of two strings,
            which are used one in each direction
        length (Optional[int]): the natural length that should be used in the style
        block (Optional[int]): if defined, split chars in blocks with this size
        background (Optional[str]): the pattern to be used besides or underneath the animations
        hiding (bool): controls whether the animation goes outside the borders or stays inside
        is_text (bool): optimizes text display, scrolling slower and pausing at the edges
        overlay (bool): fixes the background in place if overlay, scrolls it otherwise

    Returns:
        a styled spinner factory

    """

    def inner_factory(length_actual=None):
        first_scroll = scrolling_spinner_factory(
            right_chars, length, block, background,
            right=not is_text, hiding=hiding, overlay=overlay)(length_actual)
        second_scroll = scrolling_spinner_factory(
            left_chars, length, block, background,
            right=is_text, hiding=hiding, overlay=overlay)(length_actual)

        ratio = float(length_actual) / length if length and length_actual else 1
        length_actual = length_actual or inner_factory.natural

        def inner_spinner():
            for gen, size in (first_scroll, first_size), (second_scroll, second_size):
                for i, fill in enumerate(gen()):
                    if i <= size:
                        for _ in range(frames_edges if i in (0, size) else frames_middle):
                            yield fill

        first_block_size = int((block or 0) * ratio) or len(right_chars)
        second_block_size = int((block or 0) * ratio) or len(left_chars)
        first_size = length_actual + first_block_size if hiding \
            else abs(length_actual - first_block_size)
        second_size = length_actual + second_block_size if hiding \
            else abs(length_actual - second_block_size)

        inner_spinner.cycles = first_size + second_size
        return inner_spinner

    right_chars, left_chars = chars if isinstance(chars, tuple) else (chars, chars)
    frames_edges, frames_middle = (6, 2) if is_text else (1, 1)

    inner_factory.natural = length or max(len(right_chars), len(left_chars))
    return inner_factory


def compound_spinner_factory(*spinner_factories, alongside=True):
    """Create a factory of a spinner that combines other spinners together, either
    alongside simultaneously or one at a time sequentially.

    Alongside
        advantages: each spinner can have a different length (their natural lengths).
        compromises: the number of cycles will be the longest of the spinners, so
            the shorter ones must be repeated.

    Sequential
        advantages: each spinner can have a different number of cycles.
        compromises: the length will be the longest of the spinners, so the others
            must be stretched.

    Args:
        spinner_factories (other spinners): the spinners to be combined
        alongside (bool): alongside if True, sequential otherwise

    Returns:
        a styled spinner factory

    """

    def inner_factory(length_actual=None):
        if alongside:
            def inner_spinner():
                for fills in zip(range(inner_spinner.cycles), *players):
                    yield ''.join(fills[1:])[:length_actual]  # needed because of the `or 1` -->

            if length_actual:
                # calculate weighted spreading of the available space for all factories.
                lengths = (length_actual / inner_factory.natural * x for x in naturals)
                lengths = [round(x) for x in accumulate(lengths)]  # needs to be resolved.
                lengths = tuple(map(lambda a, b: (a - b) or 1, lengths, [0] + lengths))  # <-- here
            else:
                lengths = (None,) * len(spinner_factories)
            spinners = [factory(length)
                        for factory, length in zip(spinner_factories, lengths)]
            cycles = max(spinner.cycles for spinner in spinners)
            players = [spinner_player(x) for x in spinners]
            inner_spinner.players = players
        else:
            def inner_spinner():
                for spinner in spinners:
                    yield from spinner()

            spinners = [factory(length_actual or inner_factory.natural)
                        for factory in spinner_factories]
            cycles = sum(spinner.cycles for spinner in spinners)

        inner_spinner.cycles = cycles
        return inner_spinner

    naturals = [spinner.natural for spinner in spinner_factories]  # needs to be resolved.
    inner_factory.natural = sum(naturals) if alongside else max(naturals)
    return inner_factory


def delayed_spinner_factory(spinner_factory, copies, offset):
    """Create a factory of a spinner that copies itself several times,
    with an increasing iteration offset between them.
    """

    # this spinner is not actually a spinner, it is more a helper factory method.
    # it does not define an inner_spinner, only creates a compound spinner internally.
    def inner_factory(length_actual=None):
        # it needed to have two levels to wait for the length_actual, since this
        # argument can change the number of copies.
        copies_actual = math.ceil(length_actual / spinner_factory.natural) \
            if length_actual else copies
        result = compound_spinner_factory(*((spinner_factory,) * copies_actual))(length_actual)
        for i, s in enumerate(result.players):
            for _ in range(i * offset):
                next(s)
        return result

    inner_factory.natural = spinner_factory.natural * copies
    return inner_factory
