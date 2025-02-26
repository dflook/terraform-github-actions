resource "random_string" "my_string" {
  length      = 11
}

output "s" {
  value = "string"
}

terraform {
  required_version = "~> 0.11.0"
}

provider "random" {
  version = "2.3.1"
}
