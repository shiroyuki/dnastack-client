# Authentications

Let define `adapter_type` is [an adapter type](glossary.md#service-endpoint-types).

Also, **all types of OAuth2 authentication** requires:

| Name         | `<adapter_type>.authentication.*` | Note                                                                                                                       |
|--------------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Client ID    | `client_id`                       | -                                                                                                                          |
| Resource URL | `resource_url`                    | The resource URL is usually the same as the base URL of the service endpoint *unless it is advised to use a different URL* |

Except for the resource URL, you will need to check out [the platform-specific authentication information](#platform-specific-authentication-information) unless you have one.

## OAuth2 Device-Code Authentication

### Authentication Information

| Name        | `<adapter_type>.authentication.*` | Fixed Value                                    |
|-------------|-----------------------------------|------------------------------------------------|
| Grant Type  | `grant_type`                      | `urn:ietf:params:oauth:grant-type:device_code` |

You will need to see [the platform-specific authentication information](#platform-specific-authentication-information)
for the following mandatory fields.

* Device Code Endpoint
* Token Endpoint

### Examples

```python
from dnastack.configuration.models import ServiceEndpoint

endpoint = ServiceEndpoint(
    # ...
    authentication=dict(
        client_id='...',
        resource_url='...',
        grant_type='urn:ietf:params:oauth:grant-type:device_code',
        device_code_endpoint='...',
        token_endpoint='...',
        # ...
    )
)
```

```shell
dnastack config endpoints set <endpoint_id> authentication.client_id "..."
dnastack config endpoints set <endpoint_id> authentication.resource_url "..."
dnastack config endpoints set <endpoint_id> authentication.grant_type "urn:ietf:params:oauth:grant-type:device_code"
dnastack config endpoints set <endpoint_id> authentication.device_code_endpoint "https://"
dnastack config endpoints set <endpoint_id> authentication.token_endpoint "https://"
```

## OAuth2 Client-Credential Authentication

> This is only for **library developers**.

### Authentication Information

| Name          | `<adapter_type>.authentication.*` | Fixed Value          |
|---------------|-----------------------------------|----------------------|
| Client Secret | `client_secret`                   | -                    |
| Grant Type    | `grant_type`                      | `client_credentials` |

You will need to see [the platform-specific authentication information](#platform-specific-authentication-information)
for the following mandatory fields.

* Token Endpoint

### Examples

```python
from dnastack.configuration.models import ServiceEndpoint

endpoint = ServiceEndpoint(
    # ...
    authentication=dict(
        client_id='...',
        client_secret='...',
        resource_url='...',
        grant_type='client_credentials',
        token_endpoint='...',
        # ...
    )
)
```

```shell
dnastack config endpoints set <endpoint_id> authentication.client_id "..."
dnastack config endpoints set <endpoint_id> authentication.client_secret "..."
dnastack config endpoints set <endpoint_id> authentication.resource_url "https://..."
dnastack config endpoints set <endpoint_id> authentication.grant_type "client_credentials"
dnastack config endpoints set <endpoint_id> authentication.token_endpoint "https://..."
```

## Platform-specific Authentication Information

### Viral AI (https://viral.ai)

> This is only for **device-code authentication**.

| Name                 | `<adapter_type>.authentication.*` | Fixed Value                                 |
|----------------------|-----------------------------------|---------------------------------------------|
| Client ID            | `client_id`                       | `dnastack-client-library`                   |
| Device Code Endpoint | `device_code_endpoint`            | `https://wallet.viral.ai/oauth/device/code` |
| Token Endpoint       | `token_endpoint`                  | `https://wallet.viral.ai/oauth/token`       |

```python
from dnastack.configuration.models import ServiceEndpoint

endpoint = ServiceEndpoint(
    # ...
    authentication=dict(
        client_id='dnastack-client-library',
        device_code_endpoint='https://wallet.viral.ai/oauth/device/code',
        grant_type='urn:ietf:params:oauth:grant-type:device_code',
        token_endpoint='https://wallet.viral.ai/oauth/token',
        resource_url='...'
    )
)
```

```shell
dnastack config endpoints set <endpoint_id> authentication.client_id "dnastack-client-library"
dnastack config endpoints set <endpoint_id> authentication.device_code_endpoint "https://wallet.viral.ai/oauth/device/code"
dnastack config endpoints set <endpoint_id> authentication.token_endpoint "https://wallet.viral.ai/oauth/token"
dnastack config endpoints set <endpoint_id> authentication.resource_url "..."
```
