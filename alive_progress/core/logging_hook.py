import logging
import sys


def install_logging_hook():
    root = logging.root
    return {h: h.setStream(sys.stdout) for h in root.handlers
            if isinstance(h, logging.StreamHandler)}


def uninstall_logging_hook(before):
    [h.setStream(s) for h, s in before.items()]
