#### Class `dnastack.client.dataconnect_client.DataConnectClient(endpoint: dnastack.configuration.ServiceEndpoint)`
A Client for the GA4GH Data Connect standard
##### Properties
###### `url`
The base URL to the endpoint
##### Methods
###### `def create_http_session(suppress_error: bool= True) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `@staticmethod def get_adapter_type() -> str`
Get the descriptive adapter type
###### `def get_table(table: Union[dnastack.client.dataconnect_client.Table, dnastack.client.dataconnect_client.TableWrapper, str]) -> dnastack.client.dataconnect_client.Table`
Get the table metadata
###### `def iterate_tables() -> Iterator[dnastack.client.dataconnect_client.Table]`
Iterate the list of tables
###### `def list_tables() -> List[dnastack.client.dataconnect_client.Table]`
List all tables
###### `@staticmethod def make(endpoint: dnastack.configuration.ServiceEndpoint)`
Create this class with the given `endpoint`.
###### `def query(query: str) -> Iterator[Dict[str, Any]]`
Run an SQL query
###### `def table(table: Union[dnastack.client.dataconnect_client.Table, dnastack.client.dataconnect_client.TableWrapper, str]) -> dnastack.client.dataconnect_client.TableWrapper`
Get the table wrapper