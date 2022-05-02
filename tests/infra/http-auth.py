import base64
import os

unauth = {
    'statusCode': 401,
    'headers': {
        'www-authenticate': 'Basic realm="terraform-module"'
    },
    'body': 'Please authenticate'
}


def lambda_handler(event, context):
    print(event)

    if 'authorization' not in event['headers']:
        return unauth

    encoded = event['headers']['authorization'][len('Basic '):]
    decoded = base64.b64decode(encoded)
    separated = decoded.decode().split(':', maxsplit=1)
    username = separated[0]
    password = separated[1]

    if username != os.environ['USERNAME'] or password != os.environ['PASSWORD']:
        return unauth

    return {
        'statusCode': 200,
        'body': '<html><head><meta name="terraform-get" content="git::https://github.com/dflook/terraform-github-actions.git//tests/workflows/test-http/test-module" />',
        'headers': {
            'content-type': 'text/html'
        }
    }
