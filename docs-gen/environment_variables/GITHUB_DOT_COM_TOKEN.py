from action import EnvVar

GITHUB_DOT_COM_TOKEN = EnvVar(
    name='GITHUB_DOT_COM_TOKEN',
    description='''
This is used to specify a token for GitHub.com when the action is running on a GitHub Enterprise instance.
This is only used for downloading OpenTofu binaries from GitHub.com.
If this is not set, an unauthenticated request will be made to GitHub.com to download the binary, which may be rate limited.
'''
)
