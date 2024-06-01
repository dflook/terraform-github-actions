variable "length" {
  description = "The length of the string"
  type        = number
  default     = 10
}

resource "random_string" "example" {
  length  = var.length
  special = false
}

output "random_string" {
  value = random_string.example.result
}
