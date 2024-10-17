from typing import Optional, Iterator
from urllib.parse import urljoin

from dnastack.alpha.client.workbench.workflow.models import ResolvedWorkflow, WorkflowDefaultsSelector, \
    WorkflowDefaults, WorkflowDefaultsListOptions, WorkflowDefaultsListResponse, WorkflowDefaultsCreateRequest, \
    WorkflowDefaultsUpdateRequest
from dnastack.client.result_iterator import ResultIterator
from dnastack.client.workbench.base_client import WorkbenchResultLoader
from dnastack.client.workbench.workflow.client import WorkflowClient
from dnastack.common.tracing import Span
from dnastack.http.session import HttpSession


class WorkflowDefaultsListResultLoader(WorkbenchResultLoader):
    def __init__(self,
                 service_url: str,
                 http_session: HttpSession,
                 trace: Optional[Span],
                 list_options: Optional[WorkflowDefaultsListOptions] = None,
                 max_results: int = None):
        super().__init__(service_url=service_url,
                         http_session=http_session,
                         list_options=list_options,
                         max_results=max_results,
                         trace=trace)

    def get_new_list_options(self) -> WorkflowDefaultsListOptions:
        return WorkflowDefaultsListOptions()

    def extract_api_response(self, response_body: dict) -> WorkflowDefaultsListResponse:
        return WorkflowDefaultsListResponse(**response_body)


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

    def list_workflow_defaults(self, workflow_id: str, version_id: str, max_results: int,
                               list_options: WorkflowDefaultsListOptions) -> Iterator[
        WorkflowDefaults]:
        """List storage accounts."""
        return ResultIterator(WorkflowDefaultsListResultLoader(
            service_url=urljoin(self.endpoint.url,
                                f'{self.namespace}/workflows/{workflow_id}/versions/{version_id}/defaults'),
            http_session=self.create_http_session(),
            list_options=list_options,
            trace=None,
            max_results=max_results))

    def get_workflow_defaults(self, workflow_id: str, version_id: str, default_id: str) -> WorkflowDefaults:
        with self.create_http_session() as session:
            response = session.get(
                urljoin(self.endpoint.url,
                        f'{self.namespace}/workflows/{workflow_id}/versions/{version_id}/defaults/{default_id}')
            )
            return WorkflowDefaults(**response.json())

    def create_workflow_defaults(self, workflow_id: str, version_id: str,
                                 workflow_defaults: WorkflowDefaultsCreateRequest) -> WorkflowDefaults:
        with self.create_http_session() as session:
            response = session.post(
                urljoin(self.endpoint.url,
                        f'{self.namespace}/workflows/{workflow_id}/versions/{version_id}/defaults'),
                json=workflow_defaults.dict()
            )
            return WorkflowDefaults(**response.json())

    def delete_workflow_defaults(self, workflow_id: str, version_id: str, default_id: str, if_match: str):
        with self.create_http_session() as session:
            session.delete(
                urljoin(self.endpoint.url,
                        f'{self.namespace}/workflows/{workflow_id}/versions/{version_id}/defaults/{default_id}'),
                headers={"If-Match": if_match}
            )

    def update_workflow_defaults(self, workflow_id: str, version_id: str, default_id: str, if_match: str,
                                 workflow_defaults: WorkflowDefaultsUpdateRequest):
        with self.create_http_session() as session:
            response = session.submit("PUT",
                urljoin(self.endpoint.url,
                        f'{self.namespace}/workflows/{workflow_id}/versions/{version_id}/defaults/{default_id}'),
                json=workflow_defaults.dict(),
                headers={"If-Match": if_match}
            )
            return WorkflowDefaults(**response.json())
