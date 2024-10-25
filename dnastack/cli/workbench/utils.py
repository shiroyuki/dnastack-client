import base64
import binascii
import os
import re
from typing import Optional, List, Union

import click
from dnastack.common.json_argument_parser import FileOrValue

from dnastack.http.session import JsonPatch

from dnastack.client.workbench.workflow.models import WorkflowFile, WorkflowFileType
from imagination import container
import zipfile as zf

from dnastack.client.workbench.ewes.client import EWesClient
from dnastack.client.workbench.samples.client import SamplesClient
from dnastack.client.workbench.storage.client import StorageClient
from dnastack.client.workbench.workflow.client import WorkflowClient
from dnastack.client.workbench.workbench_user_service.client import WorkbenchUserClient
from dnastack.cli.config.context import ContextCommandHandler
from dnastack.cli.helpers.client_factory import ConfigurationBasedClientFactory

DEFAULT_WORKBENCH_DESTINATION = "workbench.omics.ai"


def _populate_workbench_endpoint():
    handler: ContextCommandHandler = container.get(ContextCommandHandler)
    handler.use(DEFAULT_WORKBENCH_DESTINATION, context_name="workbench", no_auth=False)


def get_user_client(context_name: Optional[str] = None,
                    endpoint_id: Optional[str] = None) -> WorkbenchUserClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(WorkbenchUserClient, endpoint_id=endpoint_id, context_name=context_name)
    except AssertionError as e:
        raise e
        _populate_workbench_endpoint()
        return factory.get(WorkbenchUserClient, endpoint_id=endpoint_id, context_name=context_name)


def get_ewes_client(context_name: Optional[str] = None,
                    endpoint_id: Optional[str] = None,
                    namespace: Optional[str] = None) -> EWesClient:
    if not namespace:
        user_client = get_user_client(context_name=context_name, endpoint_id=endpoint_id)
        namespace = user_client.get_user_config().default_namespace

    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(EWesClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(EWesClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)


def get_workflow_client(context_name: Optional[str] = None,
                        endpoint_id: Optional[str] = None,
                        namespace: Optional[str] = None) -> WorkflowClient:
    if not namespace:
        user_client = get_user_client(context_name=context_name, endpoint_id=endpoint_id)
        namespace = user_client.get_user_config().default_namespace

    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(WorkflowClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(WorkflowClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)


def get_storage_client(context_name: Optional[str] = None,
                       endpoint_id: Optional[str] = None,
                       namespace: Optional[str] = None) -> StorageClient:
    if not namespace:
        user_client = get_user_client(context_name=context_name, endpoint_id=endpoint_id)
        namespace = user_client.get_user_config().default_namespace
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(StorageClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(StorageClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)


def get_samples_client(context_name: Optional[str] = None,
                       endpoint_id: Optional[str] = None,
                       namespace: Optional[str] = None) -> SamplesClient:
    if not namespace:
        user_client = get_user_client(context_name=context_name, endpoint_id=endpoint_id)
        namespace = user_client.get_user_config().default_namespace
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(SamplesClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(SamplesClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)



class UnableToMergeJsonError(RuntimeError):
    def __init__(self, key):
        super().__init__(f'Unable to merge key {key}. The value for {key} must be of type dict, str, int or float')


class UnableToFindFileError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnableToDecodeFileError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnableToDisplayFileError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class IncorrectFlagError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnableToCreateFilePathError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnableToWriteToFileError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnableToFindParameterError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NoDefaultEngineError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class JavaScriptFunctionExtractor:
    FUNCTION_PATTERN = re.compile(r'(?:let|const)\s*\w+\s*=\s*(\(.*\)\s*=>\s*\{.*\})', re.DOTALL)

    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_first_function(self) -> Optional[str]:
        with open(self.file_path, 'r') as file:
            content = file.read()
        match = self.FUNCTION_PATTERN.search(content)
        if match:
            return match.group(1)
        return None

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

