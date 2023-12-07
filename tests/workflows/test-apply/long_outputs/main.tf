variable "input" {
    type = string
    default = "This is my long string\n"
}

output "output" {
  value = repeat(var.input, 5000)
}
