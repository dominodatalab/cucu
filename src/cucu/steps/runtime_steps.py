import fcntl
import os

from cucu import logger, retry, run_steps, step
from cucu.hooks import (
    register_before_all_hook,
    register_before_scenario_hook,
    register_after_scenario_hook,
    register_after_this_scenario_hook,
)
from cucu.config import CONFIG


if CONFIG["CUCU_RESULTS_DIR"]:
    __LOCK_FILES_DIR = os.path.join(CONFIG["CUCU_RESULTS_DIR"], ".locks")
    __STATE_LOCK_NAME = "global"

    logger.warn("init lock files directory")
    os.makedirs(__LOCK_FILES_DIR, exist_ok=True)


def acquire_lock(name):
    lockfile_filepath = os.path.join(__LOCK_FILES_DIR, name)
    lockfile = open(lockfile_filepath, "a")
    fcntl.lockf(lockfile.fileno(), fcntl.LOCK_EX)
    logger.warn(f"{os.getpid()}: runtime lock {name} acquired")


def release_lock(name):
    lockfile_filepath = os.path.join(__LOCK_FILES_DIR, name)
    lockfile = open(lockfile_filepath, "a")
    fcntl.lockf(lockfile.fileno(), fcntl.LOCK_UN)
    logger.warn(f"{os.getpid()}: runtime lock {name} released")


@step(
    'I acquire the exclusive lock on the resource "{name}" for the duration of this scenario'
)
def acquire_exclusive_lock(ctx, name):
    acquire_lock(__STATE_LOCK_NAME)
    try:
        acquire_lock(name)
    finally:
        release_lock(__STATE_LOCK_NAME)

    def release_this_lock(_):
        release_lock(name)

    register_after_this_scenario_hook(release_this_lock)
