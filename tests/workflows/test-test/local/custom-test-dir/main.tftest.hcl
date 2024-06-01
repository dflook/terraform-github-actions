run "test_length" {
  command = apply

  variables {
    length = 11
  }

  assert {
    condition     = length(output.random_string) == 11
    error_message = "Length is not correct"
  }
}
