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

def test_plan_15():
    input = """

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
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

    expected_output = """Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
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

def test_plan_refresh_no_changes_11():
    input = """
Refreshing Terraform state in-memory prior to plan...    
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.

random_string.my_string: Refreshing state... (ID: Zl$lcns(v>)

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

def test_plan_refresh_no_changes_14():
    input = """
random_string.my_string: Refreshing state... [id=&)+#Z$b@=b]

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

def test_plan_refresh_no_changes_15():
    input = """
random_string.my_string: Refreshing state... [id=&)+#Z$b@=b]

No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your configuration and the remote system(s). As a result, there are no actions to take.
"""

    expected_output = """No changes. Infrastructure is up-to-date.

This means that Terraform did not detect any differences between your configuration and the remote system(s). As a result, there are no actions to take."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_refresh_no_changes_1():
    input = """
random_string.my_string: Refreshing state... [id=&)+#Z$b@=b]

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
"""

    expected_output = """No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed."""

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output


def test_plan_no_resource_output_only_11():
    input = """
Refreshing Terraform state in-memory prior to plan...
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
actions need to be performed.
    """

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_no_resource_output_only_14():
    input = """
An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:

Terraform will perform the following actions:

Plan: 0 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + t = "hello"
    """

    expected_output = """An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:

Terraform will perform the following actions:

Plan: 0 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + t = "hello"
    """

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_no_resource_output_only_15_4():
    input = """
Changes to Outputs:
  + t = "hello"

You can apply this plan to save these new output values to the Terraform state, without changing any real infrastructure.
    """

    expected_output = """Changes to Outputs:
  + t = "hello"

You can apply this plan to save these new output values to the Terraform state, without changing any real infrastructure.
    """

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_refresh_changes_11():
    input = """
Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.

random_string.my_string: Refreshing state... (ID: <2jMa%O-E$)

------------------------------------------------------------------------

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

-/+ random_string.my_string (new resource required)
      id:          "<2jMa%O-E$" => <computed> (forces new resource)
      length:      "10" => "5" (forces new resource)
      lower:       "true" => "true"
      min_lower:   "0" => "0"
      min_numeric: "0" => "0"
      min_special: "0" => "0"
      min_upper:   "0" => "0"
      number:      "true" => "true"
      result:      "<2jMa%O-E$" => <computed>
      special:     "true" => "true"
      upper:       "true" => "true"
Plan: 1 to add, 0 to change, 1 to destroy.
        """

    expected_output = """An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

-/+ random_string.my_string (new resource required)
      id:          "<2jMa%O-E$" => <computed> (forces new resource)
      length:      "10" => "5" (forces new resource)
      lower:       "true" => "true"
      min_lower:   "0" => "0"
      min_numeric: "0" => "0"
      min_special: "0" => "0"
      min_upper:   "0" => "0"
      number:      "true" => "true"
      result:      "<2jMa%O-E$" => <computed>
      special:     "true" => "true"
      upper:       "true" => "true"
Plan: 1 to add, 0 to change, 1 to destroy.
        """

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_refresh_changes_14():
    input = """
random_string.my_string: Refreshing state... [id=Iyh3jLKc]

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # random_string.my_string must be replaced
-/+ resource "random_string" "my_string" {
      ~ id          = "Iyh3jLKc" -> (known after apply)
      ~ length      = 8 -> 4 # forces replacement
      ~ result      = "Iyh3jLKc" -> (known after apply)
        # (8 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.
        """

    expected_output = """An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # random_string.my_string must be replaced
-/+ resource "random_string" "my_string" {
      ~ id          = "Iyh3jLKc" -> (known after apply)
      ~ length      = 8 -> 4 # forces replacement
      ~ result      = "Iyh3jLKc" -> (known after apply)
        # (8 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.
        """

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_refresh_changes_15():
    input = """
random_string.my_string: Refreshing state... [id=Iyh3jLKc]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # random_string.my_string must be replaced
-/+ resource "random_string" "my_string" {
      ~ id          = "Iyh3jLKc" -> (known after apply)
      ~ length      = 8 -> 4 # forces replacement
      ~ result      = "Iyh3jLKc" -> (known after apply)
        # (8 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.
        """

    expected_output = """Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # random_string.my_string must be replaced
-/+ resource "random_string" "my_string" {
      ~ id          = "Iyh3jLKc" -> (known after apply)
      ~ length      = 8 -> 4 # forces replacement
      ~ result      = "Iyh3jLKc" -> (known after apply)
        # (8 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.
        """

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output

def test_plan_move_only():
    input = """
random_string.my_string: Refreshing state... [id=Iyh3jLKc]

Terraform will perform the following actions:

  # random_string.your_string has moved to random_string.my_string
    resource "random_string" "my_string" {
        id          = "Iyh3jLKc"
        length      = 8
        # (8 unchanged attributes hidden)
    }

Plan: 0 to add, 0 to change, 0 to destroy.
        """

    expected_output = """Terraform will perform the following actions:

  # random_string.your_string has moved to random_string.my_string
    resource "random_string" "my_string" {
        id          = "Iyh3jLKc"
        length      = 8
        # (8 unchanged attributes hidden)
    }

Plan: 0 to add, 0 to change, 0 to destroy.
        """

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

def test_state_lock_12():
    input = """Acquiring state lock. This may take a few moments...
Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.

Acquiring state lock. This may take a few moments...
Releasing state lock. This may take a few moments...

------------------------------------------------------------------------
Acquiring state lock. This may take a few moments...

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create
Acquiring state lock. This may take a few moments...

Terraform will perform the following actions:

  # random_string.my_string will be created
  + resource "random_string" "my_string" {
      + id          = (known after apply)
      + length      = 11
      + lower       = true
Acquiring state lock. This may take a few moments...
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + result      = (known after apply)
      + special     = true
      + upper       = true
Releasing state lock. This may take a few moments...
    }

Plan: 1 to add, 0 to change, 0 to destroy.
Releasing state lock. This may take a few moments...
Releasing state lock. This may take a few moments...
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

def test_plan_no_changes_1_4():
    # yes really... this is what terraform 1.4 outputs if there are no changes and there are outputs defined
    input = """random_string.my_string: Refreshing state... [id=t[oR@lj(UQZ]
"""

    expected_output = input.strip()

    output = '\n'.join(compact_plan(input.splitlines()))
    assert output == expected_output