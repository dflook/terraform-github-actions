terraform {
  backend "s3" {
  }

  required_version = "~> 0.12.0"
}

output "test" {
  value = "hello"
}
