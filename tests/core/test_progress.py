from unittest import mock

import pytest

from alive_progress.core.progress import _render_title
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
