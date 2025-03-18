from action import EnvVar

TERRAFORM_PRE_RUN = EnvVar(
    name='TERRAFORM_PRE_RUN',
    description='''
A set of commands that will be ran prior to `$ToolName init`. This can be used to customise the environment before running $ProductName.
  
The runtime environment for these actions is subject to change in minor version releases. If using this environment variable, specify the minor version of the action to use.
  
The runtime image is currently based on `debian:bullseye`, with the command run using `bash -xeo pipefail`.

For example:

```yaml
env:
  TERRAFORM_PRE_RUN: |
    # Install latest Azure CLI
    curl -skL https://aka.ms/InstallAzureCLIDeb | bash
    
    # Install postgres client
    apt-get install -y --no-install-recommends postgresql-client
```
'''
)
