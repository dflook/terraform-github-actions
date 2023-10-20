from github_actions.api import GithubApi
import os

# This provides a github client for github.com
# It will use a provided token, if we think it is for github.com and not an enterprise instance

if os.environ.get('GITHUB_API_URL', 'https://api.github.com') == 'https://api.github.com':
    token = os.environ.get('TERRAFORM_ACTIONS_GITHUB_TOKEN')
else:
    token = None

github = GithubApi('https://api.github.com', token)
