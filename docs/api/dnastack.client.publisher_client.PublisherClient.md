#### Class `dnastack.client.publisher_client.PublisherClient()`
A consolidated client for a suite of APIs (Data Connect API, WES API, DRS API, and Collection Service API)

All sub-clients are automatically initiated with the configuration of the default service endpoint of each
sub-client type (as known as "adapter type"), defined in the configuration file.
##### Properties
###### `collections`
The client for the default collection API endpoint
###### `data_connect`
The client for the default data connect endpoint
###### `dataconnect`
..deprecated: v3.1
###### `files`
The client for the default data repository service (DRS) endpoint
###### `wes`
The client for the default WES endpoint
##### Methods
###### `def download(urls: Union[str, List[str]], output_dir: str= "/Users/jnopporn/Projects/dnastack/dnastack-client-library", display_progress_bar: bool)`
Download one or more DRS resources from the specified urls


| Parameter | Description |
| --- | --- |
| `urls` | One or a list of DRS urls (drs://...) |
| `output_dir` | The directory to output the downloaded files to. |
| `display_progress_bar` | Display the progress of the downloads. This is False by default |
###### `def get_services() -> List[dnastack.client.base_client.BaseServiceClient]`
Return all configured services.


| Return |
| --- |
| List of all configured clients (dataconnect, collections, wes) |
###### `def load(urls: Union[str, List[str]]) -> Any`
Return the raw output of one or more DRS resources


| Parameter | Description |
| --- | --- |
| `urls` | One or a list of DRS urls (drs://...) |

| Return |
| --- |
| The raw output of the specified DRS resource |