resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  batch_size        = 1
  event_source_arn  = "${aws_sqs_queue.some_queue.arn}"
  enabled           = true
  function_name     = "${aws_lambda_function.example_lambda.arn}"
}

resource "aws_lambda_event_source_mapping2" "event_source_mapping" {
  batch_size        = 1
  event_source_arn  = "${aws_sqs_queue.some_queue.arn}"
  enabled           = true
  function_name     = "${aws_lambda_function.example_lambda2.arn}"
}
