# Developers' Guide: Development/Testing Configuration

This documentation is NOT intended for regular users, such as researchers or data scientists.

## Environment Variables

These are designed to override configurations specifically related to how the CLI/library operates.

| Variable Name                   | Type   | Usage                                                                                                                                                                                                                                                      | Default Value (if optional)     | 
|---------------------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| `DNASTACK_CONFIG_FILE`          | `str`  | Override the default location of the configuration file. For testing, please define this variable.                                                                                                                                                         | `${HOME}/.dnastack/config.yaml` |
| `DNASTACK_SESSION_DIR`          | `str`  | Override the default location of the session files. For testing, please define this variable.                                                                                                                                                              | `${HOME}/.dnastack/sessions/`   |
| `DNASTACK_DEBUG`                | `bool` | Enable the global debug mode for the CLI/library. When the debug mode is enabled, the library will override the default log level (`DNASTACK_LOG_LEVEL`) to `DEBUG`. The debug mode of the library/CLI will also enable the debug mode of the HTTP client. | `false`                         |
| `DNASTACK_LOG_LEVEL`            | `str`  | The default log level. You can choose either `DEBUG`, `INFO`, `WARNING`, or `ERROR`. Please note that setting to `DEBUG` WILL NOT enable the debug mode (`DNASTACK_DEBUG`).                                                                                | `ERROR`                         |
| `DNASTACK_SHOW_LIST_ITEM_INDEX` | `bool` | Allow the CLI to show the index number of the list items in the output. This feature is automatically disabled when the CLI runs in the non-interactive shell.                                                                                             | `false`                         |

## Troubleshooting

### Quirk in configuring the collection service client

As the explorer service has implemented its own version of collection API, the `mode` property of the service endpoint
must be set to `explorer`. Depending on which service you plan to use, you need to make sure that you set the client
mode correctly.

| Collection API Spec       | The `mode` value | Default? |
|---------------------------|------------------|----------|
| explorer (e.g., viral.ai) | `explorer`       | Yes      |
| collection-service        | `standard`       | No       |


#### Configure for an explorer service

Here is the example.

```python
# Python code
from dnastack import CollectionServiceClient
from dnastack.configuration.models import ServiceEndpoint

endpoint = ServiceEndpoint(url='https://viral.ai/api/')
# Alternative: endpoint = ServiceEndpoint(url='https://viral.ai/api/', mode='explorer')

client = CollectionServiceClient.make(endpoint)
```

or

```bash
# Shell script
dnastack config set collections.url https://viral.ai/api/
# ↓ You don't need this unless you just change the URL to an explorer service, like Viral.ai.
#dnastack config set collections.mode explorer
```

#### Configure for a collection service

Here is the example.

```python
# Python code
from dnastack import CollectionServiceClient
from dnastack.configuration.models import ServiceEndpoint

endpoint = ServiceEndpoint(url='https://collection-service.red-panda.com', mode='standard')
client = CollectionServiceClient.make(endpoint)
```

or

```bash
# Shell script
dnastack config set collections.url https://collection-service.red-panda.com
dnastack config set collections.mode standard
```
