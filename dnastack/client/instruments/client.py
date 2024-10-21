from typing import List, Iterator, Optional
from urllib.parse import urljoin

from dnastack.client.instruments.models import InstrumentListOptions, InstrumentListResponse
from dnastack.client.models import ServiceEndpoint
from dnastack.client.result_iterator import ResultIterator
from dnastack.client.service_registry.models import ServiceType
from dnastack.client.workbench.base_client import BaseWorkbenchClient, WorkbenchResultLoader
from dnastack.common.tracing import Span
from dnastack.http.session import HttpSession


class InstrumentListResultLoader(WorkbenchResultLoader):

    def __init__(self,
                 service_url: str,
                 http_session: HttpSession,
                 trace: Span,
                 list_options: Optional[InstrumentListOptions] = None,
                 max_results: int = None):
        super().__init__(service_url=service_url,
                         http_session=http_session,
                         list_options=list_options,
                         max_results=max_results,
                         trace=trace)

    def get_new_list_options(self) -> InstrumentListOptions:
        return InstrumentListOptions()

    def extract_api_response(self, response_body: dict) -> InstrumentListResponse:
        return InstrumentListResponse(**response_body)


class InstrumentsClient(BaseWorkbenchClient):

    @staticmethod
    def get_adapter_type() -> str:
        return 'instrument-service'

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        return [
            ServiceType(group='com.dnastack.workbench', artifact='instrument-service', version='1.0.0'),
        ]

    @classmethod
    def make(cls, endpoint: ServiceEndpoint, namespace: str):
        """Create this class with the given `endpoint` and `namespace`."""
        if not endpoint.type:
            endpoint.type = cls.get_default_service_type()
        return cls(endpoint, namespace)

    def list_instruments(self,
                          list_options: Optional[InstrumentListOptions] = None,
                          max_results: Optional[int] = None,
                          trace: Optional[Span] = None
                          ) -> Iterator[InstrumentListResponse]:
        trace = trace or Span(origin=self)
        return ResultIterator(InstrumentListResultLoader(
            service_url=urljoin(self.endpoint.url, f'{self.namespace}/instruments'),
            http_session=self.create_http_session(),
            list_options=list_options,
            max_results=max_results,
            trace=trace
        ))