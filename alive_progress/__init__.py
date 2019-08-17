# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

VERSION = (1, 1, 0)

__author__ = 'Rogério Sampaio de Almeida'
__email__ = 'rsalmei@gmail.com'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'An animated and smart Progress Bar for python.'

from .bars import standard_bar_factory, unknown_bar_factory
from .progress import alive_bar
from .spinners import bouncing_spinner_factory, compound_spinner_factory, \
    delayed_spinner_factory, frame_spinner_factory, spinner_player, scrolling_spinner_factory
from .styles import BARS, SPINNERS
from .exhibit import showtime
from .configuration import config_handler

__all__ = ['alive_bar', 'standard_bar_factory', 'unknown_bar_factory', 'spinner_player',
           'frame_spinner_factory', 'scrolling_spinner_factory', 'bouncing_spinner_factory',
           'compound_spinner_factory', 'delayed_spinner_factory', 'BARS', 'SPINNERS',
           'showtime', 'config_handler']

import sys

if sys.version_info <= (3,):
    __all__ = [bytes(x) for x in __all__]
