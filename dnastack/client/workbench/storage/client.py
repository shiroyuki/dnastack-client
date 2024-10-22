from typing import List, Optional, Iterator
from urllib.parse import urljoin

from dnastack import ServiceEndpoint
from dnastack.client.result_iterator import ResultIterator
from dnastack.client.service_registry.models import ServiceType
from dnastack.client.workbench.base_client import BaseWorkbenchClient, WorkbenchResultLoader
from dnastack.client.workbench.storage.models import StorageAccount, StorageListOptions, StorageListResponse, \
    Platform, PlatformListOptions, PlatformListResponse
from dnastack.common.tracing import Span
from dnastack.http.session import HttpSession


class StorageAccountListResultLoader(WorkbenchResultLoader):
    def __init__(self,
                 service_url: str,
                 http_session: HttpSession,
                 trace: Optional[Span],
                 list_options: Optional[StorageListOptions] = None,
                 max_results: int = None):
        super().__init__(service_url=service_url,
                         http_session=http_session,
                         list_options=list_options,
                         max_results=max_results,
                         trace=trace)

    def get_new_list_options(self) -> StorageListOptions:
        return StorageListOptions()

    def extract_api_response(self, response_body: dict) -> StorageListResponse:
        return StorageListResponse(**response_body)


class PlatformListResultLoader(WorkbenchResultLoader):
    def __init__(self,
                 service_url: str,
                 http_session: HttpSession,
                 trace: Optional[Span],
                 list_options: Optional[PlatformListOptions] = None,
                 max_results: int = None):
        super().__init__(service_url=service_url,
                         http_session=http_session,
                         list_options=list_options,
                         max_results=max_results,
                         trace=trace)

    def get_new_list_options(self) -> PlatformListOptions:
        return PlatformListOptions()

    def extract_api_response(self, response_body: dict) -> PlatformListResponse:
        return PlatformListResponse(**response_body)


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

    def add_storage_account(self, storage_account: StorageAccount) -> StorageAccount:
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

    def list_storage_accounts(self, list_options: Optional[StorageListOptions], max_results: int) -> Iterator[
        StorageAccount]:
        """List storage accounts."""
        return ResultIterator(StorageAccountListResultLoader(
            service_url=urljoin(self.endpoint.url, f'{self.namespace}/storage'),
            http_session=self.create_http_session(),
            list_options=list_options,
            trace=None,
            max_results=max_results))

    def add_platform(self, platform: Platform) -> Platform:
        """Create a new platform."""
        with self.create_http_session() as session:
            response = session.post(
                urljoin(self.endpoint.url, f'{self.namespace}/storage/{platform.storage_account_id}/platforms'),
                json=platform.dict()
            )
        return Platform(**response.json())

    def delete_platform(self, platform_id: str, storage_account_id: str) -> None:
        """Delete a platform."""
        with self.create_http_session() as session:
            session.delete(urljoin(self.endpoint.url, f'{self.namespace}/storage/{storage_account_id}/platforms/{platform_id}'))
        return None

    def get_platform(self, platform_id: str, storage_account_id: str) -> Platform:
        """Get a platform of storage account by its ID."""
        with self.create_http_session() as session:
            response = session.get(urljoin(self.endpoint.url, f'{self.namespace}/storage/{storage_account_id}/platforms/{platform_id}'))
        return Platform(**response.json())

    def list_platforms(self, list_options: Optional[PlatformListOptions], max_results: int) -> Iterator[Platform]:
        """List platforms."""
        url = f'{self.namespace}/storage/{list_options.storage_account_id}/platforms' \
            if list_options.storage_account_id \
            else f'{self.namespace}/storage/platforms'
        return ResultIterator(PlatformListResultLoader(
            service_url=urljoin(self.endpoint.url, url),
            http_session=self.create_http_session(),
            list_options=list_options,
            trace=None,
            max_results=max_results))