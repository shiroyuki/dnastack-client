import os
from typing import Optional

from dnastack.cli.helpers.iterator_printer import show_iterator
from dnastack.client.data_connect import DataConnectClient
from dnastack.common.tracing import Span


def handle_query(data_connect: DataConnectClient,
                 query: str,
                 decimal_as: str = 'string',
                 no_auth: bool = False,
                 output_format: Optional[str] = None,
                 allow_using_query_from_file: bool = False,
                 trace: Optional[Span] = None):
    """
    Initiate a Data Connect query
    :param data_connect: The Data Connect client
    :param query: The query to the endpoint
    :param decimal_as: Decimal representation
    :param no_auth: Flag to disable authentication or temporarily disregard session info
    :param output_format: Output format (e.g., JSON, CSV, YAML)
    :param allow_using_query_from_file: Flag to allow the CLI user to run a query from a file
    :param trace: Distributed Trace Context
    :return:
    """
    actual_query = query

    if allow_using_query_from_file:
        if query.startswith('@'):
            query_file_path = query[1:]
            if os.path.exists(query_file_path):
                with open(query_file_path, 'r') as f:
                    actual_query = f.read()
            else:
                raise IOError(f'File not found: {query_file_path}')

    iterator = data_connect.query(actual_query, no_auth=no_auth, trace=trace)
    show_iterator(output_format, iterator, decimal_as=decimal_as, sort_keys=False)
