from github_pr_comment.plan_formatting import format_diff


def test_diff():
    plan = '''
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
  ~ update in-place
  - destroy
-/+ destroy and then create replacement
+/- create replacement and then destroy

Terraform will perform the following actions:

  # aws_s3_object.update will be updated in-place
  ~ resource "aws_s3_object" "update" {
      ~ content                = "hello" -> "update"
        id                     = "test-plan-colours-test-object"
        tags                   = {}
      + version_id             = (known after apply)
        # (10 unchanged attributes hidden)
    }

  # random_string.add[0] will be created
  + resource "random_string" "add" {
      + id          = (known after apply)
      + length      = 3
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + numeric     = true
      + result      = (known after apply)
      + special     = true
      + upper       = true
    }

  # random_string.create_before_delete must be replaced
+/- resource "random_string" "create_before_delete" {
      ~ id          = "BW8p" -> (known after apply)
      ~ length      = 4 -> 3 # forces replacement
      ~ result      = "BW8p" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

  # random_string.delete[0] will be destroyed
  # (because index [0] is out of range for count)
  - resource "random_string" "delete" {
      - id          = "02g" -> null
      - length      = 3 -> null
      - lower       = true -> null
      - min_lower   = 0 -> null
      - min_numeric = 0 -> null
      - min_special = 0 -> null
      - min_upper   = 0 -> null
      - number      = true -> null
      - numeric     = true -> null
      - result      = "02g" -> null
      - special     = true -> null
      - upper       = true -> null
    }

  # random_string.delete_before_create must be replaced
-/+ resource "random_string" "delete_before_create" {
      ~ id          = "S@M" -> (known after apply)
      ~ length      = 3 -> 4 # forces replacement
      ~ result      = "S@M" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

Plan: 3 to add, 1 to change, 3 to destroy.

Changes to Outputs:
  + add    = "hello"
  - delete = "goodbye" -> null
  ~ update = "hello" -> "update"

'''

    expected = '''
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
+   create
!   update in-place
-   destroy
-/+ destroy and then create replacement
+/- create replacement and then destroy

Terraform will perform the following actions:

  # aws_s3_object.update will be updated in-place
!   resource "aws_s3_object" "update" {
!       content                = "hello" -> "update"
        id                     = "test-plan-colours-test-object"
        tags                   = {}
+       version_id             = (known after apply)
#        (10 unchanged attributes hidden)
    }

  # random_string.add[0] will be created
+   resource "random_string" "add" {
+       id          = (known after apply)
+       length      = 3
+       lower       = true
+       min_lower   = 0
+       min_numeric = 0
+       min_special = 0
+       min_upper   = 0
+       number      = true
+       numeric     = true
+       result      = (known after apply)
+       special     = true
+       upper       = true
    }

  # random_string.create_before_delete must be replaced
+/- resource "random_string" "create_before_delete" {
!       id          = "BW8p" -> (known after apply)
!       length      = 4 -> 3 # forces replacement
!       result      = "BW8p" -> (known after apply)
#        (9 unchanged attributes hidden)
    }

  # random_string.delete[0] will be destroyed
  # (because index [0] is out of range for count)
-   resource "random_string" "delete" {
-       id          = "02g" -> null
-       length      = 3 -> null
-       lower       = true -> null
-       min_lower   = 0 -> null
-       min_numeric = 0 -> null
-       min_special = 0 -> null
-       min_upper   = 0 -> null
-       number      = true -> null
-       numeric     = true -> null
-       result      = "02g" -> null
-       special     = true -> null
-       upper       = true -> null
    }

  # random_string.delete_before_create must be replaced
-/+ resource "random_string" "delete_before_create" {
!       id          = "S@M" -> (known after apply)
!       length      = 3 -> 4 # forces replacement
!       result      = "S@M" -> (known after apply)
#        (9 unchanged attributes hidden)
    }

Plan: 3 to add, 1 to change, 3 to destroy.

Changes to Outputs:
+   add    = "hello"
-   delete = "goodbye" -> null
!   update = "hello" -> "update"
'''

    print(format_diff(plan))
    assert format_diff(plan) == expected


def test_heredoc():
    plan = '''
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
  - destroy
-/+ destroy and then create replacement
+/- create replacement and then destroy
  ~ update in-place

Terraform will perform the following actions:

  # random_string.add will be created
  + resource "random_string" "add" {
      + id          = <<EOT
  + create
  - destroy
-/+ destroy and then create replacement
+/- create replacement and then destroy
  ~ update in-place


  # random_string.create_before_delete must be replaced
+/- resource "random_string" "create_before_delete" {
      ~ id          = "83_{" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

  # random_string.delete will be destroyed
  # (because random_string.delete is not in configuration)
  - resource "random_string" "delete" {
      - id          = "t0)" -> null
      - length      = 3 -> null
      - lower       = true -> null
      - min_lower   = 0 -> null
      - min_numeric = 0 -> null
      - min_special = 0 -> null
      - min_upper   = 0 -> null
      - number      = true -> null
      - numeric     = true -> null
      - result      = "t0)" -> null
      - special     = true -> null
      - upper       = true -> null
    }

  # random_string.delete_before_create must be replaced
-/+ resource "random_string" "delete_before_create" {
      ~ id          = "zBS?I" -> (known after apply)
      ~ length      = 5 -> 2 # forces replacement
        # (9 unchanged attributes hidden)
    }

  # aws_cloudwatch_log_group.health will be updated in-place
  ~ resource "aws_cloudwatch_log_group" "health" {
        id                = "/aws/events/health"
      ~ retention_in_days = 180 -> 150
      + skip_destroy      = false
        # (3 unchanged attributes hidden)
    }

EOT
    }

Plan: 3 to add, 1 to change, 3 to destroy.
'''

    expected = '''
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
+   create
-   destroy
-/+ destroy and then create replacement
+/- create replacement and then destroy
!   update in-place

Terraform will perform the following actions:

  # random_string.add will be created
+   resource "random_string" "add" {
+       id          = <<EOT
  + create
  - destroy
-/+ destroy and then create replacement
+/- create replacement and then destroy
  ~ update in-place


  # random_string.create_before_delete must be replaced
+/- resource "random_string" "create_before_delete" {
      ~ id          = "83_{" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

  # random_string.delete will be destroyed
  # (because random_string.delete is not in configuration)
  - resource "random_string" "delete" {
      - id          = "t0)" -> null
      - length      = 3 -> null
      - lower       = true -> null
      - min_lower   = 0 -> null
      - min_numeric = 0 -> null
      - min_special = 0 -> null
      - min_upper   = 0 -> null
      - number      = true -> null
      - numeric     = true -> null
      - result      = "t0)" -> null
      - special     = true -> null
      - upper       = true -> null
    }

  # random_string.delete_before_create must be replaced
-/+ resource "random_string" "delete_before_create" {
      ~ id          = "zBS?I" -> (known after apply)
      ~ length      = 5 -> 2 # forces replacement
        # (9 unchanged attributes hidden)
    }

  # aws_cloudwatch_log_group.health will be updated in-place
  ~ resource "aws_cloudwatch_log_group" "health" {
        id                = "/aws/events/health"
      ~ retention_in_days = 180 -> 150
      + skip_destroy      = false
        # (3 unchanged attributes hidden)
    }

EOT
    }

Plan: 3 to add, 1 to change, 3 to destroy.'''

    assert format_diff(plan) == expected