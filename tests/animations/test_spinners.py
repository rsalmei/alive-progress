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
def test_scrolling_spinner(length, block, blank, right, hiding, expected):
    spinner_factory = scrolling_spinner_factory('abc', length, block, blank, right, hiding)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    assert tuple(tuple(spinner()) for _ in expected) == expected


@pytest.mark.parametrize('length, block, blank, hiding, expected', [
    (None, None, None, True, (('   ', 'c  ', 'bc ', 'abc', ' ab', '  a',
                               '   ', '  d', ' de', 'def', 'ef ', 'f  '),)),
    (None, None, None, False, (('abc', 'def'),)),
    (2, None, '~', True, (('~~', 'c~', 'bc', 'ab', '~a', '~~', '~d', 'de', 'ef', 'f~'),)),
    (2, None, '~', False, (('bc', 'ab', 'de', 'ef'),)),
    (3, None, '+', True, (('+++', 'c++', 'bc+', 'abc', '+ab', '++a',
                           '+++', '++d', '+de', 'def', 'ef+', 'f++'),)),
    (3, None, '+', False, (('abc', 'def'),)),
    (4, None, ' ', True, (('    ', 'c   ', 'bc  ', 'abc ', ' abc', '  ab', '   a',
                           '    ', '   d', '  de', ' def', 'def ', 'ef  ', 'f   '),)),
    (4, None, ' ', False, (('abc ', ' abc', ' def', 'def '),)),
    (3, 1, '_', True, (('___', 'a__', '_a_', '__a', '___', '__d', '_d_', 'd__'),
                       ('___', 'b__', '_b_', '__b', '___', '__e', '_e_', 'e__'),
                       ('___', 'c__', '_c_', '__c', '___', '__f', '_f_', 'f__'))),
    (5, 2, '_', False, (('aa___', '_aa__', '__aa_', '___aa', '___dd', '__dd_', '_dd__', 'dd___'),
                        ('bb___', '_bb__', '__bb_', '___bb', '___ee', '__ee_', '_ee__', 'ee___'),
                        ('cc___', '_cc__', '__cc_', '___cc', '___ff', '__ff_', '_ff__', 'ff___'))),
])
def test_bouncing_spinner_no_text(length, block, blank, hiding, expected):
    spinner_factory = bouncing_spinner_factory(('abc', 'def'), length, block, blank, hiding)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    assert tuple(tuple(spinner()) for _ in expected) == expected


