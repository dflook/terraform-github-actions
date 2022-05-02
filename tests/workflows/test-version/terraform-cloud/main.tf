terraform {
  backend "remote" {
    organization = "flooktech"

    workspaces {
      prefix = "github-actions-version-"
    }
  }
}
