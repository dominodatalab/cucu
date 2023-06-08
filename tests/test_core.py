import time
from multiprocessing import Process
from unittest import mock

from click.testing import CliRunner
from cucu.cli import core

RUNTIME_TIMEOUT = 10


def process_func_to_run_cucu(workers, runtime_timeout):
    isdir_mock = mock.MagicMock(return_value=False)
    with mock.patch("os.path.isdir", isdir_mock):
        behave_mock = mock.MagicMock(side_effect=RuntimeError("something bad"))
        with mock.patch("cucu.cli.core.behave", behave_mock):
            runner = CliRunner()
            runner.invoke(
                core.run,
                f"--runtime-timeout {runtime_timeout} --workers={workers} abc",
            )


def test_timeout_with_behave_exception_in_workers():
    start = time.time()
    p = Process(target=process_func_to_run_cucu, args=(2, RUNTIME_TIMEOUT))
    p.start()
    p.join()
    elapsed_time = time.time() - start
    assert elapsed_time < 5
