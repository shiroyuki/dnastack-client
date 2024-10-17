import click

from dnastack.alpha.cli.workbench.runs_commands import alpha_runs_command_group
from dnastack.alpha.cli.workbench.sample_commands import alpha_samples_command_group
from dnastack.alpha.cli.workbench.storage_commands import alpha_storage_command_group


@click.group('workbench')
def alpha_workbench_command_group():
    """ Interact with Workbench """


alpha_workbench_command_group.add_command(alpha_storage_command_group)
alpha_workbench_command_group.add_command(alpha_samples_command_group)
alpha_workbench_command_group.add_command(alpha_runs_command_group)
