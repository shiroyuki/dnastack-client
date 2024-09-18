from typing import List
from urllib.parse import urljoin

from dnastack import ServiceEndpoint
from dnastack.alpha.client.workbench.storage.models import StorageAccount
from dnastack.client.service_registry.models import ServiceType
from dnastack.client.workbench.base_client import BaseWorkbenchClient


class StorageClient(BaseWorkbenchClient):
    @staticmethod
    def get_adapter_type() -> str:
        return 'sample-service'

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        return [
            ServiceType(group='com.dnastack.workbench', artifact='sample-service', version='1.0.0'),
        ]

    @classmethod
    def make(cls, endpoint: ServiceEndpoint, namespace: str):
        """Create this class with the given `endpoint` and `namespace`."""
        if not endpoint.type:
            endpoint.type = cls.get_default_service_type()
        return cls(endpoint, namespace)


    def create_storage_account(self, storage_account: StorageAccount) -> StorageAccount:
        """Create a new storage account."""
        with self.create_http_session() as session:
            response = session.post(
                urljoin(self.endpoint.url, f'{self.namespace}/storage'),
                json=storage_account.dict()
            )
        return StorageAccount(**response.json())


    # Add method for deleting a storage account
    def delete_storage_account(self, storage_account_id: str) -> None:
        """Delete a storage account."""
        with self.create_http_session() as session:
            session.delete(urljoin(self.endpoint.url, f'{self.namespace}/storage/{storage_account_id}'))
        return None


    def get_storage_account(self, storage_account_id: str) -> StorageAccount:
        """Get a storage account by its ID."""
        with self.create_http_session() as session:
            response = session.get(urljoin(self.endpoint.url, f'{self.namespace}/storage/{storage_account_id}'))
        return StorageAccount(**response.json())
