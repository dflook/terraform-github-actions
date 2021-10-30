from github_pr_comment import format_body, ActionInputs, create_summary

plan = '''An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.'''


def action_inputs(*,
                  path='/test/terraform',
                  workspace='default',
                  backend_config='',
                  backend_config_file='',
                  variables='',
                  var='',
                  var_file='',
                  label='',
                  target='',
                  replace=''
                  ) -> ActionInputs:
    return ActionInputs(
        INPUT_WORKSPACE=workspace,
        INPUT_PATH=path,
        INPUT_BACKEND_CONFIG=backend_config,
        INPUT_BACKEND_CONFIG_FILE=backend_config_file,
        INPUT_VARIABLES=variables,
        INPUT_VAR=var,
        INPUT_VAR_FILE=var_file,
        INPUT_LABEL=label,
        INPUT_ADD_GITHUB_COMMENT='true',
        INPUT_TARGET=target,
        INPUT_REPLACE=replace
    )


def test_path_only():
    inputs = action_inputs(
        path='/test/terraform'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_nondefault_workspace():
    inputs = action_inputs(
        path='/test/terraform',
        workspace='myworkspace'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__ in the __myworkspace__ workspace
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_variables_single_line():
    inputs = action_inputs(
        path='/test/terraform',
        variables='var1="value"'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With variables: `var1="value"`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_variables_multi_line():
    inputs = action_inputs(
        path='/test/terraform',
        variables='''var1="value"
var2="value2"'''
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__<details><summary>With variables</summary>

```hcl
var1="value"
var2="value2"
```
</details>

<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_var():
    inputs = action_inputs(
        path='/test/terraform',
        var='var1=value'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With vars: `var1=value`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_var_file():
    inputs = action_inputs(
        path='/test/terraform',
        var_file='vars.tf'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With var files: `vars.tf`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_backend_config():
    inputs = action_inputs(
        path='/test/terraform',
        backend_config='bucket=test,key=backend'
    )
    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_backend_config_bad_words():
    inputs = action_inputs(
        path='/test/terraform',
        backend_config='bucket=test,password=secret,key=backend,token=secret'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()

def test_target():
    inputs = action_inputs(
        path='/test/terraform',
        target='''kubernetes_secret.tls_cert_public[0]
kubernetes_secret.tls_cert_private'''
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
Targeting resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()

def test_replace():
    inputs = action_inputs(
        path='/test/terraform',
        replace='''kubernetes_secret.tls_cert_public[0]
kubernetes_secret.tls_cert_private'''
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
Replacing resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()

def test_backend_config_file():
    inputs = action_inputs(
        path='/test/terraform',
        backend_config_file='backend.tf'
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__
With backend config files: `backend.tf`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_all():
    inputs = action_inputs(
        path='/test/terraform',
        workspace='test',
        var='myvar=hello',
        var_file='vars.tf',
        backend_config='bucket=mybucket,password=secret',
        backend_config_file='backend.tf',
        target = '''kubernetes_secret.tls_cert_public[0]
kubernetes_secret.tls_cert_private''',
        replace='''kubernetes_secret.tls_cert_public[0]
kubernetes_secret.tls_cert_private'''
    )

    status = 'Testing'

    expected = '''Terraform plan in __/test/terraform__ in the __test__ workspace
Targeting resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
Replacing resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
With backend config: `bucket=mybucket`
With backend config files: `backend.tf`
With vars: `myvar=hello`
With var files: `vars.tf`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_label():
    inputs = action_inputs(
        path='/test/terraform',
        workspace='test',
        var='myvar=hello',
        var_file='vars.tf',
        backend_config='bucket=mybucket,password=secret',
        backend_config_file='backend.tf',
        label='test_label'
    )

    status = 'Testing'

    expected = '''Terraform plan for __test_label__
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    assert format_body(inputs, plan, status, 10).splitlines() == expected.splitlines()


def test_summary_plan_11():
    plan = '''An execution plan has been generated and is shown below.
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

    assert create_summary(plan) == expected


def test_summary_plan_12():
    plan = '''An execution plan has been generated and is shown below.
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

    assert create_summary(plan) == expected


def test_summary_plan_14():
    plan = '''An execution plan has been generated and is shown below.
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

    assert create_summary(plan) == expected


def test_summary_error_11():
    plan = """
Error: random_string.my_string: length: cannot parse '' as int: strconv.ParseInt: parsing "ten": invalid syntax

"""
    expected = "Error: random_string.my_string: length: cannot parse '' as int: strconv.ParseInt: parsing \"ten\": invalid syntax"

    assert create_summary(plan) == expected


def test_summary_error_12():
    plan = """
Error: Incorrect attribute value type

  on main.tf line 2, in resource "random_string" "my_string":
   2:   length      = "ten"

Inappropriate value for attribute "length": a number is required.
"""

    expected = "Error: Incorrect attribute value type"
    assert create_summary(plan) == expected


def test_summary_no_change_11():
    plan = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed.
"""

    expected = "No changes. Infrastructure is up-to-date."
    assert create_summary(plan) == expected


def test_summary_no_change_14():
    plan = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed.
"""

    expected = "No changes. Infrastructure is up-to-date."
    assert create_summary(plan) == expected


def test_summary_output_only_change_14():
    plan = """An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:

Terraform will perform the following actions:

Plan: 0 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + hello = "world"

"""

    expected = "Plan: 0 to add, 0 to change, 0 to destroy. Changes to Outputs."
    assert create_summary(plan) == expected


def test_summary_unknown():
    plan = """
This is not anything like terraform output we know. We don't want to generate a summary for this.
"""
    assert create_summary(plan) is None
