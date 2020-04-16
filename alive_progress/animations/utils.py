# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from functools import wraps


def repeating(length, natural=0):
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
