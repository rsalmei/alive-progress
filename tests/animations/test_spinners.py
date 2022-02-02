import pytest

from alive_progress.animations.spinners import alongside_spinner_factory, \
    bouncing_spinner_factory, delayed_spinner_factory, frame_spinner_factory, \
    scrolling_spinner_factory, sequential_spinner_factory
from alive_progress.utils.cells import join_cells


@pytest.mark.parametrize('frames, expected', [
    ('a\nb', (('a', ' ', 'b'),)),
    ('abc', (('a', 'b', 'c'),)),
    (('a\nb', '\nc '), (('a b', ' c '),)),
    (('a  ', ' b ', '  c'), (('a  ', ' b ', '  c'),)),
    (('a', '(a)', ' (*) '), (('aaaaa', '(a)(a', ' (*) '),)),
    (('ok', '😺😺'), (('okok', '😺😺'),)),
])
def test_frame_spinner(frames, expected):
    spinner_factory = frame_spinner_factory(frames)
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('length, block, background, right, hide, expected', [
    (None, None, ' ', True, True, (('   ', 'c  ', 'bc ', 'abc', ' ab', '  a'),)),
    (None, None, ' ', False, True, (('   ', '  a', ' ab', 'abc', 'bc ', 'c  '),)),
    (None, None, ' ', True, False, (('abc', 'cab', 'bca'),)),
    (None, None, ' ', False, False, (('abc', 'bca', 'cab'),)),
    (2, None, '~', True, True, (('~~', 'c~', 'bc', 'ab', '~a'),)),
    (2, None, '~', True, False, (('bc', 'ab', 'ca'),)),
    (2, None, '~', False, True, (('~~', '~a', 'ab', 'bc', 'c~'),)),
    (2, None, '~', False, False, (('ab', 'bc', 'ca'),)),
    (3, None, '~', True, True, (('~~~', 'c~~', 'bc~', 'abc', '~ab', '~~a'),)),
    (3, None, '~', True, False, (('abc', 'cab', 'bca'),)),
    (3, None, '~', False, True, (('~~~', '~~a', '~ab', 'abc', 'bc~', 'c~~'),)),
    (3, None, '~', False, False, (('abc', 'bca', 'cab'),)),
    (4, None, ' ', True, True, (('    ', 'c   ', 'bc  ', 'abc ', ' abc', '  ab', '   a'),)),
    (4, None, ' ', True, False, (('abc ', ' abc', 'c ab', 'bc a'),)),
    (4, None, ' ', False, True, (('    ', '   a', '  ab', ' abc', 'abc ', 'bc  ', 'c   '),)),
    (4, None, ' ', False, False, ((' abc', 'abc ', 'bc a', 'c ab'),)),
    (4, 1, '_', True, True, (('____', 'a___', '_a__', '__a_', '___a'),
                             ('____', 'b___', '_b__', '__b_', '___b'),
                             ('____', 'c___', '_c__', '__c_', '___c'))),
    (4, 2, '_', True, False, (('aa__', '_aa_', '__aa', 'b__a'),
                              ('bb__', '_bb_', '__bb', 'c__b'),
                              ('cc__', '_cc_', '__cc', 'a__c'))),
])
def test_scrolling_spinner(length, block, background, right, hide, expected):
    spinner_factory = scrolling_spinner_factory('abc', length, block, background,
                                                right=right, hide=hide)
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('length, block, background, hide, expected', [
    (None, None, None, True, (('   ', 'c  ', 'bc ', 'abc', ' ab', '  a'),
                              ('   ', '  d', ' de', 'def', 'ef ', 'f  '),)),
    (None, None, None, False, (('abc',), ('def',),)),
    (2, None, '~', True, (('~~', 'c~', 'bc', 'ab', '~a'), ('~~', '~d', 'de', 'ef', 'f~'),)),
    (2, None, '~', False, (('bc', 'ab'), ('de', 'ef'),)),
    (3, None, '+', True, (('+++', 'c++', 'bc+', 'abc', '+ab', '++a'),
                          ('+++', '++d', '+de', 'def', 'ef+', 'f++'),)),
    (3, None, '+', False, (('abc',), ('def',),)),
    (4, None, ' ', True, (('    ', 'c   ', 'bc  ', 'abc ', ' abc', '  ab', '   a'),
                          ('    ', '   d', '  de', ' def', 'def ', 'ef  ', 'f   '),)),
    (4, None, ' ', False, (('abc ', ' abc'), (' def', 'def '),)),
    (3, 1, '_', True, (('___', 'a__', '_a_', '__a'),
                       ('___', '__d', '_d_', 'd__'),
                       ('___', 'b__', '_b_', '__b'),
                       ('___', '__e', '_e_', 'e__'),
                       ('___', 'c__', '_c_', '__c'),
                       ('___', '__f', '_f_', 'f__'))),
    (5, 2, '_', False, (('aa___', '_aa__', '__aa_', '___aa'),
                        ('___dd', '__dd_', '_dd__', 'dd___'),
                        ('bb___', '_bb__', '__bb_', '___bb'),
                        ('___ee', '__ee_', '_ee__', 'ee___'),
                        ('cc___', '_cc__', '__cc_', '___cc'),
                        ('___ff', '__ff_', '_ff__', 'ff___'))),
])
def test_bouncing_spinner(length, block, background, hide, expected):
    spinner_factory = bouncing_spinner_factory(('abc', 'def'), length, block, background,
                                               right=True, hide=hide)
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('inputs, expected', [
    (('123', 'abc'), (('1a', '2b', '3c'),)),
    (('12', 'abc'), (('1a', '2b', '1c', '2a', '1b', '2c'),)),
    ((('12', '34', '56'), 'ab'), (('12a', '34b', '56a', '12b', '34a', '56b'),)),
])
def test_alongside_spinner(inputs, expected, spinner_test):
    spinner_factory = alongside_spinner_factory(*(spinner_test(x) for x in inputs))
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('inputs, expected', [
    (('123', 'abc'), (('1a', '2b', '3c'),)),
    (('12', 'abc'), (('1a', '2b'), ('1c', '2a'), ('1b', '2c'))),
    ((('12', '34', '56'), 'ab'), (('12a', '34b', '56a'), ('12b', '34a', '56b'))),
])
def test_alongside_spinner_with_pivot(inputs, expected, spinner_test):
    spinner_factory = alongside_spinner_factory(*(spinner_test(x) for x in inputs), pivot=0)
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('inputs, expected', [
    (('123', 'abc'), (('11a', '22b', '33c'),)),
    (('12', 'abc'), (('11a', '22b', '11c', '22a', '11b', '22c'),)),
    ((('12', '34', '56'), 'ab'), (('12a', '34b', '56a', '12b', '34a', '56b'),)),
])
def test_alongside_spinner_custom(inputs, expected, spinner_test):
    spinner_factory = alongside_spinner_factory(*(spinner_test(x) for x in inputs))
    spinner = spinner_factory(3)  # custom spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('inputs, expected', [
    (('123', 'abc'), (('1',), ('a',), ('2',), ('b',), ('3',), ('c',))),
    (('12', 'abc'), (('1',), ('a',), ('2',), ('b',), ('1',), ('c',),
                     ('2',), ('a',), ('1',), ('b',), ('2',), ('c',))),
    ((('12', '34', '56'), 'ab'), (('1', '2'), ('a',), ('3', '4'), ('b',), ('5', '6'), ('a',),
                                  ('1', '2'), ('b',), ('3', '4'), ('a',), ('5', '6'), ('b',))),
])
def test_sequential_spinner(inputs, expected, spinner_test):
    spinner_factory = sequential_spinner_factory(*(spinner_test(*x) for x in inputs))
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('inputs, expected', [
    (('123', 'abc'), (('1',), ('2',), ('3',), ('a',), ('b',), ('c',))),
    (('12', 'abc'), (('1',), ('2',), ('a',), ('b',), ('c',))),
    ((('12', '34', '56'), 'ab'), (('1', '2'), ('3', '4'), ('5', '6'), ('a',), ('b',))),
])
def test_sequential_spinner_no_intermix(inputs, expected, spinner_test):
    spinner_factory = sequential_spinner_factory(*(spinner_test(*x) for x in inputs),
                                                 intermix=False)
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected


@pytest.mark.parametrize('copies, offset, expected', [
    (3, 1, (('123', '234', '345', '451', '512'),)),
    (4, 2, (('1352', '2413', '3524', '4135', '5241'),)),
])
def test_delayed_spinner(copies, offset, expected, spinner_test):
    spinner_factory = delayed_spinner_factory(spinner_test('12345'), copies, offset)
    spinner = spinner_factory()  # natural spinner size.
    assert tuple(tuple(join_cells(f) for f in spinner()) for _ in expected) == expected
