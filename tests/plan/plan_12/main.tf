resource "random_string" "my_string" {
  length      = 11
}

output "s" {
  value = "string"
}

terraform {
  required_version = "~> 0.12.0"
}
