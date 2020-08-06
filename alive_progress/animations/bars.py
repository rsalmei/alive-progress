import math

from .utils import bordered, extract_fill_chars, spinner_player


def standard_bar_factory(chars, tip=None, background=None, borders=None, errors=None):
    def inner_standard_bar_factory(length):
        def char_fill(complete, filling):
            fill = chars[-1] * complete
            if filling:
                fill = fill + chars[filling - 1]
            return fill[len_tip:]

        def invisible_fill(complete, filling):
            return padding[:complete + bool(filling) - len_tip]

        @bordered(borders, '||')
        def draw_bar(percent, end=False):
            virtual_fill = round(virtual_length * max(0., percent))
            complete, filling = divmod(virtual_fill, len_chars)
            fill = fill_style(complete, filling)

            if percent >= 1.:
                return fill[:length], None if percent == 1. else overflow

            size_fill = complete + bool(filling)
            if end:
                texts = fill, underflow, blanks
            elif size_fill > len_tip:
                texts = fill, tip, padding[size_fill:]
            elif size_fill == len_tip:
                texts = tip, padding[size_fill:]
            else:
                texts = tip[-size_fill:] if size_fill else '', padding[size_fill:]
            return ''.join(texts)[:length], None  # with normal border

        virtual_length, blanks = len_chars * (length + len_tip), ' ' * length
        padding = background * math.ceil((length + len_tip) / len(background))
        fill_style = char_fill if chars else invisible_fill
        return draw_bar

    if not chars and not tip:
        raise ValueError('tip is mandatory for transparent bars')
    tip, background = tip or '', background or ' '
    underflow, overflow = extract_fill_chars(errors, '⚠✗')
    len_chars, len_tip = len(chars) or 1, len(tip)

    return inner_standard_bar_factory


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
