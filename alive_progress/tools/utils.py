import argparse

from .. import __version__


def parser(descr):
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('-v', '--version', action='version',
                        version=f'alive_progress {__version__}')
    return parser
