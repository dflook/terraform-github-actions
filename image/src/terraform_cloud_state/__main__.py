import os
import re
import sys
from pathlib import Path
from typing import Optional

from github_actions.commands import output
from terraform.cloud import TerraformCloudApi
from terraform.module import BackendConfig
from terraform.module import load_module, get_remote_backend_config, get_cloud_config


def get_run_id(plan: str) -> Optional[str]:
    if match := re.search(r'https://.*/(?P<workspace>[^/]*)/runs/(?P<run_id>run-.*)$', plan, re.MULTILINE):
        return match[2]


def get_cloud_json_plan(backend_config: BackendConfig, run_id: str) -> bytes:
    terraform_cloud = TerraformCloudApi(backend_config["hostname"], backend_config['token'])
    response = terraform_cloud.get(f'runs/{run_id}/plan/json-output')
    response.raise_for_status()
    return response.content

def remote_run_id():
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: remote-run-id <terraform_plan.txt>\n')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        run_id = get_run_id(f.read())

    if run_id is None:
        sys.stderr.write('run_id not found in plan\n')
        sys.exit(1)

    sys.stdout.write(run_id)

def main():
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: terraform-cloud-state RUN_ID\n')
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

    run_id = sys.argv[1]

    sys.stdout.write(get_cloud_json_plan(backend_config, run_id).decode())
    sys.stdout.write('\n')

if __name__ == '__main__':
    main()
