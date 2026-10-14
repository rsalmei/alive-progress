# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

# noinspection PyProtectedMember
from alive_progress.core.progress import _create_fps_controller, _normalize_total


@pytest.mark.parametrize('total, expected', [
    (None, None),
    (0, None),
    (-1, None),
    (1, 1),
    (100, 100),
])
def test_normalize_total(total, expected):
    assert _normalize_total(total) == expected


@pytest.mark.parametrize('total', [
    1.,
    '1',
    [],
])
def test_normalize_total_error(total):
    with pytest.raises(TypeError):
        _normalize_total(total)


def test_create_fps_controller_bootstrap_speed():
    fps = _create_fps_controller(lambda: 0., None, 1.e6)

    assert fps() == pytest.approx(10.)


def test_create_fps_controller_calibrates_to_maximum():
    rate = [100.]
    fps = _create_fps_controller(lambda: rate[0], 100., 1.e6)

    assert fps() == pytest.approx(60.)


def test_create_fps_controller_scales_before_calibration():
    rate = [1.]
    fps = _create_fps_controller(lambda: rate[0], 100., 1.e6)

    assert 2. < fps() < 60.
