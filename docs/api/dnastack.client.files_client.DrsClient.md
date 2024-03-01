#### Class `dnastack.client.files_client.DrsClient(endpoint: dnastack.configuration.ServiceEndpoint)`
Client for Data Repository Service
##### Properties
###### `url`
The base URL to the endpoint
##### Methods
###### `def create_http_session(suppress_error: bool= True) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `def download_file(url: str, output_dir: str, display_progress_bar: bool, output_buffer_list: Union[list, NoneType], exit_codes: Union[dict, NoneType])`
Download a single DRS resource and output to a file or list


| Parameter | Description |
| --- | --- |
| `url` | The DRS resource url to download |
| `output_dir` | The directory to download output to. |
| `display_progress_bar` | Display a progress bar for the downloads to standard output |
| `output_buffer_list` | If specified, output downloaded data to the list specified in the argument |
| `exit_codes` | A shared dictionary of the exit statuses and messages |
###### `def download_files(urls: List[str], output_dir: str= "/Users/jnopporn/Projects/dnastack/dnastack-client-library", display_progress_bar: bool, parallel_download: bool= True, out: List)`
Download a list of files and output either to files in the current directory or dump to a specified list

:raises: DRSDownloadException if one or more of the downloads fail

| Parameter | Description |
| --- | --- |
| `urls` | A list of DRS resource urls to download |
| `output_dir` | The directory to download output to. |
| `display_progress_bar` | Display a progress bar for the downloads to standard output |
| `out` | If specified, output downloaded data to the list specified in the argument |
###### `def exit_download(url: str, status: dnastack.client.files_client.DownloadStatus, message: str, exit_codes: dict)`
Report a file download with a status and message


| Parameter | Description |
| --- | --- |
| `url` | The downloaded resource's url |
| `status` | The reported status of the download |
| `message` | A message describing the reason for setting the status |
| `exit_codes` | A shared dict for all reports used by download_files |
###### `@staticmethod def get_adapter_type()`
Get the descriptive adapter type
###### `def get_download_url(drs_url: str) -> Union[str, NoneType]`
Get the URL to download the DRS object
###### `@staticmethod def make(endpoint: dnastack.configuration.ServiceEndpoint)`
Create this class with the given `endpoint`.