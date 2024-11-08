import json
import os

import click
from click import style


def validate_and_load_service_account_json(service_account_json: str) -> str:
    if not service_account_json.startswith("@"):
        click.echo(style("Error: Service account JSON must be a file path starting with '@'", fg='red'), err=True, color=True)
        exit(1)
    service_account_json_file_path = service_account_json[1:]
    if not os.path.isfile(service_account_json_file_path):
        click.echo(style(f"Error: File '{service_account_json_file_path}' does not exist.", fg='red'), err=True, color=True)
        exit(1)

    try:
        with open(service_account_json_file_path, 'r') as f:
            service_account = json.load(f)
    except json.JSONDecodeError:
        click.echo(style("Error: Malformed service account JSON.", fg='red'), err=True, color=True)
        exit(1)
    except Exception as e:
        click.echo(style(f"Error: {str(e)}", fg='red'), err=True, color=True)
        exit(1)

    # return service_account
    return json.dumps(service_account)
