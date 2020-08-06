import math
from functools import wraps


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


def sliding_window_factory(length, content, step, initial):
    """Implement a sliding window over a text content, which can go left or right."""
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
    assert length <= original, 'window slides inside content, length must be <= len(content)'
    content += content[:length]
    return window




