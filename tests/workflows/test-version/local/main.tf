variable "my_variable" {}
output "out" {
  value = "${var.my_variable}"
}
