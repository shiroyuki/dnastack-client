from typing import Optional

import click
from kotoba.parser import selector

from dnastack.alpha.cli.workbench.utils import get_alpha_workflow_client
from dnastack.alpha.client.workbench.samples.models import Sample
from dnastack.alpha.client.workbench.workflow.models import WorkflowDefaultsSelector
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.exporter import to_json, normalize
from dnastack.cli.workbench.utils import NoDefaultEngineError, UnableToFindParameterError, get_ewes_client, \
    get_workflow_client
from dnastack.client.workbench.ewes.models import ExecutionEngineListOptions, BatchRunRequest, ExtendedRunRequest
from dnastack.common.json_argument_parser import JsonLike, merge_param_json_data, merge, parse_and_merge_arguments


@click.group('runs')
def alpha_runs_command_group():
    """ Interact with samples """


@command(alpha_runs_command_group,
         'submit',
         specs=[
             ArgumentSpec(
                 name='namespace',
                 arg_names=['--namespace', '-n'],
                 help='An optional flag to define the namespace to connect to. By default, the namespace will be '
                      'extracted from the users credentials.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='workflow_url',
                 arg_names=['--url'],
                 help='The URL to the workflow file (*.wdl). Only urls from workflow-service are '
                      'currently supported.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='engine_id',
                 arg_names=['--engine'],
                 help='Use the given engine id for execution of runs. If this value is not defined then it is assumed '
                      'that the default engine will be used.',
                 as_option=True
             ),
             ArgumentSpec(
                 name='default_workflow_engine_parameters',
                 arg_names=['--engine-params'],
                 help='Set the global engine parameters for all runs that are to be submitted. '
                      'Engine params can be specified as inlined JSON, json file preceded by the "@" symbol, '
                      'KV pair, parameter preset ID, or as a comma-separated-list containing any of those types '
                      '(e.g. my-preset-id,key=value,\'{"literal":"json"}\',@file.json).',
                 as_option=True,
                 default=None,
                 required=False
             ),
             ArgumentSpec(
                 name='default_workflow_params',
                 arg_names=['--default-params'],
                 help='Specify the global default inputs as a json file or as inlined json to use when submitting '
                      'multiple runs. Default inputs have the lowest level of precedence and will be overridden '
                      'by any run input or override.',
                 as_option=True,
                 default=None,
                 required=False
             ),
             ArgumentSpec(
                 name='workflow_params',
                 arg_names=['--workflow-params'],
                 help='Optional flag to specify the workflow params for a given run. The workflow params can be any'
                      'JSON-like value, such as inline JSON, command separated key value pairs or a json file referenced'
                      'preceded by the "@" symbol. This field may be repeated, with each repetition specifying '
                      'a separate run request that will be submitted.',
                 as_option=True,
                 required=False,
                 default=None,
                 nargs=-1,
                 type=JsonLike
             ),
             ArgumentSpec(
                 name='tags',
                 help='Set the global tags for all runs that are to be submitted. '
                      'Tags can be any JSON-like value, such as inline JSON, command separated key value pairs or'
                      'a json file referenced preceded by the "@" symbol.',
                 as_option=True,
                 default=None,
                 required=False
             ),
             ArgumentSpec(
                 name='overrides',
                 help='Additional arguments to set input values for all runs. The override values can be any '
                      'JSON-like value such as inline JSON, command separated key value pairs or '
                      'a json file referenced preceded by the "@" symbol.',
                 as_option=False,
                 default=None,
                 nargs=-1,
                 type=JsonLike,
                 required=False
             ),
             ArgumentSpec(
                 name='dry_run',
                 arg_names=['--dry-run'],
                 help='If specified, the command will print the request without actually submitting the workflow.',
                 as_option=True,
                 default=False,
                 required=False
             ),
             ArgumentSpec(
                 name='no_defaults',
                 arg_names=['--no-defaults'],
                 help='If specified, the command will not use any default values for the workflow.',
                 as_option=True,
                 default=False,
                 required=False
             ),
             ArgumentSpec(
                 name='sample_ids',
                 arg_names=['--samples'],
                 help='An optional flag that accepts a comma separated list of Sample IDs to use in the given workflow.',
                 as_option=True,
                 required=False,
             ),
         ])
