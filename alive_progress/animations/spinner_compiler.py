import operator
import random
import time
from inspect import signature
from itertools import chain, count, islice, repeat
from types import SimpleNamespace

from about_time import about_time

from .utils import fix_signature
from ..utils.cells import fix_cells, is_wide, join_cells, strip_marks, to_cells
from ..utils.colors import BLUE, BLUE_BOLD, CYAN, DIM, GREEN, ORANGE, ORANGE_BOLD, RED, YELLOW_BOLD
from ..utils.terminal import hide_cursor, show_cursor


def spinner_controller(*, natural, skip_compiler=False):
    def inner_controller(spinner_inner_factory, op_params=None, extra_commands=None):
        def compiler_dispatcher(actual_length=None):
            """Compile this spinner factory into an actual spinner runner.
            The previous parameters were the styling parameters, which defined a style.
            These are called operational parameters, which `alive_progress` binds dynamically
            as needed. Do not call this manually.

            Args:
                actual_length (int): the actual length to compile the frames renditions

            Returns:
                a spinner runner

            """
            if skip_compiler:
                return spinner_inner_factory(actual_length, **op_params)

            with about_time() as t_compile:
                gen = spinner_inner_factory(actual_length, **op_params)
                spec = spinner_compiler(gen, natural, extra_commands.get(True, ()))
            return spinner_runner_factory(spec, t_compile, extra_commands.get(False, ()))

        def compile_and_check(*args, **kwargs):
            """Compile this spinner factory at its natural length, and..."""
            compiler_dispatcher().check(*args, **kwargs)

        def set_operational(**params):
            signature(spinner_inner_factory).bind(1, **params)  # test arguments (one is provided).
            return inner_controller(spinner_inner_factory, params, extra_commands)

        def schedule_command(command):
            def inner_schedule(*args, **kwargs):
                signature(command).bind(1, *args, **kwargs)  # test arguments (one is provided).
                extra, cmd_type = dict(extra_commands), EXTRA_COMMANDS[command]
                extra[cmd_type] = extra.get(cmd_type, ()) + ((command, args, kwargs),)
                return inner_controller(spinner_inner_factory, op_params, extra)

            return fix_signature(inner_schedule, command, 1)

        compiler_dispatcher.__dict__.update(
            check=fix_signature(compile_and_check, check, 1), op=set_operational,
            **{c.__name__: schedule_command(c) for c in EXTRA_COMMANDS},
        )
        op_params, extra_commands = op_params or {}, extra_commands or {}
        compiler_dispatcher.natural = natural  # share with the spinner code.
        return compiler_dispatcher

    return inner_controller


"""
The commands here are made available in the compiler controller, thus in all spinners.

They work lazily: when called they only schedule themselves to be run when the spinner
gets compiled, i.e., when it receives the operational parameters like `actual_length`.

They can take place inside the compiler or inside the runner.
Compiler commands can change the data at will, before the animation specs are computed.
Runner commands can only change presentation order.
"""


def extra_command(is_compiler):
    def inner_command(command):
        EXTRA_COMMANDS[command] = is_compiler
        return command

    return inner_command


EXTRA_COMMANDS = {}
compiler_command, runner_command = extra_command(True), extra_command(False)


@compiler_command
def replace(spec, old, new):  # noqa
    """Replace a portion of the frames by another with the same length.

    Args:
        old (str): the old string to be replaced
        new (str): the new string

    """
    # different lengths could lead to broken frames, but they will be verified afterwards.
    spec.data = tuple(tuple(
        to_cells(join_cells(frame).replace(old, new)) for frame in cycle
    ) for cycle in spec.data)


@compiler_command
def pause(spec, n_edges=None, n_middle=None):  # noqa
    """Make the animation appear to pause on the edges or the middle, or make it slower as
    a whole, or both.

    In the future, I'd like to make this a `pace` command, which would receive a sequence
    of ints of any length, and apply it bouncing across the cycle. For example to smoothly
    decelerate it could be (6, 3, 2, 1), which would become (6, 3, 2, 1, 1, ..., 1, 2, 3, 6).

    Args:
        n_edges (Optional[int]): how many times the first and last frames on a cycle repeats
            default is 6.
        n_middle (Optional[int]): how many times the middle frames on a cycle repeats
            default is 1.

    """
    n_edges, n_middle = max(1, n_edges or 6), max(1, n_middle or 1)
    spec.data = tuple(tuple(
        chain.from_iterable(repeat(frame, n_edges if i in (0, length - 1) else n_middle)
                            for i, frame in enumerate(cycle)))
                      for cycle, length in ((cycle, len(cycle)) for cycle in spec.data))


