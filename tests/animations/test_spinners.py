# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from alive_progress.animations.spinners import bouncing_spinner_factory, delayed_spinner_factory, \
    frame_spinner_factory, scrolling_spinner_factory, compound_spinner_factory


@pytest.mark.parametrize('frames, expected', [
    (('abc',), ('a', 'b', 'c')),
    (('a  ', ' b ', '  c'), ('a  ', ' b ', '  c')),
])
def test_frame_spinner(frames, expected):
    spinner_factory = frame_spinner_factory(*frames)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    cycle = spinner()
    assert tuple(cycle) == expected


@pytest.mark.parametrize('length, block, blank, right, hiding, expected', [
    (None, None, ' ', True, True, (('   ', 'c  ', 'bc ', 'abc', ' ab', '  a'),)),
    (None, None, ' ', False, True, (('   ', '  a', ' ab', 'abc', 'bc ', 'c  '),)),
    (None, None, ' ', True, False, (('abc', 'cab', 'bca'),)),
    (None, None, ' ', False, False, (('abc', 'bca', 'cab'),)),
    (2, None, '~', True, True, (('~~', 'c~', 'bc', 'ab', '~a'),)),
    (2, None, '~', False, True, (('~~', '~a', 'ab', 'bc', 'c~'),)),
    (4, None, ' ', True, True, (('    ', 'c   ', 'bc  ', 'abc ', ' abc', '  ab', '   a'),)),
    (4, None, ' ', False, True, (('    ', '   a', '  ab', ' abc', 'abc ', 'bc  ', 'c   '),)),
    (4, 1, '_', True, True, (('____', 'a___', '_a__', '__a_', '___a'),
                             ('____', 'b___', '_b__', '__b_', '___b'),
                             ('____', 'c___', '_c__', '__c_', '___c'))),
    (4, 2, '_', True, False, (('aa__', '_aa_', '__aa', 'b__a'),
                              ('bb__', '_bb_', '__bb', 'c__b'),
                              ('cc__', '_cc_', '__cc', 'a__c'))),
])
def test_scrolling_spinner(length, block, blank, right, hiding, expected):
    spinner_factory = scrolling_spinner_factory('abc', length, block, blank, right, hiding)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    for result in expected:
        cycle = spinner()
        assert tuple(cycle) == result


@pytest.mark.parametrize('length, block, blank, hiding, expected', [
    (3, None, ' ', True, (('   ', 'c  ', 'bc ', 'abc', ' ab', '  a',
                           '   ', '  d', ' de', 'def', 'ef ', 'f  '),)),
    (2, None, '~', True, (('~~', 'c~', 'bc', 'ab', '~a', '~~', '~d', 'de', 'ef', 'f~'),)),
    (3, None, ' ', False, (('abc', 'def'),)),
    (6, None, ' ', False, (('abc   ', ' abc  ', '  abc ', '   def', '  def ', ' def  '),)),
    (3, 1, '_', True, (('___', 'a__', '_a_', '__a', '___', '__d', '_d_', 'd__'),
                       ('___', 'b__', '_b_', '__b', '___', '__e', '_e_', 'e__'),
                       ('___', 'c__', '_c_', '__c', '___', '__f', '_f_', 'f__'))),
    (5, 2, '_', False, (('aa___', '_aa__', '__aa_', '___dd', '__dd_', '_dd__'),
                        ('bb___', '_bb__', '__bb_', '___ee', '__ee_', '_ee__'),
                        ('cc___', '_cc__', '__cc_', '___ff', '__ff_', '_ff__'))),
])
def test_bouncing_spinner(length, block, blank, hiding, expected):
    spinner_factory = bouncing_spinner_factory('abc', length, block, 'def', blank, hiding)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    for result in expected:
        cycle = spinner()
        assert tuple(cycle) == result


@pytest.mark.parametrize('outputs, expected', [
    (('123', 'abc'), ('1a', '2b', '3c')),
    (('12345', 'abc'), ('1a', '2b', '3c', '4a', '5b')),
    ((('123', '456'), 'abc'), ('123a', '456b', '123c')),
])
def test_compound_spinner(outputs, expected, spinner_test):
    spinner_factory = compound_spinner_factory(*(spinner_test(x) for x in outputs))
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    cycle = spinner()
    assert tuple(cycle) == expected


@pytest.mark.parametrize('copies, offset, expected', [
    (3, 1, ('123', '234', '345', '451', '512')),
    (4, 2, ('1352', '2413', '3524', '4135', '5241')),
])
def test_delayed_spinner(copies, offset, expected, spinner_test):
    spinner_factory = delayed_spinner_factory(spinner_test('12345'), copies, offset)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    cycle = spinner()
    assert tuple(cycle) == expected
