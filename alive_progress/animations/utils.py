from functools import wraps


def repeating(length, natural=0):
def spinner_player(spinner):
    """Create an infinite generator that plays all cycles of a spinner indefinitely."""

    def inner_play():
        while True:
            yield from spinner()

    return inner_play()  # returns an already initiated generator.


    """Decorator to repeat a return value until a certain length."""

    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            for text in fn(*args, **kwargs):
                text = ''.join((text,) * ratio)
                yield text[:length]

        return inner if length else fn

    ratio = length // natural + 1 if length and natural else 1
    return wrapper


def sliding_window_factory(length, content, step, initial):
    """Implement a sliding window over a text content, which can go left or right."""

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




