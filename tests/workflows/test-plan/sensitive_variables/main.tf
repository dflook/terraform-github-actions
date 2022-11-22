variable "my_string" {
  type = string
}

variable "my_int" {
  default = 100
}

variable "my_float" {
  default = 0.0
}

variable "my_sensitive_string" {
  sensitive = true
}

variable "complex" {
}

variable "complex_sensitive" {
  sensitive = true
}