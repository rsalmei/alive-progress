from unittest import mock

import pytest

from alive_progress.core.progress import _GatedAssignProperty, _GatedProperty, _render_title
from alive_progress.utils.cells import join_cells


@pytest.mark.parametrize('length, text, expected', [
    (0, None, ''),
    (0, '', ''),
    (0, 'c', 'c'),
    (0, 'cool bar title', 'cool bar title'),
    (1, None, ' '),
    (1, '', ' '),
    (1, 'c', 'c'),
    (1, 'cool bar title', '…'),
    (1, '😺', '…'),
    (2, '😺', '😺'),
    (5, 'cool bar title', 'cool…'),
    (14, 'cool bar title', 'cool bar title'),
    (20, 'cool bar title', 'cool bar title      '),
    (15, 'cool bar title😺', 'cool bar title…'),
    (16, 'cool bar title😺', 'cool bar title😺'),
    (16, 'cool bar title😺a', 'cool bar title …'),
    (16, 'cool bar title😺😺', 'cool bar title …'),
])
def test_render_title(length, text, expected):
    local_config = mock.Mock(title=text, title_length=length)
    assert join_cells(_render_title(local_config)) == expected


def test_gated_properties():
    class AClass:
        readonly = _GatedProperty()
        assignable = _GatedAssignProperty()

    instance, m = AClass(), mock.Mock()
    instance._handle = True
    instance._readonly = lambda: 1
    instance._assignable = m

    assert instance.readonly() == 1

    instance.assignable()
    m.assert_called_once_with()

    m.reset_mock()
    instance.assignable(2)
    m.assert_called_once_with(2)

    m.reset_mock()
    instance.assignable = 3
    m.assert_called_once_with(3)
