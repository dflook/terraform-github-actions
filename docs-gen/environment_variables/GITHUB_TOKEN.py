from action import EnvVar

GITHUB_TOKEN = EnvVar(
    name='GITHUB_TOKEN',
    description='''
The token provided by GitHub Actions can be used - it can be passed by
using the `${{ secrets.GITHUB_TOKEN }}` expression, e.g.

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The token provided by GitHub Actions has default permissions at GitHub's whim. You can see what it is for your repo under the repo settings.

The minimum permissions are `pull-requests: write`.
It will also likely need `contents: read` so the job can checkout the repo.

You can also use any other App token that has `pull-requests: write` permission.

You can use a fine-grained Personal Access Token which has repository permissions:
- Read access to metadata
- Read and Write access to pull requests

You can also use a classic Personal Access Token which has the `repo` scope.
'''
)
