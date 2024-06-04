import binascii
import os
from pathlib import Path
from typing import Optional

import click
from click import style

from dnastack.cli.drs import download
from dnastack.cli.workbench.utils import get_workflow_client, UnableToFindFileError, \
    UnableToDisplayFileError, UnableToDecodeFileError, IncorrectFlagError, UnableToCreateFilePathError, \
    UnableToWriteToFileError
from dnastack.client.workbench.workflow.models import WorkflowCreate, WorkflowVersionCreate, WorkflowSource, \
    WorkflowListOptions, WorkflowVersionListOptions, WorkflowFileType, WorkflowFile
from dnastack.client.workbench.workflow.utils import WorkflowSourceLoader
from dnastack.http.session import JsonPatch
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat
from dnastack.common.json_argument_parser import *
import base64
import zipfile as zf


@click.group('versions')
def workflow_versions_command_group():
    """ Create and interact with workflow versions """


@click.group('workflows')
def workflows_command_group():
    """ Create and interact with  workflows"""


def _get_author_patch(authors: str) -> Union[JsonPatch, None]:
    if authors == "":
        return JsonPatch(path="/authors", op="remove")
    elif authors:
        return JsonPatch(path="/authors", op="replace", value=authors.split(","))
    return None


def _get_description_patch(description: Optional[FileOrValue]) -> Union[JsonPatch, None]:
    if not description:
        return None
    if description.raw_value == "":
        return JsonPatch(path="/description", op="remove")
    elif description:
        return JsonPatch(path="/description", op="replace", value=description.value())
    return None


def _get_replace_patch(path: str, value: str) -> Union[JsonPatch, None]:
    if value:
        return JsonPatch(path=path, op="replace", value=value)
    return None


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


def get_descriptor_file(files_list: List[WorkflowFile]):
    for file in files_list:
        if file.file_type == WorkflowFileType.primary:
            return file
    raise UnableToFindFileError("No primary descriptor file found for the workflow. Must specify a file's "
                                "path using --path flag.")


def find_file(file_path: str, files_list: List[WorkflowFile]):
    for file in files_list:
        if file_path == file.path:
            return file
    raise UnableToFindFileError(f'File not found at {file_path}')


def decode_base64_content(base64_content: str):
    try:
        return base64.b64decode(base64_content)
    except binascii.Error as e:
        raise UnableToDecodeFileError(f"Failed to decode base64 content: {e}")


def decode_readable_file(file: WorkflowFile):
    if file.content_type == "application/json" or file.content_type.startswith("text/"):
        return decode_base64_content(file.base64_content)
    else:
        raise UnableToDisplayFileError(f"File cannot be displayed due to unsupported content type: {file.content_type}")


def is_folder(path):
    base, extension = os.path.splitext(path)
    return extension == ""


def is_zip_file(path):
    base, extension = os.path.splitext(path)
    return extension.lower() == ".zip"


def create_missing_directories(path):
    if not os.path.exists(path) and path != "":
        try:
            os.makedirs(path)
        except Exception:
            raise UnableToCreateFilePathError(f"Could not create file path: {path}")


def handle_zip_output(output: str, files: List[WorkflowFile], workflow_name, workflow_version):
    output_path = None
    if not output:
        output = os.getcwd()
        output_path = os.path.join(output, f'{workflow_name}-{workflow_version}-files.zip')
        click.secho(f"No --output flag specified. Downloading zip file as "
                    f"{workflow_name}-{workflow_version}-files.zip into current directory", fg='green')

    # checks if output is a directory
    elif is_folder(output):
        create_missing_directories(output)
        output_path = os.path.join(output, f'{workflow_name}-{workflow_version}-files.zip')
        click.secho(f"--output flag specified a folder instead of a zip file path. "
                    f"Downloading zip file into {output_path}", fg='green')

    # check if output is a zip file
    elif is_zip_file(output):
        zip_file_dir_path = os.path.dirname(output)
        create_missing_directories(zip_file_dir_path)
        output_path = output

    # if output ends with an existing file that is a zip file then raise error
    else:
        raise IncorrectFlagError("The path specified with --output ends with a file. Must either specify --output "
                                 "to end with a .zip extension or to end with a folder")

    with zf.ZipFile(output_path, mode='w') as z:
        for file in files:
            content = decode_base64_content(file.base64_content)
            # must decode bytes to string to write to a zip file
            if file.content_type == "application/json" or file.content_type.startswith("text/"):
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnableToDecodeFileError(f"Failed to decode binary content: {e}")
            z.writestr(file.path, content)


def write_to_file(output, content):
    try:
        with open(output, mode='w') as file_path:
            click.echo(content, file=file_path, nl=False)
    # fails when writing specific file and output has trailing separator or is directory
    except Exception:
        raise UnableToWriteToFileError(f"Unable to write to file specified by --output: {output} Please ensure that "
                                       f"if you are writing to a specific file that your path specified by "
                                       f"--output does not have a trailing separator and does not point to a directory")


def handle_files_output(output: str, files: List[WorkflowFile]):
    # if --path, --output and --zip flags are NOT specified, print the descriptor file contents
    if not output:
        output_file = get_descriptor_file(files)
        content = decode_readable_file(output_file)
        click.echo(content)

    # if only --output then write the entire hierarchy of files to output location
    else:
        create_missing_directories(output)
        if os.path.isdir(output):
            for file in files:
                content = decode_base64_content(file.base64_content)
                appended_path = os.path.join(output, file.path)
                # if file.path contains more nested directories, we create them
                directory = os.path.dirname(appended_path)
                create_missing_directories(directory)
                write_to_file(appended_path, content)
        else:
            raise IncorrectFlagError("The path specified with --output ends with a file. Must either specify "
                                     "a specific file with --path flag to be copied into the location specified "
                                     "by --output or change the path specified by --output to end with a folder.")


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


workflows_command_group.add_command(workflow_versions_command_group)
