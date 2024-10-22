from pathlib import Path
from typing import Optional

import click
from click import style

from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat
from dnastack.cli.workbench.utils import get_workflow_client
from dnastack.cli.workbench.utils import _get_author_patch, _get_description_patch, _get_replace_patch
from dnastack.cli.workbench.workflows_versions_commands import workflow_versions_command_group
from dnastack.client.workbench.workflow.models import WorkflowCreate, WorkflowSource, \
    WorkflowListOptions
from dnastack.client.workbench.workflow.utils import WorkflowSourceLoader
from dnastack.common.json_argument_parser import *




@click.group('workflows')
def workflows_command_group():
    """ Create and interact with  workflows"""


workflows_command_group.add_command(workflow_versions_command_group)


@command(workflows_command_group,
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
                 help='Limit the total number of results.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='page',
                 arg_names=['--page'],
                 help='Set the page number. '
                      'This allows for jumping into an arbitrary page of results. Zero-based.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='page_size',
                 arg_names=['--page-size'],
                 help='Set the page size returned by the server.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='sort',
                 arg_names=['--sort'],
                 help='Define how results are sorted. '
                      'The value should be in the form `column(:direction)?(;(column(:direction)?)*`'
                      'If no directions are specified, the results are returned in ascending order'
                      'To change the direction of ordering include the "ASC" or "DESC" string after the column. '
                      'e.g.: --sort "last_updated_at:ASC", --sort "name;source:DESC;"',

                 as_option=True
             ),
             ArgumentSpec(
                 name='order',
                 arg_names=['--order'],
                 help='This flag is now deprecated, please use --sort instead. '
                      'Define the ordering of the results. '
                      'The value should return to the attribute name to order the results by. '
                      'By default, results are returned in descending order. '
                      'To change the direction of ordering include the "ASC" or "DESC" string after the column. '
                      'e.g.: --O "end_time", --O "end_time ASC"',

                 as_option=True
             ),
             ArgumentSpec(
                 name='source',
                 arg_names=['--source'],
                 help='Filter the results to only include workflows from the defined source. '
                      'Note: The CUSTOM workflow source has been renamed to Private',
                 as_option=True,
                 required=False,
                 default=None,
                 type=WorkflowSource,
                 choices=[e.value for e in WorkflowSource]

             ),
             ArgumentSpec(
                 name='search',
                 arg_names=['--search'],
                 help='Perform a full text search across various fields using the search value',
                 as_option=True
             ),
             ArgumentSpec(
                 name='include_deleted',
                 arg_names=['--include-deleted'],
                 help='Include deleted workflows in the list',
                 as_option=True

             ),
         ]
         )
def list_workflows(context: Optional[str],
                   endpoint_id: Optional[str],
                   namespace: Optional[str],
                   max_results: Optional[int],
                   page: Optional[int],
                   page_size: Optional[int],
                   sort: Optional[str],
                   order: Optional[str],
                   search: Optional[str],
                   source: Optional[WorkflowSource],
                   include_deleted: Optional[bool] = False):
    """
    List workflows

    docs: https://docs.omics.ai/docs/workflows-list
    """
    order_direction = None
    if order:
        order_and_direction = order.split()
        if len(order_and_direction) > 1:
            order = order_and_direction[0]
            order_direction = order_and_direction[1]

    ## Migration
    if source and source == WorkflowSource.custom:
        source = WorkflowSource.private

    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    list_options = WorkflowListOptions(
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
        direction=order_direction,
        source=source,
        search=search,
        deleted=include_deleted
    )
    show_iterator(output_format=OutputFormat.JSON,
                  iterator=workflows_client.list_workflows(list_options=list_options, max_results=max_results))


@command(workflows_command_group,
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
                 name='include_deleted',
                 arg_names=['--include-deleted'],
                 help='An optional flag to include deleted workflows in the list',
                 as_option=True

             ),
         ]
         )
