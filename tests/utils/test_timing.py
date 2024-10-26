import pytest

from alive_progress.utils.timing import time_display, eta_text, fn_simple_eta, RUN, END, \
    gen_simple_exponential_smoothing


@pytest.mark.parametrize('elapsed, conf, expected', [
    (1.4, RUN, '1s'),
    (1.4, END, '1.4s'),
    (1.45, END, '1.4s'),
    (1.5, RUN, '2s'),
    (1.5, END, '1.5s'),
    (1.55, END, '1.6s'),
    (61.4, RUN, '1:01'),
    (61.4, END, '1:01.4'),
    (119.5, RUN, '2:00'),
    (119.5, END, '1:59.5'),
    (119.95, END, '2:00.0'),
    (120.1, RUN, '2:00'),
    (120.1, END, '2:00.1'),
    (4000, RUN, '1:06:40'),
    (4000, END, '1:06:40.0'),
])
def test_to_elapsed_text(elapsed, conf, expected):
    assert time_display(elapsed, conf) == expected


@pytest.mark.parametrize('eta, expected', [
    (-.1, '?'),
    (-1000., '?'),
    (0., '~0s'),
    (10., '~10s'),
])
def test_to_eta_text(eta, expected):
    assert eta_text(eta) == expected


def test_simple_eta():
    assert fn_simple_eta(10)(2, 5.) == pytest.approx(1.6)


def test_gen_simple_exponential_smoothing_eta():
    data = (  # according to the study of simple_exponential_smoothing in docs directory.
        (88., 88.),
        (75., 81.5),
        (60., 70.75),
        (75., 72.875),
        (56., 64.4375),
        (41., 52.71875),
        (51., 51.859375),
        (23., 37.4296875),
        (22., 29.71484375),
        (17., 23.357421875),
        (12., 17.6787109375),
        (20., 18.83935546875),
        (9., 13.919677734375),
        (5., 9.4598388671875),
        (3., 6.22991943359375),
    )
    gen_eta = gen_simple_exponential_smoothing(.5, lambda r: r)
    gen_eta.send(None)
    for i, (y, ses) in enumerate(data):
        assert gen_eta.send((y,)) == pytest.approx(ses)
