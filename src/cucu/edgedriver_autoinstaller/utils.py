# coding: utf-8
"""
Helper functions for filename and URL generation.
"""

import logging
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as elemTree
import zipfile
from io import BytesIO

import requests

__author__ = "Yeongbin Jo <iam.yeongbin.jo@gmail.com>"


def get_edgedriver_filename():
    """
    Returns the filename of the binary for the current platform.
    :return: Binary filename
    """
    if sys.platform.startswith("win"):
        return "msedgedriver.exe"
    return "msedgedriver"


def get_variable_separator():
    """
    Returns the environment variable separator for the current platform.
    :return: Environment variable separator
    """
    if sys.platform.startswith("win"):
        return ";"
    return ":"


def get_platform_architecture():
    if sys.platform.startswith("linux") and sys.maxsize > 2**32:
        platform = "linux"
        architecture = "64"
    elif sys.platform == "darwin":
        platform = "mac"
        architecture = "64"
    elif sys.platform.startswith("win"):
        platform = "win"
        architecture = "32"
    else:
        raise RuntimeError(
            "Could not determine edgedriver download URL for this platform."
        )
    return platform, architecture


def get_edgedriver_url(version):
    """
    Generates the download URL for current platform , architecture and the given version.
    Supports Linux, MacOS and Windows.
    :param version: edgedriver version string
    :return: Download URL for edgedriver
    """
    base_url = "https://msedgedriver.azureedge.net//"
    platform, architecture = get_platform_architecture()
    return (
        base_url + version + "/edgedriver_" + platform + architecture + ".zip"
    )


def find_binary_in_path(filename):
    """
    Searches for a binary named `filename` in the current PATH. If an executable is found, its absolute path is returned
    else None.
    :param filename: Filename of the binary
    :return: Absolute path or None
    """
    if "PATH" not in os.environ:
        return None
    for directory in os.environ["PATH"].split(get_variable_separator()):
        binary = os.path.abspath(os.path.join(directory, filename))
        if os.path.isfile(binary) and os.access(binary, os.X_OK):
            return binary
    return None


def check_version(binary, required_version):
    try:
        version = subprocess.check_output([binary, "-v"])
        version = re.match(r".*?([\d.]+).*?", version.decode("utf-8"))[1]
        if version == required_version:
            return True
    except Exception:
        return False
    return False


def get_edge_version():
    """
    :return: the version of edge installed on client
    """
    platform, _ = get_platform_architecture()
    if platform == "linux":
        return  # Edge for linux still doesn't exists
    elif platform == "mac":
        process = subprocess.Popen(
            [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "--version",
            ],
            stdout=subprocess.PIPE,
        )
        version = (
            process.communicate()[0]
            .decode("UTF-8")
            .replace("Microsoft Edge", "")
            .strip()
        )
    elif platform == "win":
        process = subprocess.Popen(
            [
                "reg",
                "query",
                "HKEY_CURRENT_USER\\Software\\Microsoft\\Edge\\BLBeacon",
                "/v",
                "version",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        version = process.communicate()[0].decode("UTF-8").strip().split()[-1]
    else:
        return
    return version


def get_major_version(version):
    """
    :param version: the version of edge
    :return: the major version of edge
    """
    return version.split(".")[0]


def get_matched_edgedriver_version(version):
    """
    :param version: the version of edge
    :return: the version of edgedriver
    """
    doc = requests.get(
        "https://msedgedriver.azureedge.net/",
        headers={"accept-encoding": "gzip, deflate, br"},
    ).text
    root = elemTree.fromstring(doc)
    for k in root.iter("Name"):
        if k.text.find(get_major_version(version) + ".") == 0:
            return k.text.split("/")[0]
    return


def get_edgedriver_path():
    """
    :return: path of the edgedriver binary
    """
    return os.path.abspath(os.path.dirname(__file__))


def print_edgedriver_path():
    """
    Print the path of the edgedriver binary.
    """
    print(get_edgedriver_path())


def download_edgedriver(cwd=False):
    """
    Downloads, unzips and installs edgedriver.
    If a edgedriver binary is found in PATH it will be copied, otherwise downloaded.

    :param cwd: Flag indicating whether to download to current working directory
    :return: The file path of edgedriver
    """
    edge_version = get_edge_version()
    if not edge_version:
        logging.debug("edge is not installed.")
        return
    edgedriver_version = get_matched_edgedriver_version(edge_version)
    if not edgedriver_version:
        logging.debug(
            "Can not find edgedriver for currently installed edge version."
        )
        return
    major_version = get_major_version(edgedriver_version)

    if cwd:
        edgedriver_dir = os.path.join(
            os.path.abspath(os.getcwd()), major_version
        )
    else:
        edgedriver_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), major_version
        )
    edgedriver_filename = get_edgedriver_filename()
    edgedriver_filepath = os.path.join(edgedriver_dir, edgedriver_filename)
    if not os.path.isfile(edgedriver_filepath) or not check_version(
        edgedriver_filepath, edgedriver_version
    ):
        logging.debug(f"Downloading edgedriver ({edgedriver_version})...")
        if not os.path.isdir(edgedriver_dir):
            os.makedirs(edgedriver_dir)
        url = get_edgedriver_url(version=edgedriver_version)
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("URL Not Found")
        except Exception:
            raise RuntimeError(f"Failed to download edgedriver archive: {url}")
        archive = BytesIO(response.content)
        with zipfile.ZipFile(archive) as zip_file:
            zip_file.extract(edgedriver_filename, edgedriver_dir)
    else:
        logging.debug("edgedriver is already installed.")
    if not os.access(edgedriver_filepath, os.X_OK):
        os.chmod(edgedriver_filepath, 0o744)
    return edgedriver_filepath


if __name__ == "__main__":
    print(get_edge_version())
    print(download_edgedriver())
