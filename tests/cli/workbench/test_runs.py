import json
from datetime import date, timedelta

from dnastack.client.workbench.samples.models import Sample

from dnastack.client.workbench.ewes.models import ExtendedRunStatus, ExtendedRun, BatchActionResult, BatchRunResponse, \
    MinimalExtendedRunWithInputs, BatchRunRequest, RunEvent, EventType, State, MinimalExtendedRun, \
    MinimalExtendedRunWithOutputs

from tests.cli.base import WorkbenchCliTestCase


class TestWorkbenchRunsCommand(WorkbenchCliTestCase):
    @staticmethod
    def reuse_session() -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.invoke('use', f'{self.workbench_base_url}/api/service-registry')
