terraform {
  cloud {
    workspaces {
      tags = ["animal", "mineral"]
    }
  }
}
