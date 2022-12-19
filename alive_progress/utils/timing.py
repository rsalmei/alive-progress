def elapsed_text(seconds, precise, prefix=''):
    seconds = round(seconds, 1 if precise else 0)
    if seconds < 60.:
        return '{}{:{}f}s'.format(prefix, seconds, .1 if precise else .0)

    minutes, seconds = divmod(seconds, 60.)
    if minutes < 60.:
        return '{}{:.0f}:{:0{}f}'.format(prefix, minutes, seconds, 4.1 if precise else 2.0)

    hours, minutes = divmod(minutes, 60.)
    return '{}{:.0f}:{:02.0f}:{:0{}f}'.format(prefix, hours, minutes, seconds,
                                              4.1 if precise else 2.0)


def eta_text(eta):
    if eta < 0.:
        return '?'
    return elapsed_text(eta, False, '~')


def fn_simple_eta(logic_total):
    def simple_eta(pos, rate):
        return (logic_total - pos) / rate

    return simple_eta


def gen_simple_exponential_smoothing(alfa, fn):
    """Implements a generator with a simple exponential smoothing of some function.
    Given alfa and y_hat (t-1), we can calculate the next y_hat:
        y_hat = alfa * y + (1 - alfa) * y_hat
        y_hat = alfa * y + y_hat - alfa * y_hat
        y_hat = y_hat + alfa * (y - y_hat)

    Args:
        alfa (float): the smoothing coefficient
        fn (Callable): the function

    Returns:

    """
    p = (0.,)
    while any(x == 0. for x in p):
        p = yield 0.
    y_hat = fn(*p)
    while True:
        p = yield y_hat
        y = fn(*p)
        y_hat += alfa * (y - y_hat)
