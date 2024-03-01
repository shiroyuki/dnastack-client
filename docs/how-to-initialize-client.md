# How to initialize the client

## Configure your CLI tool for Viral.ai

> The setup is for the device code flow. Your email may need to be listed in the Wallet's access policy for the CLI tool.
> Please contact the technical support for help. For more details on the setup, please see [Client Authorization](authentications.md).

### Simple setup

Run `dnastack config factory-reset`.

### Advanced setup

```shell
# Data Connect Service
dnastack config set data_connect.authentication.client_id dnastack-client-library
dnastack config set data_connect.authentication.client_secret <TBD>
dnastack config set data_connect.authentication.device_code_endpoint https://wallet.viral.ai/oauth/device/code
dnastack config set data_connect.authentication.grant_type urn:ietf:params:oauth:grant-type:device_code
dnastack config set data_connect.authentication.resource_url https://data-connect-trino.viral.ai/
dnastack config set data_connect.authentication.token_endpoint https://wallet.viral.ai/oauth/token
dnastack config set data_connect.url https://data-connect-trino.viral.ai
# Collection Service
dnastack config set collections.authentication.client_id dnastack-client-library
dnastack config set collections.authentication.client_secret <TBD>
dnastack config set collections.authentication.device_code_endpoint https://wallet.viral.ai/oauth/device/code
dnastack config set collections.authentication.grant_type urn:ietf:params:oauth:grant-type:device_code
dnastack config set collections.authentication.resource_url https://collection-service.viral.ai/
dnastack config set collections.authentication.token_endpoint https://wallet.viral.ai/oauth/token
dnastack config set collections.url https://collection-service.viral.ai
# Data Repository Service
dnastack config set drs.authentication.client_id dnastack-client-library
dnastack config set drs.authentication.client_secret <TBD>
dnastack config set drs.authentication.device_code_endpoint https://wallet.viral.ai/oauth/device/code
dnastack config set drs.authentication.grant_type urn:ietf:params:oauth:grant-type:device_code
dnastack config set drs.authentication.resource_url https://collection-service.viral.ai/
dnastack config set drs.authentication.token_endpoint https://wallet.viral.ai/oauth/token
dnastack config set drs.url https://collection-service.viral.ai
```

## Configure your Client class

Suppose that you want to initialize an instance of `DataConnectClient` with personal access token.

```python
from dnastack import DataConnectClient, ServiceEndpoint

endpoint = ServiceEndpoint(
    authentication=dict(client_id='dnastack-client-library',
                        client_secret='3FF2B5F0-0BA1-4CDA-9A40-B7AE82C2F800',
                        device_code_endpoint='https://wallet.viral.ai/oauth/device/code',
                        grant_type='urn:ietf:params:oauth:grant-type:device_code',
                        resource_url='https://data-connect-trino.viral.ai/',
                        token_endpoint='https://wallet.viral.ai/oauth/token'),
    url='https://data-connect-trino.viral.ai/'
)
client = DataConnectClient.make(endpoint)
```
