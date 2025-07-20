from unittest import mock

import pytest

from alive_progress.core.progress import _AssignFunction, _Function, _GatedFunction, _render_title
from alive_progress.utils.cells import join_cells


@pytest.mark.parametrize('config, length, title, expected', [
    (None, 0, None, ''),
    (None, 0, '', ''),
    (None, 0, 'c', 'c'),
    (None, 0, 'cool bar title', 'cool bar title'),
    (None, 1, None, ' '),
    (None, 1, '', ' '),
    (None, 1, 'c', 'c'),
    (None, 1, 'cool bar title', '…'),
    (None, 1, '😺', '…'),
    (None, 2, '😺', '😺'),
    (None, 5, 'cool bar title', 'cool…'),
    (None, 14, 'cool bar title', 'cool bar title'),
    (None, 20, 'cool bar title', 'cool bar title      '),
    (None, 15, 'cool bar title😺', 'cool bar title…'),
    (None, 16, 'cool bar title😺', 'cool bar title😺'),
    (None, 16, 'cool bar title😺a', 'cool bar title …'),
    (None, 16, 'cool bar title😺😺', 'cool bar title …'),
    # a title in the config may override the passed title.
    ('on config', 0, None, 'on config'),
    ('on config', 0, '', ''),
    ('on config', 0, 'cool bar title', 'cool bar title'),
    ('on config', 1, None, '…'),
    ('on config', 1, '', ' '),
])
def test_render_title(config, length, title, expected):
    local_config = mock.Mock(title=config, title_length=length)
    assert join_cells(_render_title(local_config, title)) == expected


def test_gated_properties():
    class AClass:
        always = _Function()
        readonly = _GatedFunction()
        assignable = _AssignFunction()

    instance, m = AClass(), mock.Mock()
    instance._always = lambda: 'ok'
    instance._readonly = lambda: 1
    instance._assignable = m

    instance._handle = True
    assert instance.always() == 'ok'
    assert instance.readonly() == 1  # works.

    instance.assignable()
    m.assert_called_once_with()

    m.reset_mock()
    instance.assignable(2)  # as parameter.
    m.assert_called_once_with(2)

    m.reset_mock()
    instance.assignable = 3  # as attribute.
    m.assert_called_once_with(3)

    instance._handle = False
    assert instance.always() == 'ok'
    assert instance.readonly() is None  # is None when handle is False.

    m.reset_mock()
    instance.assignable()
    m.assert_called_once_with()

    m.reset_mock()
    instance.assignable(2)  # as parameter.
    m.assert_called_once_with(2)

    m.reset_mock()
    instance.assignable = 3  # as attribute.
    m.assert_called_once_with(3)
