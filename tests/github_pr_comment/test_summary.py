from github_pr_comment.__main__ import create_summary


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
This is not anything like terraform output we know. We will look at the terraform exit code to see if there were changes
"""
    assert create_summary(plan, True) == 'Plan generated.'
    assert create_summary(plan, False) == 'No changes.'

def test_summary_move_only():
    plan = """Terraform will perform the following actions:

  # random_string.your_string has moved to random_string.my_string
    resource "random_string" "my_string" {
        id          = "Iyh3jLKc"
        length      = 8
        # (8 unchanged attributes hidden)
    }
    
  # random_string.blah_string has moved to random_string.my_string2
    resource "random_string" "my_string2" {
        id          = "Iyh3jLKc"
        length      = 8
        # (8 unchanged attributes hidden)
    }    

Plan: 0 to add, 0 to change, 0 to destroy.
"""

    expected = "Plan: 0 to add, 0 to change, 0 to destroy, 2 to move."

    assert create_summary(plan) == expected
