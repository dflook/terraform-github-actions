from github_actions.api import GithubApi
import os

# This provides a github client for github.com

if os.environ.get('GITHUB_DOT_COM_TOKEN'):
    # We have a specific token for github.com
    token = os.environ.get('GITHUB_DOT_COM_TOKEN')
elif os.environ.get('GITHUB_API_URL', 'https://api.github.com') == 'https://api.github.com':
    # Use the provided GITHUB_TOKEN, if we think it is for github.com and not an enterprise instance
    token = os.environ.get('TERRAFORM_ACTIONS_GITHUB_TOKEN')
else:
    token = None

github = GithubApi('https://api.github.com', token)
