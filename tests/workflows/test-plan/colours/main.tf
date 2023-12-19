terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "test-plan-colours-2"
    region = "eu-west-2"
  }
  required_version = "~> 1.5.0"
}

provider "aws" {
    region = "eu-west-2"
}

variable "diff" {
  default = false
}

resource "random_string" "add" {
  count = var.diff ? 1 : 0
  length = 3
}

resource "random_string" "delete" {
  count = var.diff ? 0 : 1
  length = 3
}

resource "random_string" "create_before_delete" {
  length = var.diff ? 3 : 4

  lifecycle {
    create_before_destroy = true
  }
}

resource "random_string" "delete_before_create" {
  length = var.diff ? 4 : 3
}

resource "aws_s3_object" "update" {
  bucket = "terraform-github-actions"
  key    = "test-plan-colours-test-object"

  content = var.diff ? "update" : "hello"
}

output "add" {
  value = "hello"
}

#output "delete" {
#  value = "goodbye"
#}

output "update" {
  value = var.diff ? "update" : "hello"
}