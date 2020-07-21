terraform {
  backend "remote" {
    organization = "flooktech"

    workspaces {
      prefix = "github-actions-"
    }
  }
}

resource "random_id" "the_id" {
  byte_length = 5
}
