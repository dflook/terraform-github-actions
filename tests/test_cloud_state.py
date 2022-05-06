from terraform_cloud_state.__main__ import get_run_id, get_cloud_json_plan


def test_get_run_url():
    plan = """
Running plan in the remote backend. Output will stream here. Pressing Ctrl-C
will stop streaming the logs, but will not stop the plan running remotely.

Preparing the remote plan...

To view this run in a browser, visit:
https://app.terraform.io/app/flooktech/github-actions-1-1temp/runs/run-6m9eAyLdeDSrPYqz

Waiting for the plan to start...

Terraform v1.1.6
on linux_amd64
Initializing plugins and modules...

Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # random_id.the_id will be created
  + resource "random_id" "the_id" {
      + b64_std     = (known after apply)
      + b64_url     = (known after apply)
      + byte_length = 5
      + dec         = (known after apply)
      + hex         = (known after apply)
      + id          = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + default        = "default"
  + from_tfvars    = "default"
  + from_variables = "default"

"""

    assert get_run_id(plan) == 'run-6m9eAyLdeDSrPYqz'
