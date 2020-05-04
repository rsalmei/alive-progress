# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import math
from itertools import chain

from .utils import spinner_player


def standard_bar_factory(chars='=', borders='||', background=' ', tip='>', errors='!x'):
    def inner_factory(length):
        def inner_standard_bar(percent, end):
            virtual_fill = int(virtual_length * max(0., min(1., percent)))
            complete, filling = divmod(virtual_fill, len(chars))
            fill = chars[-1] * complete
            if filling:
                fill += chars[filling - 1]

            if percent < 1.:
                texts = (underflow, blanks) if end else (tip, padding[len(fill):])
                return ''.join(chain((fill,), texts))[:length], True  # with border
            if percent == 1.:
                return fill, True  # no tip, with border
            return fill + overflow, False  # no border

        def draw_bar(percent, end=False):
            bar, right = inner_standard_bar(percent, end)
            return draw_bar.left_border + bar + (draw_bar.right_border if right else '')

        virtual_length = length * len(chars)
        padding = background * int(math.ceil((length - len(tip)) / len(background)))
        blanks = ' ' * (length - len(tip))

        draw_bar.left_border, draw_bar.right_border = borders
        return draw_bar

    tip = tip or ''
    underflow, overflow = errors

    return inner_factory


def unknown_bar_factory(spinner_factory):
    def inner_factory(length, receipt_bar_factory=None):
        # noinspection PyUnusedLocal
        def draw_bar(percent=None, end=False):
            if end:
                return receipt_bar(1., end=True)
            # noinspection PyUnresolvedReferences
            return receipt_bar.left_border + next(player) + receipt_bar.right_border

        player = spinner_player(spinner_factory(length))
        receipt_bar = (receipt_bar_factory or __default_bar)(length)

        return draw_bar

    return inner_factory


__default_bar = standard_bar_factory()
