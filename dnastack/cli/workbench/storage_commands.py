import os
import re
import json
from typing import Optional, List

import click
from click import style

from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import OutputFormat, show_iterator
from dnastack.cli.workbench.utils import get_storage_client
from dnastack.client.workbench.storage.models import AwsStorageAccountCredentials, StorageAccount, Provider, \
    StorageListOptions, Platform, PlatformListOptions, GcpStorageAccountCredentials


@click.group('storage')
def storage_command_group():
    """Interact with Storage accounts"""


@click.group("add")
def add_storage_command_group():
    """Add storage account"""


@click.group("update")
def update_storage_command_group():
    """Update storage account"""


storage_command_group.add_command(add_storage_command_group)
storage_command_group.add_command(update_storage_command_group)


@command(add_storage_command_group,
         'aws',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='storage_id',
                 help='The storage account id',
                 as_option=False
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='An human readable name for the storage account',
                 as_option=True
             ),
             ArgumentSpec(
                 name='access_key_id',
                 arg_names=['--access-key-id'],
                 help='The access key id for the storage account to use when authenticating with AWS',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='secret_access_key',
                 arg_names=['--secret-access-key'],
                 help='The Secret Access key for the storage account to use when authenticating with AWS',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='region',
                 arg_names=['--region'],
                 help='The region for the storage account',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='bucket',
                 arg_names=['--bucket'],
                 help='The name of the bucket to use for the storage account',
                 as_option=True,
                 required=True,
                 default=None
             ),
         ]
         )
def add_aws_storage_account(context: Optional[str],
                            endpoint_id: Optional[str],
                            namespace: Optional[str],
                            storage_id: str,
                            name: str,
                            access_key_id: str,
                            secret_access_key: str,
                            region: str,
                            bucket: str):
    # Validate bucket format
    if not re.match(r'^s3://', bucket):
        click.echo(style("Error: Bucket name must start with 's3://'", fg='red'), err=True, color=True)
        exit(1)

    """Create a new aws storage account"""
    client = get_storage_client(context, endpoint_id, namespace)

    credentials = AwsStorageAccountCredentials(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=region,
        bucket=bucket
    )

    storage_account = StorageAccount(
        id=storage_id,
        name=name,
        provider=Provider.aws,
        credentials=credentials
    )

    response = client.add_storage_account(storage_account)
    click.echo(to_json(normalize(response)))


@command(add_storage_command_group,
         'gcp',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='storage_id',
                 help='The storage account id',
                 as_option=False
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='An human readable name for the storage account',
                 as_option=True
             ),
             ArgumentSpec(
                 name='service_account_json',
                 arg_names=['--service-account-json'],
                 help='The json file for the storage account to use when authenticating with GCP',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='region',
                 arg_names=['--region'],
                 help='The region for the storage account',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='project_id',
                 arg_names=['--project-id'],
                 help='The id of the GCP project',
                 as_option=True,
                 required=True,
                 default=None
             ),
         ]
         )
def add_gcp_storage_account(context: Optional[str],
                            endpoint_id: Optional[str],
                            namespace: Optional[str],
                            storage_id: str,
                            name: str,
                            service_account_json: str,
                            region: str,
                            project_id: str):
    # Load service account from file if necessary
    if service_account_json.startswith('@'):
        file_path = service_account_json[1:]
        if not os.path.exists(file_path):
            click.echo(style(f"Error: Service account file {file_path} does not exist.", fg='red'), err=True,
                       color=True)
            exit(1)
        with open(file_path, 'r') as f:
            service_account_json = f.read()

    # Validate service account JSON
    try:
        service_account = json.loads(service_account_json)
    except json.JSONDecodeError:
        click.echo(style("Error: Malformed service account JSON.", fg='red'), err=True, color=True)
        exit(1)

    # Validate project ID
    if not project_id:
        click.echo(style("Error: Project ID is required.", fg='red'), err=True, color=True)
        exit(1)

    """Create a new GCP storage account"""
    client = get_storage_client(context, endpoint_id, namespace)

    credentials = GcpStorageAccountCredentials(
        service_account_json=service_account_json,
        region=region,
        project_id=project_id
    )

    storage_account = StorageAccount(
        id=storage_id,
        name=name,
        provider=Provider.gcp,
        credentials=credentials
    )

    response = client.add_storage_account(storage_account)
    click.echo(to_json(normalize(response)))


