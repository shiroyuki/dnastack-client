# Service Endpoint Adapters

The library and CLI tool have four different types of service endpoint adapters.

| Service Endpoint Type Name    | Type ID        | Class Path                                                   |
|-------------------------------|----------------|--------------------------------------------------------------|
| Collection Service            | `collections`  | `dnastack.client.collections_client.CollectionServiceClient` |
| Data Connect Service          | `data_connect` | `dnastack.client.dataconnect_client.DataConnectClient`       |
| Data Repository Service (DRS) | `drs`          | `dnastack.client.files_client.DrsClient`                     |

## Notes

1. The adapter works as designed but it is not fully tested.
