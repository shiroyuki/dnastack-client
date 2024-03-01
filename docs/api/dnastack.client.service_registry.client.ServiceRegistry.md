#### Class `dnastack.client.service_registry.client.ServiceRegistry(endpoint: dnastack.client.models.ServiceEndpoint)`
The base class for all DNAStack Clients 
##### Properties
###### `endpoint`

###### `events`

###### `url`
The base URL to the endpoint
##### Methods
###### `def create_http_session(suppress_error: bool, no_auth: bool) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `@staticmethod def get_adapter_type() -> str`
Get the descriptive adapter type
###### `@staticmethod def get_supported_service_types() -> List[dnastack.client.service_registry.models.ServiceType]`
The list of supported service types

The first one is always regarded as the default type.
###### `@staticmethod def make(endpoint: dnastack.client.models.ServiceEndpoint)`
Create this class with the given `endpoint`.