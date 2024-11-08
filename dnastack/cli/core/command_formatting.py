from typing import List

import click
from click import Command, Option, style, Parameter, Argument

from dnastack.cli.core.constants import *
from dnastack.cli.core.formatting_utils import get_visual_length, wrap_text


class FormattedHelpCommand(Command):
    """Command class that provides formatted and colored help output."""
    def __init__(self, *args, **kwargs):
        kwargs['context_settings'] = {
            'help_option_names': ['-h', '--help'],  # Add all help variants
            'token_normalize_func': lambda x: x.lower(),    # Make help flags case-insensitive
        }
        super().__init__(*args, **kwargs)
        # Store help texts for arguments
        self.argument_help_texts = {}

    def store_argument_help(self, arg_name: str, help_text: str):
        """Store help text for an argument"""
        self.argument_help_texts[arg_name] = help_text

    def get_help(self, ctx: click.Context) -> str:
        """Override get_help to customize and colorize the help output."""
        # Extract the command description
        description = self.help or ''

        # Organize parameters
        positional_args: List[Parameter] = []
        required_options: List[Parameter] = []
        optional_options: List[Parameter] = []

        for param in self.params:
            if isinstance(param, Argument):
                positional_args.append(param)
            elif isinstance(param, Option):
                if param.required:
                    required_options.append(param)
                else:
                    optional_options.append(param)

        # Build the command path without the full executable path
        ctx_path_parts = ctx.command_path.split()
        if ctx_path_parts[0].endswith('__main__.py'):
            command_parts = [APP_NAME] + ctx_path_parts[1:]
        else:
            command_parts = ctx_path_parts

        # Build the new help text starting with Usage
        new_help = [
            style("Usage:", fg='bright_white', bold=True) + " " +
            style(' '.join(command_parts), fg='bright_white')
        ]

        # Add arguments to usage line
        usage_parts = []
        if positional_args:
            usage_parts.extend(style(param.name.upper(), fg='bright_yellow') for param in positional_args)
        if required_options:
            usage_parts.append(style("REQUIRED_OPTIONS", fg='bright_red'))
        if optional_options:
            usage_parts.append(style("[OPTIONS]", fg='bright_blue'))

        if usage_parts:
            new_help[0] += " " + " ".join(usage_parts)

        # Add description and rest of the help text
        if description:
            new_help.extend([
                '',
                style(description, fg='bright_white')
            ])

        # Rest of the method remains the same...
        if positional_args:
            new_help.extend([
                '',
                style('Positional Arguments:', fg='bright_yellow', bold=True),
                style('--------------------', fg='bright_yellow', dim=True)
            ])
            # Sort positional arguments: required first, then optional
            sorted_positional_args = sorted(
                positional_args,
                key=lambda param: (
                    not getattr(param, 'required', True),  # Required args first (True sorts before False)
                    param.name  # Then alphabetically by name
                )
            )
            for param in sorted_positional_args:
                new_help.append(self._format_argument(param))

        if required_options:
            new_help.extend([
                '',
                style('Required Options:', fg='bright_red', bold=True),
                style('----------------', fg='bright_red', dim=True)
            ])
            for param in required_options:
                new_help.append(self._format_option(param, required=True))

        if optional_options:
            new_help.extend([
                '',
                style('Optional Options:', fg='bright_blue', bold=True),
                style('----------------', fg='bright_blue', dim=True)
            ])
            for param in optional_options:
                new_help.append(self._format_option(param, required=False))

        new_help.extend([
            '',
            style('Examples:', fg='bright_green', bold=True),
            style('--------', fg='bright_green', dim=True),
            self._format_examples(positional_args, required_options)
        ])

        return '\n'.join(new_help)

    def _format_argument(self, param: Argument) -> str:
        """Format a positional argument for the help output."""
        name = style(param.name.upper(), fg='bright_yellow', bold=True)

        # Get help text from stored help texts
        help_text = self.argument_help_texts.get(param.name, '')
        help_str = style(help_text, fg='white')

        # Add required indicator for positional arguments
        if getattr(param, 'required', True):  # Positional args are required by default
            required_indicator = style(' (Required)', fg='bright_red', bold=True)
            help_str += required_indicator

        # Add multiple indicator
        if getattr(param, 'nargs', 1) < 0 or getattr(param, 'multiple', False):
            multiple_indicator = style(' (Multiple values accepted)', fg='bright_blue')
            help_str += multiple_indicator

        if param.default is not None and not param.required:
            default_str = style(f' (default: {param.default})', fg='bright_black', dim=True)
            help_str += default_str

        # Calculate available width for description text
        description_start = len(INDENT) + OPTION_WIDTH + OPTION_PADDING
        available_width = TOTAL_WIDTH - description_start

        # Wrap and align the help text
        help_parts = wrap_text(help_str, available_width)
        return self._align_text(name, help_parts, description_start)

    def _format_option(self, param: Option, required: bool = False) -> str:
        """Format an option for the help output."""
        opts = []
        for opt in param.opts:
            opts.append(opt)
        for opt in param.secondary_opts:
            opts.append(opt)

        opt_str = ', '.join(opts)
        help_str = param.help or ''
        default = param.default if param.default is not None and not param.required else None

        colored_opt_str = style(opt_str, fg='yellow', bold=True)

        # Add required indicator
        if required:
            help_str = style(help_str, fg='white')
            required_indicator = style(' (Required)', fg='bright_red', bold=True)
            help_str += required_indicator
        else:
            help_str = style(help_str, fg='white')

        # Add multiple indicator for options
        if getattr(param, 'multiple', False):
            multiple_indicator = style(' (Multiple values accepted)', fg='bright_blue')
            help_str += multiple_indicator

        # Add choices if available
        if hasattr(param, 'type') and hasattr(param.type, 'choices') and param.type.choices:
            choices_str = style(f" (Choices: {', '.join(param.type.choices)})", fg='bright_green')
            help_str += choices_str

        # Add default value
        if default is not None and str(default) != '':
            default_str = style(f' (default: ', fg='white', dim=True) + \
                          style(str(default), fg='bright_white', dim=False) + \
                          style(')', fg='white', dim=True)
            help_str += default_str

        # Calculate available width for description text
        description_start = len(INDENT) + OPTION_WIDTH + OPTION_PADDING
        available_width = TOTAL_WIDTH - description_start

        # Build the help text
        help_parts = wrap_text(help_str, available_width)
        return self._align_text(colored_opt_str, help_parts, description_start)



    def _align_text(self, opt_str: str, help_parts: List[str], description_start: int) -> str:
        """Align option and help text parts."""
        option_part = f"{INDENT}{opt_str}"
        visual_length = get_visual_length(option_part)
        padding_needed = description_start - visual_length

        first_line = f"{option_part}{' ' * padding_needed}{help_parts[0]}"

        if len(help_parts) == 1:
            return first_line + "\n"

        result = [first_line]
        description_padding = ' ' * description_start
        result.extend(f"{description_padding}{part}" for part in help_parts[1:])
        return '\n'.join(result) + '\n'

    def _format_examples(self, positional_args: List[Parameter], required_options: List[Parameter]) -> str:
        """
        Create colored example usage section with full command path.
        Uses Click's context to determine the full command path.
        """
        # Get the full command path from context
        ctx = click.get_current_context()
        command_path_parts = []
        current_ctx = ctx

        # Build the command path by walking up the context chain
        while current_ctx.parent is not None:
            if current_ctx.command.name != '':  # Skip empty command names
                command_path_parts.insert(0, current_ctx.command.name)
            current_ctx = current_ctx.parent

        # Create the styled full command path
        command_path = ' '.join([
            style(part, fg='green', bold=True)
            for part in command_path_parts
        ])

        # Build example with required positional args only
        positional_part = ' '.join(
            style(f"{param.name.upper()}{' [...]' if getattr(param, 'multiple', False) else ''}", fg='bright_yellow')
            for param in positional_args
            if getattr(param, 'required', True)  # Arguments are required by default
        )

        # Build example with required options
        required_part = ' '.join(
            style(f"--{param.name.replace('_', '-')} VALUE{' [...]' if getattr(param, 'multiple', False) else ''}", fg='yellow')
            for param in required_options
        )

        # Combine parts
        parts = [command_path]
        if positional_part:
            parts.append(positional_part)
        if required_part:
            parts.append(required_part)

        # Create examples with the full command path
        examples = []

        # Full example with all required parameters
        if len(parts) > 1:  # If we have any required params
            examples.append(f"  $ {APP_NAME} {' '.join(parts)}")
        else:
            examples.append(f"  $ {APP_NAME} {command_path} [OPTIONS]")

        # Help example
        examples.append(f"  $ {APP_NAME} {command_path} --help")

        return style('\n'.join(examples), fg='bright_black')

