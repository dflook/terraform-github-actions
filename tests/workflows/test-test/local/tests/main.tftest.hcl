run "test" {
  command = apply

  assert {
    condition     = length(output.random_string) == 10
    error_message = "Length is not correct"
  }
}