@pytest.mark.parametrize('length, block, blank, hiding, expected', [
    (None, None, None, True, (
            ('   ', '   ', '   ', '   ', '   ', '   ', '  a', '  a', ' ab', ' ab', 'abc', 'abc',
             'bc ', 'bc ', 'c  ', 'c  ', '   ', '   ', '   ', '   ', '   ', '   ', 'f  ', 'f  ',
             'ef ', 'ef ', 'def', 'def', ' de', ' de', '  d', '  d'),
    )),
    (None, None, None, False, (
            ('abc', 'abc', 'abc', 'abc', 'abc', 'abc', 'def', 'def', 'def', 'def', 'def', 'def'),
    )),
    (2, None, '~', True, (
            ('~~', '~~', '~~', '~~', '~~', '~~', '~a', '~a', 'ab', 'ab', 'bc', 'bc', 'c~', 'c~',
             '~~', '~~', '~~', '~~', '~~', '~~', 'f~', 'f~', 'ef', 'ef', 'de', 'de', '~d', '~d'),
    )),
    (2, None, '~', False, (
            ('ab', 'ab', 'ab', 'ab', 'ab', 'ab', 'bc', 'bc', 'bc', 'bc', 'bc', 'bc', 'ef', 'ef',
             'ef', 'ef', 'ef', 'ef', 'de', 'de', 'de', 'de', 'de', 'de'),
    )),
    (3, None, '+', True, (
            ('+++', '+++', '+++', '+++', '+++', '+++', '++a', '++a', '+ab', '+ab', 'abc', 'abc',
             'bc+', 'bc+', 'c++', 'c++', '+++', '+++', '+++', '+++', '+++', '+++', 'f++', 'f++',
             'ef+', 'ef+', 'def', 'def', '+de', '+de', '++d', '++d'),
    )),
    (3, None, ' ', False, (
            ('abc', 'abc', 'abc', 'abc', 'abc', 'abc', 'def', 'def', 'def', 'def', 'def', 'def'),
    )),
    (4, None, ' ', True, (
            ('    ', '    ', '    ', '    ', '    ', '    ', '   a', '   a', '  ab', '  ab', ' abc',
             ' abc', 'abc ', 'abc ', 'bc  ', 'bc  ', 'c   ', 'c   ', '    ', '    ', '    ', '    ',
             '    ', '    ', 'f   ', 'f   ', 'ef  ', 'ef  ', 'def ', 'def ', ' def', ' def', '  de',
             '  de', '   d', '   d'),
    )),
    (4, None, ' ', False, (
            (' abc', ' abc', ' abc', ' abc', ' abc', ' abc', 'abc ', 'abc ', 'abc ', 'abc ', 'abc ',
             'abc ', 'def ', 'def ', 'def ', 'def ', 'def ', 'def ', ' def', ' def', ' def', ' def',
             ' def', ' def'),
    )),
    (3, 1, '_', True, (
            ('___', '___', '___', '___', '___', '___', '__a', '__a', '_a_', '_a_', 'a__', 'a__',
             '___', '___', '___', '___', '___', '___', 'd__', 'd__', '_d_', '_d_', '__d', '__d'),
            ('___', '___', '___', '___', '___', '___', '__b', '__b', '_b_', '_b_', 'b__', 'b__',
             '___', '___', '___', '___', '___', '___', 'e__', 'e__', '_e_', '_e_', '__e', '__e'),
            ('___', '___', '___', '___', '___', '___', '__c', '__c', '_c_', '_c_', 'c__', 'c__',
             '___', '___', '___', '___', '___', '___', 'f__', 'f__', '_f_', '_f_', '__f', '__f')
    )),
    (5, 2, '_', False, (
            ('___aa', '___aa', '___aa', '___aa', '___aa', '___aa', '__aa_', '__aa_', '_aa__',
             '_aa__', 'aa___', 'aa___', 'aa___', 'aa___', 'aa___', 'aa___', 'dd___', 'dd___',
             'dd___', 'dd___', 'dd___', 'dd___', '_dd__', '_dd__', '__dd_', '__dd_', '___dd',
             '___dd', '___dd', '___dd', '___dd', '___dd'),
            ('___bb', '___bb', '___bb', '___bb', '___bb', '___bb', '__bb_', '__bb_', '_bb__',
             '_bb__', 'bb___', 'bb___', 'bb___', 'bb___', 'bb___', 'bb___', 'ee___', 'ee___',
             'ee___', 'ee___', 'ee___', 'ee___', '_ee__', '_ee__', '__ee_', '__ee_', '___ee',
             '___ee', '___ee', '___ee', '___ee', '___ee'),
            ('___cc', '___cc', '___cc', '___cc', '___cc', '___cc', '__cc_', '__cc_', '_cc__',
             '_cc__', 'cc___', 'cc___', 'cc___', 'cc___', 'cc___', 'cc___', 'ff___', 'ff___',
             'ff___', 'ff___', 'ff___', 'ff___', '_ff__', '_ff__', '__ff_', '__ff_', '___ff',
             '___ff', '___ff', '___ff', '___ff', '___ff')
    )),
])
def test_bouncing_spinner_is_text(length, block, blank, hiding, expected):
    spinner_factory = bouncing_spinner_factory(('abc', 'def'), length, block, blank, hiding,
                                               is_text=True)
    spinner = spinner_factory(length_actual=None)  # natural spinner size.
    assert tuple(tuple(spinner()) for _ in expected) == expected


@pytest.mark.parametrize('length_actual, inputs, expected', [
    (None, ('123', 'abc'), ('1a', '2b', '3c')),
    (None, ('12345', 'abc'), ('1a', '2b', '3c', '4a', '5b')),
    (None, (('123', '456'), 'abc'), ('123a', '456b', '123c')),
    (4, ('123', 'abc'), ('11aa', '22bb', '33cc')),
])
def test_compound_spinner_alongside(length_actual, inputs, expected, spinner_test):
    spinner_factory = compound_spinner_factory(*(spinner_test(x) for x in inputs), alongside=True)
    spinner = spinner_factory(length_actual=length_actual)
    cycle = spinner()
    assert tuple(cycle) == expected


@pytest.mark.parametrize('outputs, expected', [
    (('123', 'abc'), ('1', '2', '3', 'a', 'b', 'c')),
    (('12345', 'abc'), ('1', '2', '3', '4', '5', 'a', 'b', 'c')),
    ((('123', '456'), 'abc'), ('123', '456', 'aaa', 'bbb', 'ccc')),
])
def test_compound_spinner_sequential(outputs, expected, spinner_test):
    spinner_factory = compound_spinner_factory(*(spinner_test(x) for x in outputs), alongside=False)
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
