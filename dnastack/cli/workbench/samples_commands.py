import click
from typing import Optional

from dnastack.client.workbench.storage.models import Platform, PlatformType
from dnastack.cli.workbench.utils import get_samples_client
from dnastack.client.workbench.samples.models import SampleListOptions, SampleFilesListOptions
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat


@click.group('samples')
def samples_command_group():
    """ Interact with samples """


@click.group("files")
def files_command_group():
    """ Interact with files """


samples_command_group.add_command(files_command_group)


@command(samples_command_group,
         'list',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             )
         ])
def list_samples(context: Optional[str],
                 endpoint_id: Optional[str],
                 namespace: Optional[str]
                 ):
    """
    List samples
    docs: https://docs.dnastack.com/docs/samples-list
    """

    client = get_samples_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    list_options: SampleListOptions = SampleListOptions()
    samples_list = client.list_samples(list_options)
    show_iterator(output_format=OutputFormat.JSON, iterator=samples_list)


@command(samples_command_group,
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
                 name='sample_id',
                 help='The id of the sample to describe.',
                 as_option=False
             )
         ])
def describe_samples(context: Optional[str],
                     endpoint_id: Optional[str],
                     namespace: Optional[str],
                     sample_id: str):
    """
    Describe a sample

    docs: https://docs.dnastack.com/docs/samples-describe
    """
    client = get_samples_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    described_sample = client.get_sample(sample_id)
    click.echo(to_json(normalize(described_sample)))


@command(
    files_command_group,
    'list',
    specs=[
        ArgumentSpec(
            name='sample_id',
            arg_names=['--sample'],
            help='The ID of the sample for which the files will be listed.',
            required=True,
            as_option=True
        ),
        ArgumentSpec(
            name='namespace',
            arg_names=['--namespace'],
            help='Namespace to connect to. By default, the namespace will be extracted from the user credentials.',
            as_option=True
        ),
        ArgumentSpec(
            name='max_results',
            arg_names=['--max-results'],
            help='Limit the maximum number of results printed to the console.',
            type=int,
            as_option=True
        ),
        ArgumentSpec(
            name='page',
            arg_names=['--page'],
            help='Offset page number for jumping to an arbitrary page of results.',
            type=int,
            as_option=True
        ),
        ArgumentSpec(
            name='page_size',
            arg_names=['--page-size'],
            help='Number of results returned per page (default 100).',
            type=int,
            as_option=True
        ),
        ArgumentSpec(
            name='sort',
            arg_names=['--sort'],
            help='Sort the files by properties in the form column(:direction)?(;(column(:direction)?)*.',
            as_option=True
        ),
        ArgumentSpec(
            name='platform',
            arg_names=['--platform'],
            help='Filter the files to show only those that originated from a specific platform.',
            as_option=True
        ),
        ArgumentSpec(
            name='storage',
            arg_names=['--storage'],
            help='Filter the files by their storage account.',
            as_option=True
        ),
        ArgumentSpec(
            name='instrument_id',
            arg_names=['--instrument'],
            help='Filter the files by the instrument ID that generated them.',
            as_option=True
        ),
        ArgumentSpec(
            name='platform_type',
            arg_names=['--platform-type'],
            help='Filter the files by the platform type.',
            type=PlatformType,
            as_option=True
        ),
        ArgumentSpec(
            name='search',
            arg_names=['--search'],
            help='Filter the files by a search term.',
            as_option=True
        )
    ]
)
def list_sample_files(
        context: Optional[str],
        endpoint_id: Optional[str],
        sample_id: str,
        namespace: Optional[str],
        max_results: Optional[int],
        page: Optional[int],
        page_size: Optional[int],
        sort: Optional[str],
        platform: Optional[str],
        storage: Optional[str],
        instrument_id: Optional[str],
        platform_type: Optional[PlatformType],
        search: Optional[str]
):
    """
    List files for a given sample.
    """

    client = get_samples_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)
    options = SampleFilesListOptions(
        page=page,
        page_size=page_size,
        sort=sort,
        storage_id=storage,
        platform_id=platform,
        platform_type=platform_type,
        instrument_id=instrument_id,
        search=search
    )

    files_list = client.list_sample_files(
        sample_id=sample_id,
        list_options=options,
        max_results=max_results
    )
    show_iterator(output_format=OutputFormat.JSON, iterator=files_list)
