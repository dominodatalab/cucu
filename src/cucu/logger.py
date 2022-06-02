import logging
import sys

from functools import wraps


def init_logging(logging_level):
    """
    initialize the cucu logger
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging_level)

    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)

    logging.debug("logger initialized")

    logging.getLogger("parse").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def init_debug_logger(output_file):
    """
    initialize a debug logger handler that runs at debug level and pushes
    all of the logs to the output file provided without affecting the logging
    of the main root logger
    """
    # assume that there's only 2 loggers the first one is the console one and
    # the second one if present is a previously set debug logger for the
    # previously executed scenario
    if len(logging.getLogger().handlers) != 1:
        logging.getLogger().removeHandler(logging.getLogger().handlers[1])

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.StreamHandler(output_file)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)


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
