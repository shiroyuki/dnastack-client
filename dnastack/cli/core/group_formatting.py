from typing import Optional, List

import click
from click import style

from dnastack.cli.core.constants import APP_NAME, INDENT, OPTION_WIDTH, TOTAL_WIDTH, OPTION_PADDING
from dnastack.cli.core.formatting_utils import wrap_text, get_visual_length


class FormattedHelpGroup(click.Group):
    """Group class that provides formatted and colored help output."""
    def __init__(self, *args, aliases: Optional[List[str]] = None, **kwargs):
        kwargs['context_settings'] = {
            'help_option_names': ['-h', '--help'],
            'token_normalize_func': lambda x: x.lower(),
        }
        super().__init__(*args, **kwargs)
        self.aliases = aliases or []

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        # First try getting the command directly
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        # If cmd_name is an alias for this group, return the group itself
        if cmd_name in self.aliases:
            return self

        # For sub-commands, check their aliases
        for name in self.list_commands(ctx):
            cmd = self.get_command(ctx, name)
            if hasattr(cmd, 'aliases') and cmd_name in cmd.aliases:
                return cmd

        return None

    def format_command_path(self, ctx: click.Context) -> str:
        """Format the command path correctly"""
        parts = ctx.command_path.split()
        if len(parts) > 0 and parts[0].endswith('__main__.py'):
            return APP_NAME + ' ' + ' '.join(parts[1:])
        return ' '.join(parts)

    def get_help(self, ctx: click.Context) -> str:
        """Override get_help to customize and colorize the help output."""
        # Extract the command description
        description = self.help or ''

        # Get properly formatted command path
        command_display = self.format_command_path(ctx)

        # Build the new help text
        new_help = [
            style("Usage:", fg='bright_white', bold=True) + " " +
            style(command_display, fg='bright_white') + " " +
            style("[COMMAND]", fg='bright_blue')
        ]

        # Add description
        if description:
            new_help.extend([
                '',
                style(description, fg='bright_white')
            ])

        # Add commands section
        commands = self.list_commands(ctx)
        if commands:
            new_help.extend([
                '',
                style('Commands:', fg='bright_green', bold=True),
                style('--------', fg='bright_green', dim=True)
            ])

            # Process and format all commands first
            formatted_commands = []
            for cmd in commands:
                cmd_obj = self.get_command(ctx, cmd)
                if cmd_obj is None or cmd_obj.hidden:
                    continue

                # Get command help and process it
                cmd_help = cmd_obj.get_short_help_str() or ''

                # Option 1: Aliases on the same line
                if hasattr(cmd_obj, 'aliases') and cmd_obj.aliases:
                    alias_text = f"({', '.join(cmd_obj.aliases)})"
                    cmd_name = f"{cmd} {style(alias_text, fg='bright_black')}"
                else:
                    cmd_name = cmd

                formatted_commands.append((cmd_name, cmd_help))

            # Calculate the start position for help text
            description_start = len(INDENT) + OPTION_WIDTH + OPTION_PADDING
            available_width = TOTAL_WIDTH - description_start

            # Format and align each command
            for cmd_name, cmd_help in formatted_commands:
                if not cmd_help:
                    new_help.append(f"{INDENT}{style(cmd_name, fg='green', bold=True)}")
                    continue

                # Wrap the help text
                help_parts = wrap_text(style(cmd_help, fg='white'), available_width)

                # Format the command with aligned help text
                cmd_part = f"{INDENT}{style(cmd_name, fg='green', bold=True)}"
                visual_length = get_visual_length(cmd_part)
                padding_needed = description_start - visual_length

                # First line with command and start of help
                first_line = f"{cmd_part}{' ' * padding_needed}{help_parts[0]}"

                if len(help_parts) == 1:
                    new_help.append(first_line)
                else:
                    # Add wrapped lines aligned with the first help text
                    help_lines = [first_line]
                    description_padding = ' ' * description_start
                    help_lines.extend(f"{description_padding}{part}" for part in help_parts[1:])
                    new_help.append('\n'.join(help_lines))

        # Add usage hint
        command_path = self.format_command_path(ctx)
        new_help.extend([
            '',
            style('Usage Examples:', fg='bright_yellow', bold=True),
            style('---------------', fg='bright_yellow', dim=True),
            style(f'  $ {command_path} COMMAND --help', fg='bright_black')
        ])

        return '\n'.join(new_help)
