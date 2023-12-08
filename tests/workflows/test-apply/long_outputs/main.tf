variable "input" {
    type = string
    default = "This is my long string."
}

resource "random_string" "s" {
  length = 200
  special = false
}

output "output" {
  value = join("\n", [for i in range(0, 100): var.input])
}

output "unknown" {
  value = join("\n", [for i in range(0, 1024): random_string.s.result])
}