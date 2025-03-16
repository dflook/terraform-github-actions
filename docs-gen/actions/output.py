import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.path import path
from inputs.workspace import workspace
from outputs.terraform_outputs import terraform_outputs

output = Action(
    'output',
    '''
    Retrieve the root-level outputs from a $ProductName configuration.
    ''',
    inputs=[
        path,
        dataclasses.replace(workspace, description='$ProductName workspace to get outputs from'),
        backend_config,
        backend_config_file,
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TERRAFORM_PRE_RUN
    ],
    outputs=[
        terraform_outputs
    ],
    extra='''
## Example usage

### String

This example uses a $ProductName string output to get a hostname:

```yaml
on: [push]

jobs:
  show_hostname:
    runs-on: ubuntu-latest
    name: Show the hostname
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Get outputs
        uses: dflook/$ToolName-output@v1
        id: tf-outputs
        with:
          path: my-$ToolName-config

      - name: Print the hostname
        run: echo "The hostname is ${{ steps.tf-outputs.outputs.hostname }}"
```

### Complex output

This example gets information from object and array(object) outputs.

With this $ProductName config:

```hcl
output "vpc" {
  value = aws_vpc.test
}
output "subnets" {
  value = [aws_subnet.a, aws_subnet.b, aws_subnet.c]
}
```

We can use the workflow:

```yaml
jobs:
  output_example:
    runs-on: ubuntu-latest
    name: An example of workflow expressions with $ToolName output
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Get outputs
        uses: dflook/$ToolName-output@v1
        id: tf-outputs
        with:
          path: my-$ToolName-config

      - name: Print VPC
        run: |
          echo "The vpc-id is ${{ fromJson(steps.tf-outputs.outputs.vpc).id }}"
          echo "The subnet-ids are ${{ join(fromJson(steps.tf-outputs.outputs.subnets).*.id) }}"          
```

Which will print to the workflow log:

```text
The vpc-id is vpc-01463b6b84e1454ce
The subnet-ids are subnet-053008016a2c1768c,subnet-07d4ce437c43eba2f,subnet-0a5f8c3a20023b8c0
```
'''
)