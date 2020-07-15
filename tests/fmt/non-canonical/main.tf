resource "aws_s3_bucket" "hello" {
  bucket = "asd"
  bucket_prefix = "hgd"
}

variable "test-var" {
  type           = string
  description  =    "A test variable that is formatted wrong"

}