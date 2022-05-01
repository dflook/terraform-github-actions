resource "random_string" "my_string" {
  length      = var.len
}

output "s" {
  value = "${random_string.my_string}"
}

terraform {
  required_version = "~> 0.15.0"
}

variable "len" {}
