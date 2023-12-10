from github_pr_comment.plan_formatting import format_diff


def test_diff():
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
      + id          = (known after apply)
    }

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

Plan: 3 to add, 1 to change, 3 to destroy.

Changes to Outputs:
  ~ dnssec = "test" -> "hello"
  + new    = "hello"
  - old    = "hello" -> null

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
+       id          = (known after apply)
    }

  # random_string.create_before_delete must be replaced
+/- resource "random_string" "create_before_delete" {
!       id          = "83_{" -> (known after apply)
#        (9 unchanged attributes hidden)
    }

  # random_string.delete will be destroyed
#  (because random_string.delete is not in configuration)
-   resource "random_string" "delete" {
-       id          = "t0)" -> null
-       length      = 3 -> null
-       lower       = true -> null
-       min_lower   = 0 -> null
-       min_numeric = 0 -> null
-       min_special = 0 -> null
-       min_upper   = 0 -> null
-       number      = true -> null
-       numeric     = true -> null
-       result      = "t0)" -> null
-       special     = true -> null
-       upper       = true -> null
    }

  # random_string.delete_before_create must be replaced
-/+ resource "random_string" "delete_before_create" {
!       id          = "zBS?I" -> (known after apply)
!       length      = 5 -> 2 # forces replacement
#        (9 unchanged attributes hidden)
    }

  # aws_cloudwatch_log_group.health will be updated in-place
!   resource "aws_cloudwatch_log_group" "health" {
        id                = "/aws/events/health"
!       retention_in_days = 180 -> 150
+       skip_destroy      = false
#        (3 unchanged attributes hidden)
    }

Plan: 3 to add, 1 to change, 3 to destroy.

Changes to Outputs:
!   dnssec = "test" -> "hello"
+   new    = "hello"
-   old    = "hello" -> null
'''

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

Plan: 3 to add, 1 to change, 3 to destroy.'''

    assert format_diff(plan) == expected