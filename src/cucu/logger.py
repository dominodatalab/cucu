import logging
import sys
from functools import wraps

from cucu.config import CONFIG


def init_logging(logging_level):
    """
    initialize the cucu logger
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging_level)

    logging.getLogger().addHandler(handler)
    # set the top level logger to DEBUG while the console stream handler is
    # actually set to whatever you passed in using --logging-level which is
    # INFO by default
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
    if len(logging.getLogger().handlers) > 1:
        logging.getLogger().removeHandler(logging.getLogger().handlers[1])

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.StreamHandler(output_file)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)


@wraps(logging.log)
def log(*args, **kwargs):
    console_handler = logging.getLogger().handlers[0]
    logging_level = console_handler.level

    msg_level = args[0]
    if logging_level <= msg_level:
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = True

    logging.getLogger().log(*args, **kwargs)


@wraps(logging.debug)
def debug(*args, **kwargs):
    console_handler = logging.getLogger().handlers[0]
    logging_level = console_handler.level

    if logging_level <= logging.DEBUG:
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = True

    logging.getLogger().debug(*args, **kwargs)


@wraps(logging.info)
def info(*args, **kwargs):
    console_handler = logging.getLogger().handlers[0]
    logging_level = console_handler.level

    if logging_level <= logging.INFO:
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = True

    logging.info(*args, **kwargs)


@wraps(logging.warn)
def warn(*args, **kwargs):
    console_handler = logging.getLogger().handlers[0]
    logging_level = console_handler.level

    if logging_level <= logging.WARN:
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = True

    logging.getLogger().warning(*args, **kwargs)


@wraps(logging.error)
def error(*args, **kwargs):
    console_handler = logging.getLogger().handlers[0]
    logging_level = console_handler.level

    if logging_level <= logging.ERROR:
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = True

    logging.getLogger().error(*args, **kwargs)


@wraps(logging.exception)
def exception(*args, **kwargs):
    console_handler = logging.getLogger().handlers[0]
    logging_level = console_handler.level

    if logging_level <= logging.ERROR:
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = True

    logging.getLogger().exception(*args, **kwargs)
