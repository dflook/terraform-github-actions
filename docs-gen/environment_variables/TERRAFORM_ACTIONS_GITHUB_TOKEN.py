from action import EnvVar

TERRAFORM_ACTIONS_GITHUB_TOKEN = EnvVar(
    name='TERRAFORM_ACTIONS_GITHUB_TOKEN',
    description='''
When this is set it is used instead of `GITHUB_TOKEN`, with the same behaviour.
The GitHub $ProductName provider also uses the `GITHUB_TOKEN` environment variable,
so this can be used to make the github actions and the $ProductName provider use different tokens.
'''
)
