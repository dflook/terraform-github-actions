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

variable "acm_certificate_version" {
  type = string
  default = "4.3.0"
}

variable "passphrase" {
  type = string
  sensitive = true
}

module "s3-bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = var.acm_certificate_version
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
