variable "input" {
    type = string
    default = "This is my long string"
}

output "output" {
  value = join('\n', [for i in range(0, 5000): var.input])
}