def submit_batch(context: Optional[str],
                 endpoint_id: Optional[str],
                 namespace: Optional[str],
                 workflow_url: str,
                 engine_id: Optional[str],
                 default_workflow_engine_parameters: JsonLike,
                 default_workflow_params: JsonLike,
                 tags: JsonLike,
                 workflow_params,
                 overrides,
                 dry_run: bool,
                 no_defaults: bool,
                 sample_ids: Optional[str]):
    """
    Submit one or more workflows for execution

    docs: https://docs.omics.ai/docs/runs-submit
    """

    ewes_client = get_ewes_client(context_name=context, endpoint_id=endpoint_id, namespace=namespace)

    def parse_samples():
        if not sample_ids:
            return None

        sample_list = sample_ids.split(',')
        return [Sample(id=sample_id) for sample_id in sample_list]

    def get_default_engine_id():
        list_options = ExecutionEngineListOptions()
        engines = ewes_client.list_engines(list_options)
        for engine in engines:
            if engine.default:
                return engine.id
        raise NoDefaultEngineError("No default engine found. Please specify an engine id using the --engine flag "
                                   "or in the workflow engine parameters list using ENGINE_ID_KEY=....")

    def get_workflow_defaults(engine_id_to_fetch: str):
        alpha_workflow_client = get_alpha_workflow_client(context_name=context, endpoint_id=endpoint_id,
                                                          namespace=namespace)
        resolved_workflow = alpha_workflow_client.resolve_workflow(workflow_url)
        defaults_selector = WorkflowDefaultsSelector()
        resolved_defaults = dict()
        engine = ewes_client.get_engine(engine_id_to_fetch)
        defaults_selector.engine = engine.id
        defaults_selector.region = engine.region
        defaults_selector.provider = engine.provider

        try:
            resolved_defaults = alpha_workflow_client.resolve_workflow_defaults(
                workflow_id=resolved_workflow.internalId,
                workflow_version_id=resolved_workflow.versionId,
                selector=defaults_selector).values
        except Exception as e:
            pass
        return resolved_defaults

    if not engine_id:
        engine_id = get_default_engine_id()

    if default_workflow_engine_parameters:
        [param_ids_list, kv_pairs_list, json_literals_list,
         files_list] = default_workflow_engine_parameters.extract_arguments_list()

        param_presets = merge_param_json_data(kv_pairs_list, json_literals_list, files_list)

        if param_ids_list:
            for param_id in param_ids_list:
                try:
                    param_preset = ewes_client.get_engine_param_preset(engine_id, param_id)
                    merge(param_presets, param_preset.preset_values)
                except Exception as e:
                    raise UnableToFindParameterError(f"Unable to find engine parameter preset with id {param_id}. {e}")

        default_workflow_engine_parameters = param_presets
    else:
        default_workflow_engine_parameters = None

    default_workflow_params = default_workflow_params.parsed_value() if default_workflow_params else {}
    if not no_defaults:
        workflow_defaults = get_workflow_defaults(engine_id)
        merge(default_workflow_params, workflow_defaults)

    batch_request: BatchRunRequest = BatchRunRequest(
        workflow_url=workflow_url,
        workflow_type="WDL",
        engine_id=engine_id,
        default_workflow_engine_parameters=default_workflow_engine_parameters,
        default_workflow_params=default_workflow_params,
        default_tags=tags.parsed_value() if tags else None,
        run_requests=list(),
        samples=parse_samples()
    )

    for workflow_param in workflow_params:
        run_request = ExtendedRunRequest(
            workflow_params=workflow_param.parsed_value() if workflow_param else None
        )
        batch_request.run_requests.append(run_request)

    override_data = parse_and_merge_arguments(overrides)
    if override_data:
        if not batch_request.default_workflow_params:
            batch_request.default_workflow_params = dict()
        merge(batch_request.default_workflow_params, override_data)

        for run_request in batch_request.run_requests:
            if not run_request.workflow_params:
                run_request.workflow_params = dict()
            merge(run_request.workflow_params, override_data)

    if dry_run:
        click.echo(to_json(normalize(batch_request)))
    else:
        minimal_batch = ewes_client.submit_batch(batch_request)
        click.echo(to_json(normalize(minimal_batch)))
