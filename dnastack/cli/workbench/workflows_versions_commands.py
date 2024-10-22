import os
from pathlib import Path
from typing import Optional, List

import click

from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat
from dnastack.cli.workbench.utils import get_workflow_client
from dnastack.cli.workbench.utils import _get_replace_patch, _get_description_patch, _get_author_patch, \
    find_file, handle_zip_output, decode_base64_content, create_missing_directories, write_to_file, \
    decode_readable_file, handle_files_output
from dnastack.cli.workbench.workflow_versions_transformations_commands import \
    workflow_versions_transformations_command_group
from dnastack.cli.workbench.workflows_versions_defaults_commands import \
    workflows_versions_defaults_command_group
from dnastack.client.workbench.workflow.models import WorkflowVersionListOptions, WorkflowVersionCreate
from dnastack.client.workbench.workflow.utils import WorkflowSourceLoader
from dnastack.common.json_argument_parser import FileOrValue


@click.group('versions')
def workflow_versions_command_group():
    """ Create and interact with workflow versions """


workflow_versions_command_group.add_command(workflows_versions_defaults_command_group)
workflow_versions_command_group.add_command(workflow_versions_transformations_command_group)


@command(workflow_versions_command_group,
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
                 name='workflow',
                 arg_names=['--workflow', ],
                 help='The workflow id to add the version to.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='max_results',
                 arg_names=['--max-results'],
                 help='Limit the total number of results.',
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
def list_versions(context: Optional[str],
                  endpoint_id: Optional[str],
                  namespace: Optional[str],
                  workflow: str,
                  max_results: Optional[int],
                  include_deleted: Optional[bool] = False
                  ):
    """
    List the available versions for the given workflow

    docs: https://docs.omics.ai/docs/workflows-versions-list
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    list_options = WorkflowVersionListOptions(
        deleted=include_deleted
    )
    show_iterator(output_format=OutputFormat.JSON,
                  iterator=workflows_client.list_workflow_versions(workflow_id=workflow,
                                                                   list_options=list_options,
                                                                   max_results=max_results))


@command(workflow_versions_command_group,
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
                 name='workflow',
                 arg_names=['--workflow', ],
                 help='The workflow id to add the version to.',
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
def describe_version(context: Optional[str],
                     endpoint_id: Optional[str],
                     namespace: Optional[str],
                     workflow: str,
                     versions: List[str],
                     include_deleted: Optional[bool] = False
                     ):
    """
    Describe one or more workflow versions for the given workflow

    docs: https://docs.omics.ai/docs/workflows-versions-describe
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    click.echo(to_json(normalize(
        [workflows_client.get_workflow_version(workflow_id=workflow, version_id=version_id,
                                               include_deleted=include_deleted) for version_id in versions]
    )))


@command(workflow_versions_command_group,
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
             ArgumentSpec(
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
         ]
         )
def delete_workflow_version(context: Optional[str],
                            endpoint_id: Optional[str],
                            namespace: Optional[str],
                            workflow_id: str,
                            version_id: str,
                            force: Optional[bool] = False):
    """
    Delete an existing workflow version

    docs: https://docs.omics.ai/docs/workflows-versions-delete
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    workflow = workflows_client.get_workflow(workflow_id)
    version = workflows_client.get_workflow_version(workflow_id, version_id)
    if not force and not click.confirm(
            f'Do you want to delete "{version.versionName}" from workflow "{workflow.name}"?'):
        return

    workflows_client.delete_workflow_version(workflow_id, version_id, version.etag)
    click.echo("Deleted...")


@command(workflow_versions_command_group,
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
                 name='workflow',
                 arg_names=['--workflow', ],
                 help='The workflow id to add the version to.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='name',
                 arg_names=['--name'],
                 help='The version name to create',
                 as_option=True
             ),
             ArgumentSpec(
                 name='description',
                 arg_names=['--description'],
                 help='An optional description for the workflow version in markdown format.'
                      ' You can specify a file by prepending "@" to a path: @<path>',
                 as_option=True,
                 required=False,
                 default=None
             )
         ]
         )
def add_version(context: Optional[str],
                endpoint_id: Optional[str],
                namespace: Optional[str],
                workflow: str,
                name: str,
                description: FileOrValue,
                entrypoint: str,
                workflow_files: List[Path]):
    """
    Add a new version to an existing workflow

    To specify the primary descriptor for the workflow,
    use the --entrypoint flag.
    Ensure that this path correctly points to the intended .wdl file,
    as this file serves as the central definition or entrypoint of your workflow.

    Workflow files can encompass a variety of file types, including any standard file or compressed ZIP file.
    The system will recognize and process these files according to their type and content.

    docs: https://docs.omics.ai/docs/workflows-versions-create
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)

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

    create_request = WorkflowVersionCreate(
        version_name=name,
        description=description.value() if description else None,
        entrypoint=entrypoint,
        files=workflow_files_list
    )

    result = workflows_client.create_version(workflow_id=workflow, workflow_version_create_request=create_request)
    click.echo(to_json(normalize(result)))


