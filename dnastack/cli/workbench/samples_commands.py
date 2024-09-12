import os
import uuid
from typing import Optional, Iterable

import click
from click import style

from dnastack.cli.workbench.utils import get_ewes_client, NoDefaultEngineError, \
    UnableToFindParameterError
from dnastack.client.workbench.samples.models import Sample, SamplesListOptions
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.helpers.iterator_printer import show_iterator, OutputFormat
from dnastack.common.json_argument_parser import *
from dnastack.common.tracing import Span

@click.group('samples')
def samples_command_group():
    """ Interact with samples """


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
    list_options: SamplesListOptions = SamplesListOptions()
    samples_list = client.list_samples(list_options)
    show_iterator(output_format=OutputFormat.JSON, iterator=samples_list)