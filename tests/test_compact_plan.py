from compact_plan import compact_plan


def test_plan_11():
    input = """Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.


------------------------------------------------------------------------

An execution plan has been generated and is shown below.
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
"""

    expected_output = """An execution plan has been generated and is shown below.
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
Plan: 1 to add, 0 to change, 0 to destroy."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_12():
    input = """Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.


------------------------------------------------------------------------

An execution plan has been generated and is shown below.
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
"""

    expected_output = """An execution plan has been generated and is shown below.
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

Plan: 1 to add, 0 to change, 0 to destroy."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_14():
    input = """
An execution plan has been generated and is shown below.
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
"""

    expected_output = """An execution plan has been generated and is shown below.
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
  + s = "string\""""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_error_11():
    input = """
Error: random_string.my_string: length: cannot parse '' as int: strconv.ParseInt: parsing "ten": invalid syntax

"""

    expected_output = """Error: random_string.my_string: length: cannot parse '' as int: strconv.ParseInt: parsing "ten": invalid syntax
"""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_error_12():
    input = """
Error: Incorrect attribute value type

  on main.tf line 2, in resource "random_string" "my_string":
   2:   length      = "ten"

Inappropriate value for attribute "length": a number is required.
"""

    expected_output = """Error: Incorrect attribute value type

  on main.tf line 2, in resource "random_string" "my_string":
   2:   length      = "ten"

Inappropriate value for attribute "length": a number is required."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_no_change_11():
    input = """Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.


------------------------------------------------------------------------

No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed.
"""

    expected_output = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_no_change_14():
    input = """
No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed.
"""

    expected_output = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your
configuration and real physical resources that exist. As a result, no
actions need to be performed."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_no_output():
    input = """
This is not anything like terraform output we know. We want this to be output unchanged.
This should protect against the output changing again.
"""

    expected_output = """
This is not anything like terraform output we know. We want this to be output unchanged.
This should protect against the output changing again."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

