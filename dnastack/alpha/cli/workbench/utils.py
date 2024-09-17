from typing import Optional

from imagination import container

from dnastack.alpha.client.workbench.storage.client import StorageClient
from dnastack.cli.helpers.client_factory import ConfigurationBasedClientFactory
from dnastack.cli.workbench.utils import _populate_workbench_endpoint

WORKBENCH_HOSTNAME = "workbench.dnastack.com"


def get_storage_client(context_name: Optional[str] = None,
                        endpoint_id: Optional[str] = None,
                        namespace: Optional[str] = None) -> StorageClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(StorageClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(StorageClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
