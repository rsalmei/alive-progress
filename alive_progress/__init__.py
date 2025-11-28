from importlib import metadata

from .core.configuration import config_handler
from .core.progress import alive_bar, alive_it

try:
    pkg_metadata = metadata.metadata('alive-progress')
    __version__ = pkg_metadata['Version']
    __author__ = pkg_metadata['Author-Email']
    __email__ = __author__.split('<')[1][:-1]  # simple parser for "Name <email@addr.com>".
    __description__ = pkg_metadata['Summary']  # also known as "description" in the metadata.
except metadata.PackageNotFoundError:  # pragma: no cover
    # the package is not installed, so we can't get the metadata; common during development.
    __version__ = '0.0.0'
    __author__ = None
    __email__ = None
    __description__ = None

VERSION = tuple(map(int, __version__.split('.')))

__all__ = ('alive_bar', 'alive_it', 'config_handler')
