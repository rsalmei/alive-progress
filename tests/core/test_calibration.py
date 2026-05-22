import pytest

from alive_progress.core.calibration import reactive_fps, custom_fps


@pytest.mark.parametrize('min_fps, calibrate, rate, expected', [
    (0., 0., 0., 10.),  # bootstrap speed.
    (2., 2., 0., 10.),  # bootstrap speed.
    (2., 20., 0., 10.),  # bootstrap speed.
    (2., 0., 10., 60.),  # max fps.
    (2., 20., 20., 60.),  # max fps.
    (2., 1e15, 1e15, 60.),  # max fps.
    (2., 1e30, 1e30, 60.),  # max fps.
    (2., 1., 1e-6, pytest.approx(2., abs=.01)),  # min fps.
    (10., 1., 1e-6, pytest.approx(10., abs=.01)),  # min fps.
    (0., 1., 1e-6, pytest.approx(0., abs=.01)),  # min fps.
    # calibration curve.
    (2., 1e30, 5., pytest.approx(3., abs=1)),
    (2., 1e15, 5., pytest.approx(5., abs=1)),
    (2., 20., 1., pytest.approx(24., abs=1)),
    (2., 20., 5., pytest.approx(42., abs=1)),
    (2., 20., 9., pytest.approx(50., abs=1)),
    (2., 1e15, 2e12, pytest.approx(50., abs=1)),
    (2., 1e30, 1e25, pytest.approx(50., abs=1)),
])
def test_calibrate(min_fps, calibrate, rate, expected):
    fps = reactive_fps(min_fps, calibrate)
    assert fps(rate) == expected


@pytest.mark.parametrize('refresh_secs, rate, expected', [
    (1., 0., 10.),  # bootstrap speed.
    (1., 1e-6, 1.),
    (1., 1e30, 1.),
    (10., 0., 10.),  # bootstrap speed.
    (10., 1e-6, .1),
    (10., 1e30, .1),
    (.2, .0, 10.),  # bootstrap speed.
    (.2, 1e-6, 5.),
    (.2, 1e30, 5.),

])
def test_custom(refresh_secs, rate, expected):
    fps = custom_fps(refresh_secs)
    assert fps(rate) == expected
