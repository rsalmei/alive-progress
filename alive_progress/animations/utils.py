import math
from functools import wraps
from itertools import chain, repeat


def spinner_player(spinner):
    """Create an infinite generator that plays all cycles of a spinner indefinitely."""

    def inner_play():
        while True:
            yield from spinner()

    return inner_play()  # returns an already initiated generator.


def repeating(length):
    """Decorator to repeat a return value until a certain length."""

    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            for text in fn(*args, **kwargs):
                yield (text * math.ceil((length or 1) / len(text)))[:length]

        return inner if length else fn

    assert not length or length > 0, 'length must be None or non negative'
    return wrapper


def bordered(borders, default):
    """Decorator to include controllable borders in the outputs of a function."""

    def wrapper(fn):
        @wraps(fn)
        def inner_dynamic(*args, **kwargs):
            content, right = fn(*args, **kwargs)
            return left_border + content + (right or right_border)

        return inner_dynamic

    left_border, right_border = extract_fill_chars(borders, default)

    return wrapper


def extract_fill_chars(string, default):
    """Extract the exact same number of chars as default, filling missing ones."""
    if not string:
        return default
    return (string * math.ceil(len(default) / len(string)))[:len(default)]


def static_sliding_window_factory(sep, gap, contents, length, step, initial):
    """Implement a sliding window over some content interspersed with a separator.
    It is very efficient, storing data in only one string.

    Note that the implementation is "static" in the sense that the content is pre-
    calculated and maintained static, but actually when the window slides both the
    separator and content seem to be moved.

    """

    def sliding_window():
        pos = initial
        while True:
            if pos < 0:
                pos += original
            elif pos >= original:
                pos -= original
            yield content[pos:pos + length]
            pos += step

    adjusted_sep = (sep * math.ceil(gap / len(sep)))[:gap]
    content = ''.join(chain.from_iterable(zip(repeat(adjusted_sep), contents)))
    original = len(content)
    assert length <= original, 'window slides inside content, length must be <= len(content)'
    content += content[:length]
    return sliding_window()




