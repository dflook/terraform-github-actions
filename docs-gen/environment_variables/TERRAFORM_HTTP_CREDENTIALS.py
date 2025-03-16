from action import EnvVar

TERRAFORM_HTTP_CREDENTIALS = EnvVar(
    name='TERRAFORM_HTTP_CREDENTIALS',
    description='''
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
'''
)
