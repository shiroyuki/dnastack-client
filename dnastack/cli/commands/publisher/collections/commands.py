from typing import Optional, List

import click
from click import Group

from dnastack.cli.commands.dataconnect.utils import DECIMAL_POINT_OUTPUT_ARG, handle_query
from dnastack.cli.commands.publisher.collections.utils import _filter_collection_fields, _get_collection_service_client, \
    _transform_to_public_collection, COLLECTION_ID_ARG, _switch_to_data_connect, \
    _get_context
from dnastack.cli.core.command import formatted_command
from dnastack.cli.core.command_spec import ArgumentSpec, RESOURCE_OUTPUT_ARG, DATA_OUTPUT_ARG, ArgumentType
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator
from dnastack.client.collections.model import Collection, Tag
from dnastack.common.json_argument_parser import FileOrValue
from dnastack.common.tracing import Span


def init_collections_commands(group: Group):
    @formatted_command(
        group=group,
        name='list',
        specs=[
            RESOURCE_OUTPUT_ARG,
        ]
    )
    def list_collections(output: Optional[str] = None):
        """ List collections """
        span = Span()
        show_iterator(output,
                      [
                          _filter_collection_fields(collection=collection)
                          for collection in _get_collection_service_client().list_collections(trace=span)
                      ],
                      transform=_transform_to_public_collection)

    
    @formatted_command(
        group=group,
        name='query',
        specs=[
            ArgumentSpec(
                name='query',
                arg_type=ArgumentType.POSITIONAL,
                help='The SQL query.',
                required=True,
            ),
            COLLECTION_ID_ARG,
            DECIMAL_POINT_OUTPUT_ARG,
            DATA_OUTPUT_ARG,
        ]
    )
    def query_collection(collection: str,
                         query: str,
                         decimal_as: str = 'string',
                         no_auth: bool = False,
                         output: Optional[str] = None):
        """ Query data """
        trace = Span(origin='cli.collections.query')
        client = _switch_to_data_connect(_get_context(), _get_collection_service_client(), collection, no_auth=no_auth)
        return handle_query(client, query,
                            decimal_as=decimal_as,
                            no_auth=no_auth,
                            output_format=output,
                            trace=trace)


    @formatted_command(
        group=group,
        name='create',
        specs=[
            ArgumentSpec(
                name='name',
                arg_names=['--name'],
                help='The name of the collection you want to create or manage.',
                required=True,
            ),
            ArgumentSpec(
                name='description',
                arg_names=['--description'],
                help='A short summary or explanation of the purpose or contents of the collection. '
                     'Use @<path> to load from file.',
                type=FileOrValue,
                required=True,
            ),
            ArgumentSpec(
                name='slug',
                arg_names=['--slug'],
                help='A unique identifier for the collection, often used in URLs for easy reference.',
                required=True,
            ),
            ArgumentSpec(
                name='tags',
                arg_names=['--tags'],
                help='A comma-separated list of tags to categorize and organize the collection.',
                required=False,
            ),
        ]
    )
    def create_collection(name: str,
                         description: FileOrValue,
                         slug: str,
                         tags: Optional[str] = None):
        """ Create a new collection """
        def parse_tags(tags: Optional[str]) -> Optional[List[Tag]]:
            if not tags:
                return None
            return [Tag(label=tag.strip()) for tag in tags.split(',')]

        collection = Collection(
            name=name,
            description=description.value(),
            slugName=slug,
            tags=parse_tags(tags),
            itemsQuery=";",
        )

        client = _get_collection_service_client()
        response = client.create_collection(collection)
        click.echo(to_json(normalize(response)))


    @formatted_command(
        group=group,
        name='describe',
        specs=[
            ArgumentSpec(
                name='id_or_slugs',
                arg_type=ArgumentType.POSITIONAL,
                help='The ID or slug name of the target collection',
                required=True,
                multiple=True,
            ),
        ]
    )
    def describe_collection(id_or_slugs: List[str]):
        """ View details of a specific collection """
        client = _get_collection_service_client()
        # Get unique collections by id, with the last occurrence taking precedence
        unique_collections = {
            collection.id: collection
            for id_or_slug in id_or_slugs
            for collection in [client.get(id_or_slug_name=id_or_slug)]
        }

        click.echo(to_json(normalize(list(unique_collections.values()))))
