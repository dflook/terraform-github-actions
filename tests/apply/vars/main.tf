resource "random_string" "my_string" {
  length      = 11
}

output "output_string" {
  value = "the_string"
}

variable "my_var" {
  type = string
}

variable "my_var_from_file" {
  type = string
}

output "from_var" {
  value = var.my_var
}

output "from_varfile" {
  value = var.my_var_from_file
}
