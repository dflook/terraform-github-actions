variable "region" {
  type = string
  default = "eu-west-2"
}

variable "mv" {
  type = string
  default = "non-ephemeral"
}

provider "aws" {
  region = var.region
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
