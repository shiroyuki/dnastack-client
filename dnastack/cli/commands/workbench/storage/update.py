import re
from typing import Optional

import click
from click import style

from dnastack.cli.commands.workbench.storage.utils import validate_and_load_service_account_json
from dnastack.cli.commands.workbench.utils import get_storage_client, NAMESPACE_ARG
from dnastack.cli.core.command import formatted_command
from dnastack.cli.core.command_spec import ArgumentSpec, ArgumentType, CONTEXT_ARG, SINGLE_ENDPOINT_ID_ARG
from dnastack.cli.core.group import formatted_group
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.client.workbench.storage.models import AwsStorageAccountCredentials, StorageAccount, Provider, \
    GcpStorageAccountCredentials


@formatted_group("update")
def update_storage_command_group():
    """Update storage account"""


@formatted_command(
    group=update_storage_command_group,
    name='aws',
    specs=[
        ArgumentSpec(
            name='storage_id',
            arg_type=ArgumentType.POSITIONAL,
            help='The storage account id',
            required=False,
        ),
        NAMESPACE_ARG,
        ArgumentSpec(
            name='name',
            arg_names=['--name'],
            help='An human readable name for the storage account',
            required=True,
        ),
        ArgumentSpec(
            name='access_key_id',
            arg_names=['--access-key-id'],
            help='The access key id for the storage account to use when authenticating with AWS',
            required=True,
        ),
        ArgumentSpec(
            name='secret_access_key',
            arg_names=['--secret-access-key'],
            help='The Secret Access key for the storage account to use when authenticating with AWS',
            required=True,
        ),
        ArgumentSpec(
            name='region',
            arg_names=['--region'],
            help='The region for the storage account',
            required=True,
        ),
        ArgumentSpec(
            name='bucket',
            arg_names=['--bucket'],
            help='The name of the bucket to use for the storage account',
            required=True,
        ),
        CONTEXT_ARG,
        SINGLE_ENDPOINT_ID_ARG,
    ]
)
def update_aws_storage_account(context: Optional[str],
                               endpoint_id: Optional[str],
                               namespace: Optional[str],
                               storage_id: Optional[str],
                               name: str,
                               access_key_id: str,
                               secret_access_key: str,
                               region: str,
                               bucket: str):
    # Validate bucket format
    if not re.match(r'^s3://', bucket):
        click.echo(style("Error: Bucket name must start with 's3://'", fg='red'), err=True, color=True)
        exit(1)

    """Update an existing aws storage account"""
    credentials = AwsStorageAccountCredentials(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=region,
    )
    storage_account = StorageAccount(
        id=storage_id,
        name=name,
        provider=Provider.aws,
        bucket=bucket,
        credentials=credentials
    )

    client = get_storage_client(context, endpoint_id, namespace)
    existing_storage_account = client.get_storage_account(storage_account_id=storage_id)
    response = client.update_storage_account(storage_id, storage_account, existing_storage_account.etag)
    click.echo(to_json(normalize(response)))


@formatted_command(
    group=update_storage_command_group,
    name='gcp',
    specs=[
        ArgumentSpec(
            name='storage_id',
            arg_type=ArgumentType.POSITIONAL,
            help='The storage account id',
            required=False,
        ),
        NAMESPACE_ARG,
        ArgumentSpec(
            name='name',
            arg_names=['--name'],
            help='A human readable name for the storage account',
            required=True,
        ),
        ArgumentSpec(
            name='service_account_json',
            arg_names=['--service-account'],
            help='The json file for the storage account to use when authenticating with GCP. Use @<path> to load from a file.',
            required=True,
        ),
        ArgumentSpec(
            name='region',
            arg_names=['--region'],
            help='The region for the storage account',
            required=True,
        ),
        ArgumentSpec(
            name='project_id',
            arg_names=['--project-id'],
            help='The id of the GCP project',
            required=True,
        ),
        ArgumentSpec(
            name='bucket',
            arg_names=['--bucket'],
            help='The name of the bucket to use for the storage account',
            required=True,
        ),
        CONTEXT_ARG,
        SINGLE_ENDPOINT_ID_ARG,
    ]
)
def update_gcp_storage_account(context: Optional[str],
                               endpoint_id: Optional[str],
                               namespace: Optional[str],
                               storage_id: str,
                               name: str,
                               bucket: str,
                               service_account_json: str,
                               region: str,
                               project_id: str):
    """Update an existing GCP storage account"""

    loaded_service_account = validate_and_load_service_account_json(service_account_json)
    credentials = GcpStorageAccountCredentials(
        service_account_json=loaded_service_account,
        region=region,
        project_id=project_id
    )
    storage_account = StorageAccount(
        id=storage_id,
        name=name,
        provider=Provider.gcp,
        bucket=bucket,
        credentials=credentials
    )

    client = get_storage_client(context, endpoint_id, namespace)
    existing_storage_account = client.get_storage_account(storage_account_id=storage_id)
    response = client.update_storage_account(storage_id, storage_account, existing_storage_account.etag)
    click.echo(to_json(normalize(response)))
