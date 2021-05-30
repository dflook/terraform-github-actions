from http_credential_actions_helper import (
    read_credentials,
    Credential,
    read_attributes,
    write_attributes,
    split_path,
    git_credential
)


def test_read_credentials():
    input = '''

nonsense
example.com=dflook:mypassword
 github.com/dflook/terraform-github-actions.git=dflook-actions:anotherpassword

github.com/dflook=dflook:secretpassword    
github.com=graham:abcd

almost/=        user   :  pass

'''

    expected_credentials = [
        Credential('example.com', [], 'dflook', 'mypassword'),
        Credential('github.com', ['dflook', 'terraform-github-actions.git'], 'dflook-actions', 'anotherpassword'),
        Credential('github.com', ['dflook'], 'dflook', 'secretpassword'),
        Credential('github.com', [], 'graham', 'abcd'),
        Credential('almost', [], 'user', 'pass')
    ]

    actual_credentials = list(read_credentials(input))
    assert actual_credentials == expected_credentials

    assert [] == list(read_credentials(''))

def test_read_attributes():
    input = '''
protocol=https
host=example.com
path=abcd.git
username=bob
password=secr3t
    '''

    expected = {
        'protocol': 'https',
        'host': 'example.com',
        'path': 'abcd.git',
        'username': 'bob',
        'password': 'secr3t'
    }

    actual = read_attributes(input)
    assert actual == expected

    assert {} == read_attributes('')

def test_write_attributes():
    input = {
        'protocol': 'https',
        'host': 'example.com',
        'path': 'abcd.git',
        'username': 'bob',
        'somethingelse': 'hello',
        'password': 'secr3t'
    }

    expected = '''
protocol=https
host=example.com
path=abcd.git
username=bob
somethingelse=hello
password=secr3t
    '''.strip()

    actual = write_attributes(input)
    assert actual == expected

    assert '' == write_attributes({})

def test_split_path():
    assert [] == split_path(None)
    assert [] == split_path('/')
    assert ['hello'] == split_path('/hello')
    assert ['dflook', 'terraform-github-actions.git'] == split_path('/dflook/terraform-github-actions.git')

def test_get():

    credentials = [
        Credential('example.com', [], 'dflook', 'mypassword'),
        Credential('github.com', ['dflook', 'terraform-github-actions.git'], 'dflook-actions', 'anotherpassword'),
        Credential('github.com', ['dflook'], 'dflook-org', 'secretpassword'),
        Credential('github.com', [], 'graham', 'abcd'),
        Credential('almost', [], 'user', 'pass')
    ]

    def merge(attributes, **kwargs):
        return {**attributes, **kwargs}

    # No path, no username
    attributes = dict(protocol='https', host='example.com')
    assert git_credential('get', attributes, credentials) == merge(attributes, username='dflook', password='mypassword')

    # No path, required username match
    attributes = dict(protocol='https', host='example.com', username='dflook')
    assert git_credential('get', attributes, credentials) == merge(attributes, password='mypassword')

    # No path, required username no match
    attributes = dict(protocol='https', host='example.com', username='sandra')
    assert git_credential('get', attributes, credentials) == attributes

    # partial path, required username no match
    attributes = dict(protocol='https', host='github.com', path='dflook', username='keith')
    assert git_credential('get', attributes, credentials) == attributes

    # full path
    attributes = dict(protocol='https', host='github.com', path='dflook/terraform-github-actions.git')
    assert git_credential('get', attributes, credentials) == merge(attributes, username='dflook-actions', password='anotherpassword')

    # partial path multiple segments
    attributes = dict(protocol='https', host='github.com', path='dflook/terraform-github-actions.git/additional-segment')
    assert git_credential('get', attributes, credentials) == merge(attributes, username='dflook-actions', password='anotherpassword')

    # partial path single segment
    attributes = dict(protocol='https', host='github.com', path='dflook')
    assert git_credential('get', attributes, credentials) == merge(attributes, username='dflook-org', password='secretpassword')

    # no path match
    attributes = dict(protocol='https', host='github.com', path='sausage')
    assert git_credential('get', attributes, credentials) == merge(attributes, username='graham', password='abcd')

    # Cases we don't handle - return attributes unchanged
    attributes = dict(protocol='https', host='example.com', username='dflook', password='mypassword')
    assert git_credential('store', attributes, credentials) == attributes

    attributes = dict(protocol='https', host='example.com')
    assert git_credential('erase', attributes, credentials) == attributes

    attributes = dict(protocol='https', host='example.com')
    assert git_credential('nonsense', attributes, credentials) == attributes

    attributes = dict(protocol='git', host='example.com')
    assert git_credential('get', attributes, credentials) == attributes

    attributes = dict(host='example.com')
    assert git_credential('get', attributes, credentials) == attributes

    attributes = dict(protocol='http')
    assert git_credential('get', attributes, credentials) == attributes
