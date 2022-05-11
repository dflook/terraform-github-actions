module "https_source" {
  source = "https://5qcb7mjppk.execute-api.eu-west-2.amazonaws.com/my_module"
}

output "https" {
  value = module.https_source.my-output
}
