data "archive_file" "example_lambda2" {
  type        = "zip"
  source_file = "${path.module}/example_lambda2.js"
  output_path = "${path.module}/example_lambda2.js.zip"
}

resource "aws_lambda_function" "example_lambda" {
  function_name = "example_lambda2"
  handler = "example_lambda2.handler"
  role = "${aws_iam_role.example_lambda.arn}"
  runtime = "nodejs6.10"

  filename = "${data.archive_file.example_lambda2.output_path}"
  source_code_hash = "${data.archive_file.example_lambda2.output_base64sha256}"

  timeout = 30
  memory_size = 128
}