import asyncio

from dnastack.client.workbench.storage.models import Platform, StorageAccount

from dnastack.client.workbench.samples.models import Sample, SampleFile
from tests.cli.base import WorkbenchCliTestCase


class TestWorkbenchSamplesCommand(WorkbenchCliTestCase):
    @staticmethod
    def reuse_session() -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.invoke('use', f'{self.workbench_base_url}/api/service-registry')
        self.submit_hello_world_workflow_batch()
        self.storage_account = None
        self.platform = None



