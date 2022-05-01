variable "cause-changes" {
  default = false
}

variable "len" {
  default = 5
}

resource "random_string" "the_string" {
  count = var.cause-changes ? 1 : 0
  length = var.len
}
