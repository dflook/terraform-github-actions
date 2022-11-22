from terraform.hcl import loads
from terraform.module import get_sensitive_variables


def test_get_sensitive_variables():
    module = loads('''
variable hello {
    type = string
}

variable not_secret {
    type = string
    sensitive = false
}

variable secret {
    type = string
    sensitive = true
}

variable super_secret {
    type = string
    sensitive = true
}

''')

    assert get_sensitive_variables(module) == ['secret', 'super_secret']
