import os
import sys
from collections import namedtuple
from string import Formatter
from types import FunctionType

from ..utils.terminal import FULL, NON_TTY

ERROR = object()  # represents a config value not accepted.


def _spinner_input_factory(default):
    from ..animations import spinner_compiler
    from ..styles.internal import SPINNERS
    return __style_input_factory(SPINNERS, spinner_compiler,
                                 'spinner_compiler_dispatcher_factory', default)


def _bar_input_factory():
    from ..animations import bars
    from ..styles.internal import BARS
    return __style_input_factory(BARS, bars, 'bar_assembler_factory', None)


def __style_input_factory(name_lookup, module_lookup, inner_name, default):
    def _input(x):
        return name_lookup(x) or func_lookup(x) or default

    name_lookup = __name_lookup_factory(name_lookup)
    func_lookup = __func_lookup_factory(module_lookup, inner_name)
    return _input


def __name_lookup_factory(name_lookup):
    def _input(x):
        if isinstance(x, str):
            return name_lookup.get(x) or ERROR

    return _input


def __func_lookup_factory(module_lookup, inner_name):
    def _input(x):
        if isinstance(x, FunctionType):
            func_file, _ = os.path.splitext(module_lookup.__file__)
            if x.__code__.co_name == inner_name \
                    and os.path.splitext(x.__code__.co_filename)[0] == func_file:
                return x
            return ERROR

    return _input


def _int_input_factory(lower, upper):
    def _input(x):
        if isinstance(x, int) and lower <= x <= upper:
            return int(x)
        return ERROR

    return _input


def _bool_input_factory():
    def _input(x):
        return bool(x)

    return _input


def _force_tty_input_factory():
    def _input(x):
        return table.get(x, ERROR)

    table = {
        None: FULL if sys.stdout.isatty() else NON_TTY,
        False: NON_TTY,
        True: FULL,
    }
    return _input


def _text_input_factory():
    def _input(x):
        return None if x is None else str(x)

    return _input


def _format_input_factory(allowed):
    def _input(x):
        if not isinstance(x, str):
            return bool(x)
        fvars = parser.parse(x)
        if any(f[1] not in allowed for f in fvars):
            # f is a tuple (literal_text, field_name, format_spec, conversion)
            return ERROR
        return x

    # I want to accept only some field names, and pure text.
    allowed = set(allowed.split() + [None])
    parser = Formatter()
    return _input


Config = namedtuple('Config', 'title length spinner bar unknown force_tty disable manual '
                              'enrich_print receipt receipt_text monitor elapsed stats '
                              'title_length spinner_length refresh_secs monitor_end '
                              'elapsed_end stats_end ctrl_c dual_line')


def create_config():
    def reset():
        """Resets global configuration to the default one."""
        set_global(  # this must have all available config vars.
            title=None,
            length=40,
            theme='smooth',  # includes spinner, bar and unknown.
            force_tty=None,
            disable=False,
            manual=False,
            enrich_print=True,
            receipt=True,
            receipt_text=False,
            monitor=True,
            elapsed=True,
            stats=True,
            monitor_end=True,
            elapsed_end=True,
            stats_end=True,
            title_length=0,
            spinner_length=0,
            refresh_secs=0,
            ctrl_c=True,
            dual_line=False,
        )

    def set_global(theme=None, **options):
        """Update the global configuration, to be used in subsequent alive bars.

        See Also:
            alive_progress#alive_bar(**options)

        """
        lazy_init()
        global_config.update(_parse(theme, options))

    def create_context(theme=None, **options):
        """Create an immutable copy of the current configuration, with optional customization."""
        lazy_init()
        local_config = {**global_config, **_parse(theme, options)}
        return Config(**local_config)

    def _parse(theme, options):
        """Validate and convert some configuration options."""

        def validator(key, value):
            try:
                result = validations[key](value)
                if result is ERROR:
                    raise ValueError
                return result
            except KeyError:
                raise ValueError(f'invalid config name: {key}')
            except Exception:
                raise ValueError(f'invalid config value: {key}={value!r}')

        from ..styles.internal import THEMES
        if theme:
            if theme not in THEMES:
                raise ValueError(f'invalid theme name={theme}')
            swap = options
            options = dict(THEMES[theme])
            options.update(swap)
        return {k: validator(k, v) for k, v in options.items()}

    def lazy_init():
        if validations:
            return

        validations.update(  # the ones the user can configure.
            title=_text_input_factory(),
            length=_int_input_factory(3, 300),
            spinner=_spinner_input_factory(None),  # accept empty.
            bar=_bar_input_factory(),
            unknown=_spinner_input_factory(ERROR),  # do not accept empty.
            force_tty=_force_tty_input_factory(),
            disable=_bool_input_factory(),
            manual=_bool_input_factory(),
            enrich_print=_bool_input_factory(),
            receipt=_bool_input_factory(),
            receipt_text=_bool_input_factory(),
            monitor=_format_input_factory('count total percent'),
            monitor_end=_format_input_factory('count total percent'),
            elapsed=_format_input_factory('elapsed'),
            elapsed_end=_format_input_factory('elapsed'),
            stats=_format_input_factory('rate eta'),
            stats_end=_format_input_factory('rate'),
            title_length=_int_input_factory(0, 100),
            spinner_length=_int_input_factory(0, 100),
            refresh_secs=_int_input_factory(0, 60 * 60 * 24),  # maximum 24 hours.
            ctrl_c=_bool_input_factory(),
            dual_line=_bool_input_factory(),
            # title_effect=_enum_input_factory(),  # TODO someday.
        )
        assert all(k in validations for k in Config._fields)  # ensures all fields have validations.

        reset()
        assert all(k in global_config for k in Config._fields)  # ensures all fields have been set.

    global_config, validations = {}, {}
    create_context.set_global, create_context.reset = set_global, reset
    return create_context


config_handler = create_config()
