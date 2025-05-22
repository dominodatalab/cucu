from behave.model_core import Status
from behave.reporter.base import Reporter

from cucu.database import operations
from cucu.database.connection import get_connection


class CucuDBReporter(Reporter):
    def __init__(self, config, cucu_run_id):
        super(CucuDBReporter, self).__init__(config)
        self.status = Status.undefined
        self.cucu_run_id = cucu_run_id

    def feature(self, feature):
        if feature.status not in (Status.passed, Status.skipped):
            self.status = Status.failed

        if feature.status == Status.executing:
            for scenario in feature.scenarios:
                if scenario.status == Status.executing:
                    scenario.status = Status.failed

                    conn = get_connection()
                    operations.update_scenario(
                        conn,
                        scenario.db_scenario_id,
                        "termiated",
                        scenario.duration,
                    )

    def end(self):
        conn = get_connection()
        if self.status == Status.undefined:
            self.status = Status.passed

        operations.update_cucu_run(
            conn,
            self.cucu_run_id,
            self.status.name,
        )