@compiler_command
def reshape(spec, num_frames):  # noqa
    """Reshape frame data into another grouping. It can be used to simplify content
    description, or for artistic effects.

    Args:
        num_frames (int): the number of consecutive frames to group

    """
    flatten = chain.from_iterable(cycle for cycle in spec.data)
    spec.data = tuple(iter(lambda: tuple(islice(flatten, num_frames)), ()))


@compiler_command
def bounce(spec):
    """Make the animation bounce its cycles."""
    spec.data = tuple(chain(spec.data, spec.data[-2:0:-1]))


@compiler_command
def transpose(spec):
    """Transpose the frame content matrix, exchanging columns for rows. It can be used
    to simplify content description, or for artistic effects."""
    spec.data = tuple(tuple(cycle) for cycle in zip(*spec.data))


@runner_command
def sequential(spec):
    """Configure the runner to play the compiled cycles in sequential order."""

    def cycle_data(data):
        while True:
            yield from data

    cycle_data.name = 'sequential'
    spec.__dict__.update(strategy=cycle_data, cycles=len(spec.data))


@runner_command
def randomized(spec, cycles=None):  # noqa
    """Configure the runner to play the compiled cycles in random order.

    Args:
        cycles (Optional[int]): number of cycles to play randomized

    """

    def cycle_data(data):
        while True:
            yield random.choice(data)

    cycle_data.name = 'randomized'
    spec.__dict__.update(strategy=cycle_data, cycles=max(0, cycles or 0) or spec.cycles)


def apply_extra_commands(spec, extra_commands):
    for command, args, kwargs in extra_commands:
        command(spec, *args, **kwargs)


def spinner_compiler(gen, natural, extra_commands):
    """Optimized spinner compiler, which compiles ahead of time all frames of all cycles
    of a spinner.

    Args:
        gen (Generator): the generator expressions that defines the cycles and their frames
        natural (int): the natural length of the spinner
        extra_commands (tuple[tuple[cmd, list[Any], dict[Any]]]): requested extra commands

    Returns:
        the spec of a compiled animation

    """

    spec = SimpleNamespace(
        data=tuple(tuple(fix_cells(frame) for frame in cycle) for cycle in gen),
        natural=natural, strategy=None)
    apply_extra_commands(spec, extra_commands)

    # generate spec info.
    frames = tuple(len(cycle) for cycle in spec.data)
    spec.__dict__.update(cycles=len(spec.data), length=len(spec.data[0][0]),
                         frames=frames, total_frames=sum(frames))

    assert (max(len(frame) for cycle in spec.data for frame in cycle) ==
            min(len(frame) for cycle in spec.data for frame in cycle)), \
        render_data(spec, True) or 'Different cell lengths detected in frame data.'
    return spec


def spinner_runner_factory(spec, t_compile, extra_commands):
    """Optimized spinner runner, which receives the spec of an animation, and controls
    the flow of cycles and frames already compiled to a certain screen length and with
    wide chars fixed, thus avoiding any overhead in runtime within complex spinners,
    while allowing their factories to be garbage collected.

    Args:
        spec (SimpleNamespace): the spec of an animation
        t_compile (about_time.Handler): the compile time information
        extra_commands (tuple[tuple[cmd, list[Any], dict[Any]]]): requested extra commands

    Returns:
        a spinner runner

    """

    def spinner_runner():
        """Wow, you are really deep! This is the runner of a compiled spinner.
        Every time you call this function, a different generator will kick in,
        which yields the frames of the current animation cycle. Enjoy!"""

        yield from next(cycle_gen)  # I love generators!

    def runner_check(*args, **kwargs):
        return check(spec, *args, **kwargs)

    spinner_runner.__dict__.update(spec.__dict__, check=fix_signature(runner_check, check, 1))
    spec.__dict__.update(t_compile=t_compile, runner=spinner_runner)  # set after the update above.

    apply_extra_commands(spec, extra_commands or ((sequential, (), {}),))
    cycle_gen = spec.strategy(spec.data)
    return spinner_runner


