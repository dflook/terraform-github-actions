locals {
  aws_provider_config = {
    prod = {
      region     = "..."
      account_id = "..."
      profile    = "..."
    }
    dev = {
      region     = "..."
      account_id = "..."
      profile    = "..."
    }
  }
}

provider "aws" {
  region              = local.aws_provider_config[terraform.workspace].region
  profile             = local.aws_provider_config[terraform.workspace].profile
  allowed_account_ids = [local.aws_provider_config[terraform.workspace].account_id]
}

resource "aws_s3_bucket" "bucket" {
  bucket = "hello"
}
