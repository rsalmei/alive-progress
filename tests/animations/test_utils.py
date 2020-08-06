import pytest

from alive_progress.animations.utils import extract_fill_chars, overlay_sliding_window_factory, \
    repeating, static_sliding_window_factory, \
    spinner_player


@pytest.mark.parametrize('length, text, expected', [
    (None, 'text', 'text'),
    (0, 'text', 'text'),
    (10, 'abc', 'abcabcabca'),
    (7, 'more than len', 'more th'),
])
def test_repeating(length, text, expected):
    @repeating(length)
    def func():
        yield text

    assert next(func()) == expected


def test_repeating_empty():
    @repeating(99)
    def func():
        if False:
            yield  # noqa

    with pytest.raises(StopIteration):
        next(func())


@pytest.mark.parametrize('gap, contents, length, step, initial, expected_6', [
    (0, ('abc',), 1, 1, 0, ('a', 'b', 'c', 'a', 'b', 'c')),
    (0, ('abc',), 1, -1, 0, ('a', 'c', 'b', 'a', 'c', 'b')),
    (0, ('abc',), 1, 1, -2, ('b', 'c', 'a', 'b', 'c', 'a')),
    (0, ('abc',), 1, -1, 1, ('b', 'a', 'c', 'b', 'a', 'c')),
    (0, ('abcdef',), 4, -1, 7, ('bcde', 'abcd', 'fabc', 'efab', 'defa', 'cdef')),
    (1, ('abc',), 1, 1, 0, ('!', 'a', 'b', 'c', '!', 'a')),
    (1, ('abc',), 1, -1, 0, ('!', 'c', 'b', 'a', '!', 'c')),
    (1, ('abc',), 1, 1, -2, ('b', 'c', '!', 'a', 'b', 'c')),
    (1, ('abc',), 1, -1, 1, ('a', '!', 'c', 'b', 'a', '!')),
    (1, ('abcdef',), 4, -1, 7, ('!abc', 'f!ab', 'ef!a', 'def!', 'cdef', 'bcde')),
    (1, ('abc', 'xy'), 1, 1, 0, ('!', 'a', 'b', 'c', '!', 'x')),
    (1, ('abc', 'xy'), 1, -1, 0, ('!', 'y', 'x', '!', 'c', 'b')),
    (1, ('abc', 'xy'), 1, 1, -2, ('x', 'y', '!', 'a', 'b', 'c')),
    (1, ('abc', 'xy'), 1, -1, 1, ('a', '!', 'y', 'x', '!', 'c')),
    (1, ('abcdef', 'xy'), 4, -1, 7, ('!xy!', 'f!xy', 'ef!x', 'def!', 'cdef', 'bcde')),
])
def test_static_sliding_window(gap, contents, length, step, initial, expected_6):
    ribbon = static_sliding_window_factory('!@#$%', gap, contents, length, step, initial)
    assert tuple(next(ribbon) for _ in range(6)) == expected_6


@pytest.mark.parametrize('gap, contents, length, step, initial, expected_6', [
    (1, ('abcdef',), 4, 1, 0, ('!abc', 'abcd', 'bcde', 'cdef', 'def$', 'ef#a')),
    (1, ('abcdef',), 4, -1, 0, ('!abc', 'f@ab', 'ef#a', 'def$', 'cdef', 'bcde')),
    (2, ('abc', 'xy'), 2, 1, 0, ('!@', '!a', 'ab', 'bc', 'c@', '!@')),
    (3, ('abc', 'xy'), 4, -1, 0, ('!@#a', 'y@#$', 'xy#$', '!xy$', '!@xy', '!@#x')),
    (4, ('abc', 'xy'), 6, 1, -2, ('xy#$%!', 'y@#$%a', '!@#$ab', '!@#abc', '!@abc!', '!abc%!')),
])
def test_overlay_sliding_window(gap, contents, length, step, initial, expected_6):
    ribbon = overlay_sliding_window_factory('!@#$%', gap, contents, length, step, initial)
    assert tuple(next(ribbon) for _ in range(6)) == expected_6


def test_sliding_window_error():
    with pytest.raises(AssertionError):
        static_sliding_window_factory('back', 10, ('window that slides',), 100, 1, 0)


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
    ('a', '---', 'aaa'),
    ('ab', '!!!', 'aba'),
    ('ab', '$$', 'ab'),
    ('abc', '##', 'ab'),
])
def test_extract_exactly_n_chars(text, default, expected):
    assert extract_fill_chars(text, default) == expected
