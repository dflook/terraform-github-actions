"""
Manage Terraform Cloud/Enterprise workspaces

Usage:
    terraform-cloud-workspace list
    terraform-cloud-workspace new <WORKSPACE>
    terraform-cloud-workspace delete <WORKSPACE>

For whatever reason, the terraform workspace command needs an initialized backend.
When using the remote backend there may be no workspaces to initialize, so we are a bit stuck.

This directly uses the cloud API to manage workspaces instead.

"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from terraform.cloud import delete_workspace, get_workspaces, new_workspace, CloudException
from terraform.module import load_module, get_remote_backend_config, get_cloud_config


def main() -> None:
    """Entrypoint for terraform-cloud-workspace."""

    if len(sys.argv) <= 1:
        sys.stdout.write(f'{__doc__}\n')
        sys.exit(1)

    module = load_module(Path(os.environ.get('INPUT_PATH', '.')))

    backend_config = get_remote_backend_config(
        module,
        backend_config_files=os.environ.get('INPUT_BACKEND_CONFIG_FILE', ''),
        backend_config_vars=os.environ.get('INPUT_BACKEND_CONFIG', ''),
        cli_config_path=Path('~/.terraformrc'),
    )

    if backend_config is None:
        backend_config = get_cloud_config(
            module,
            cli_config_path=Path('~/.terraformrc'),
        )

    if backend_config is None:
        sys.stdout.write('Current directory doesn\'t use terraform cloud\n')
        sys.exit(1)

    if backend_config.get('token') is None:
        sys.stdout.write(f'No token found for {backend_config["hostname"]}\n')
        sys.exit(1)

    if not backend_config.get('workspaces'):
        sys.stdout.write('No required workspaces option found in backend block\n')
        sys.exit(1)

    if len([k for k in backend_config['workspaces'] if k in ['tags', 'prefix', 'name']]) != 1:
        sys.stdout.write('name or prefix required for remote backend. cloud config requires tags.\n')
        sys.exit(1)

    try:
        if sys.argv[1] == 'list':
            for workspace in get_workspaces(backend_config):
                if 'prefix' in backend_config['workspaces']:
                    sys.stdout.write(workspace['attributes']['name'][len(backend_config['workspaces']['prefix']):])
                else:
                    sys.stdout.write(workspace['attributes']['name'])
                sys.stdout.write('\n')
            sys.exit(0)

        if len(sys.argv) <= 2 or not sys.argv[2]:
            sys.stdout.write(f'{__doc__}\n')
            sys.exit(1)

        workspace_name = sys.argv[2]

        if sys.argv[1] == 'new':
            new_workspace(backend_config, workspace_name)
            sys.stdout.write(f'Created remote workspace {workspace_name}\n')

        elif sys.argv[1] == 'delete':
            delete_workspace(backend_config, sys.argv[2])
            sys.stdout.write(f'Delete remote workspace {workspace_name}\n')

        else:
            sys.stdout.write(f'{__doc__}\n')
            sys.exit(1)

    except CloudException as cloud_exception:
        sys.stderr.write(str(cloud_exception))
        sys.stderr.write('\n')
        sys.exit(1)
