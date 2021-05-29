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

## Environment Variables

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for terraform cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used with the `remote` backend and for fetching required modules from the registry.

  e.g for terraform cloud:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
  ```

  With Terraform Enterprise or other registries:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: |
      app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
      terraform.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_SSH_KEY`

  A SSH private key that terraform will use to fetch git module sources.

  This should be in PEM format.

  For example:
  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_HTTP_CREDENTIALS`

  Credentials that will be used for fetching modules sources with `git::http://`, `git::https://`, `http://` & `https://` schemes.

  Credentials have the format `<host>=<username>:<password>`. Multiple credentials may be specified, one per line.

  Each credential is evaluated in order, and the first matching credentials are used. 

  Credentials that are used by git (`git::http://`, `git::https://`) allow a path after the hostname.
  Paths are ignored by `http://` & `https://` schemes.
  For git module sources, a credential matches if each mentioned path segment is an exact match.

  For example:
  ```yaml
  env:
    TERRAFORM_HTTP_CREDENTIALS: |
      example.com=dflook:${{ secrets.HTTPS_PASSWORD }}
      github.com/dflook/terraform-github-actions.git=dflook-actions:${{ secrets.ACTIONS_PAT }}
      github.com/dflook=dflook:${{ secrets.DFLOOK_PAT }}
      github.com=graham:${{ secrets.GITHUB_PAT }}  
  ```

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
The subnet-ids are subnet-053008016a2c1768c,subnet-07d4ce437c43eba2f,subnet-0a5f8c3a20023b8c0
```
