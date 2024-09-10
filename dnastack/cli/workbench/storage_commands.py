from typing import Optional

import click

from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import normalize, to_json
from dnastack.cli.workbench.utils import get_storage_client, UnsupportedCloudProviderError
from dnastack.client.workbench.storage.models import Repository, AwsAccessCredentials, CloudProvider


@click.group(name='storage')
def samples_commands():
    pass


@command(
    samples_commands,
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
            name='bucket',
            arg_names=['--bucket'],
            help='Bucket resource',
            as_option=True,
            required=True,
        ),
        ArgumentSpec(
            name='region',
            arg_names=['--region'],
            help='Cloud region',
            as_option=True,
            required=True,
        ),
        ArgumentSpec(
            name='cloud',
            arg_names=['--cloud'],
            help='The cloud provider (currently only AWS is supported)',
            as_option=True,
            default=CloudProvider.AWS.value,
        ),
        ArgumentSpec(
            name='access_key_id',
            arg_names=['--access-key-id'],
            help='AWS Access Key ID',
            as_option=True
        ),
        ArgumentSpec(
            name='secret_access_key',
            arg_names=['--secret-access-key'],
            help='AWS Secret Access Key',
            as_option=True
        ),
    ]
)
def add(context: Optional[str],
        endpoint_id: Optional[str],
        namespace: Optional[str],
        access_key_id: Optional[str],
        secret_access_key: Optional[str],
        storage_id: str,
        bucket: str,
        region: str,
        cloud: str):
    """
    Creates a new repository in the Sample Service

    docs: https://docs.omics.ai/products/command-line-interface/reference/workbench/samples
    """
    try:
        cloud_provider = CloudProvider[cloud.upper()]
    except KeyError:
        raise UnsupportedCloudProviderError(f"Cloud provider {cloud} is not supported")

    if cloud_provider == CloudProvider.AWS:
        if not access_key_id or not secret_access_key:
            raise ValueError("Both --access-key-id and --secret-access-key parameters must be provided for AWS cloud provider.")
        credentials = AwsAccessCredentials(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key
        )
    else:
        raise UnsupportedCloudProviderError(f"Cloud provider {cloud_provider.value} is not supported")

    repository = Repository(
        id = storage_id,
        bucket = bucket,
        region = region,
        provider = cloud,
        credentials = credentials
    )

    samples_client = get_storage_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    response = samples_client.create_repository(repository)
    click.echo(to_json(normalize(response)))


@command(samples_commands,
         "get",
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
         ]
         )
def get(context: Optional[str],
        endpoint_id: Optional[str],
        namespace: Optional[str],
        storage_id: str):
    """
    Returns a repository from the Sample Service

    docs: https://docs.omics.ai/products/command-line-interface/reference/workbench/samples
    """
    samples_client = get_storage_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    repository = samples_client.get_repository(storage_id)
    click.echo(to_json(normalize(repository)))


@command(samples_commands,
     "delete",
     specs=[
         ArgumentSpec(
             name='namespace',
             arg_names=['--namespace', '-n'],
             help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                  'extracted from the users credentials.',
             as_option=True
         ),
         ArgumentSpec(
             name='force',
             arg_names=['--force'],
             help='Force the deletion without prompting for confirmation.',
             as_option=True,
             default=False
         ),
     ]
 )
def delete(context: Optional[str],
                    endpoint_id: Optional[str],
                    namespace: Optional[str],
                    storage_id: str,
                    force: Optional[bool] = False):
    """
    Deletes an existing repository from the Sample Service

    docs: https://docs.omics.ai/products/command-line-interface/reference/workbench/samples
    """
    samples_client = get_storage_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    repository = samples_client.get_repository(storage_id)
    if not force and not click.confirm(
            f'Do you want to delete storage "{repository.id}"?'):
        return
    samples_client.delete_repository(storage_id, repository.etag)
    click.echo("Deleted...")
