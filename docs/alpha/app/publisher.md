# Publisher Client

| Classification    | Stability         | Automatic Test | Added in |
|-------------------|-------------------|---------------|----------|
| High-level Client | Alpha/Expermental | Yes           | 3.1      |

## Known developers
* Jim Vlasblom
* Juti Noppornpitak

## Basic usage

First, let’s start with instantiating the client.

```python
from dnastack.alpha.app.publisher import Publisher

publisher = Publisher('publisher-data.foo.dnastack.com')
```
where the first parameter is the hostname of **the Publisher Data service with Service Registry API enabled** or **the collection service (if accessible)**.

To list all collections, you can do this:
```python
collection_list = publisher.list_collections()
```
where it returns the list of all collection metadata.

To list the tables in a collection, for example `foo-bar`, you can do this:
```python
collection = publisher.collection('foo-bar')
```
where the first parameter is either the ID (`id`) or the slug name (`slugName`) of the collection.

Then, to get the list of tables:
```python
from dnastack.alpha.app.publisher_helper import ItemType

table_info_list = collection.list_items(kind=ItemType.TABLE)
```

Now, suppose that we randomly pick one of the listed tables and assign to a variable called table. here is how to see the content:

```python
result_iterator = publisher.query(
    # language=sql
    f'SELECT * FROM {table.name} LIMIT 1234'
)
```
where result_iterator is an iterator of type `Dict[str, Any]`.