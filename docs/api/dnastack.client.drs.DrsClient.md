#### Class `dnastack.client.drs.DrsClient(endpoint: dnastack.client.models.ServiceEndpoint)`
Client for Data Repository Service
##### Properties
###### `endpoint`

###### `events`

###### `url`
The base URL to the endpoint
##### Methods
###### `def create_http_session(suppress_error: bool, no_auth: bool) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `def exit_download(url: str, status: dnastack.client.drs.DownloadStatus, message: str, exit_codes: dict)`
Report a file download with a status and message


| Parameter | Description |
| --- | --- |
| `url` | The downloaded resource's url |
| `status` | The reported status of the download |
| `message` | A message describing the reason for setting the status |
| `exit_codes` | A shared dict for all reports used by download_files |
###### `@staticmethod def get_adapter_type()`
Get the descriptive adapter type
###### `@staticmethod def get_supported_service_types() -> List[dnastack.client.service_registry.models.ServiceType]`
The list of supported service types

The first one is always regarded as the default type.
###### `@staticmethod def make(endpoint: dnastack.client.models.ServiceEndpoint)`
Create this class with the given `endpoint`.