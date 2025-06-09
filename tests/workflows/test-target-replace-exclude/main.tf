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

# Additional resources for exclude testing
resource "random_string" "exclude_me" {
  length = var.length
  special = false
  min_special = 0
}

resource "random_string" "keep_me" {
  length = var.length
  special = false
  min_special = 0
}

resource "random_string" "also_exclude" {
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

output "exclude_me" {
  value = random_string.exclude_me.result
}

output "keep_me" {
  value = random_string.keep_me.result
}

output "also_exclude" {
  value = random_string.also_exclude.result
}
