terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "test-unlock-state"
    region = "eu-west-2"
    dynamodb_table = "terraform-github-actions"
  }

  required_providers {
    null = {
      source = "hashicorp/null"
      version = "3.2.1"
    }
  }

  required_version = "~> 1.3.6"
}

resource "null_resource" "lock" {
  count = var.lock ? 1 : 0

  triggers = {
    always = timestamp()
  }

  provisioner "local-exec" {
    command = "pkill -9 --session 0 --exact terraform"
  }
}

variable "lock" {
  type    = bool
  default = false
}
