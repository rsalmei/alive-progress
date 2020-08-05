from unittest import mock

import pytest

from alive_progress import unknown_bar_factory
# noinspection PyProtectedMember
from alive_progress.core.configuration import Config, _bool_input_factory, _int_input_factory, \
    _style_input_factory, _unknown_bar_input_factory, create_config
from alive_progress.styles.internal import BARS, SPINNERS, THEMES


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


def func_style_123():
    def inner_factory():
        pass

    return inner_factory


def func_not_style():
    pass


STYLE_1 = func_style_123()
STYLE_2 = func_style_123()
NAMES = dict(name_1=STYLE_1, name_2=STYLE_2)


@pytest.mark.parametrize('param, expected', [
    (STYLE_1, STYLE_1),
    (STYLE_2, STYLE_2),
    ('name_1', STYLE_1),
    ('name_2', STYLE_2),
])
def test_style_input_factory(param, expected):
    test_style_input_factory.__file__ = __file__

    func = _style_input_factory(NAMES, test_style_input_factory, 'inner_factory')
    assert func(param) == expected


@pytest.mark.parametrize('param', [
    'banana', func_not_style, STYLE_1,
])
def test_style_input_factory_error(param):
    test_style_input_factory_error.__file__ = ''  # simulates a func_style declared elsewhere.

    func = _style_input_factory(NAMES, test_style_input_factory_error, 'inner_factory')
    assert func(param) is None


@pytest.mark.parametrize('param, expected', [
    ('pulse', SPINNERS['pulse']),
    (SPINNERS['waves'], SPINNERS['waves']),
])
def test_unknown_input_factory_creation(param, expected):
    func = _unknown_bar_input_factory()
    with mock.patch('alive_progress.animations.bars.unknown_bar_factory') as mock_unknown:
        func(param)
        mock_unknown.assert_called_once_with(expected)


def test_unknown_input_factory_bypass():
    func, param = _unknown_bar_input_factory(), unknown_bar_factory(SPINNERS['fish'])
    with mock.patch('alive_progress.animations.bars.unknown_bar_factory') as mock_unknown:
        assert func(param) is param
        mock_unknown.assert_not_called()


@pytest.fixture
def handler():
    yield create_config()


def test_config_creation(handler):
    config = handler()
    assert isinstance(config, Config)
    assert all(x is not None for x in config)


NEW_UNKNOWN = unknown_bar_factory(SPINNERS['pulse'], '[]')


@pytest.fixture(params=[
    (dict(length=9), dict()),
    (dict(spinner='pulse'), dict(spinner=SPINNERS['pulse'])),
    (dict(spinner=SPINNERS['pulse']), dict()),
    (dict(bar='solid'), dict(bar=BARS['solid'])),
    (dict(bar=BARS['solid']), dict()),
    (dict(unknown=NEW_UNKNOWN), dict()),
    (dict(force_tty=True), dict()),
    (dict(manual=True), dict()),
    (dict(enrich_print=False), dict()),
    (dict(title_length=20), dict()),
    (dict(spinner=SPINNERS['pulse'], bar=BARS['solid'], unknown=NEW_UNKNOWN), dict()),
    (dict(force_tty=True, manual=True, enrich_print=False, title_length=10), dict()),
    (dict(spinner=None, length=None, manual=None),
     dict(spinner=SPINNERS['waves'], length=40, manual=False)),
])
def config_params(request):
    yield request.param


def test_config_global(config_params, handler):
    params, expected = config_params
    expected = dict(params, **expected)
    handler.set_global(**params)
    config = handler()
    assert {k: v for k, v in config._asdict().items() if k in params} == expected


def test_config_local(config_params, handler):
    params, expected = config_params
    expected = dict(params, **expected)
    config = handler(**params)
    assert {k: v for k, v in config._asdict().items() if k in params} == expected


@pytest.fixture(params=[
    dict(length=9999),
    dict(spinner='banana'),
    dict(bar='coolest'),
    dict(unknown='nope'),
    dict(theme='rogerio'),
    dict(spinner=SPINNERS['pulse'], bar='oops', unknown=SPINNERS['fish']),
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
    with mock.patch.dict(THEMES, cool=config_params[0]):
        yield config_params


def test_config_global_theme(config_params_theme, handler):
    params, expected = config_params_theme
    expected = dict(params, **expected)
    handler.set_global(theme='cool')
    config = handler()
    assert {k: getattr(config, k) for k in params} == expected
