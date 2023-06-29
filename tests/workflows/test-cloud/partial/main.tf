terraform {
  cloud {
    organization = "flooktech"
  }
  required_version = "1.4.5"
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
