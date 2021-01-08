# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from .animations.bars import standard_bar_factory, unknown_bar_factory
from .animations.spinners import bouncing_spinner_factory, compound_spinner_factory, \
    delayed_spinner_factory, frame_spinner_factory, scrolling_spinner_factory
from .animations.utils import spinner_player
from .core.configuration import config_handler
from .core.progress import alive_bar
from .styles.exhibit import print_chars, show_bars, show_spinners, showtime
from .styles.internal import BARS, SPINNERS, THEMES

VERSION = (1, 6, 2)

__author__ = 'Rogério Sampaio de Almeida'
__email__ = 'rsalmei@gmail.com'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'A new kind of Progress Bar, with real-time throughput, ' \
                  'eta and very cool animations!'

__all__ = ['alive_bar', 'standard_bar_factory', 'unknown_bar_factory', 'spinner_player',
           'frame_spinner_factory', 'scrolling_spinner_factory', 'bouncing_spinner_factory',
           'compound_spinner_factory', 'delayed_spinner_factory', 'BARS', 'SPINNERS', 'THEMES',
           'print_chars', 'show_bars', 'show_spinners', 'showtime', 'config_handler']

if sys.version_info < (3,):  # pragma: no cover
    __all__ = [bytes(x) for x in __all__]
