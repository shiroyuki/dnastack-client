# How to configure CLI Tool

> If you are working with [service adapters](glossary.md#service-endpoint-types) directly, please check out
> [the introduction for the library](introduction-library.md) or [the documentation on authentications](authentications.md).

## Configure via command lines (recommended)

You can configure the service endpoints with [the configuration commands](cli.md#configuration).

## Update the configuration file directly

You can see the schema of the configuration file by invoking `dnastack config schema`.

> **Information for Library Developers**
> 
> The schema of the configuration file is the direct representation of class `dnastack.configuration.Configuration`.

Conceptually, there are two main properties.

* `endpoints` - the list of [service endpoints](glossary.md#service-endpoint)
  * There can be more than one endpoint with the same adapter type.
* `defaults` - [the default service endpoint map](glossary.md#default-service-endpoints)

### Example

```yaml
version: 3
defaults:
  collections: 57851eb3-6d7b-4ebb-aea8-657e62ddf711
  data_connect: 628d234b-ca2d-4822-8080-92d03ee88c94
endpoints:
- adapter_type: collections
  id: 57851eb3-6d7b-4ebb-aea8-657e62ddf711
  mode: explorer
  url: https://viral.ai/api/
- adapter_type: data_connect
  authentication:
    oauth2:
      authorization_endpoint: null
      client_id: dnastack-client-library
      client_secret: 3FF2B5F0-0BA1-4CDA-9A40-B7AE82C2F800
      device_code_endpoint: https://wallet.viral.ai/oauth/device/code
      grant_type: urn:ietf:params:oauth:grant-type:device_code
      personal_access_email: null
      personal_access_endpoint: null
      personal_access_token: null
      redirect_url: null
      resource_url: https://data-connect-trino.viral.ai/
      scope: null
      token_endpoint: https://wallet.viral.ai/oauth/token
      type: oauth2
  id: 628d234b-ca2d-4822-8080-92d03ee88c94
  mode: explorer
  url: https://data-connect-trino.viral.ai
```