@command(update_storage_command_group,
         'gcp',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='storage_id',
                 help='The storage account id',
                 as_option=False
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='A human readable name for the storage account',
                 as_option=True
             ),
             ArgumentSpec(
                 name='service_account_json',
                 arg_names=['--service-account-json'],
                 help='The json file for the storage account to use when authenticating with GCP. Use @<path> to load from a file.',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='region',
                 arg_names=['--region'],
                 help='The region for the storage account',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='project_id',
                 arg_names=['--project-id'],
                 help='The id of the GCP project',
                 as_option=True,
                 required=True,
                 default=None
             ),
         ]
         )
def update_gcp_storage_account(context: Optional[str],
                               endpoint_id: Optional[str],
                               namespace: Optional[str],
                               storage_id: str,
                               name: str,
                               service_account_json: str,
                               region: str,
                               project_id: str):
    # Load service account from file if necessary
    if service_account_json.startswith('@'):
        file_path = service_account_json[1:]
        if not os.path.exists(file_path):
            click.echo(style(f"Error: Service account file {file_path} does not exist.", fg='red'), err=True,
                       color=True)
            exit(1)
        with open(file_path, 'r') as f:
            service_account_json = f.read()

    # Validate service account JSON
    try:
        service_account = json.loads(service_account_json)
    except json.JSONDecodeError:
        click.echo(style("Error: Malformed service account JSON.", fg='red'), err=True, color=True)
        exit(1)

    # Validate project ID
    if not project_id:
        click.echo(style("Error: Project ID is required.", fg='red'), err=True, color=True)
        exit(1)

    """Update an existing GCP storage account"""
    client = get_storage_client(context, endpoint_id, namespace)

    credentials = GcpStorageAccountCredentials(
        service_account_json=service_account_json,
        region=region,
        project_id=project_id
    )

    storage_account = StorageAccount(
        id=storage_id,
        name=name,
        provider=Provider.gcp,
        credentials=credentials
    )

    response = client.update_storage_account(storage_id, storage_account)
    click.echo(to_json(normalize(response)))


## Add a command to delete a storage account
@command(storage_command_group,
         'delete',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='storage_id',
                 help='The storage account id',
                 as_option=False
             ),
             ArgumentSpec(
                 name='force',
                 arg_names=['--force'],
                 help='Force the deletion without prompting for confirmation.',
                 as_option=True,
                 default=False
             )

         ],
         )
def delete_storage_account(context: Optional[str],
                           endpoint_id: Optional[str],
                           namespace: Optional[str],
                           storage_id: str,
                           force: Optional[bool]):
    """Delete a storage account"""
    client = get_storage_client(context, endpoint_id, namespace)

    if not force and not click.confirm(
            f'Confirm deletion of storage account {storage_id}. This action cannot be undone.'):
        return

    client.delete_storage_account(storage_id)
    click.echo(f"Storage account {storage_id} deleted successfully")


@command(storage_command_group,
         'list',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='max_results',
                 arg_names=['--max-results'],
                 help='An optional flag to limit the total number of results.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='page',
                 arg_names=['--page'],
                 help='An optional flag to set the offset page number. This allows for jumping into an arbitrary page of results. Zero-based.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='page_size',
                 arg_names=['--page-size'],
                 help='An optional flag to set the page size returned by the server.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='sort',
                 arg_names=['--sort'],
                 help='An optional flag to define how results are sorted. '
                      'The value should be in the form `column(:direction)?(;(column(:direction)?)*`'
                      'If no directions are specified, the results are returned in ascending order'
                      'To change the direction of ordering include the "ASC" or "DESC" string after the column. '
                      'e.g.: --sort "name:ASC", --sort "name;provider:DESC;"',

                 as_option=True
             ),
             ArgumentSpec(
                 name='provider',
                 arg_names=['--provider'],
                 help='An optional flag to filter results by provider.',
                 as_option=True
             )
         ]
         )
def list_storage_accounts(context: Optional[str],
                          endpoint_id: Optional[str],
                          namespace: Optional[str],
                          max_results: Optional[int],
                          page: Optional[int],
                          page_size: Optional[int],
                          sort: Optional[str],
                          provider: Optional[str]):
    """List storage accounts"""
    client = get_storage_client(context, endpoint_id, namespace)
    list_options = StorageListOptions(
        page=page,
        page_size=page_size,
        sort=sort,
        provider=provider
    )
    show_iterator(output_format=OutputFormat.JSON,
                  iterator=client.list_storage_accounts(list_options, max_results))


@command(storage_command_group,
         'describe',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             )
         ]
         )
