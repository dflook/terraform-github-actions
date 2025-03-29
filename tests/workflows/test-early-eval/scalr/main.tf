terraform {
  backend "remote" {
    hostname = "dflook.scalr.io"
    organization = "Environment-A"

    workspaces {
      prefix = "scalr-"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "module_version" {
  type = string
  default = "4.3.0"
}

variable "passphrase" {
  type = string
  sensitive = true
}

module "s3-bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = var.module_version
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

  required_version = "1.8.8"
}
