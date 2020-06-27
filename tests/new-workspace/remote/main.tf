resource "random_string" "my_string" {
  length = 5
}

variable "my_string" {
  type = string
}

output "my_string" {
  value = var.my_string
}

terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "terraform-new-workspace"
    region = "eu-west-2"
  }
}