resource "random_string" "count" {
  count = 1

  length = var.length

  special = false
  min_special = 0
}

resource "random_string" "foreach" {
  for_each = toset(["hello"])

  length = var.length

  special = false
  min_special = 0
}

variable "length" {

}

output "count" {
  value = random_string.count[0].result
}

output "foreach" {
  value = random_string.foreach["hello"].result
}
