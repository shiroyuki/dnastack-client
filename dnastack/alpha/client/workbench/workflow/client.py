from urllib.parse import urljoin

from dnastack.alpha.client.workbench.workflow.models import ResolvedWorkflow, WorkflowDefaultsSelector, WorkflowDefaults
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.client.workbench.workflow.client import WorkflowClient


class AlphaWorkflowClient(WorkflowClient):

    def resolve_workflow(self, workflow_url: str) -> ResolvedWorkflow:
        with self.create_http_session() as session:
            response = session.get(
                urljoin(self.endpoint.url, f'{self.namespace}/workflows/resolve'),
                params={"workflow-url": workflow_url}
            )
            return ResolvedWorkflow(**response.json())

    def resolve_workflow_defaults(self, workflow_id: str, workflow_version_id: str,
                                  selector: WorkflowDefaultsSelector) -> WorkflowDefaults:
        with self.create_http_session() as session:
            response = session.post(
                urljoin(self.endpoint.url,
                        f'{self.namespace}/workflows/{workflow_id}/versions/{workflow_version_id}/defaults/resolve'),
                params={
                    "engine": selector.engine,
                    "provider": selector.provider,
                    "region": selector.region
                }
            )
            return WorkflowDefaults(**response.json())
