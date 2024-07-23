import time
from multiprocessing import Process

from click.testing import CliRunner
from cucu.cli import core

RUNTIME_TIMEOUT = 10


def process_func_to_run_cucu(workers, runtime_timeout):
    # not using mocks here since mocked `behave` doesn't pickle
    failing_scenario = "data/features/feature_with_failing_scenario.feature"
    runner = CliRunner()
    runner.invoke(
        core.run,
        f"--runtime-timeout {runtime_timeout} --workers={workers} {failing_scenario}",
    )


def test_subprocess_failure_shortcuts_runtime_timeout():
    start = time.time()
    p = Process(target=process_func_to_run_cucu, args=(2, RUNTIME_TIMEOUT))
    p.start()
    p.join()
    elapsed_time = time.time() - start
    assert elapsed_time < 10
