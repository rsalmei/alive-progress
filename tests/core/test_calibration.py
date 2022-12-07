import pytest

from alive_progress.core.calibration import calibrated_fps, custom_fps


@pytest.mark.parametrize(
    "calibrate, rate, expected",
    [
        (-5.0, -5.0, 10.0),
        (-5.0, 0.0, 10.0),
        (-5.0, 10.0, 60.0),
        (20.0, -5.0, 10.0),
        (20.0, 0.0, 10.0),
        (20.0, 20.0, 60.0),
        (20.0, 9.0, pytest.approx(50.0, abs=1)),
        (1e15, -5.0, 10.0),
        (1e15, 0.0, 10.0),
        (1e15, 1e15, 60.0),
        (1e15, 2e12, pytest.approx(50.0, abs=1)),
        (1e30, -5.0, 10.0),
        (1e30, 0.0, 10.0),
        (1e30, 1e30, 60.0),
        (1e30, 1e25, pytest.approx(50.0, abs=1)),
    ],
)
def test_calibrate(calibrate, rate, expected):
    fps = calibrated_fps(calibrate)
    assert fps(rate) == expected


@pytest.mark.parametrize(
    "rate, expected",
    [
        (1.0, 1),
        (10.0, 0.1),
        (10.0 * 60.0, pytest.approx(0.001666666666666)),
        (0.1, 10.0),
    ],
)
def test_custom(rate, expected):
    fps = custom_fps(rate)
    assert fps(rate) == expected
