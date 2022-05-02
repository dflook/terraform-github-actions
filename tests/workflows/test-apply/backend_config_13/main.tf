terraform {
  backend "s3" {
  }

  required_version = "~> 0.13.0"
}

output "test" {
  value = "hello"
}
