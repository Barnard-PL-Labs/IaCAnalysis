// Existing Terraform src code found at /var/folders/m3/_3kbnn117njf9qm08gvnjk040000gn/T/terraform_src.

resource "aws_iam_role" "lambda_execution_role" {
  assume_role_policy = {
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "lambda.amazonaws.com"
          ]
        }
        Action = [
          "sts:AssumeRole"
        ]
      }
    ]
  }
  force_detach_policies = [
    {
      PolicyName = "allowLambdaLogs"
      PolicyDocument = {
        Version = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Action = [
              "logs:*"
            ]
            Resource = "arn:aws:logs:*:*:*"
          }
        ]
      }
    },
    {
      PolicyName = "allowSqs"
      PolicyDocument = {
        Version = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Action = [
              "sqs:ReceiveMessage",
              "sqs:DeleteMessage",
              "sqs:GetQueueAttributes",
              "sqs:ChangeMessageVisibility"
            ]
            Resource = aws_sqs_queue.my_queue.arn
          }
        ]
      }
    }
  ]
}

resource "aws_lambda_function" "lambda_function" {
  code_signing_config_arn = {
    S3Bucket = "my-source-bucket"
    S3Key = "lambda/my-nodejs-app.zip"
  }
  handler = "index.handler"
  role = aws_iam_role.lambda_execution_role.arn
  runtime = "nodejs8.10"
  timeout = 60
  memory_size = 512
}

resource "aws_lambda_event_source_mapping" "lambda_function_event_source_mapping" {
  batch_size = 10
  enabled = True
  event_source_arn = aws_sqs_queue.my_queue.arn
  function_name = aws_lambda_function.lambda_function.arn
}

resource "aws_sqs_queue" "my_queue" {
  delay_seconds = 0
  visibility_timeout_seconds = 120
}
