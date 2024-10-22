from typing import Optional, List

import click

from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat
from dnastack.cli.workbench.utils import get_workflow_client
from dnastack.client.workbench.workflow.models import WorkflowDefaultsSelector, WorkflowDefaultsCreateRequest, \
    WorkflowDefaultsListOptions, WorkflowDefaultsUpdateRequest
from dnastack.common.json_argument_parser import JsonLike


@click.group('defaults')
def workflows_versions_defaults_command_group():
    """ Interact with workflow versions defaults """


@command(workflows_versions_defaults_command_group,
         'create',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
             ArgumentSpec(
                 name='version_id',
                 arg_names=['--version'],
                 help='The id of the workflow version',
                 as_option=True
             ),

             ArgumentSpec(
                 name='engine',
                 arg_names=['--engine'],
                 help='The selector to use when creating the defaults',
                 as_option=True
             ),
             ArgumentSpec(
                 name="provider",
                 arg_names=["--provider"],
                 help="The provider selector to use when creating the defaults",
                 as_option=True
             ),
             ArgumentSpec(
                 name='region',
                 arg_names=['--region'],
                 help='The region selector to use when creating the defaults',
                 as_option=True
             ),
             ArgumentSpec(
                 name='values',
                 arg_names=['--values'],
                 help='The values to use when creating the defaults',
                 as_option=True
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='The human readable name of the defaults',
                 as_option=True
             )
         ])
def create_workflow_defaults(context: Optional[str],
                             endpoint_id: Optional[str],
                             namespace: Optional[str],
                             workflow_id: str,
                             version_id: str,
                             provider: Optional[str],
                             region: Optional[str],
                             engine: Optional[str],
                             values: JsonLike,
                             name: str,
                             id: Optional[str]):
    """
    Create a default for a workflow
    """
    client = get_workflow_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    parsed = values.parsed_value()
    selector = WorkflowDefaultsSelector(engine=engine, provider=provider, region=region)
    workflow_defaults = WorkflowDefaultsCreateRequest(id=id, name=name, selector=selector, values=parsed)
    click.echo(to_json(normalize(client.create_workflow_defaults(workflow_id=workflow_id, version_id=version_id,
                                                                       workflow_defaults=workflow_defaults))))


@command(workflows_versions_defaults_command_group,
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
                      'e.g.: --sort "name:ASC", --sort "name;created_on:DESC;"',

                 as_option=True
             ),
             ArgumentSpec(
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
             ArgumentSpec(
                 name='version_id',
                 arg_names=['--version'],
                 help='The id of the workflow version',
                 as_option=True
             )
         ]
         )
def list_workflow_defaults(context: Optional[str],
                           endpoint_id: Optional[str],
                           namespace: Optional[str],
                           max_results: Optional[int],
                           page: Optional[int],
                           page_size: Optional[int],
                           sort: Optional[str],
                           workflow_id: str,
                           version_id: str):
    """
    List the defaults available for a workflow
    """
    client = get_workflow_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)

    show_iterator(output_format=OutputFormat.JSON,
                  iterator=
                  client.list_workflow_defaults(workflow_id=workflow_id, version_id=version_id,
                                                      max_results=max_results,
                                                      list_options=WorkflowDefaultsListOptions(page=page,
                                                                                               page_size=page_size,
                                                                                               sort=sort)))


@command(workflows_versions_defaults_command_group,
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
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
             ArgumentSpec(
                 name='version_id',
                 arg_names=['--version'],
                 help='The id of the workflow version',
                 as_option=True
             ),

         ])
def describe_workflow_defaults(context: Optional[str],
                               endpoint_id: Optional[str],
                               namespace: Optional[str],
                               workflow_id: str,
                               version_id: str,
                               default_ids: List[str]):
    """
    Describe one or more default values for a workflow
    """

    client = get_workflow_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)

    if not default_ids:
        click.echo("You must specify at least one default id")
        exit(1)

    workflow_defaults = [
        client.get_workflow_defaults(workflow_id=workflow_id, version_id=version_id, default_id=default_id) for
        default_id in default_ids]
    click.echo(to_json(normalize(workflow_defaults)))


@command(workflows_versions_defaults_command_group,
         'update',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='workflow',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
             ArgumentSpec(
                 name='version',
                 arg_names=['--version'],
                 help='The id of the workflow version',
                 as_option=True
             ),
             ArgumentSpec(
                 name='engine',
                 arg_names=['--engine'],
                 help='The selector to use when creating the defaults',
                 as_option=True
             ),
             ArgumentSpec(
                 name="provider",
                 arg_names=["--provider"],
                 help="The provider selector to use when creating the defaults",
                 as_option=True
             ),
             ArgumentSpec(
                 name='region',
                 arg_names=['--region'],
                 help='The region selector to use when creating the defaults',
                 as_option=True
             ),
             ArgumentSpec(
                 name='values',
                 arg_names=['--values'],
                 help='The values to use when creating the defaults',
                 as_option=True
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='The human readable name of the defaults',
                 as_option=True
             )
         ])
def update_workflow_defaults(context: Optional[str],
                             endpoint_id: Optional[str],
                             namespace: Optional[str],
                             workflow: str,
                             version: str,
                             name: str,
                             provider: Optional[str],
                             region: Optional[str],
                             engine: Optional[str],
                             values: JsonLike,
                             default_id: str
                             ):
    """
    Update a default for a workflow
    """
    client = get_workflow_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    parsed = values.parsed_value()
    selector = WorkflowDefaultsSelector(engine=engine, provider=provider, region=region)
    workflow_defaults = WorkflowDefaultsUpdateRequest(name=name, selector=selector, values=parsed)
    existing = client.get_workflow_defaults(workflow_id=workflow, version_id=version, default_id=default_id)
    click.echo(to_json(normalize(client.update_workflow_defaults(workflow_id=workflow, version_id=version,
                                                                       default_id=default_id,
                                                                       if_match=existing.etag,
                                                                       workflow_defaults=workflow_defaults))))


@command(workflows_versions_defaults_command_group,
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
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
             ArgumentSpec(
                 name='version_id',
                 arg_names=['--version'],
                 help='The id of the workflow version',
                 as_option=True
             ),
             ArgumentSpec(
                 name="force",
                 arg_names=["--force"],
                 help="Force the deletion of the workflow defaults",
                 as_option=True
             )
         ])
def delete_workflow_defaults(context: Optional[str],
                             endpoint_id: Optional[str],
                             namespace: Optional[str],
                             workflow_id: str,
                             version_id: str,
                             default_id: str,
                             force: Optional[bool]):
    """
    Delete a default for a workflow
    """
    client = get_workflow_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    if not force:
        click.confirm(f"Are you sure you want to delete the workflow defaults with id {default_id}?", abort=True)
    existing = client.get_workflow_defaults(workflow_id=workflow_id, version_id=version_id, default_id=default_id)
    client.delete_workflow_defaults(workflow_id=workflow_id, version_id=version_id, default_id=default_id,
                                          if_match=existing.etag)
    click.echo("Deleted...")
