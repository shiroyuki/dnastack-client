from dnastack.client.workbench.ewes.models import ExecutionEngine, EngineParamPreset, EngineHealthCheck

from tests.cli.base import WorkbenchCliTestCase


class TestWorkbenchEnginesCommand(WorkbenchCliTestCase):
    @staticmethod
    def reuse_session() -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.invoke('use', f'{self.workbench_base_url}/api/service-registry')


