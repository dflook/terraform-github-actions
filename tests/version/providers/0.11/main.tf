provider "random" {
  version = "2.2.0"
}

provider "acme" {
}

terraform {
  required_version = "~>0.11.0"
}
