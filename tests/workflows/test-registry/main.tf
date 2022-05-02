module "hello" {
  source  = "app.terraform.io/flooktech/test/aws"
  version = "0.0.1"
}

output "word" {
  value = module.hello.my-output
}
