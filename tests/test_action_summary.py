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
        'import': 0
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
        'import': 5
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
        'import': 0
    }

