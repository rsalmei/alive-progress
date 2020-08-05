import os
from collections import namedtuple
from types import FunctionType

from ..animations import bars, spinners
from ..styles.internal import BARS, SPINNERS, THEMES


def _style_input_factory(name_lookup, module_lookup, inner_name):
    def _input(x):
        return name_lookup(x) or func_lookup(x)

    name_lookup = __name_lookup_factory(name_lookup)
    func_lookup = __func_lookup_factory(module_lookup, inner_name)
    return _input


def _unknown_bar_input_factory():
    def _input(x):
        obj = name_lookup(x) or spinner_lookup(x)
        if obj:
            return bars.unknown_bar_factory(obj)
        return unknown_lookup(x)

    name_lookup = __name_lookup_factory(SPINNERS)
    spinner_lookup = __func_lookup_factory(spinners, 'inner_factory')
    unknown_lookup = __func_lookup_factory(bars, 'inner_unknown_bar_factory')
    return _input


def _int_input_factory(lower, upper):
    def _input(x):
        if lower <= int(x) <= upper:
            return int(x)

    return _input


def _bool_input_factory():
    def _input(x):
        return bool(x)

    return _input


def __name_lookup_factory(name_lookup):
    def _input(x):
        if isinstance(x, str):
            return name_lookup.get(x)

    return _input


def __func_lookup_factory(module_lookup, inner_name):
    def _input(x):
        if isinstance(x, FunctionType):
            func_file, _ = os.path.splitext(module_lookup.__file__)
            if x.__code__.co_name == inner_name \
                    and os.path.splitext(x.__code__.co_filename)[0] == func_file:
                return x

    return _input


CONFIG_VARS = dict(
    length=_int_input_factory(3, 300),
    spinner=_style_input_factory(SPINNERS, spinners, 'inner_factory'),
    bar=_style_input_factory(BARS, bars, 'inner_standard_bar_factory'),
    unknown=_unknown_bar_input_factory(),
    force_tty=_bool_input_factory(),
    manual=_bool_input_factory(),
    enrich_print=_bool_input_factory(),
    title_length=_int_input_factory(0, 100),
)

Config = namedtuple('Config', tuple(CONFIG_VARS.keys()))
Config.__new__.__defaults__ = (None,) * len(CONFIG_VARS)


def create_config():
    def reset():
        """Resets global configuration to the default one."""
        set_global(  # this must have all available config vars.
            length=40,
            theme='smooth',  # includes spinner, bar and unknown.
            force_tty=False,
            manual=False,
            enrich_print=True,
            title_length=0,
        )

    def set_global(theme=None, **options):
        """Update the global configuration, to be used in subsequent alive bars.

        See Also:
            alive_progress#alive_bar(**options)

        """
        global_config.update(_parse(theme, options))

    def create_context(theme=None, **options):
        """Create an immutable copy of the current configuration, with optional customization."""
        local_config = dict(global_config)
        local_config.update(_parse(theme, options))
        # noinspection PyArgumentList
        return Config(**local_config)

    def _parse(theme, options):
        """Validate and convert some configuration options."""

        def validator(key, value):
            try:
                result = CONFIG_VARS[key](value)
                if result is None:
                    raise ValueError
                return result
            except KeyError:
                raise ValueError(f'invalid config name: {key}')
            except Exception:
                raise ValueError(f'invalid config value: {key}={value!r}')

        if theme:
            if theme not in THEMES:
                raise ValueError(f'invalid theme name={theme}')
            swap = options
            options = dict(THEMES[theme])
            options.update(swap)
        return {k: validator(k, v) for k, v in options.items()}

    global_config = {}
    reset()

    create_context.set_global = set_global
    create_context.reset = reset
    return create_context


config_handler = create_config()
