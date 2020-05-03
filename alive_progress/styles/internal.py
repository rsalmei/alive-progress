# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from collections import OrderedDict

from ..animations.bars import standard_bar_factory, unknown_bar_factory
from ..animations.spinners import bouncing_spinner_factory, compound_spinner_factory, \
    delayed_spinner_factory, frame_spinner_factory, scrolling_spinner_factory


def _wrap_ordered(result, desired_order):
    assert set(result) == set(desired_order), \
        'missing={} extra={}'.format(str(set(result) - set(desired_order)),
                                     str(set(desired_order) - set(result)))
    if sys.version_info >= (3, 7):
        return result
    return OrderedDict((x, result[x]) for x in desired_order)


def __create_spinners():
    classic = frame_spinner_factory(r'-\|/')
    stars = scrolling_spinner_factory('*', 4, 1, hiding=False)
    arrow = frame_spinner_factory('←↖↑↗→↘↓↙')
    arrows = delayed_spinner_factory(arrow, 3, 1)
    vertical = frame_spinner_factory('▁▂▃▄▅▆▇█▇▆▅▄▃▂')
    waves = delayed_spinner_factory(vertical, 3, 2)
    waves2 = delayed_spinner_factory(vertical, 3, 5)
    waves3 = delayed_spinner_factory(vertical, 3, 7)
    horizontal = frame_spinner_factory('▏▎▍▌▋▊▉█▉▊▋▌▍▎▏')
    dots = frame_spinner_factory('⠁⠈⠐⠠⢀⡀⠄⠂')
    dots_reverse = frame_spinner_factory('⣾⣷⣯⣟⡿⢿⣻⣽')
    dots_waves = delayed_spinner_factory(dots, 5, 1)
    dots_waves2 = delayed_spinner_factory(dots, 5, 2)
    ball_scrolling = scrolling_spinner_factory('●', 3, 0, blank='∙')
    balls_scrolling = scrolling_spinner_factory('●', 3, 1, blank='∙')
    ball_bouncing = bouncing_spinner_factory('●', 8, 0, hiding=False)
    balls_bouncing = bouncing_spinner_factory('●', 8, 1, hiding=False)
    dots_recur = bouncing_spinner_factory('.', 3, 3)
    bar_recur = bouncing_spinner_factory('=', 4, 3)
    pointer = scrolling_spinner_factory('►', 5, 2, hiding=False)
    arrows_recur = bouncing_spinner_factory('→', 6, 3, '←')
    triangles = bouncing_spinner_factory('▶', 6, 2, '◀', hiding=False)
    _triangles = bouncing_spinner_factory('▶▷', 6, 3, '◁◀')
    triangles2 = delayed_spinner_factory(_triangles, 2, 9)
    brackets = bouncing_spinner_factory('>', 8, 3, '<', hiding=False)
    balls_filling = bouncing_spinner_factory('∙●', 10, 5, left_chars='○', hiding=False)
    notes = bouncing_spinner_factory('♩♪', 10, 4, left_chars='♫♬')
    notes2 = bouncing_spinner_factory('♩♪', 10, 4, left_chars='♫♬', hiding=False)
    notes_scrolling = scrolling_spinner_factory('♩♪♫♬', 10, 4, hiding=False)

    _arrows_left = scrolling_spinner_factory('<.', 6, 4, right=False)
    _arrows_right = scrolling_spinner_factory('>.', 6, 4, right=True)
    arrows_incoming = compound_spinner_factory(_arrows_right, _arrows_left)
    arrows_outgoing = compound_spinner_factory(_arrows_left, _arrows_right)
    real_arrow = scrolling_spinner_factory('>>------>', 18)

    fish = scrolling_spinner_factory("><(((('>", 15, hiding=False)
    fish2 = scrolling_spinner_factory('¸.·´¯`·.·´¯`·.¸¸.·´¯`·.¸><(((º>', 16)
    fish_bouncing = bouncing_spinner_factory("><(((('>", 18, left_chars="<'))))><", hiding=False)
    fishes = bouncing_spinner_factory('><>     ><>', 18, left_chars='<><  <><    <><')
    message_scrolling = scrolling_spinner_factory('please wait...', right=False)
    message_bouncing = bouncing_spinner_factory('please', 15,
                                                left_chars='wait', hiding=False)
    long_message = bouncing_spinner_factory(
        'processing', 15, left_chars='well, this is taking longer than anticipated, hold on'
    )
    pulse = frame_spinner_factory(
        r'•–––––––––––––',
        r'–•––––––––––––',
        r'––•–––––––––––',
        r'–––•––––––––––',
        r'––––•–––––––––',
        r'–––––√––––––––',
        r'–––––√\–––––––',
        r'–––––√\/––––––',
        r'–––––√\/•–––––',
        r'–––––√\/–•––––',
        r'––––––\/––•–––',
        r'–––––––/–––•––',
        r'––––––––––––•–',
        r'–––––––––––––•',
    )

    result = {k: (v, unknown_bar_factory(v))
              for k, v in locals().items() if not k.startswith('_')}
    desired_order = 'classic stars arrow arrows vertical waves waves2 waves3 horizontal dots ' \
                    'dots_reverse dots_waves dots_waves2 ball_scrolling balls_scrolling ' \
                    'ball_bouncing balls_bouncing dots_recur bar_recur pointer arrows_recur ' \
                    'triangles triangles2 brackets balls_filling notes notes2 notes_scrolling ' \
                    'arrows_incoming arrows_outgoing real_arrow fish fish2 fish_bouncing fishes ' \
                    'message_scrolling message_bouncing long_message pulse'.split()
    return _wrap_ordered(result, desired_order)


SPINNERS = __create_spinners()


def __create_bars():
    classic = standard_bar_factory(borders='[]')
    classic2 = standard_bar_factory(background='.', chars='#', borders='[]', tip='')
    smooth = standard_bar_factory(chars='▏▎▍▌▋▊▉█', tip=None, errors='⚠✗')
    blocks = standard_bar_factory(chars='▏▎▍▌▋▊▉', tip=None, errors='⚠✗')
    bubbles = standard_bar_factory(chars='∙○⦿●', borders='<>', tip='', errors='⚠✗')
    circles = standard_bar_factory(background='○', chars='●', borders='<>', tip='', errors='⚠✗')
    hollow = standard_bar_factory(chars='❒', borders='<>', tip='▷', errors='⚠✗')
    squares = standard_bar_factory(background='❒', chars='■', borders='<>', tip='', errors='⚠✗')
    solid = standard_bar_factory(chars='■', borders='<>', tip='►', errors='⚠✗')
    checks = standard_bar_factory(chars='✓', tip='', errors='⚠✗')
    filling = standard_bar_factory(chars='▁▂▃▄▅▆▇█', tip=None, errors='⚠✗')

    result = {k: v for k, v in locals().items() if not k.startswith('_')}
    desired_order = 'classic classic2 smooth blocks bubbles circles hollow squares solid checks ' \
                    'filling'.split()
    return _wrap_ordered(result, desired_order)


BARS = __create_bars()


def __create_themes():
    smooth = dict(spinner='waves', bar='smooth', unknown='triangles')
    # noinspection PyShadowingBuiltins
    ascii = dict(spinner='classic', bar='classic', unknown='brackets')

    result = {k: v for k, v in locals().items() if not k.startswith('_')}
    desired_order = 'smooth ascii'.split()
    return _wrap_ordered(result, desired_order)


THEMES = __create_themes()
