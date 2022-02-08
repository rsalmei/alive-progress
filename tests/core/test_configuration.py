from unittest import mock

import pytest

# noinspection PyProtectedMember
from alive_progress.core.configuration import Config, ERROR, __style_input_factory, \
    _bool_input_factory, _int_input_factory, create_config, _format_input_factory
from alive_progress.styles.internal import BARS, SPINNERS, THEMES
from alive_progress.utils.terminal import NON_TTY, FULL


@pytest.mark.parametrize('lower, upper, num, expected', [
    (100, 110, 100, 100),
    (100, 110, 110, 110),
    (100, 110, -1, ERROR),
    (100, 110, 111, ERROR),
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


@pytest.mark.parametrize('param, expected', [
    (True, True),
    (False, False),
    (1.2345, True),
    (object(), True),
    (None, False),
    ([], False),
    ('', ''),
    ('any text', 'any text'),
    ('text {{text', 'text {{text'),
    ('text {{apple', 'text {{apple'),
    ('text apple}}', 'text apple}}'),
    ('text {{text}}', 'text {{text}}'),
    ('{kiwi}', '{kiwi}'),
    ('text {kiwi} text', 'text {kiwi} text'),
    ('{mango}', ERROR),
    ('text {mango} text', ERROR),
])
def test_format_input_factory(param, expected):
    func = _format_input_factory('banana apple kiwi')
    assert func(param) == expected


def func_style_123():
    def artifact_super_cool_compiler_assembler_factory():
        pass

    return artifact_super_cool_compiler_assembler_factory


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

    func = __style_input_factory(NAMES, test_style_input_factory,
                                 'artifact_super_cool_compiler_assembler_factory', None)
    assert func(param) == expected


@pytest.mark.parametrize('param', [
    'banana', func_not_style, STYLE_1,
])
def test_style_input_factory_error(param):
    test_style_input_factory_error.__file__ = ''  # simulates a func_style declared elsewhere.

    func = __style_input_factory(NAMES, test_style_input_factory_error,
                                 'artifact_super_cool_compiler_assembler_factory', None)
    assert func(param) is ERROR


@pytest.fixture
def handler():
    yield create_config()


def test_config_creation(handler):
    config = handler()
    assert isinstance(config, Config)


@pytest.fixture(params=[
    (dict(length=9), {}),
    (dict(spinner='pulse'), dict(spinner=SPINNERS['pulse'])),
    (dict(spinner=SPINNERS['pulse']), {}),
    (dict(bar='solid'), dict(bar=BARS['solid'])),
    (dict(bar=BARS['solid']), {}),
    (dict(force_tty=False), dict(force_tty=NON_TTY)),
    (dict(manual=True), {}),
    (dict(enrich_print=False), {}),
    (dict(title_length=20), {}),
    (dict(force_tty=True, manual=True, enrich_print=False, title_length=10), dict(force_tty=FULL)),
    (dict(spinner=None, manual=None), dict(manual=False)),
])
def config_params(request):
    yield request.param


def test_config_global(config_params, handler):
    params, diff = config_params
    expected = dict(params, **diff)
    handler.set_global(**params)
    config = handler()
    assert {k: v for k, v in config._asdict().items() if k in params} == expected


def test_config_local(config_params, handler):
    params, diff = config_params
    expected = dict(params, **diff)
    config = handler(**params)
    assert {k: v for k, v in config._asdict().items() if k in params} == expected


@pytest.fixture(params=[
    dict(length=None),
    dict(length=9999),
    dict(spinner='banana'),
    dict(bar='coolest'),
    dict(unknown=None),
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
