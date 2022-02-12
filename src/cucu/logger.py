import logging

from cucu import config
from functools import wraps


def init_logging(logging_level):
    logging.basicConfig(level=logging_level)
    logging.debug('logger initialized')


@wraps(logging.debug)
def debug(*args, **kwargs):
    if logging.root.level == 'DEBUG':
        logging.debug(*args, **kwargs)
        config.CONFIG['CUCU_WROTE_TO_STDOUT'] = True


@wraps(logging.warn)
def warn(*args, **kwargs):
    if logging.root.level == 'WARN':
        logging.warn(*args, **kwargs)
        config.CONFIG['CUCU_WROTE_TO_STDOUT'] = True


@wraps(logging.info)
def info(*args, **kwargs):
    if logging.root.level == 'INFO':
        logging.info(*args, **kwargs)
        config.CONFIG['CUCU_WROTE_TO_STDOUT'] = True
