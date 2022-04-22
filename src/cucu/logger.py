import logging
import sys

from cucu.config import CONFIG
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
        CONFIG["__CUCU_WROTE_TO_STDOUT"] = True


@wraps(logging.warn)
def warn(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.WARN:
        logging.getLogger("cucu").warn(*args, **kwargs)
        CONFIG["__CUCU_WROTE_TO_STDOUT"] = True


@wraps(logging.info)
def info(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.INFO:
        logging.getLogger("cucu").info(*args, **kwargs)
        CONFIG["__CUCU_WROTE_TO_STDOUT"] = True


@wraps(logging.error)
def error(*args, **kwargs):
    if logging.getLogger("cucu").getEffectiveLevel() <= logging.error:
        logging.getLogger("cucu").error(*args, **kwargs)
        CONFIG["__CUCU_WROTE_TO_STDOUT"] = True
