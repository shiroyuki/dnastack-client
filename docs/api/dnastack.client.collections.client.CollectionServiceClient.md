#### Class `dnastack.client.collections.client.CollectionServiceClient(endpoint: dnastack.client.models.ServiceEndpoint)`
Client for Collection API
##### Properties
###### `endpoint`

###### `events`

###### `url`
The base URL to the endpoint
##### Methods
###### `def create_http_session(suppress_error: bool, no_auth: bool) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `def data_connect_endpoint(collection: Union[str, dnastack.client.collections.model.Collection, NoneType], no_auth: bool) -> dnastack.client.models.ServiceEndpoint`
Get the URL to the corresponding Data Connect endpoint


| Parameter | Description |
| --- | --- |
| `collection` | The collection or collection ID. It is optional and only used by the explorer. |
| `no_auth` | Trigger this method without invoking authentication even if it is required. |
###### `def get(id_or_slug_name: str, no_auth: bool, trace: Optional[dnastack.common.tracing.Span]) -> dnastack.client.collections.model.Collection`
Get a collection by ID or slug name
###### `@staticmethod def get_adapter_type() -> str`
Get the descriptive adapter type
###### `@staticmethod def get_supported_service_types() -> List[dnastack.client.service_registry.models.ServiceType]`
The list of supported service types

The first one is always regarded as the default type.
###### `def list_collections(no_auth: bool, trace: Optional[dnastack.common.tracing.Span]) -> List[dnastack.client.collections.model.Collection]`
List all available collections
###### `@staticmethod def make(endpoint: dnastack.client.models.ServiceEndpoint)`
Create this class with the given `endpoint`.