from typing import Optional

import click

from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.workbench.utils import get_user_client


@click.group(name='namespaces')
def namespace_commands():
    pass


@command(
    namespace_commands,
    'get-default',
)
def get_default_namespace(context: Optional[str],
                          endpoint_id: Optional[str],
                          ):
    """
    Get the default namespace

    docs: https://docs.omics.ai/products/command-line-interface/reference/workbench/namespaces-get-default
    """

    namespace = get_user_client(context, endpoint_id).get_user_config().default_namespace
    click.echo(namespace)
