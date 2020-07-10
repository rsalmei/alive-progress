# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

try:
    from unittest import mock
except ImportError:
    import mock  # noqa

from alive_progress.styles.internal import BARS, SPINNERS, THEMES
# noinspection PyProtectedMember
from alive_progress.core.configuration import Config, _bool_input_factory, _int_input_factory, \
    _style_input_factory, create_config


@pytest.mark.parametrize('lower, upper, num, expected', [
    (100, 110, 100, 100),
    (100, 110, 110, 110),
    (100, 110, -1, None),
    (100, 110, 111, None),
])
def test_int_input_factory(lower, upper, num, expected):
    func = _int_input_factory(lower, upper)
    assert func(num) == expected


@pytest.mark.parametrize('param, expected', [
    (False, False),
    (0, False),
    ('', False),
    (None, False),
    (True, True),
    (1, True),
    ('asd', True),
])
def test_bool_input_factory(param, expected):
    func = _bool_input_factory()
    assert func(param) == expected


def func_style_test():
    def inner_factory():
        pass

    return inner_factory


def func_not_style():
    pass


STYLE_TEST = func_style_test()
NAMES = dict(name_test='ok')
NAMES_INDEXED = dict(name_test=(1, 1, 'ok'))


@pytest.mark.parametrize('param, expected', [
    (STYLE_TEST, STYLE_TEST),
    ('name_test', 'ok'),
])
def test_style_input_factory(param, expected):
    test_style_input_factory.__file__ = __file__

    func = _style_input_factory(NAMES, test_style_input_factory)
    assert func(param) == expected


@pytest.mark.parametrize('param, expected', [
    (STYLE_TEST, STYLE_TEST),
    ('name_test', 'ok'),
])
def test_style_input_factory_indexed(param, expected):
    test_style_input_factory_indexed.__file__ = __file__

    func = _style_input_factory(NAMES_INDEXED, test_style_input_factory_indexed, 2)
    assert func(param) == expected


@pytest.mark.parametrize('param', [
    'banana', func_not_style, STYLE_TEST,
])
def test_style_input_factory_error(param):
    test_style_input_factory_error.__file__ = ''  # simulates a func_style declared elsewhere.

    func = _style_input_factory(NAMES, test_style_input_factory_error)
    assert func(param) is None


@pytest.fixture
def handler():
    yield create_config()


def test_config_create(handler):
    config = handler()
    assert isinstance(config, Config)
    assert all(x is not None for x in config)


@pytest.fixture(params=[
    dict(length=9),
    dict(spinner=SPINNERS['pulse'][0]),
    dict(bar=BARS['solid']),
    dict(unknown=SPINNERS['pulse'][1]),
    dict(force_tty=True),
    dict(manual=True),
    dict(enrich_print=False),
    dict(spinner=SPINNERS['pulse'][0], bar=BARS['solid'], unknown=SPINNERS['fish'][1]),
    dict(force_tty=True, manual=True, enrich_print=False),
])
def config_params(request):
    yield request.param


def test_config_global(config_params, handler):
    handler.set_global(**config_params)
    config = handler()
    assert {k: v for k, v in config._asdict().items() if k in config_params} == config_params


def test_config_local(config_params, handler):
    config = handler(**config_params)
    assert {k: v for k, v in config._asdict().items() if k in config_params} == config_params


@pytest.fixture(params=[
    dict(length=9999),
    dict(spinner='banana'),
    dict(bar='coolest'),
    dict(unknown='nope'),
    dict(theme='rogerio'),
    dict(spinner=SPINNERS['pulse'][0], bar='oops', unknown=SPINNERS['fish'][1]),
    dict(hey=True),
    dict(length=10, cool='very'),
])
def config_params_error(request):
    yield request.param


def test_config_global_error(config_params_error, handler):
    with pytest.raises(ValueError):
        handler.set_global(**config_params_error)


def test_config_local_error(config_params_error, handler):
    with pytest.raises(ValueError):
        handler(**config_params_error)


@pytest.fixture
def config_params_theme(config_params):
    with mock.patch.dict(THEMES, cool=config_params):
        yield config_params


def test_config_global_theme(config_params_theme, handler):
    handler.set_global(theme='cool')
    config = handler()
    assert {k: getattr(config, k) for k in config_params_theme} == config_params_theme
