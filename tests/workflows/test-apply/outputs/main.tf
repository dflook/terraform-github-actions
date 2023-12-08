output "sensitive" {
  value = "This is a sensistive value"
  sensitive = true
}

output "not_sensitive" {
  value = "This is not a sensistive value"
}

output "sensitive_map" {
  value = {
    "password" = "passw0rd"
  }
  sensitive = true
}

output "not_sensitive_complex" {
  value = [
    {
      "hello" = "world"
    },
    {
      "hello" = "again"
    }
  ]
}
