variable "region" {
  type = string
  default = "eu-west-2"
}

variable "mv" {
  type = string
  default = "non-ephemeral"
}

variable "secret" {
  type = string
  ephemeral = true
}

variable "session_tag" {
  type = string
  ephemeral = true
  default = "ephemeral-default"
}

provider "aws" {
  region = var.region
  token = var.secret
}

output "v" {
  value = var.mv
}

resource "random_string" "add" {
  length = 5
}

terraform {
  required_version = ">=1.10"
}
