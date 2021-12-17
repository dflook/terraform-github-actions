variable "my_variable" {}
output "out" {
  value = "${var.my_variable}"
}

terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "terraform-version-12"
    region = "eu-west-2"
  }
}
