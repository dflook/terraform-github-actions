from plan_summary.__main__ import summary


def test_summary():
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

    assert summary(plan) == {
        'add': 1,
        'change': 0,
        'destroy': 0,
        'move': 0,
        'import': 0,
        'forget': 0,
        'invoke': 0
    }

def test_summary_import():
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
Plan: 5 to import, 1 to add, 0 to change, 0 to destroy.
'''

    assert summary(plan) == {
        'add': 1,
        'change': 0,
        'destroy': 0,
        'move': 0,
        'import': 5,
        'forget': 0,
        'invoke': 0
    }

def test_summary_remove():
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
Plan: 5 to import, 1 to add, 3 to remove, 0 to change, 0 to destroy.
'''

    assert summary(plan) == {
        'add': 1,
        'change': 0,
        'destroy': 0,
        'move': 0,
        'import': 5,
        'forget': 0,
        'invoke': 0,
        'remove': 3
    }

def test_summary_move():
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

Plan: 4 to add, 8 to change, 1 to destroy.
"""

    actual = summary(plan)
    assert actual == {
        'add': 4,
        'change': 8,
        'destroy': 1,
        'move': 2,
        'import': 0,
        'forget': 0,
        'invoke': 0
    }

def test_summary_forget():
    plan = '''OpenTofu used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  . forget

OpenTofu will perform the following actions:

  # terraform_data.x will be removed from the OpenTofu state but will not be destroyed
  . resource "terraform_data" "x" {
    id     = "c5464233-23a4-f524-e5c8-d28838eb0687"
    input  = "hello"
    output = "hello"
}

Plan: 0 to add, 0 to change, 0 to destroy, 1 to forget.
'''

    assert summary(plan) == {
        'add': 0,
        'change': 0,
        'destroy': 0,
        'move': 0,
        'import': 0,
        'forget': 1,
        'invoke': 0
    }

def test_summary_forget_terraform():
    # Terraform does not include forgotten resources in the summary line,
    # so they are counted from the plan text
    plan = '''Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:

Terraform will perform the following actions:

 # terraform_data.x will no longer be managed by Terraform, but will not be destroyed
 # (destroy = false is set in the configuration)
 . resource "terraform_data" "x" {
        id     = "c5464233-23a4-f524-e5c8-d28838eb0687"
        # (2 unchanged attributes hidden)
    }

 # terraform_data.y will no longer be managed by Terraform, but will not be destroyed
 # (destroy = false is set in the configuration)
 . resource "terraform_data" "y" {
        id     = "0e352811-a659-4933-af31-7e39d3fda849"
        # (2 unchanged attributes hidden)
    }

Plan: 0 to add, 0 to change, 0 to destroy.

Warning: Some objects will no longer be managed by Terraform

If you apply this plan, Terraform will discard its tracking information for
the following objects, but it will not delete them:
 - terraform_data.x
 - terraform_data.y
'''

    assert summary(plan) == {
        'add': 0,
        'change': 0,
        'destroy': 0,
        'move': 0,
        'import': 0,
        'forget': 2,
        'invoke': 0
    }

def test_summary_invoke():
    plan = '''Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # terraform_data.x will be created
  + resource "terraform_data" "x" {
      + id = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy. Actions: 2 to invoke.
'''

    assert summary(plan) == {
        'add': 1,
        'change': 0,
        'destroy': 0,
        'move': 0,
        'import': 0,
        'forget': 0,
        'invoke': 2
    }

