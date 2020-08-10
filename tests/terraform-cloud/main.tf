terraform {
  backend "remote" {
    organization = "flooktech"

    workspaces {
      prefix = "github-actions-"
    }
  }
  required_version = "~> 0.13.0"
}

resource "random_id" "the_id" {
  byte_length = 5
}
