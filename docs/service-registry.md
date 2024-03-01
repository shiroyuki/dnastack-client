# Auto-configuration with GA4GH Service Registries

Starting from **version 3.0**, you can rely on _a GA4GH service registry service_ to simplify the initialization process
of a service client with just the base URL to the [service endpoint](glossary.md#service-endpoint).

## Service registries in Python code

### How to set up a client factory

To begin, we first create a client factory, which will use the service information from one or more service registries
to initialize a [service client](service-clients.md).

```python
from dnastack.client.service_registry.factory import ClientFactory

factory = ClientFactory.use(
    'https://collection-service.viral.ai/service-registry/',
    'https://viral.ai/api/service-registry/',
)
```

`ClientFactory.use` is a short-handed (class) method to create an instance of `ClientFactory` which relies on the
information from public registries. In case that you need to use a protected service registry, you will need to use the
advanced setup method. Here is an example.

```python
from dnastack.client.service_registry.client import ServiceRegistry
from dnastack.client.service_registry.factory import ClientFactory
from dnastack.configuration.models import ServiceEndpoint

# Initialize service registry clients
registries = [
    ServiceRegistry.make(ServiceEndpoint(url=..., authentication=...)),
    ServiceRegistry.make(ServiceEndpoint(url=..., authentication=...)),
    ...,
    ServiceRegistry.make(ServiceEndpoint(url=..., authentication=...))
]

# Then, initialize the client factory.
factory = ClientFactory(registries)
```

### Instantiate a service client

Use the `create` method of the client factory to instantiate a service. Here is an example.

```python
from dnastack.client.service_registry.factory import ClientFactory
from dnastack import CollectionServiceClient, DataConnectClient, DrsClient

factory: ClientFactory = ...  # Suppose we create a factory.
client_1 = factory.create(CollectionServiceClient, 'https://collection-service.viral.ai/')
client_2 = factory.create(DataConnectClient, 'https://collection-service.viral.ai/data-connect/')
client_3 = factory.create(DrsClient, 'https://collection-service.viral.ai/')
```

or alternatively, you can use the `get` method if you know the ID of service.

```python
from dnastack.client.service_registry.factory import ClientFactory

factory: ClientFactory = ...  # Suppose we create a factory.
drs_client = factory.get('drs')
```

## Service registries with CLI

### Getting started

Let's start with one service registry.

```shell
dnastack config registries add viral-ai-reg "https://collection-service.viral.ai/service-registry/"
# ↑ Syntax: dnastack config registries add <registry_id> <registry_url>
```

As the service registry client also supports OAuth2 authentication, you can configure the endpoint with
the endpoint commands. 

```shell
dnastack config endpoints set <registry_id> authentication.<...> "<...>"
```

See [the documentation on authentication](./authentications.md).

### Use service registries with CLI

When you use `dnastack config registries add` or `dnastack config registries sync`, it will automatically synchronize the list. After
that, you can find out the endpoints you want to use with `dnastack config registries list-endpoints`.

Then, you can use the endpoint ID to interact the endpoint with `dnastack collections`, `dnastack dataconnect`, and
`dnastack files` with `--endpoint-id`, for example:

```shell
dnastack dataconnect query --endpoint-id viral-ai-reg:data-connect "SELECT * FROM abc.public.table"
```
