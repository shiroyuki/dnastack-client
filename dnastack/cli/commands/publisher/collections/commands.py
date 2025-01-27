from typing import Optional, List

import click
from click import Group

from dnastack.cli.commands.dataconnect.utils import DECIMAL_POINT_OUTPUT_ARG, handle_query
from dnastack.cli.commands.publisher.collections.utils import _filter_collection_fields, _simplify_collection, _get, \
    _transform_to_public_collection, COLLECTION_ID_CLI_ARG, _switch_to_data_connect, \
    _get_context
from dnastack.cli.core.command import formatted_command
from dnastack.cli.core.command_spec import ArgumentSpec, RESOURCE_OUTPUT_ARG, DATA_OUTPUT_ARG, CONTEXT_ARG, \
    SINGLE_ENDPOINT_ID_ARG, ArgumentType
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
            ArgumentSpec(
                name='simplified',
                arg_names=['--simplified'],
                help='Use the simplified representation (experimental)',
                type=bool,
            ),
            ArgumentSpec(
                name='selected_fields',
                arg_names=['--select'],
                nargs='*',
                help='Select a certain field (experimental)',
            ),
            ArgumentSpec(
                name='no_auth',
                arg_names=['--no-auth'],
                help='Skip automatic authentication if set',
                type=bool,
                required=False,
                hidden=True,
            ),
            RESOURCE_OUTPUT_ARG,
            CONTEXT_ARG,
            SINGLE_ENDPOINT_ID_ARG,
        ]
    )
    def list_collections(context: Optional[str],
                         endpoint_id: Optional[str],
                         selected_fields: Optional[str] = None,
                         simplified: Optional[bool] = False,
                         no_auth: bool = False,
                         output: Optional[str] = None):
        """ List collections """
        span = Span()
        show_iterator(output,
                      [
                          _filter_collection_fields(_simplify_collection(collection) if simplified else collection, selected_fields)
                          for collection in _get(context, endpoint_id).list_collections(no_auth=no_auth, trace=span)
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
            COLLECTION_ID_CLI_ARG,
            DECIMAL_POINT_OUTPUT_ARG,
            DATA_OUTPUT_ARG,
            CONTEXT_ARG,
            SINGLE_ENDPOINT_ID_ARG,
        ]
    )
    def query_collection(context: Optional[str],
                         endpoint_id: Optional[str],
                         collection: Optional[str],
                         query: str,
                         decimal_as: str = 'string',
                         no_auth: bool = False,
                         output: Optional[str] = None):
        """ Query data """
        trace = Span(origin='cli.collections.query')
        client = _switch_to_data_connect(_get_context(context), _get(context, endpoint_id), collection, no_auth=no_auth)
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
            CONTEXT_ARG,
            SINGLE_ENDPOINT_ID_ARG,
        ]
    )
    def create_collection(context: Optional[str],
                         endpoint_id: Optional[str],
                         name: str,
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

        client = _get(context, endpoint_id)
        response = client.create_collection(collection)
        click.echo(to_json(normalize(response)))
