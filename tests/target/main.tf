resource "random_string" "count" {
  count = 1

  length = var.length
}

resource "random_string" "foreach" {
  for_each = toset(["hello"])

  length = var.length
}

variable "length" {

}

output "count" {
  value = random_string.count[0].result
}

output "foreach" {
  value = random_string.foreach["hello"].result
}
