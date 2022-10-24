terraform {
  backend "s3" {
    bucket = "terraform-github-actions"
    key    = "terraform-remote-state"
    region = "eu-west-2"
  }
  required_version = "~> 0.12.0"
}

output "my_number" {
  value = 5
}

output "my_sensitive_number" {
  value = 6
  sensitive = true
}

output "my_string" {
  value = "hello"
}

output "my_sensitive_string" {
  value = "password"
  sensitive = true
}

output "my_multiline_string" {
  value = <<EOF
mcnbcvnxdgjt
iyriuytifdcv
pydrtdxfgcvj
EOF
}

output "my_sensitive_multiline_string" {
  value = <<EOF
qowicznobnad
trewptonopce
zxicvbnoberg
EOF
  sensitive = true
}

output "my_bool" {
  value = true
}

output "my_sensitive_bool" {
  value = false
  sensitive = true
}

output "my_list" {
  value = tolist(toset(["one", "two"]))
}

output "my_sensitive_list" {
  value = tolist(toset(["one", "two"]))
  sensitive = true
}

output "my_map" {
  value = tomap({
    first = "one"
    second = "two"
    third = 3
  })
}

output "my_sensitive_map" {
  value = tomap({
    first = "one"
    second = "two"
    third = 3
  })
  sensitive = true
}

output "my_set" {
  value = toset(["one", "two"])
}

output "my_sensitive_set" {
  value = toset(["one", "two"])
  sensitive = true
}

output "my_object" {
  value = {
    first = "one"
    second = "two"
    third = 3
  }
}

output "my_sensitive_object" {
  value = {
    first = "one"
    second = "two"
    third = 3
  }
  sensitive = true
}

output "my_tuple" {
  value = ["one", "two"]
}

output "my_sensitive_tuple" {
  value = ["one", "two"]
  sensitive = true
}

output "my_compound_output" {
  value = {
    first = tolist(toset(["one", "two"]))
    second = toset(["one", "two"])
    third = 3
  }
}

output "awkward_string" {
  value = "hello \"there\", here are some 'quotes'."
}

output "awkward_compound_output" {
  value = {
    nested = {
      thevalue = ["hello \"there\", here are some 'quotes'."]
    }
  }
}
