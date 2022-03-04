import logging

from cucu import config
from functools import wraps


def init_logging(logging_level):
    format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(level=logging_level, format=format)
    logging.debug('logger initialized')

    #logging.getLogger('parse').setLevel(logging.WARNING)
    #logging.getLogger('selenium').setLevel(logging.WARNING)
    #logging.getLogger('urllib3').setLevel(logging.WARNING)


@wraps(logging.debug)
def debug(*args, **kwargs):
    logging.getLogger('cucu').debug(*args, **kwargs)


@wraps(logging.warn)
def warn(*args, **kwargs):
    logging.getLogger('cucu').warn(*args, **kwargs)


@wraps(logging.info)
def info(*args, **kwargs):
    logging.getLogger('cucu').info(*args, **kwargs)


@wraps(logging.error)
def error(*args, **kwargs):
    logging.getLogger('cucu').error(*args, **kwargs)
