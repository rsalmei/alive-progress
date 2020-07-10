# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import os
from collections import namedtuple
from copy import deepcopy
from types import FunctionType

from ..animations import bars, spinners
from ..styles.internal import BARS, SPINNERS, THEMES


def _style_input_factory(name_lookup, func_lookup, name_index=None):
    def _input(x):
        if isinstance(x, FunctionType):
            if x.__code__.co_name == 'inner_factory' \
                    and os.path.splitext(x.__code__.co_filename)[0] == func_file:
                return x
        elif x in name_lookup:
            return getter(name_lookup[x])

    func_file, _ = os.path.splitext(func_lookup.__file__)
    getter = (lambda x: x) if name_index is None else lambda x: x[name_index]
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


# noinspection PyTypeChecker
CONFIG_VARS = dict(
    length=_int_input_factory(3, 300),
    spinner=_style_input_factory(SPINNERS, spinners, 0),
    bar=_style_input_factory(BARS, bars),
    unknown=_style_input_factory(SPINNERS, bars, 1),
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
        local_config = deepcopy(global_config)
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
                raise ValueError('invalid config name: {}'.format(key))
            except Exception:
                raise ValueError('invalid config value: {}={}'.format(key, repr(value)))

        if theme:
            if theme not in THEMES:
                raise ValueError('invalid theme name={}'.format(repr(theme)))
            swap = options
            options = deepcopy(THEMES[theme])
            options.update(swap)
        return {k: validator(k, v) for k, v in options.items()}

    global_config = {}
    reset()

    create_context.set_global = set_global
    create_context.reset = reset
    return create_context


config_handler = create_config()
