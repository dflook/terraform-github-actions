from action import EnvVar

TERRAFORM_CLOUD_TOKENS = EnvVar(
    name='TERRAFORM_CLOUD_TOKENS',
    description='''
API tokens for cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
These tokens may be used with the `remote` backend and for fetching required modules from the registry.
''',
    example='''
e.g:

```yaml
env:
  TERRAFORM_CLOUD_TOKENS: app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
```

With other registries:

```yaml
env:
  TERRAFORM_CLOUD_TOKENS: |
    app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
    $ToolName.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
```
'''
)
