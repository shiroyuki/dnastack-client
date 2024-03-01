#### Class `dnastack.client.data_connect.DataConnectClient(endpoint: dnastack.client.models.ServiceEndpoint)`
A Client for the GA4GH Data Connect standard
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
###### `def iterate_tables(no_auth: bool) -> Iterator[dnastack.client.data_connect.TableInfo]`
Iterate the list of tables
###### `def list_tables(no_auth: bool) -> List[dnastack.client.data_connect.TableInfo]`
List all tables
###### `@staticmethod def make(endpoint: dnastack.client.models.ServiceEndpoint)`
Create this class with the given `endpoint`.
###### `def query(query: str, no_auth: bool, trace: Optional[dnastack.common.tracing.Span]) -> Iterator[Dict[str, Any]]`
Run an SQL query
###### `def table(table: Union[dnastack.client.data_connect.TableInfo, dnastack.client.data_connect.Table, str], no_auth: bool) -> dnastack.client.data_connect.Table`
Get the table wrapper