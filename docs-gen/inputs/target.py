from action import Input

target = Input(
    name='target',
    type='string',
    description='''
List of resources to target, one per line.
The plan will be limited to these resources and their dependencies.
''',
    example = '''
```yaml
with:
  target: |
    kubernetes_secret.tls_cert_public
    kubernetes_secret.tls_cert_private
```
''',
    default='',
    required=False
)
