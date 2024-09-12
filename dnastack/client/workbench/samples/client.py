from typing import List, Iterator, Optional, Union, Iterable
from urllib.parse import urljoin

from dnastack.client.models import ServiceEndpoint
from dnastack.client.result_iterator import ResultIterator
from dnastack.client.service_registry.models import ServiceType
from dnastack.client.workbench.base_client import BaseWorkbenchClient, WorkbenchResultLoader
from dnastack.client.workbench.samples.models import Sample
from dnastack.common.tracing import Span
from dnastack.http.session import HttpSession


class SamplesClient(BaseWorkbenchClient):

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


    def list_samples(self,
                  list_options: Optional[SamplesListOptions] = None
                  ) -> Iterator[Sample]:
        return ResultIterator(ExtendedRunListResultLoader(
            service_url=urljoin(self.endpoint.url, f'{self.namespace}/ga4gh/wes/v1/runs'),
            http_session=self.create_http_session(),
            list_options=list_options,
            max_results=max_results,
            trace=trace,
        ))


class ExtendedRunListResultLoader(WorkbenchResultLoader):

    def __init__(self,
                 service_url: str,
                 http_session: HttpSession,
                 trace: Span,
                 list_options: Optional[ExtendedRunListOptions] = None,
                 max_results: int = None):
        super().__init__(service_url=service_url,
                         http_session=http_session,
                         list_options=list_options,
                         max_results=max_results,
                         trace=trace)

    def get_new_list_options(self) -> ExtendedRunListOptions:
        return ExtendedRunListOptions()

    def extract_api_response(self, response_body: dict) -> ExtendedRunListResponse:
        return ExtendedRunListResponse(**response_body)