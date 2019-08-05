# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import math
import operator
from functools import wraps
from itertools import chain, repeat


def _ensure_length(length, natural=0):
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            for text in fn(*args, **kwargs):
                text = ''.join((text,) * ratio)
                yield text[:length]

        return inner if length else fn

    ratio = length // natural + 1 if length and natural else 1
    return wrapper


def _sliding_window_factory(length, content, step, initial):
    def sliding_window():
        pos = initial
        while True:
            if pos < 0:
                pos += original
            elif pos >= original:
                pos -= original
            yield content[pos:pos + length]
            pos += step

    original, window = len(content), sliding_window()
    content += content[:length]
    return window


def frame_spinner_factory(*frames):
    """Create a factory of a spinner that delivers frames in sequence."""

    def inner_factory(length=None):
        @_ensure_length(length, inner_factory.natural)
        def inner_spinner():
            for frame in frames:
                yield frame

        inner_spinner.cycles = len(frames)
        return inner_spinner

    if len(frames) == 1:
        frames = frames[0]

    inner_factory.natural = len(frames[0])
    return inner_factory


def scrolling_spinner_factory(chars, length=None, block=None, blank=' ', right=True, hiding=True):
    """Create a factory of a spinner that scrolls characters alongside a line."""

    def inner_factory(length_actual=None):
        if block and not (length_actual or length):
            raise ValueError('length must be set with block')

        ratio = float(length_actual) / length if length and length_actual else 1
        length_actual = length_actual or inner_factory.natural

        @_ensure_length(length_actual)
        def inner_spinner():
            for _ in range(inner_spinner.cycles):
                yield next(infinite_ribbon)

        if not hiding and block and block >= length_actual:
            block_size = length_actual - 1
        else:
            block_size = int((block or 0) * ratio) or len(chars)

        initial = 0
        if hiding:
            gap = length_actual
        else:
            gap = max(0, length_actual - block_size)
            if right:
                initial = -block_size

        if block:
            content = reversed(chars) if right else chars
            content = ''.join(chain.from_iterable(zip(repeat(blank * gap),
                                                      map(lambda c: c * block_size, content))))
        else:
            content = ''.join(chain(blank * gap, chars))

        infinite_ribbon = _sliding_window_factory(length_actual, content, step, initial)

        inner_spinner.cycles = gap + block_size
        return inner_spinner

    step = -1 if right else 1

    inner_factory.natural = length or len(chars)
    return inner_factory


def bouncing_spinner_factory(right_chars, length, block=None, left_chars=None,
                             blank=' ', hiding=True):
    """Create a factory of a spinner that bounces characters inside a line."""

    def inner_factory(length_actual=None):
        right_scroll = scrolling_spinner_factory(right_chars, length, block=block, blank=blank,
                                                 right=True, hiding=hiding)(length_actual)
        left_scroll = scrolling_spinner_factory(left_chars, length, block=block, blank=blank,
                                                right=False, hiding=hiding)(length_actual)

        ratio = float(length_actual) / length if length and length_actual else 1
        length_actual = length_actual or inner_factory.natural

        @_ensure_length(length_actual)
        def inner_spinner():
            for i, fill in enumerate(right_scroll()):
                if i < right_direction_size:
                    yield fill
            for i, fill in enumerate(left_scroll()):
                if i < left_direction_size:
                    yield fill

        right_block_size = int((block or 0) * ratio) or len(right_chars)
        left_block_size = int((block or 0) * ratio) or len(left_chars)
        right_direction_size = length_actual + right_block_size \
            if hiding else abs(length_actual - right_block_size) or 1
        left_direction_size = length_actual + left_block_size \
            if hiding else abs(length_actual - left_block_size) or 1

        inner_spinner.cycles = right_direction_size + left_direction_size
        return inner_spinner

    left_chars = left_chars or right_chars

    inner_factory.natural = length
    return inner_factory


def delayed_spinner_factory(spinner_factory, copies, offset):
    """Create a factory of a spinner that copies itself several times,
    with an increasing iteration offset between them.
    """

    def inner_factory(length=None):
        copies_actual = int(math.ceil(length / spinner_factory.natural)) if length else copies
        result = compound_spinner_factory(*((spinner_factory,) * copies_actual))(length)
        for i, s in enumerate(result.players):
            for _ in range(i * offset):
                next(s)
        return result

    inner_factory.natural = spinner_factory.natural * copies
    return inner_factory


def compound_spinner_factory(*spinner_factories):
    """Create a factory of a spinner that combines any other spinners together."""

    def inner_factory(length=None):
        @_ensure_length(length)
        def inner_spinner():
            for fills in zip(range(inner_spinner.cycles), *players):
                yield ''.join(fills[1:])

        # this could be weighted on the natural length of the factories,
        # but they will usually be the same types of factories.
        each_length = int(math.ceil(length / len(spinner_factories))) if length else None
        spinners = [factory(each_length) for factory in spinner_factories]
        op_cycles = operator.attrgetter('cycles')
        longest = max(spinners, key=op_cycles)
        players = [spinner_player(x) for x in spinners]

        # noinspection PyUnresolvedReferences
        inner_spinner.cycles = longest.cycles
        inner_spinner.players = players
        return inner_spinner

    op_natural = operator.attrgetter('natural')
    inner_factory.natural = sum(map(op_natural, spinner_factories))
    return inner_factory


def spinner_player(spinner):
    """Create an infinite generator that plays all cycles of a spinner indefinitely."""

    def inner_play():
        while True:
            for c in spinner():
                yield c

    return inner_play()  # returns an already initiated generator.
