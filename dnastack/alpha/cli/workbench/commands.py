import click

from dnastack.alpha.cli.workbench.storage_commands import alpha_storage_command_group


@click.group('workbench')
def alpha_workbench_command_group():
    """ Interact with Workbench """


alpha_workbench_command_group.add_command(alpha_storage_command_group)
