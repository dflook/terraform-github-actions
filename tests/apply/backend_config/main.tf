terraform {
  backend "s3" {
  }
}

output "test" {
  value = "hello"
}
