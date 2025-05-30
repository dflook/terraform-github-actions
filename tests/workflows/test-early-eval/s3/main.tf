terraform {
  backend "s3" {
    bucket = var.state_bucket
    key    = "test-plan-early-eval"
    region = "eu-west-2"
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "state_bucket" {
  type = string
}

variable "module_version" {
  type = string
  default = "0.25.0"
}

variable "passphrase" {
  type = string
  sensitive = true
}

module "label" {
  source  = "cloudposse/label/null"
  version = var.module_version

  name = "hello"
}

resource "random_string" "my_String" {
  length = 10
}

terraform {
  encryption {
    key_provider "pbkdf2" "my_passphrase" {
      passphrase = var.passphrase
    }

    method "aes_gcm" "my_method" {
      keys = key_provider.pbkdf2.my_passphrase
    }

    state {
      method = method.aes_gcm.my_method
    }
  }

  required_version = "1.9.0"
}
