module "hello" {
  source = "git::ssh://git@github.com/dflook/terraform-github-actions//tests/registry/test-module"
}

output "word" {
  value = module.hello.my-output
}
