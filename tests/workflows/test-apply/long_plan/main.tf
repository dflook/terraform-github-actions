resource "random_id" "a" {
  count = 250

  byte_length = 3
}

resource "random_id" "b" {
  byte_length = var.length
}

variable "length" {
  type = number
  default = 3
}
