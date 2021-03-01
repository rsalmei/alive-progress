def elapsed_text(seconds, precise):
    seconds = round(seconds, 1 if precise else 0)
    if seconds < 60.:
        return '{:{}f}s'.format(seconds, .1 if precise else .0)

    minutes, seconds = divmod(seconds, 60.)
    if minutes < 60.:
        return '{:.0f}:{:0{}f}'.format(minutes, seconds, 4.1 if precise else 2.0)

    hours, minutes = divmod(minutes, 60.)
    return '{:.0f}:{:02.0f}:{:0{}f}'.format(hours, minutes, seconds, 4.1 if precise else 2.0)


def eta_text(eta):
    if eta is None or eta < 0.:
        return '-'
    return elapsed_text(eta, False)


def simple_eta(logic_total, pos, rate):
    return (logic_total - pos) / rate


def gen_simple_exponential_smoothing_eta(alfa, logic_total):
    """Implements a generator with a simple exponential smoothing of the
    eta time series.
    Given alfa and y_hat (t-1), we can calculate the next y_hat:
        y_hat = alfa * y + (1 - alfa) * y_hat
        y_hat = alfa * y + y_hat - alfa * y_hat
        y_hat = y_hat + alfa * (y - y_hat)

    Args:
        alfa (float): the smoothing coefficient
        logic_total (float):

    Returns:

    """
    pos = rate = None
    while not rate:
        pos, rate = yield
    y_hat = simple_eta(logic_total, pos, rate)
    while True:
        temp, rate = yield y_hat
        if temp == pos:  # reduce numbers bouncing around.
            continue
        pos = temp
        y = simple_eta(logic_total, pos, rate)
        y_hat += alfa * (y - y_hat)
