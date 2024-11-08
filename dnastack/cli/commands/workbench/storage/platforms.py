from typing import Optional, List

import click
from click import style

from dnastack.cli.commands.workbench.utils import get_storage_client, NAMESPACE_ARG, MAX_RESULTS_ARG, \
    PAGINATION_PAGE_ARG, PAGINATION_PAGE_SIZE_ARG, create_sort_arg
from dnastack.cli.core.command import formatted_command
from dnastack.cli.core.command_spec import ArgumentSpec, ArgumentType, CONTEXT_ARG, SINGLE_ENDPOINT_ID_ARG
from dnastack.cli.core.group import formatted_group
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import OutputFormat, show_iterator
from dnastack.client.workbench.storage.models import Platform, PlatformListOptions, PlatformType


@formatted_group("platforms")
def storage_platforms_command_group():
    """Interact with Platforms"""



@formatted_command(
    group=storage_platforms_command_group,
    name='add',
    specs=[
        ArgumentSpec(
            name='platform_id',
            arg_type=ArgumentType.POSITIONAL,
            help='The platform id',
            required=False,
        ),
        NAMESPACE_ARG,
        ArgumentSpec(
            name='name',
            arg_names=['--name'],
            help='An human readable name for the platform',
            required=True,
        ),
        ArgumentSpec(
            name='storage_id',
            arg_names=['--storage-id'],
            help='The ID of the storage account associated with the platform.',
            required=True,
        ),
        ArgumentSpec(
            name='platform_type',
            arg_names=['--platform'],
            help='The sequencing platform associated with the platform.',
            type=PlatformType,
            choices=[e.value for e in PlatformType],
            required=True,
        ),
        ArgumentSpec(
            name='path',
            arg_names=['--path'],
            help='The path in the storage account where platform data is located.',
        ),
        CONTEXT_ARG,
        SINGLE_ENDPOINT_ID_ARG,
    ]
)
def add_platform(context: Optional[str],
                 endpoint_id: Optional[str],
                 namespace: Optional[str],
                 platform_id: str,
                 name: str,
                 storage_id: str,
                 platform_type: PlatformType,
                 path: str):
    """Create a new platform"""
    client = get_storage_client(context, endpoint_id, namespace)
    platform = Platform(
        id=platform_id,
        storage_account_id=storage_id,
        name=name,
        path=path,
        type=platform_type
    )

    response = client.add_platform(platform)
    click.echo(to_json(normalize(response)))


@formatted_command(
    group=storage_platforms_command_group,
    name='delete',
    specs=[
        ArgumentSpec(
            name='platform_id',
            arg_type=ArgumentType.POSITIONAL,
            help='The platform id',
            required=False,
        ),
        NAMESPACE_ARG,
        ArgumentSpec(
            name='storage_id',
            arg_names=['--storage-id'],
            help='The ID of the storage account associated with the platform.',
            required=True,
        ),
        ArgumentSpec(
            name='force',
            arg_names=['--force', '-f'],
            help='Force the deletion without prompting for confirmation.',
            type=bool,
        ),
        CONTEXT_ARG,
        SINGLE_ENDPOINT_ID_ARG,
    ]
)
def delete_platform(context: Optional[str],
                    endpoint_id: Optional[str],
                    namespace: Optional[str],
                    platform_id: str,
                    storage_id: str,
                    force: Optional[bool]):
    """Delete a platform"""
    if not force and not click.confirm(
            f'Confirm deletion of platform {platform_id}. This action cannot be undone.'):
        return

    client = get_storage_client(context, endpoint_id, namespace)
    client.delete_platform(platform_id, storage_id)
    click.echo(f"Platform {platform_id} deleted successfully")


@formatted_command(
    group=storage_platforms_command_group,
    name='describe',
    specs=[
        ArgumentSpec(
            name='platform_id',
            arg_type=ArgumentType.POSITIONAL,
            help='The platform id',
            required=False,
            multiple=True
        ),
        NAMESPACE_ARG,
        ArgumentSpec(
            name='storage_account_id',
            arg_names=['--storage-id'],
            help='The ID of the storage account associated with the platforms.',
            required=True,
        ),
        CONTEXT_ARG,
        SINGLE_ENDPOINT_ID_ARG,
    ]
)
def describe_platform(context: Optional[str],
                      endpoint_id: Optional[str],
                      namespace: Optional[str],
                      platform_id: List[str],
                      storage_account_id: str):
    """Describe a Platform of storage account"""

    if not platform_id:
        click.echo(style("You must specify at least one platform ID", fg='red'), err=True, color=True)
        exit(1)

    client = get_storage_client(context, endpoint_id, namespace)
    platforms = [client.get_platform(platform_id, storage_account_id) for platform_id in platform_id]
    click.echo(to_json(normalize(platforms)))


@formatted_command(
    group=storage_platforms_command_group,
    name='list',
    specs=[
        ArgumentSpec(
            name='storage_account_id',
            arg_names=['--storage-id'],
            arg_type=ArgumentType.POSITIONAL,
            help='Define the ID of the storage account to retrieve platforms from.',
            required=True,
        ),
        NAMESPACE_ARG,
        MAX_RESULTS_ARG,
        PAGINATION_PAGE_ARG,
        PAGINATION_PAGE_SIZE_ARG,
        create_sort_arg('--sort "name:ASC", --sort "name;provider:DESC;"'),
        CONTEXT_ARG,
        SINGLE_ENDPOINT_ID_ARG,
    ]
)
def list_platforms(context: Optional[str],
                   endpoint_id: Optional[str],
                   namespace: Optional[str],
                   max_results: Optional[int],
                   page: Optional[int],
                   page_size: Optional[int],
                   sort: Optional[str],
                   storage_account_id: Optional[str]):
    """List Platforms"""
    client = get_storage_client(context, endpoint_id, namespace)
    list_options = PlatformListOptions(
        page=page,
        page_size=page_size,
        sort=sort,
        storage_account_id=storage_account_id
    )
    show_iterator(output_format=OutputFormat.JSON,
                  iterator=client.list_platforms(list_options, max_results))
