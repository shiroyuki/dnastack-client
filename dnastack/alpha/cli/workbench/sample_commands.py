import click
from typing import Optional

from dnastack.alpha.cli.workbench.utils import get_samples_client
from dnastack.alpha.client.workbench.samples.models import SampleListOptions
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat


@click.group('samples')
def alpha_samples_command_group():
    """ Interact with samples """


@command(alpha_samples_command_group,
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


@command(alpha_samples_command_group,
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