def check(spec, verbosity=0):  # noqa
    """Check the specs, contents, codepoints, and even the animation of this compiled spinner.
    
    Args:
        verbosity (int): change the verbosity level
                             0 for specs only (default)
                               /                 \\
                              /           3 to include animation
                             /                      \\
            1 to unfold frame data   --------   4 to unfold frame data
                            |                        |
            2 to reveal codepoints   --------   5 to reveal codepoints

    """
    verbosity = max(0, min(5, verbosity or 0))
    if verbosity in (1, 2, 4, 5):
        render_data(spec, verbosity in (2, 5))
    spec_data(spec)  # spec_data here displays calculated frame data, always shown.

    duration = spec.t_compile.duration_human.replace('us', 'µs')
    print(f'\nSpinner frames compiled in: {GREEN(duration)}')
    print(f'(call {HELP_MSG[verbosity]})')

    if verbosity in (3, 4, 5):
        animate(spec)


SECTION = ORANGE_BOLD
CHECK = lambda p: f'{BLUE(f".{check.__name__}(")}{BLUE_BOLD(p)}{BLUE(")")}'
HELP_MSG = {
    0: f'{CHECK(1)} to unfold frame data, or {CHECK(3)} to include animation',
    1: f'{CHECK(2)} to reveal codepoints, or {CHECK(4)} to include animation,'
       f' or {CHECK(0)} to fold up frame data',
    2: f'{CHECK(5)} to include animation, or {CHECK(1)} to hide codepoints',
    3: f'{CHECK(4)} to unfold frame data, or {CHECK(0)} to omit animation',
    4: f'{CHECK(5)} to reveal codepoints, or {CHECK(1)} to omit animation,'
       f' or {CHECK(3)} to fold up frame data',
    5: f'{CHECK(2)} to omit animation, or {CHECK(4)} to hide codepoints',
}


def spec_data(spec):
    print(f'\n{SECTION("Specs")}')
    info = lambda field: f'{YELLOW_BOLD(field.split(".")[0])}: {operator.attrgetter(field)(spec)}'
    print(info('length'), f'({info("natural")})')
    print(info('cycles'), f'({info("strategy.name")})')
    print('\n'.join(info(field) for field in ('frames', 'total_frames')))


def format_codepoints(frame):
    codes = '|'.join((ORANGE if is_wide(g) else BLUE)(
        ' '.join(hex(ord(c)).replace('0x', '') for c in g)) for g in frame)
    return f" -> {RED(sum(len(fragment) for fragment in frame))}:[{codes}]"


def render_data(spec, show_codepoints):
    print(f'\n{SECTION("Frame data")}', end='')
    whole_index = count(1)
    lf, wf = f'>{1 + len(str(max(spec.frames)))}', f'<{len(str(spec.total_frames))}'
    codepoints = format_codepoints if show_codepoints else lambda _: ''
    for i, cycle in enumerate(spec.data, 1):
        frames = map(lambda fragment: tuple(strip_marks(fragment)), cycle)
        print(f'\ncycle {i}\n' + '\n'.join(
            DIM(li, lf) + f' |{"".join(frame)}| {DIM(wi, wf)}' + codepoints(frame)
            for li, frame, wi in zip(count(1), frames, whole_index)
        ))


def animate(spec):
    print(f'\n{SECTION("Animation")}')
    cf, lf = f'>{len(str(spec.cycles))}', f'>{len(str(max(spec.frames)))}'
    from itertools import cycle
    cycles = cycle(range(1, spec.cycles + 1))
    hide_cursor()
    try:
        while True:
            c = next(cycles)
            for i, f in enumerate(spec.runner(), 1):
                print('\r', f'{CYAN(c, cf)}:{CYAN(i, lf)}', f'-->{join_cells(f)}<--',
                      DIM('(press CTRL+C to stop)'), end='')
                time.sleep(1 / 15)
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
