# Getting started with library

DNAstack provides official support for [several types of service clients](service-clients.md). Here are examples.

## Example with Viral AI

Suppose you want to work with the client for the collection service and query data from the `ncbi-sra` collection. Here
is how you can do it.

```python
from dnastack import CollectionServiceClient
from dnastack.configuration.models import ServiceEndpoint
from dnastack.cli.helpers import switch_to_data_connect

client = CollectionServiceClient.make(ServiceEndpoint(adapter_type="collections", url="https://viral.ai/api"))

# Get all collections
collections = client.list_collections()

# Get the Data Connect client for a specific collection
data_connect_client = switch_to_data_connect(client, 'ncbi-sra')

# List tables
tables = data_connect_client.list_tables()

# Query
result = data_connect_client.query('SELECT * FROM collections.ncbi_sra.public_variants LIMIT 101')
```

## Example with a protected service endpoint

In this example, we will set up a Data Connect client for a service endpoint that
requires [the device-code authentication](authentications.md#oauth2-device-code-authentication).

```python
from dnastack.configuration.models import ServiceEndpoint
from dnastack import DataConnectClient

data_connect_url = 'https://data-connect-trino.viral.ai/'
endpoint = ServiceEndpoint(
    id='data-connect-colab-demo',
    adapter_type='data_connect',
    url=data_connect_url,
    authentication=dict(
        client_id='dnastack-client-library',
        client_secret='3FF2B5F0-0BA1-4CDA-9A40-B7AE82C2F800',
        device_code_endpoint='https://wallet.viral.ai/oauth/device/code',
        grant_type='urn:ietf:params:oauth:grant-type:device_code',
        resource_url=data_connect_url,
        token_endpoint='https://wallet.viral.ai/oauth/token',
    )
)

client = DataConnectClient.make(endpoint)
tables = [table for table in client.list_tables()]  # This line will trigger the authentication if the session is not already valid.
```

## More readings

* [Service Clients](service-clients.md)
* [Authentications](authentications.md)
* [API Reference](full-api-reference.md)
