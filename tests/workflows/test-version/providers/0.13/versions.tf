terraform {
  required_providers {
    acme = {
      source = "terraform-providers/acme"
    }
    random = {
      source = "hashicorp/random"
      version = "2.2.0"
    }
  }
  required_version = "~> 0.13.0"
}
