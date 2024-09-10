from typing import List, Optional
from urllib.parse import urljoin

from dnastack.client.models import ServiceEndpoint
from dnastack.client.service_registry.models import ServiceType
from dnastack.client.workbench.base_client import BaseWorkbenchClient
from dnastack.client.workbench.storage.models import Repository
from dnastack.common.tracing import Span


class StorageClient(BaseWorkbenchClient):

    @staticmethod
    def get_adapter_type() -> str:
        return 'sample-service'

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        return [
            ServiceType(group='com.dnastack.workbench', artifact='sample-service', version='1.0.0'),
        ]

    # noinspection PyMethodOverriding
    @classmethod
    def make(cls, endpoint: ServiceEndpoint, namespace: str):
        """Create this class with the given `endpoint` and `namespace`."""
        if not endpoint.type:
            endpoint.type = cls.get_default_service_type()
        return cls(endpoint, namespace)


    def create_repository(self, data: Repository, trace: Optional[Span] = None) -> Repository:
        with self.create_http_session() as session:
            response = session.post(
                urljoin(self.endpoint.url, f'{self.namespace}/repositories'),
                json=data.dict(),
                trace_context=trace
            )
        return Repository(**response.json())


    def get_repository(self, repository_id: str) -> Repository:
        with self.create_http_session() as session:
            response = session.get(
                urljoin(self.endpoint.url, f'{self.namespace}/repositories/{repository_id}'))
            return Repository(**response.json())


    def delete_repository(self, repository_id: str, etag: str):
        with self.create_http_session() as session:
            session.delete(
                urljoin(self.endpoint.url, f'{self.namespace}/repositories/{repository_id}'),
                headers={'If-Match': etag}
            )
