---
title: "Python Library"
weight: 2
draft: false
lastmod: 2021-2-17
type: docs
layout: single-col
---

#### Installation

This guide will help you install **dnastack-client-library 3.0**.
If you need to install a specific version,  please check out the list
of available versions on
[the release history page](https://pypi.org/project/dnastack-client-library/#history).

{{<code/float-window>}}
{{< tabs tabTotal="3" tabID="1" tabName1="Normal Installation" tabName3="Jupyter Notebooks" tabName2="Windows 10/11">}}
{{% tab tabNum="1" %}}

##### Normal installation

First, you need to have
* **Python 3.7** or higher,
* and optionally **pip 21.3** or newer are required for ARM-based systems, e.g., ARM-based MacOS machines.

You just need to run the `pip` command:

{{%code/code-block%}}
```shell
pip3 install -U dnastack-client-library
```
{{%/code/code-block%}}

> **Tips:**
>
> If `pip3` is not available on your system, please try `pip`, `python -m pip`, or `python3 -m pip`.

This package will come with the command line tool which is available as:
* `dnastack`
* `python3 -m dnastack` or `python -m dnastack` (depending on your Python installation)

{{% /tab %}}
{{% tab tabNum="2" %}}

##### Install the package alongside Anaconda 3 on Windows 10/11 with Powershell

Assume that you have Anaconda 3 installed.

To install with **Powershell**,

1. Open "Anaconda Powershell Prompt". You can do it from the start menu or **Anaconda Navigator**<sup>1</sup>.
2. Then, when the Powershell is ready, run [the `pip` command previously mentioned above](#normal-installation).

This package will come with the command line tool which is available as:
* `dnastack`
* `python -m dnastack`

{{% /tab %}}
{{% tab tabNum="3" %}}

##### Install the package via Jupyter Notebook

In case that you don't have full access to the machine's terminal app, you can add this to one of your code blocks:

{{%code/code-block%}}
```jupyter
!pip3 install -U dnastack-client-library
```
{{%/code/code-block%}}

{{% /tab %}}
{{< /tabs >}}
{{</code/float-window>}}

---

#### Using with your Python applications or Jupyter notebooks

##### Set up with a service registry

To get started, we will get the endpoints from the service registry by just specifying the hostname of the service
registry. In this example, we will use Viral AI's collection service.

{{%code/code-block%}}
```python
from dnastack import use

factory = use('viral.ai')
```
{{%/code/code-block%}}

The `factory` has two methods:

* `factory.all()` will give you the list of `dnastack.ServiceEndpoint` objects,
* `factory.get(id: str)` is to instantiate a service client for the requested endpoint.

The `factory.get` method relies on the `type` property of the `ServiceEndpoint` object to determine which client
class to use. Here is an example on how it does that.

It will instantiate a `dnastack.CollectionServiceClient` for:
* `com.dnastack:collection-service:1.0.0`
* `com.dnastack.explorer:collection-service:1.1.0`

It will instantiate a `dnastack.DataConnectClient` for:
* `org.ga4gh:data-connect:1.0.0`

It will instantiate a `dnastack.DrsClient` for:
* `org.ga4gh:drs:1.1.0`

##### Interact with Collection Service API

Now that we get the information of the factory from the service registry, we can create a client to the collection
service.

{{%code/code-block%}}
```python
collection_service_client = factory.get('collection-service')
```
{{%/code/code-block%}}

And this is how to list all available collections.

{{%code/code-block%}}
```python
import json

collections = collection_service_client.list_collections()

print(json.dumps(
    [
        {
            'id': c.id,
            'slugName': c.slugName,
            'itemsQuery': c.itemsQuery,
        }
        for c in collections
    ],
    indent=2
))
```
{{%/code/code-block%}}

where `slugName` is the alternative ID of a collection and `itemsQuery` is the SQL query of items in the collection.

##### Set up a client for Data Connect Service

In this section, we switch to use a Data Connect client.

{{%code/code-block%}}
```python
from dnastack import DataConnectClient

data_connect_client: DataConnectClient = factory.get('data-connect-ncbi-sra')
```
{{%/code/code-block%}}

##### List all accessible tables

But before we can run a query, we need to get the list of available tables
(`dnastack.client.data_connect.TableInfo` objects).

{{%code/code-block%}}
```python
tables = data_connect_client.list_tables()

print(json.dumps(
    [
        dict(
            name=table.name
        )
        for table in tables
    ],
    indent=2
))
```
{{%/code/code-block%}}

where the `name` property of each item (`TableInfo` object) in `tables` is the name of the table that we can use in the
query.

> Please note that, depending on the implementation of the `/tables` endpoint, the `TableInfo` object in the list may be
> incomplete, for example, the data model (`data_model`) may only contain the reference URL, instead of an object
> schema. To get the more complete information, please use `Table` which will be mentioned in _the next section_.

##### Get the table information and data

To get started, we need to use the `table` method, which returns a table wrapper object
(`dnastack.client.data_connect.Table`). In this example, we use the first table available.

{{%code/code-block%}}
```python
table = data_connect_client.table(tables[0])
```
{{%/code/code-block%}}

The `table` method also takes a string where it assumes that the given string is the name of the table, e.g.,

{{%code/code-block%}}
```python
table = data_connect_client.table(tables[0].name)
```
{{%/code/code-block%}}

or

{{%code/code-block%}}
```python
table = data_connect_client.table('cat.sch.tbl')
```
{{%/code/code-block%}}

A `Table` object also has the `name` property, which is the table name (same as `Table.name`). However, it
provides two properties:

* The `info` property provides _the more complete table information_ as a `TableInfo` object<sup>2</sup>,
* The `data` property provides **an iterator to the actual table data**.

##### Integrate a `Table` object with `pandas.DataFrame`

You can easily instantiate a `pandas.DataFrame` object like this.

{{%code/code-block%}}
```python
import pandas
csv_df = pandas.DataFrame(table.data)
```
{{%/code/code-block%}}

where `table` is a `Table` object.

##### Query data

Now, let's say we will select up to 10 rows from the first table.

{{%code/code-block%}}
```python
result_iterator = data_connect_client.query(f'SELECT * FROM {table.name} LIMIT 10')
```
{{%/code/code-block%}}

The `query` method will return an iterator to the result where each item in the result is a string-to-anything
dictionary.

##### Integrate the query result (iterator) with `pandas.DataFrame`

You can easily instantiate a `pandas.DataFrame` object like this.

{{%code/code-block%}}
```python
import pandas
csv_df = pandas.DataFrame(result_iterator)
```
{{%/code/code-block%}}

##### Download blobs with DRS API

To download a blob, you need to find out the blobs that you have access to from a collection. To get the list of
available blob items, you have to run the items query with a data connect client.

In this example, suppose that the first collection has blobs. We would like to get the first 20 blobs.

{{%code/code-block%}}
```python
blob_collection = [c for c in collections if c.slugName == 'ncbi-sra'][0]
items = [i
         for i in data_connect_client.query(blob_collection.itemsQuery + ' LIMIT 20')
         if i['type'] == 'blob']
```
{{%/code/code-block%}}

> **Tips:**
>
> The items query may contain both "table" and "blob" items. You may want to filter them.

And here is how to get a blob object.

{{%code/code-block%}}
```python
from dnastack import DrsClient

drs_client: DrsClient = factory.get("drs")
blob = drs_client.get_blob(items[0]['id'])
```
{{%/code/code-block%}}

> **Tips:**
>
> Also, if you have external DRS URL, you can use it to by setting the `url` parameter instead of `id`. For example,
>
> {{%code/code-block%}}
> ```python
> blob = drs_client.get_blob('drs://viral.ai/fmyfkmy1230-3rhbfa8weyf')
> ```
> {{%/code/code-block%}}
>
> If the endpoint is *publicly accessible*, you can set `no_auth` to `True` to ensure that the client will never initate the authentication procedure.
>
> {{%code/code-block%}}
> ```python
> blob = drs_client.get_blob(..., no_auth=True)
> ```
> {{%/code/code-block%}}

And this is how to download the blob data.

{{%code/code-block%}}
```python
blob.data
```
{{%/code/code-block%}}

Where the `data` property returns a byte array.

##### Integrate `Blob` objects with `pandas.DataFrame`

You can easily instantiate a `pandas.DataFrame` object like this.

{{%code/code-block%}}
```python
import pandas
csv_df = pandas.read_csv(blob.get_download_url())
```
{{%/code/code-block%}}

where `blob.get_download_url()` returns the access URL.

---

#### Footnotes

1. The normal Powershell or Window Terminal does not work in this case.
2. The completion of the information depends on the implementation of the `/table/<table_name>/info` endpoint.