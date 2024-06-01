run "require_provider" {
  # This will require terraform to be initialised correctly to bring in the time provider
  command = apply

  module {
    source = "./sleep"
  }
}

run "test_third" {
  command = apply

  variables {
    length = 15
  }

  assert {
    condition     = length(output.random_string) == 15
    error_message = "Length is not correct"
  }
}
