run "test_length" {
  command = apply

  variables {
    length = 12
  }

  assert {
    condition     = length(output.random_string) == 12
    error_message = "Length is not correct"
  }
}
