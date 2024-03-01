#### Class `dnastack.client.wes_client.WesClient(endpoint: dnastack.configuration.ServiceEndpoint)`
A client for the Workflow Execution Service (WES) standard
##### Properties
###### `url`
The base URL to the endpoint
##### Methods
###### `def cancel(run_id: str) -> dict`
Cancel a running workflow with a specified Run ID

| Parameter | Description |
| --- | --- |
| `run_id` | The Run ID of the workflow |

| Return |
| --- |
| A dict of the cancelled workflow's Run ID if successful |
###### `def create_http_session(suppress_error: bool= True) -> dnastack.http.session.HttpSession`
Create HTTP session wrapper
###### `def execute(workflow_url: str, attachment_files: list, input_params_file: str, engine_param: str, engine_params_file: str, tag: str, tags_file: str) -> dict`
Submit a workflow to be executed

(in which case an attachment with that name must be present),
or it can be an absolute path to a file on the internet

| Parameter | Description |
| --- | --- |
| `workflow_url` | The url of the workflow to be executed. This can either be a relative path |
| `attachment_files` | If workflow_url is a relative path, this is the file to be executed |
| `input_params_file` | A path to a JSON file containing all of the inputs of the workflow |
| `engine_param` | A single engine parameter of the form "K=V" |
| `engine_params_file` | A path to a JSON file containing all of the engine parameters of the workflow |
| `tag` | A single tag value of the form "K=V" |
| `tags_file` | A path to a JSON file containing all of the engine parameters of the workflow |

| Return |
| --- |
| A dict containing the response given by the WES instance |
###### `def get(run_id: str, status_only: bool) -> dict`
Get the details of a run including status


| Parameter | Description |
| --- | --- |
| `run_id` | The Run ID of the workflow |
| `status_only` | Only return the status of the workflow |

| Return |
| --- |
| A dict containing run information |
###### `@staticmethod def get_adapter_type() -> str`
Get the descriptive adapter type
###### `def info() -> dict`
Get the service info of the Workflow Execution Service (WES) instance


| Return |
| --- |
| A dict containing the WES instance metadata |
###### `def list(page_size: int, next_page_token: str) -> dict`
Get a list of all previously executed workflows, including current state


| Parameter | Description |
| --- | --- |
| `page_size` | Specify how many results to return on a single page (excluding a next page token) |
| `next_page_token` | If given, get the results starting after the provided page token |

| Return |
| --- |
| A dict of the Run ID and current state of all previously run workflows |
###### `@staticmethod def make(endpoint: dnastack.configuration.ServiceEndpoint)`
Create this class with the given `endpoint`.
###### `def run_logs(run_id: str, stdout: bool, stderr: bool, url: str, task: str, index: int) -> str`
Get the logs of a workflow from either stdout or stderr

If no index is provided, 0 will be used by default

| Parameter | Description |
| --- | --- |
| `run_id` | The Run ID of the workflow |
| `stdout` | Get the logs of stdout |
| `stderr` | Get the logs of stderr |
| `url` | Get the logs at a specified url. If this is specified, no other parameters are required |
| `task` | The name of the task to get logs for. If unspecified, the logs for all tasks will be retrieved |
| `index` | The (zero-based) index of the task to get logs for. |

| Return |
| --- |
| The logs of the workflow's task and index as a str |