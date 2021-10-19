import timeit

from about_time import duration_human

from .utils import toolkit
from ..core.configuration import config_handler
from ..core.progress import __alive_bar


def overhead(total=None, *, calibrate=None, **options):
    number = 400  # timeit number of runs inside each repetition.
    repeat = 300  # timeit how many times to repeat the whole test.

    config = config_handler(disable=True, **options)
    with __alive_bar(config, total, calibrate=calibrate, _cond=__lock):
        # the timing of the print_cells function increases proportionately with the
        # number of columns in the terminal, so I want a baseline here `VOID.cols == 0`.
        res = timeit.repeat('_alive_repr()', repeat=repeat, number=number,
                            globals=__alive_bar.__dict__)

    return duration_human(min(res) / number).replace('us', 'µs')


OVERHEAD_SAMPLING_GROUP = [
    ('definite', dict(total=1)),
    ('manual(b)', dict(total=1, manual=True)),
    ('manual(u)', dict(manual=True)),
    ('unknown', dict()),
]
OVERHEAD_SAMPLING = [
    ('default', dict()),
    ('receipt', dict(receipt_text=True)),
    ('no spinner', dict(spinner=None, receipt_text=True)),
    ('no monitor', dict(monitor=False, receipt_text=True)),
    ('no stats', dict(stats=False, receipt_text=True)),
    ('no monitor/stats', dict(stats=False, monitor=False, receipt_text=True)),
    ('only bar', dict(spinner=None, stats=False, monitor=False, elapsed=False, receipt_text=True)),
    ('no bar', dict(bar=None, receipt_text=True)),
    ('no bar/spinner', dict(bar=None, spinner=None, receipt_text=True)),
    ('only spinner', dict(bar=None, stats=False, monitor=False, elapsed=False, receipt_text=True)),
]


def overhead_sampling():
    print('warmup', end='', flush=True)
    for _ in range(5):
        print('.', end='', flush=True)
        overhead()
    print('\r', end='', flush=True)

    max_name = max(len(x) for x, _ in OVERHEAD_SAMPLING)
    print(f'{"":>{max_name}} | {" | ".join(g for g, _ in OVERHEAD_SAMPLING_GROUP)} |')
    for name, config in OVERHEAD_SAMPLING:
        print(f'{name:>{max_name}} ', end='', flush=True)
        for group, data in OVERHEAD_SAMPLING_GROUP:
            print(f'| {overhead(**data, **config):^{len(group)}} ', end='', flush=True)
        print('|')


def __noop_p(_ignore):
    return 0


class __lock:
    def __enter__(self):
        pass

    def __exit__(self, _type, value, traceback):
        pass


if __name__ == '__main__':
    parser, run = toolkit('Estimates the alive_progress overhead per cycle on your system.')

    run(overhead_sampling)
