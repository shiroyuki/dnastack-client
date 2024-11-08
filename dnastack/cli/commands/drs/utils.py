from typing import Optional

from imagination import container

from dnastack.cli.helpers.client_factory import ConfigurationBasedClientFactory
from dnastack.client.drs import DrsClient


def _get(context: Optional[str], id: Optional[str] = None) -> DrsClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    return factory.get(DrsClient, context_name=context, endpoint_id=id)
