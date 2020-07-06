# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


def to_elapsed_text(seconds, precise):
    seconds = round(seconds, 1 if precise else 0)
    if seconds < 60.:
        return '{:{}f}s'.format(seconds, .1 if precise else .0)

    minutes, seconds = divmod(seconds, 60.)
    if minutes < 60.:
        return '{:.0f}:{:0{}f}'.format(minutes, seconds, 4.1 if precise else 2.0)

    hours, minutes = divmod(minutes, 60.)
    return '{:.0f}:{:02.0f}:{:0{}f}'.format(hours, minutes, seconds, 4.1 if precise else 2.0)
