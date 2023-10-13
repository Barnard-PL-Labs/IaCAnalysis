provider "aws" {
  region = "ap-southeast-1"
  # version = "1.26.0"
}

resource "aws_s3_bucket" "bucket" {
  count = 3

  bucket = "bucket-${count.index}"
}
