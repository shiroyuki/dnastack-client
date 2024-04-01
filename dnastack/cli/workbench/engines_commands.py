from typing import Optional

import click
from click import style

from dnastack.cli.workbench.utils import get_ewes_client
from dnastack.client.workbench.ewes.models import ExecutionEngineListOptions
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat
from dnastack.common.json_argument_parser import *


@click.group('engines')
def engines_command_group():
    """ Create and interact with engines """


@click.group('parameters')
def engine_parameters_command_group():
    """ Create and interact with engine parametesrs """


@command(engines_command_group,
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
         ])
def list_engines(context: Optional[str],
                 endpoint_id: Optional[str],
                 namespace: Optional[str],
                 max_results: Optional[int]
                 ):
    """
    List engines

    docs: https://docs.dnastack.com/docs/engines-list
    """

    client = get_ewes_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    list_options: ExecutionEngineListOptions = ExecutionEngineListOptions()
    show_iterator(output_format=OutputFormat.JSON, iterator=client.list_engines(list_options, max_results))


@command(engines_command_group,
         'describe',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             )
         ])
def describe_engines(context: Optional[str],
                     endpoint_id: Optional[str],
                     namespace: Optional[str],
                     engines: List[str]):
    """
    Describe one or more engines

    docs: https://docs.dnastack.com/docs/engines-describe
    """
    client = get_ewes_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)

    if not engines:
        click.echo(style("You must specify at least one engine ID", fg='red'), err=True, color=True)
        exit(1)

    described_engines = [client.get_engine(engine_id=engine) for engine in engines]
    click.echo(to_json(normalize(described_engines)))


@command(engine_parameters_command_group,
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
                 name='engine_id',
                 arg_names=['--engine'],
                 help='A flag to specify the engine whose parameters should be listed',
                 as_option=True
             )
         ])
def list_engine_parameters(context: Optional[str],
                           endpoint_id: Optional[str],
                           namespace: Optional[str],
                           engine_id: str = None):
    """
    Lists engine parameter preset values for a specified engine id
    """
    click.echo('list engine parameter presets')


@command(engine_parameters_command_group,
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
                 name='engine_id',
                 arg_names=['--engine'],
                 help='A flag to specify the engine whose parameter should be described',
                 as_option=True
             )
         ])
def describe_engine_parameters(context: Optional[str],
                               endpoint_id: Optional[str],
                               namespace: Optional[str],
                               engine_id: str = None,
                               preset_id: str = None):
    """
    Describes an engine's parameter preset value for a specified engine id and parameter id
    """
    click.echo('describe engine parameter presets')


engines_command_group.add_command(engine_parameters_command_group)
