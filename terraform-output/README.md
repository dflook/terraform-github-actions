# terraform-output action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Retrieve the root-level outputs from a terraform configuration.

## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

* `workspace`

  Terraform workspace to get outputs from

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  Comma separated list of terraform backend config values.

  - Type: string
  - Optional

* `backend_config_file`

  Comma separated list of terraform backend config files to use.
  Paths should be relative to the GitHub Actions workspace

  - Type: string
  - Optional

## Outputs

An action output will be created for each output of the terraform configuration.

For example, with the terraform config:
```hcl
output "service_hostname" {
  value = "example.com"
}
```

Running this action will produce a `service_hostname` output with the value `example.com`.

### Primitive types (string, number, bool)

The values for these types get cast to a string with boolean values being 'true' and 'false'.

### Complex types (list/set/tuple & map/object)

The values for complex types are output as a JSON string. Terraform `list`, `set` & `tuple` types are cast to a JSON array, `map` and `object` types are cast to a JSON object.

These values can be used in a workflow expression by using the [fromJSON](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#fromjson) function

## Example usage

### String

This example uses a terraform string output to get a hostname:

```yaml
on: [push]

jobs:
  show_hostname:
    runs-on: ubuntu-latest
    name: Show the terraformed hostname
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Get outputs
        uses: dflook/terraform-output@v1
        id: tf-outputs
        with:
          path: my-terraform-config

      - name: Print the hostname
        run: echo "The terraform version was ${{ steps.tf-outputs.outputs.hostname }}"
```

### Complex output

This example gets information from object and array(object) outputs.

With this terraform config:
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
    name: An example of workflow expressions with terraform output
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Get outputs
        uses: dflook/terraform-output@v1
        id: tf-outputs
        with:
          path: my-terraform-config

      - name: Print VPC
        run: |
          echo "The vpc-id is ${{ fromJson(steps.tf-outputs.outputs.vpc).id }}"
          echo "The subnet-ids are ${{ join(fromJson(steps.tf-outputs.outputs.subnets).*.id) }}"          
```

Which will print to the workflow log:
```
The vpc-id is vpc-01463b6b84e1454ce
The subnet-ids are is subnet-053008016a2c1768c,subnet-07d4ce437c43eba2f,subnet-0a5f8c3a20023b8c0
```
