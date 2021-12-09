resource "random_string" "my_string" {
  length = 5
}

variable "my_string" {
  type = string
}

output "my_string" {
  value = var.my_string
}