@command(workflow_versions_command_group,
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
                 name='version_name',
                 arg_names=['--name'],
                 help='The new name of the workflow version',
                 as_option=True
             ),
             ArgumentSpec(
                 name='description',
                 arg_names=['--description'],
                 help='The new description of the workflow version in markdown format.'
                      ' You can specify a file by prepending "@" to a path: @<path>. To'
                      ' unset the description the value should be ""',
                 as_option=True,
                 required=False,
                 default=None
             ),
             ArgumentSpec(
                 name='authors',
                 arg_names=['--authors'],
                 help='List of authors to update. This value can be a comma separated list',
                 as_option=True
             ),
             ArgumentSpec(
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             )
         ]
         )
def update_workflow_version(context: Optional[str],
                            endpoint_id: Optional[str],
                            namespace: Optional[str],
                            workflow_id: str,
                            version_id: str,
                            version_name: Optional[str],
                            description: FileOrValue,
                            authors: Optional[str]):
    """
    Update an existing workflow version

    docs: https://docs.omics.ai/docs/workflows-versions-update
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)
    workflow_version = workflows_client.get_workflow_version(workflow_id, version_id)

    patch_list = [
        _get_replace_patch("/versionName", version_name),
        _get_description_patch(description),
        _get_author_patch(authors)
    ]
    patch_list = [patch for patch in patch_list if patch]

    if patch_list:
        workflow_version = workflows_client.update_workflow_version(workflow_id, version_id, workflow_version.etag,
                                                                    patch_list)
        click.echo(to_json(normalize(workflow_version)))
    else:
        raise ValueError("Must specify at least one attribute to update")


@command(workflow_versions_command_group,
         "files",
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='path',
                 arg_names=['--path'],
                 help='An optional flag to define a path to print the specific file',
                 as_option=True
             ),
             ArgumentSpec(
                 name='output',
                 arg_names=['--output'],
                 help='An optional flag to define the path where the content should'
                      'be saved instead of being printed to the screen',
                 as_option=True
             ),
             ArgumentSpec(
                 name='zip',
                 arg_names=['--zip'],
                 help='An optional flag that specifies whether the files should be downloaded in a zip folder.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='workflow_id',
                 arg_names=['--workflow'],
                 help='The id of the workflow',
                 as_option=True
             ),
         ]
         )
def retrieve_workflow_files(context: Optional[str],
                            endpoint_id: Optional[str],
                            namespace: Optional[str],
                            path: str = None,
                            output: str = None,
                            zip: bool = False,
                            workflow_id: str = None,
                            version_id: str = None):
    """
        Output the workflow's files
    """
    workflows_client = get_workflow_client(context, endpoint_id, namespace)

    if not workflow_id:
        raise NameError("You must specify workflow ID")

    if not version_id:
        raise NameError("You must specify version ID")

    # get files
    files = workflows_client.get_workflow_files(workflow_id=workflow_id, version_id=version_id)
    if path:
        output_file = find_file(path, files)

        # --path and --zip are defined (--output is checked in the function)
        if zip:
            handle_zip_output(output, [output_file], workflow_id, version_id)

        # --path and --output are defined without --zip
        else:
            if output:
                content = decode_base64_content(output_file.base64_content)
                directory = os.path.dirname(output)
                create_missing_directories(directory)
                write_to_file(output, content)

            # only --path is defined
            else:
                content = decode_readable_file(output_file)
                click.echo(content)
    else:
        # --zip is defined without --path
        if zip:
            handle_zip_output(output, files, workflow_id, version_id)

        # --path and --zip are not defined (--output is checked in the function)
        else:
            handle_files_output(output, files)
