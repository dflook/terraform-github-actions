import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.parallelism import parallelism
from inputs.path import path
from inputs.var_file import var_file
from inputs.variables import variables
from inputs.workspace import workspace
from inputs.target import target
from inputs.exclude import exclude
from outputs.failure_reason import failure_reason
from outputs.lock_info import lock_info
from outputs.run_id import run_id

refresh = Action(
    'refresh',
    '''
This actions runs a $ProductName apply operation in refresh-only mode.
This will synchronise the $ProductName state with the actual resources, but will not make any changes to the resources.
''',
    meta_description='Refresh $ProductName state',
    inputs=[
        dataclasses.replace(path, description="Path to the $ProductName root module to refresh state for"),
        dataclasses.replace(workspace, description="$ProductName workspace to run the refresh state in"),
        variables,
        var_file,
        backend_config,
        backend_config_file,
        dataclasses.replace(target, description='''
List of resources to target, one per line.
The refresh will be limited to these resources and their dependencies.
'''),
        dataclasses.replace(exclude, description='''
List of resources to exclude from the refresh operation, one per line.
The refresh will include all resources except the specified ones and their dependencies.

Requires OpenTofu 1.9+.
'''),
        parallelism
    ],
    outputs=[
        dataclasses.replace(failure_reason, description='''
  When the job outcome is `failure`, this output may be set. The value may be one of:

  - `refresh-failed` - The $ProductName apply operation failed.
  - `state-locked` - The Terraform state lock could not be obtained because it was already locked.

  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run steps.
        '''
        ),
        lock_info,
        run_id
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TERRAFORM_PRE_RUN,
    ]
)
