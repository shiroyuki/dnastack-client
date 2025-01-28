import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from dnastack.cli.commands.publisher.collections.utils import _get_collection_service_client, \
    _abort_with_collection_list, \
    _switch_to_data_connect, _get_context, COLLECTION_ID_ARG
from dnastack.cli.core.command import formatted_command
from dnastack.cli.core.command_spec import ArgumentSpec, RESOURCE_OUTPUT_ARG
from dnastack.cli.core.group import formatted_group
from dnastack.cli.helpers.iterator_printer import show_iterator


@formatted_group("items")
def items_command_group():
    """Interact with a collection's items"""


@formatted_command(
    group=items_command_group,
    name='list',
    specs=[
        COLLECTION_ID_ARG,
        ArgumentSpec(
            name='limit',
            arg_names=['--limit', '-l'],
            help='The maximum number of items to display',
            type=int,
            default=50,
        ),
        RESOURCE_OUTPUT_ARG
    ]
)
def list(collection: str,
         limit: Optional[int],
         output: Optional[str] = None):
    """ List items of the given collection """
    assert limit >= 0, 'The limit (--limit) should be either ZERO (item query WITHOUT limit) ' \
                       'or at least ONE (item query WITH limit).'

    collection_service_client = _get_collection_service_client()

    collection_id = collection.strip() if collection else None
    if not collection_id: _abort_with_collection_list(collection_service_client=collection_service_client,
                                                      collection_id_or_slug_name=collection)

    actual_collection = collection_service_client.get(collection_id)
    data_connect_client = _switch_to_data_connect(context=_get_context(),
                                                  collection_service_client=collection_service_client,
                                                  collection_id_or_slug_name=actual_collection.slugName)

    def __simplify_item(row: Dict[str, Any]) -> Dict[str, Any]:
        # NOTE: It is implemented this way to guarantee that "id" and "name" are more likely to show first.
        property_names = ['type', 'size', 'size_unit', 'version', 'item_updated_at']

        item = dict(
            id=row['id'],
            name=row.get('qualified_table_name') or row.get('preferred_name') or row.get('display_name') or row['name'],
        )

        if row['type'] == 'blob':
            property_names.extend([
                'checksums',
                'metadata_url',
                'mime_type',
            ])
        elif row['type'] == 'table':
            property_names.extend([
                'json_schema',
            ])

        item.update({
            k: v
            for k, v in row.items()
            if k in property_names
        })

        # FIXME: Remove this logic when https://www.pivotaltracker.com/story/show/182309558 is resolved.
        if 'metadata_url' in item:
            parsed_url = urlparse(item['metadata_url'])
            item['metadata_url'] = f'{parsed_url.scheme}://{parsed_url.netloc}/{item["id"]}'

        return item

    items: List[Dict[str, Any]] = []

    items_query = actual_collection.itemsQuery.strip()

    if not re.search(r' limit\s*\d+$', items_query, re.IGNORECASE):
        items_query = f'{items_query} LIMIT {limit + 1}'  # We use +1 as an indicator whether there are more results.

    items.extend([i for i in data_connect_client.query(items_query)])

    show_iterator(
        output or RESOURCE_OUTPUT_ARG.default,
        items,
        __simplify_item,
        limit
    )
