#### Class `dnastack.client.collections_client.CollectionServiceClient(endpoint: dnastack.configuration.ServiceEndpoint)`
Client for Collection API
##### Properties
###### `url`
The base URL to the endpoint
##### Methods
###### `def create_http_session(suppress_error: bool= True) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `def get(id_or_slug_name: str) -> dnastack.client.collections_client.Collection`
Get a collection by ID or slug name
###### `@staticmethod def get_adapter_type() -> str`
Get the descriptive adapter type
###### `def get_data_connect_client(collection: Union[str, dnastack.client.collections_client.Collection]) -> dnastack.client.dataconnect_client.DataConnectClient`
Get the Data Connect client for the given collection (ID, slug name, or collection object)
###### `def list_collections() -> List[dnastack.client.collections_client.Collection]`
List all available collections
###### `@staticmethod def make(endpoint: dnastack.configuration.ServiceEndpoint)`
Create this class with the given `endpoint`.