variable "var1" {
  type    = string
  default = ""
}

variable "var2" {
  type    = string
  default = ""
}

variable "var3" {
  type    = string
  default = ""
}

variable "var4" {
  type    = string
  default = ""
}

variable "var5" {
  type    = string
  default = ""
}

variable "var6" {
  type    = string
  default = ""
}

variable "var7" {
  type    = string
  default = ""
}

variable "var8" {
  type    = string
  default = ""
}

variable "var9" {
  type    = string
  default = ""
}

variable "var_from_input" {
  type    = string
  default = ""
}

output "all_vars" {
  value = "${var.var1}-${var.var2}-${var.var3}-${var.var4}-${var.var5}-${var.var6}-${var.var7}-${var.var8}-${var.var9}-${var.var_from_input}"
}
