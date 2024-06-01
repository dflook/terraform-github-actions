run "test_length" {
  command = apply

  variables {
    length = 13
  }

  assert {
    condition     = length(output.random_string) == 13
    error_message = "Length is not correct"
  }
}
