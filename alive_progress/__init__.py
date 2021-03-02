from .core.configuration import config_handler
from .core.progress import alive_bar

VERSION = (2, 0, 0)

__author__ = 'Rogério Sampaio de Almeida'
__email__ = 'rsalmei@gmail.com'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'A new kind of Progress Bar, with real-time throughput, ' \
                  'ETA and very cool animations!'

__all__ = ('alive_bar', 'config_handler')