def get_storage_accounts(context: Optional[str],
                         endpoint_id: Optional[str],
                         namespace: Optional[str],
                         storage_account_ids: List[str]):
    """Get a storage account"""

    if not storage_account_ids:
        click.echo(style("You must specify at least one storage account ID", fg='red'), err=True, color=True)
        exit(1)

    client = get_storage_client(context, endpoint_id, namespace)
    storage_accounts = [client.get_storage_account(storage_account_id) for storage_account_id in storage_account_ids]
    click.echo(to_json(normalize(storage_accounts)))


@click.group("platforms")
def storage_platforms_command_group():
    """Interact with Platforms"""


storage_command_group.add_command(storage_platforms_command_group)


@command(storage_platforms_command_group,
         'add',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='platform_id',
                 help='The platform id',
                 as_option=False
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='An human readable name for the platform',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='storage_id',
                 arg_names=['--storage-id'],
                 help='The ID of the storage account associated with the platform.',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='platform_type',
                 arg_names=['--platform'],
                 help='The sequencing platform associated with the platform.',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='path',
                 arg_names=['--path'],
                 help='The path in the storage account where platform data is located.',
                 as_option=True,
                 required=True,
                 default=None
             ),
         ]
         )
def add_platform(context: Optional[str],
                 endpoint_id: Optional[str],
                 namespace: Optional[str],
                 platform_id: str,
                 name: str,
                 storage_id: str,
                 platform_type: str,
                 path: str):
    # Validate path format
    if re.match(r'^s3://', path):
        click.echo(style("Error: Path must not start with 's3://'", fg='red'), err=True, color=True)
        exit(1)

    # Prefix path with a forward slash if not already present
    if path and not path.startswith('/'):
        path = '/' + path

    """Create a new platform"""
    client = get_storage_client(context, endpoint_id, namespace)
    platform = Platform(
        id=platform_id,
        storage_account_id=storage_id,
        name=name,
        path=path,
        type=platform_type.upper()
    )

    response = client.add_platform(platform)
    click.echo(to_json(normalize(response)))


@command(storage_platforms_command_group,
         'delete',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='platform_id',
                 help='The platform id',
                 as_option=False
             ),
             ArgumentSpec(
                 name='storage_id',
                 arg_names=['--storage-id'],
                 help='The ID of the storage account associated with the platform.',
                 as_option=True,
                 required=True,
                 default=None
             ),
             ArgumentSpec(
                 name='force',
                 arg_names=['--force'],
                 help='Force the deletion without prompting for confirmation.',
                 as_option=True,
                 default=False
             )
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


@command(storage_platforms_command_group,
         'describe',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='storage_account_id',
                 arg_names=['--storage-id'],
                 help='The ID of the storage account associated with the platforms.',
                 as_option=True,
                 required=True,
                 default=None
             ),
         ]
         )
def describe_platform(context: Optional[str],
                      endpoint_id: Optional[str],
                      namespace: Optional[str],
                      platform_ids: List[str],
                      storage_account_id: str):
    """Describe a Platform of storage account"""

    if not platform_ids:
        click.echo(style("You must specify at least one platform ID", fg='red'), err=True, color=True)
        exit(1)

    client = get_storage_client(context, endpoint_id, namespace)
    platforms = [client.get_platform(platform_id, storage_account_id) for platform_id in platform_ids]
    click.echo(to_json(normalize(platforms)))


@command(storage_platforms_command_group,
         'list',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='max_results',
                 arg_names=['--max-results'],
                 help='An optional flag to limit the total number of results.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='page',
                 arg_names=['--page'],
                 help='An optional flag to set the offset page number. This allows for jumping into an arbitrary page of results. Zero-based.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='page_size',
                 arg_names=['--page-size'],
                 help='An optional flag to set the page size returned by the server.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='sort',
                 arg_names=['--sort'],
                 help='An optional flag to define how results are sorted. '
                      'The value should be in the form `column(:direction)?(;(column(:direction)?)*`'
                      'If no directions are specified, the results are returned in ascending order'
                      'To change the direction of ordering include the "ASC" or "DESC" string after the column. '
                      'e.g.: --sort "name:ASC", --sort "name;provider:DESC;"',

                 as_option=True
             ),
             ArgumentSpec(
                 name='storage_account_id',
                 arg_names=['--storage-id'],
                 help='An optional flag to define the ID of the storage account to retrieve platforms from.',
                 as_option=True
             ),
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
