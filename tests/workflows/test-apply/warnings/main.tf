resource "random_string" "the_string" {
  length = 4
}

terraform {
  required_version = "1.2.4"
}

