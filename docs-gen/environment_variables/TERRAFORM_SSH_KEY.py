from action import EnvVar

TERRAFORM_SSH_KEY = EnvVar(
    name='TERRAFORM_SSH_KEY',
    description='''
A SSH private key that $ProductName will use to fetch git/mercurial module sources.

This should be in PEM format.

For example:

```yaml
env:
  TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
```
'''
)
