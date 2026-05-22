import math


def reactive_fps(min_fps, calibrate):
    """Reactive frames per second engine, which adjusts the fps based on the expected task rate.

    I've started with the equation y = log10(x + m) * k + n, where:
      y is the desired fps, m and n are horizontal and vertical translation,
      k is a calibration factor, computed from some user input c (see readme for details).

    Considering minfps and maxfps as given constants, I came to:
      fps = log10(x + 1) * k + minfps, which must be equal to maxfps for x = c,
    so the factor k = (maxfps - minfps) / log10(c + 1), and
      fps = log10(x + 1) * (maxfps - minfps) / log10(c + 1) + minfps

    Neat! ;)

    Args:
        min_fps (float): minimum refreshes per second.
        calibrate (float): maximum expected rate of the task, used to adjust the fps curve.

    Returns:
        a callable to calculate the fps

    """
    max_fps = 60.
    calibrate = max(1e-6, calibrate)
    adjust_log_curve = 100. / min(calibrate, 100.)  # adjust the curve for small numbers
    factor = (max_fps - min_fps) / math.log10(calibrate * adjust_log_curve + 1.)

    def fps(rate):
        if rate <= 0:
            return 10.  # bootstrap speed
        if rate < calibrate:
            return math.log10(rate * adjust_log_curve + 1.) * factor + min_fps
        return max_fps

    return fps


def custom_fps(refresh_secs):
    """Custom frames per second engine, which calculates the fps based on a fixed refresh interval.

    Args:
        refresh_secs (float): the number of seconds between each refresh.

    Returns:
        a callable to calculate the fps

    """
    refresh_secs = 1 / refresh_secs

    def fps(rate):
        if rate <= 0:
            return 10.  # bootstrap speed
        return refresh_secs

    return fps
