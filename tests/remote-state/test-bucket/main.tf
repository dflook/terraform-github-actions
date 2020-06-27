terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "terraform-remote-state"
    region = "eu-west-2"
  }
}

output "my_number" {
  value = 5
}

output "my_sensitive_number" {
  value = 6
  sensitive = true
}

output "my_string" {
  value = "hello"
}

output "my_sensitive_string" {
  value = "password"
  sensitive = true
}

output "my_bool" {
  value = true
}

output "my_sensitive_bool" {
  value = false
  sensitive = true
}
