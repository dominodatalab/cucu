import logging
import sys

from functools import wraps


def init_logging(logging_level):
    format = "%(asctime)s %(levelname)s %(message)s"
    logging.basicConfig(level=logging_level, format=format, stream=sys.stdout)
    logging.debug("logger initialized")

    logging.getLogger("parse").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


@wraps(logging.debug)
def debug(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.DEBUG:
        logging.getLogger("cucu").debug(*args, **kwargs)


@wraps(logging.info)
def info(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.INFO:
        logging.getLogger("cucu").info(*args, **kwargs)


@wraps(logging.warn)
def warn(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.WARN:
        logging.getLogger("cucu").warning(*args, **kwargs)


@wraps(logging.error)
def error(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.ERROR:
        logging.getLogger("cucu").error(*args, **kwargs)
