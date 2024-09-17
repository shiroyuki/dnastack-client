from pickle import FALSE
from typing import Optional

import click

from dnastack.alpha.cli.workbench.utils import get_storage_client
from dnastack.alpha.client.workbench.storage.models import AwsStorageAccountCredentials, StorageAccount, Provider
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize


@click.group('storage')
def alpha_storage_command_group():
    """Interact with execution engines"""

@click.group("aws")
def alpha_aws_storage_create_group():
    """Interact with AWS storage"""

alpha_storage_command_group.add_command(alpha_aws_storage_create_group)

@command(alpha_aws_storage_create_group,
         'create',
         specs=[
             ArgumentSpec(
                 name='entrypoint',
                 arg_names=['--entrypoint'],
                 help='A required flag to set the entrypoint for the workflow. '
                      'Needs to be a path of a file in a context of the workflow. E.g. main.wdl',
                 as_option=True,
                 required=True,
             ),
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
         ]
         )
def create_workflow(context: Optional[str],
                    endpoint_id: Optional[str],
                    namespace: Optional[str],
                    storage_id: str,
                    name: str,
                    access_key_id: str,
                    secret_access_key: str,
                    region: str):
    """Create a new storage account"""
    client = get_storage_client(context, endpoint_id, namespace)

    credentials = AwsStorageAccountCredentials(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=region
    )

    storage_account = StorageAccount(
        id=storage_id,
        name=name,
        provider=Provider.aws,
        credentials=credentials
    )

    response = client.create_storage_account(storage_account)
    click.echo(to_json(normalize(response)))


## Add a command to delete a storage account
@command(alpha_storage_command_group,
            'delete',
            specs=[
ArgumentSpec(
                 name='entrypoint',
                 arg_names=['--entrypoint'],
                 help='A required flag to set the entrypoint for the workflow. '
                      'Needs to be a path of a file in a context of the workflow. E.g. main.wdl',
                 as_option=True,
                 required=True,
             ),
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

    if not force and not click.confirm(f'Confirm deletion of storage account {storage_id}. This action cannot be undone.'):
        return

    client.delete_storage_account(storage_id)
    click.echo(f"Storage account {storage_id} deleted successfully")