from .animations.bars import bar_factory
from .animations.spinners import alongside_spinner_factory, bouncing_spinner_factory, \
    delayed_spinner_factory, frame_spinner_factory, scrolling_spinner_factory, \
    sequential_spinner_factory
from .animations.utils import spinner_player
from .core.configuration import config_handler
from .core.progress import alive_bar
from .styles.exhibit import Show, show_bars, show_spinners, show_themes, showtime
from .styles.internal import BARS, SPINNERS, THEMES
from .tools.general import print_chars

VERSION = (2, 0, 0)

__author__ = 'Rogério Sampaio de Almeida'
__email__ = 'rsalmei@gmail.com'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'A new kind of Progress Bar, with real-time throughput, ' \
                  'ETA and very cool animations!'

__all__ = (
    'alive_bar', 'config_handler', 'bar_factory', 'spinner_player',
    'frame_spinner_factory', 'scrolling_spinner_factory', 'bouncing_spinner_factory',
    'sequential_spinner_factory', 'alongside_spinner_factory', 'delayed_spinner_factory', 'BARS',
    'SPINNERS', 'THEMES', 'Show', 'showtime', 'show_spinners', 'show_bars', 'show_themes',
    'print_chars'
)
