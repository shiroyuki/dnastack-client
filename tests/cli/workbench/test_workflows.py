import os
import shutil
import tempfile
import zipfile

from dnastack.client.workbench.workflow.models import Workflow, WorkflowVersion, WorkflowDefaults, \
    WorkflowTransformation
from tests.cli.base import WorkbenchCliTestCase

main_file_content = """
                version 1.0

                workflow no_task_workflow {
                    input {
                        String first_name
                        String? last_name
                    }
                }
                """
description_file_content = """
                        TITLE
                        DESCRIPTION
                        """


class TestWorkbenchWorkflowsCommand(WorkbenchCliTestCase):
    @staticmethod
    def reuse_session() -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.invoke('use', f'{self.workbench_base_url}/api/service-registry')

