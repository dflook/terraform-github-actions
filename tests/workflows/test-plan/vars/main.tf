resource "random_string" "my_string" {
  length      = 11
}

output "output_string" {
  value = "the_string"
}

variable "my_var" {
  type = string
  default = "my_var_default"
}

variable "my_var_from_file" {
  type = string
  default = "my_var_from_file_default"
}

variable "my_int" {
  default = 100
}

variable "my_float" {
  default = 0.0
}

variable "my_sensitive_string" {
  default = "danger"
  sensitive = true
}

variable "complex_input" {
  type = list(object({
    internal = number
    external = number
    protocol = string
  }))
  default = [
    {
      internal = 8300
      external = 8300
      protocol = "tcp"
    }
  ]
}

output "from_var" {
  value = var.my_var
}

output "from_varfile" {
  value = var.my_var_from_file
}

output "complex_output" {
  value = join(",", [for input in var.complex_input : "${input.internal}:${input.external}:${input.protocol}"])
}
