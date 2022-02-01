import pytest

from alive_progress.core.calibration import calibrated_fps, custom_fps


@pytest.mark.parametrize('calibrate, rate, expected', [
    (-5., -5., 10.),
    (-5., 0., 10.),
    (-5., 10., 60.),
    (20., -5., 10.),
    (20., 0., 10.),
    (20., 20., 60.),
    (20., 9., pytest.approx(50., abs=1)),
    (1e15, -5., 10.),
    (1e15, 0., 10.),
    (1e15, 1e15, 60.),
    (1e15, 2e12, pytest.approx(50., abs=1)),
    (1e30, -5., 10.),
    (1e30, 0., 10.),
    (1e30, 1e30, 60.),
    (1e30, 1e25, pytest.approx(50., abs=1)),
])
def test_calibrate(calibrate, rate, expected):
    fps = calibrated_fps(calibrate)
    assert fps(rate) == expected


@pytest.mark.parametrize('rate, expected', [
    (1., 1),
    (10., .1),
    (10. * 60., pytest.approx(.001666666666666)),
    (.1, 10.),
])
def test_custom(rate, expected):
    fps = custom_fps(rate)
    assert fps(rate) == expected
