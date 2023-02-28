resource "random_string" "my_string" {
  length      = 11
}

output "output_string" {
  value = "the_string"
}
