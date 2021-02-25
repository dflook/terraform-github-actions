import github_pr_comment
from github_pr_comment import TerraformComment

import pytest

def setup_comment(monkeypatch, *,
                  path ='/test/terraform',
                  workspace ='default',
                  backend_config ='',
                  backend_config_file ='',
                  var ='',
                  var_file ='',
                  label ='',
                  ):

    monkeypatch.setenv('INPUT_WORKSPACE', workspace)
    monkeypatch.setenv('INPUT_PATH', path)
    monkeypatch.setattr('github_pr_comment.current_user', lambda: 'github-actions[bot]')
    monkeypatch.setenv('INPUT_BACKEND_CONFIG', backend_config)
    monkeypatch.setenv('INPUT_BACKEND_CONFIG_FILE', backend_config_file)
    monkeypatch.setenv('INPUT_VAR', var)
    monkeypatch.setenv('INPUT_VAR_FILE', var_file)
    monkeypatch.setenv('INPUT_LABEL', label)
    monkeypatch.setenv('INIT_ARGS', '')
    monkeypatch.setenv('PLAN_ARGS', '')


def test_path_only(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_nondefault_workspace(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  workspace='myworkspace'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__ in the __myworkspace__ workspace
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_var(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  var='var1=value'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With vars: `var1=value`
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_var_file(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  var_file='vars.tf'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With var files: `vars.tf`
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_backend_config(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  backend_config='bucket=test,key=backend'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_backend_config_bad_words(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  backend_config='bucket=test,password=secret,key=backend,token=secret'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected


def test_backend_config_file(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  backend_config_file='backend.tf'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With backend config files: `backend.tf`
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_all(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  workspace='test',
                  var='myvar=hello',
                  var_file='vars.tf',
                  backend_config='bucket=mybucket,password=secret',
                  backend_config_file='backend.tf'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__ in the __test__ workspace
With backend config: `bucket=mybucket`
With backend config files: `backend.tf`
With vars: `myvar=hello`
With var files: `vars.tf`
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected


def test_label(monkeypatch):

    setup_comment(monkeypatch,
                  path='/test/terraform',
                  workspace='test',
                  var='myvar=hello',
                  var_file='vars.tf',
                  backend_config='bucket=mybucket,password=secret',
                  backend_config_file='backend.tf',
                  label='test_label'
                  )
    comment = TerraformComment()
    comment.plan = 'Hello, this is my plan'
    comment.status = 'Testing'

    expected = '''Terraform plan for __test_label__
```hcl
Hello, this is my plan
```
Testing'''

    assert comment.body() == expected

def test_summary_plan_11(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = '''An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

+ random_string.my_string
      id:          <computed>
      length:      "11"
      lower:       "true"
      min_lower:   "0"
      min_numeric: "0"
      min_special: "0"
      min_upper:   "0"
      number:      "true"
      result:      <computed>
      special:     "true"
      upper:       "true"
Plan: 1 to add, 0 to change, 0 to destroy.
'''
    expected = 'Plan: 1 to add, 0 to change, 0 to destroy.'

    assert comment.summary() == expected

def test_summary_plan_12(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = '''An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # random_string.my_string will be created
  + resource "random_string" "my_string" {
      + id          = (known after apply)
      + length      = 11
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + result      = (known after apply)
      + special     = true
      + upper       = true
    }

Plan: 1 to add, 0 to change, 0 to destroy.
'''
    expected = 'Plan: 1 to add, 0 to change, 0 to destroy.'

    assert comment.summary() == expected

def test_summary_plan_14(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = '''An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # random_string.my_string will be created
  + resource "random_string" "my_string" {
      + id          = (known after apply)
      + length      = 11
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + result      = (known after apply)
      + special     = true
      + upper       = true
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + s = "string"
'''
    expected = 'Plan: 1 to add, 0 to change, 0 to destroy. Changes to Outputs.'

    assert comment.summary() == expected

def test_summary_error_11(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = """
Error: random_string.my_string: length: cannot parse '' as int: strconv.ParseInt: parsing "ten": invalid syntax

"""
    expected = "Error: random_string.my_string: length: cannot parse '' as int: strconv.ParseInt: parsing \"ten\": invalid syntax"

    assert comment.summary() == expected

def test_summary_error_12(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = """
Error: Incorrect attribute value type

  on main.tf line 2, in resource "random_string" "my_string":
   2:   length      = "ten"

Inappropriate value for attribute "length": a number is required.
"""

    expected = "Error: Incorrect attribute value type"
    assert comment.summary() == expected


def test_summary_no_change_11(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed.
"""

    expected = "No changes. Infrastructure is up-to-date."
    assert comment.summary() == expected

def test_summary_no_change_14(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed.
"""

    expected = "No changes. Infrastructure is up-to-date."
    assert comment.summary() == expected

def test_summary_output_only_change_14(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = """An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:

Terraform will perform the following actions:

Plan: 0 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + hello = "world"

"""

    expected = "Plan: 0 to add, 0 to change, 0 to destroy. Changes to Outputs."
    assert comment.summary() == expected

def test_summary_unknown(monkeypatch):
    setup_comment(monkeypatch,
                  path='/test/terraform',
                  )
    comment = TerraformComment()
    comment.plan = """
This is not anything like terraform output we know. We don't want to generate a summary for this.
"""

    expected = None
    assert comment.summary() == expected

