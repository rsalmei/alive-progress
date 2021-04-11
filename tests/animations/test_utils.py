from itertools import chain

import pytest

from alive_progress.animations.utils import extract_fill_graphemes, overlay_sliding_window, \
    round_even, spinner_player, split_options, spread_weighted, static_sliding_window
from alive_progress.utils.cells import join_cells


@pytest.mark.parametrize('gap, contents, length, right, initial, expected_6', [
    (0, ('abc',), 1, False, 0, ('a', 'b', 'c', 'a', 'b', 'c')),
    (0, ('abc',), 1, True, 0, ('a', 'c', 'b', 'a', 'c', 'b')),
    (0, ('abc',), 1, False, -2, ('b', 'c', 'a', 'b', 'c', 'a')),
    (0, ('abc',), 1, True, 1, ('b', 'a', 'c', 'b', 'a', 'c')),
    (0, ('abcdef',), 4, True, 7, ('bcde', 'abcd', 'fabc', 'efab', 'defa', 'cdef')),
    (1, ('abc',), 1, False, 0, ('!', 'a', 'b', 'c', '!', 'a')),
    (1, ('abc',), 1, True, 0, ('!', 'c', 'b', 'a', '!', 'c')),
    (1, ('abc',), 1, False, -2, ('b', 'c', '!', 'a', 'b', 'c')),
    (1, ('abc',), 1, True, 1, ('a', '!', 'c', 'b', 'a', '!')),
    (1, ('abcdef',), 4, True, 7, ('!abc', 'f!ab', 'ef!a', 'def!', 'cdef', 'bcde')),
    (1, ('abc', 'xy'), 1, False, 0, ('!', 'a', 'b', 'c', '!', 'x')),
    (1, ('abc', 'xy'), 1, True, 0, ('!', 'y', 'x', '!', 'c', 'b')),
    (1, ('abc', 'xy'), 1, False, -2, ('x', 'y', '!', 'a', 'b', 'c')),
    (1, ('abc', 'xy'), 1, True, 1, ('a', '!', 'y', 'x', '!', 'c')),
    (1, ('abcdef', 'xy'), 4, True, 7, ('!xy!', 'f!xy', 'ef!x', 'def!', 'cdef', 'bcde')),
])
def test_static_sliding_window(gap, contents, length, right, initial, expected_6):
    ribbon = static_sliding_window('!@#$%', gap, contents, length, right, initial)
    assert tuple(join_cells(next(ribbon)) for _ in range(6)) == expected_6


@pytest.mark.parametrize('gap, contents, length, right, initial, expected_6', [
    (1, ('abcdef',), 4, False, 0, ('!abc', 'abcd', 'bcde', 'cdef', 'def$', 'ef#a')),
    (1, ('abcdef',), 4, True, 0, ('!abc', 'f@ab', 'ef#a', 'def$', 'cdef', 'bcde')),
    (2, ('abc', 'xy'), 2, False, 0, ('!@', '!a', 'ab', 'bc', 'c@', '!@')),
    (3, ('abc', 'xy'), 4, True, 0, ('!@#a', 'y@#$', 'xy#$', '!xy$', '!@xy', '!@#x')),
    (4, ('abc', 'xy'), 6, False, -2, ('xy#$%!', 'y@#$%a', '!@#$ab', '!@#abc', '!@abc!', '!abc%!')),
])
def test_overlay_sliding_window(gap, contents, length, right, initial, expected_6):
    ribbon = overlay_sliding_window('!@#$%', gap, contents, length, right, initial)
    assert tuple(join_cells(next(ribbon)) for _ in range(6)) == expected_6


def test_sliding_window_error():
    with pytest.raises(AssertionError):
        static_sliding_window('back', 10, ('window that slides',), 100, 1, 0)


def spinner_cycle_123():
    # noinspection PyUnusedLocal
    def inner_factory(length=None):
        def inner_spinner():
            yield from '123'

        return inner_spinner

    return inner_factory


def test_spinner_player():
    player = spinner_player(spinner_cycle_123()())
    assert tuple(next(player) for _ in range(4)) == ('1', '2', '3', '1')


@pytest.mark.parametrize('text, default, expected', [
    (None, '<>', '<>'),
    ('', '<>', '<>'),
    ('a', '---', 'a--'),
    ('ab', '!!!', 'ab!'),
    ('ab', '$$', 'ab'),
    ('abc', '##', 'ab'),
])
def test_extract_exactly_n_chars(text, default, expected):
    assert ''.join(chain.from_iterable(extract_fill_graphemes(text, default))) == expected


SAME = object()


@pytest.mark.parametrize('param, expected', [
    (None, (None, None)),
    ('', ('', '')),
    ('ok', ('ok', 'ok')),

    (('a',), SAME),
    (('a', 'b'), SAME),
    (('a', 'b', 'c'), SAME),
])
def test_split_options(param, expected):
    if expected is SAME:
        expected = param
    assert split_options(param) == expected


@pytest.mark.parametrize('actual_length, naturals, expected', [
    (2, (10,), (2,)),
    (8, (2, 2), (4, 4)),
    (14, (2, 4, 1), (4, 8, 2)),
    (12, (10, 24, 8), (3, 7, 2))
])
def test_spread_weighted(actual_length, naturals, expected):
    assert spread_weighted(actual_length, naturals) == expected


@pytest.mark.parametrize('num, expected', [
    (2, 2),
    (3, 4),
    (2.9, 2),
    (3.1, 4),
])
def test_round_even(num, expected):
    assert round_even(num) == expected
