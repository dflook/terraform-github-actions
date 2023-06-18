terraform {
  cloud {
  }
  required_version = "~> 1.5.0"
}

resource "random_id" "the_id" {
  byte_length = var.length
}

variable "length" {
  default = 5
}

output "id" {
  value = random_id.the_id.hex
}

output "len" {
  value = var.length
}
