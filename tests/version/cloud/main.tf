terraform {
  cloud {
    organization = "flooktech"
    workspaces {
      tags = ["terraformgithubactions", "version", "cloud"]
    }
  }
}
