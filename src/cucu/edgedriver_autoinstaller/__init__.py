# coding: utf-8

import os
import logging
from . import utils


def install(cwd=False):
    """
    Appends the directory of the edgedriver binary file to PATH.

    :param cwd: Flag indicating whether to download to current working directory
    :return: The file path of edgedriver
    """
    edgedriver_filepath = utils.download_edgedriver(cwd)
    if not edgedriver_filepath:
        logging.debug("Can not download edgedriver.")
        return
    edgedriver_dir = os.path.dirname(edgedriver_filepath)
    if "PATH" not in os.environ:
        os.environ["PATH"] = edgedriver_dir
    elif edgedriver_dir not in os.environ["PATH"]:
        os.environ["PATH"] = (
            edgedriver_dir
            + utils.get_variable_separator()
            + os.environ["PATH"]
        )
    return edgedriver_filepath


def get_edge_version():
    """
    Get installed version of edge on client

    :return: The version of edge
    """
    return utils.get_edge_version()
