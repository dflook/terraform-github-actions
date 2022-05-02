import hcl2

from terraform.versions import Constraint
from terraform_version.remote_state import dump_backend_hcl, get_backend_constraints


def test_simple_backend():

    expected_backend = hcl2.loads('''
    terraform {
        backend "s3" {
            bucket = "terraform-github-actions"
            key    = "blah"
            region = "eu-west-2"
        }
    }
''')

    assert expected_backend == hcl2.loads(dump_backend_hcl(expected_backend))

def test_no_backend():
    expected_backend = hcl2.loads('''
        terraform {
            required_version = "1.0.0"
        }
    ''')

    assert dump_backend_hcl(expected_backend).strip() == ''

def test_oss_assume_role():
    expected_backend = hcl2.loads('''
        terraform {
            backend "oss" {
                access_key = "sausage"
                assume_role {
                    role_arn = "asdasd"
                    session_name = "hello"
                }
            }
        }
    ''')

    assert expected_backend == hcl2.loads(dump_backend_hcl(expected_backend))

def test_backend_constraints():

    module = hcl2.loads('''
        terraform {
            backend "oss" {
                access_key = "sausage"
                mystery = true
                assume_role {
                    role_arn = "asdasd"
                    session_name = "hello"
                }
            }
        }
    ''')

    assert get_backend_constraints(module, {}) == [Constraint('>=0.12.2'), Constraint('>=0.12.2'), Constraint('>=0.12.6')]

    module = hcl2.loads('''
        terraform {
            backend "gcs" {
                bucket = "sausage"
                impersonate_service_account = true
                region = "europe-west2"
                unknown = "??"
                path = "hello"
            }
        }
    ''')

    assert get_backend_constraints(module, {}) == [
        Constraint('>=0.9.0'),
        Constraint('>=0.9.0'),
        Constraint('>=0.14.0'),
        Constraint('>=0.11.0'),
        Constraint('<=0.15.3'),
        Constraint('>=0.9.0'),
        Constraint('<=0.14.11')
    ]
