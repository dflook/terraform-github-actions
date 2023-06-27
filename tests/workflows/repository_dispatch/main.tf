resource "random_password" "p" {
  length = 5
}

terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~>3.4"
    }
  }

  required_version = "~>1.3.7"
}
