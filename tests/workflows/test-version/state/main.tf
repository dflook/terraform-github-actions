variable "my_variable" {}
output "out" {
  value = "${var.my_variable}"
}

terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "terraform-version"
    region = "eu-west-2"
    dynamodb_table = "terraform-github-actions"
  }
}