def describe_workflows(context: Optional[str],
                       endpoint_id: Optional[str],
                       namespace: Optional[str],
                       workflows: List[str],
                       include_deleted: Optional[bool] = False):
    """
    Describe one or more workflows

    docs: https://docs.omics.ai/docs/workflows-describe
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)

    if not workflows:
        click.echo(style("You must specify at least one workflow ID", fg='red'), err=True, color=True)
        exit(1)

    described_workflows = [workflows_client.get_workflow(workflow_id, include_deleted=include_deleted) for workflow_id
                           in workflows]
    click.echo(to_json(normalize(described_workflows)))


@command(workflows_command_group,
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
                 name='name',
                 arg_names=['--name'],
                 help='An optional flag to show set a workflow name. If omitted, the name within the workflow will be used',
                 as_option=True
             ),
             ArgumentSpec(
                 name='version_name',
                 arg_names=['--version-name'],
                 help='An optional flag to show set the version name. If omitted, v1.0.0 will be used',
                 as_option=True,
                 required=False,
                 default=None
             ),
             ArgumentSpec(
                 name='description',
                 arg_names=['--description'],
                 help='An optional flag to set a description for the workflow'
                      ' You can specify a file by prepending "@" to a path: @<path>',
                 as_option=True,
                 required=False,
                 default=None
             ),
             ArgumentSpec(
                 name='organization',
                 arg_names=['--organization'],
                 help='An optional flag to set a organization for the workflow',
                 as_option=True,
                 required=False,
                 default=None
             ),
         ]
         )
def create_workflow(context: Optional[str],
                    endpoint_id: Optional[str],
                    namespace: Optional[str],
                    name: Optional[str],
                    version_name: Optional[str],
                    description: FileOrValue,
                    organization: Optional[str],
                    entrypoint: str,
                    workflow_files: List[Path]):
    """
    Create a new workflow

    To specify the primary descriptor for the workflow,
    use the --entrypoint flag.
    Ensure that this path correctly points to the intended .wdl file,
    as this file serves as the central definition or entrypoint of your workflow.

    Workflow files can encompass a variety of file types, including any standard file or compressed ZIP file.
    The system will recognize and process these files according to their type and content.

    docs: https://docs.omics.ai/docs/workflows-create
    """

    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    # Add entrypoint to workflow_files

    workflow_files_list: List[Path] = list(workflow_files)

    has_zip = any([file.name.endswith("zip") for file in workflow_files_list])
    if has_zip and len(workflow_files_list) > 1:
        raise ValueError("Cannot upload both a zip file and other files at the same time")
    if not has_zip:
        if entrypoint not in workflow_files_list:
            workflow_files_list = [Path(entrypoint)] + workflow_files_list
        loader = WorkflowSourceLoader(entrypoint=entrypoint, source_files=workflow_files_list)
        workflow_files_list = [loader.to_zip()]
        entrypoint = loader.entrypoint

    create_request = WorkflowCreate(
        name=name,
        version_name=version_name,
        description=description.value() if description else None,
        organization=organization,
        entrypoint=entrypoint,
        files=workflow_files_list
    )

    result = workflows_client.create_workflow(workflow_create_request=create_request)
    click.echo(to_json(normalize(result)))


@command(workflows_command_group,
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
def delete_workflow(context: Optional[str],
                    endpoint_id: Optional[str],
                    namespace: Optional[str],
                    workflow_id: str,
                    force: Optional[bool] = False):
    """
    Delete an existing workflow

    docs: https://docs.omics.ai/docs/workflows-delete
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    workflow = workflows_client.get_workflow(workflow_id)
    if not force and not click.confirm(
            f'Do you want to delete "{workflow.name}"?'):
        return

    workflows_client.delete_workflow(workflow.internalId, workflow.etag)
    click.echo("Deleted...")


@command(workflows_command_group,
         "update",
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='The new name of the workflow',
                 as_option=True
             ),
             ArgumentSpec(
                 name='description',
                 arg_names=['--description'],
                 help='The new description of the workflow in markdown format.'
                      ' You can specify a file by prepending "@" to a path: @<path>. To'
                      ' unset the description the value should be ""',
                 as_option=True
             ),
             ArgumentSpec(
                 name='authors',
                 arg_names=['--authors'],
                 help='List of authors to update. This value can be a comma separated list, a file or JSON literal',
                 as_option=True,
                 required=False,
                 default=None
             ),
         ]
         )
def update_workflow(context: Optional[str],
                    endpoint_id: Optional[str],
                    namespace: Optional[str],
                    workflow_id: str,
                    name: Optional[str],
                    description: FileOrValue,
                    authors: Optional[str]):
    """
    Update an existing workflow

    docs: https://docs.omics.ai/docs/workflows-update
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    workflow = workflows_client.get_workflow(workflow_id)

    patch_list = [
        _get_replace_patch("/name", name),
        _get_description_patch(description),
        _get_author_patch(authors)
    ]
    patch_list = [patch for patch in patch_list if patch]

    if patch_list:
        workflow = workflows_client.update_workflow(workflow_id, workflow.etag, patch_list)
        click.echo(to_json(normalize(workflow)))
    else:
        raise ValueError("Must specify at least one attribute to update")





