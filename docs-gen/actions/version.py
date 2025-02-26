import dataclasses

from action import Action, Tool
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.path import path
from inputs.workspace import workspace
from outputs.provider_versions import provider_versions
from outputs.terraform import terraform
from outputs.tofu import tofu

backend_reason = '''
This will be used to fetch the $ProductName version set in the cloud workspace if using the `remote` backend.
For other backend types, this is used to fetch the version that most recently wrote to the $ProductName state.
'''

def description(tool: Tool) -> str:
    if tool.ProductName == 'Terraform':
        return '''
            This action determines the $ProductName and provider versions to use for the root module.
        
            The best way to specify the version is using a [`required_version`]($RequiredVersionUrl) constraint.
        
            The version to use is discovered from the first of:
            1. The version set in the cloud workspace if the module uses a `remote` backend or `cloud` configuration, and the remote workspace exists.
            2. A [`required_version`]($RequiredVersionUrl)
               constraint in the $ProductName configuration. If the constraint is range, the latest matching version is used.
            3. A [tfswitch](https://warrensbox.github.io/terraform-switcher/) `.tfswitchrc` file in the module path
            4. A [tfenv](https://github.com/tfutils/tfenv) `.terraform-version` file in the module path
            5. An [asdf](https://asdf-vm.com/) `.tool-versions` file in the module path or any parent path
            6. A `TERRAFORM_VERSION` environment variable containing a [version constraint](https://www.terraform.io/language/expressions/version-constraints). If the constraint allows multiple versions, the latest matching version is used.
            7. The $ProductName version that created the current state file (best effort).
            8. The latest $ProductName version
        
            The version of $ProductName and all required providers will be output to the workflow log.
        
            Other $ToolName actions automatically determine the $ProductName version
            in the same way. You only need to run this action if you want to use the
            outputs yourself.
            '''
    else:
        return '''
            This action determines the $ProductName and provider versions to use for the root module.
            
            The best way to specify the version is using a [`required_version`]($RequiredVersionUrl) constraint.
            
            The version to use is discovered from the first of:
            1. The version set in the cloud workspace if the module uses a `remote` backend or `cloud` configuration, and the remote workspace exists.
            2. A [`required_version`]($RequiredVersionUrl)
               constraint in the $ProductName configuration. If the constraint is range, the latest matching version is used.
            3. A [tfswitch](https://warrensbox.github.io/terraform-switcher/) `.tfswitchrc` file in the module path
            4. A [tofuenv](https://github.com/tofuutils/tofuenv) `.opentofu-version` file in the module path
            5. A [tfenv](https://github.com/tfutils/tfenv) `.terraform-version` file in the module path
            6. An [asdf](https://asdf-vm.com/) `.tool-versions` file in the module path or any parent path
            7. An `OPENTOFU_VERSION` environment variable containing a [version constraint](https://opentofu.org/docs/language/expressions/version-constraints/). If the constraint allows multiple versions, the latest matching version is used.
            8. A `TERRAFORM_VERSION` environment variable containing a [version constraint](https://opentofu.org/docs/language/expressions/version-constraints/). If the constraint allows multiple versions, the latest matching version is used.
            9. The $ProductName version that created the current state file (best effort).
            10. The latest $ProductName version
            
            The version of $ProductName and all required providers will be output to the workflow log.
            
            Other $ToolName actions automatically determine the $ProductName version
            in the same way. You only need to run this action if you want to use the
            outputs yourself.
            '''

version = Action(
    'version',
    description=description,
    meta_description='Prints $ProductName and providers versions',
    inputs=[
        path,
        dataclasses.replace(workspace, description='The workspace to determine the $ProductName version for.'),
        dataclasses.replace(backend_config, description=backend_config.description + backend_reason),
        dataclasses.replace(backend_config_file, description=backend_config_file.description + backend_reason)
    ],
    outputs=[
        terraform,
        tofu,
        provider_versions
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TERRAFORM_PRE_RUN
    ],
    extra='''
## Example usage

```yaml
on: [push]

jobs:
  required_version:
    runs-on: ubuntu-latest
    name: Print the required $ProductName and provider versions
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Test $ToolName-version
        uses: dflook/$ToolName-version@v1
        id: $ToolName-version
        with:
          path: my-configuration

      - name: Print the version
        run: echo "The version was ${{ steps.$ToolName-version.outputs.$ToolName }}"
        
      - name: Print aws provider version
        run: echo "The aws provider version was ${{ steps.$ToolName-version.outputs.aws }}"        
```
'''
)
