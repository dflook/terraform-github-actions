from github_pr_comment.cmp import remove_unchanged_attributes, remove_warnings


def test_remove_unchanged_attributes():
    plan = '''
        # (32 unchanged attributes hidden)

      ~ scaling_configuration {
          ~ seconds_until_auto_pause = 300 -> 7200
          ~ timeout_action           = "ForceApplyCapacityChange" -> "RollbackCapacityChange"
            # (3 unchanged attributes hidden)
        }
    }    
    '''

    expected = '''~ scaling_configuration {
          ~ seconds_until_auto_pause = 300 -> 7200
          ~ timeout_action           = "ForceApplyCapacityChange" -> "RollbackCapacityChange"
        }
    }'''

    assert remove_unchanged_attributes(plan) == expected

def test_remove_warnings():
    plan = '''
Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # random_string.count[0] will be created
  + resource "random_string" "count" {
      + id          = (known after apply)
      + length      = 5
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + numeric     = true
      + result      = (known after apply)
      + special     = false
      + upper       = true
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + count = (known after apply)

Warning: Resource targeting is in effect

You are creating a plan with the -target option, which means that the result
of this plan may not represent all of the changes requested by the current
configuration.

The -target option is not for routine use, and is provided only for
exceptional situations such as recovering from errors or mistakes, or when
Terraform specifically suggests to use it as part of an error message.  
    '''

    expected = '''
Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # random_string.count[0] will be created
  + resource "random_string" "count" {
      + id          = (known after apply)
      + length      = 5
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + numeric     = true
      + result      = (known after apply)
      + special     = false
      + upper       = true
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + count = (known after apply)
  
    '''

    assert remove_warnings(plan).strip() == expected.strip()


def test_remove_warnings_11():
    plan = '''
Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # random_string.foreach["hello"] must be replaced
-/+ resource "random_string" "foreach" {
      ~ id          = "**********" -> (known after apply)
      ~ length      = 10 -> 6 # forces replacement
      ~ result      = "**********" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.

Changes to Outputs:
  ~ foreach = "dmgAfES6WH" -> (known after apply)
╷
│ Warning: Resource targeting is in effect
│ 
│ You are creating a plan with the -target option, which means that the
│ result of this plan may not represent all of the changes requested by the
│ current configuration.
│ 		
│ The -target option is not for routine use, and is provided only for
│ exceptional situations such as recovering from errors or mistakes, or when
│ Terraform specifically suggests to use it as part of an error message.
╵
    '''

    expected = '''
Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # random_string.foreach["hello"] must be replaced
-/+ resource "random_string" "foreach" {
      ~ id          = "**********" -> (known after apply)
      ~ length      = 10 -> 6 # forces replacement
      ~ result      = "**********" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.

Changes to Outputs:
  ~ foreach = "dmgAfES6WH" -> (known after apply)
    '''

    assert remove_warnings(plan).strip() == expected.strip()
