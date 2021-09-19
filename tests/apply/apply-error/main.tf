# This should be valid, and generate a valid plan
# But we expect it to fail when applied, as the bucket surely already exists

resource "aws_s3_bucket" "my_bucket" {
  bucket = "hello"
}

provider aws {
  region = "eu-west-2"
}
