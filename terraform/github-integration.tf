# GitHub Integration for AI Ops Agent
# Integrates with GitHub projects for automated workflows

# GitHub repository configuration
data "github_repository" "agent_repo" {
  full_name = "${var.github_organization}/${var.github_repository}"
}

# GitHub Actions secret for AWS credentials
resource "github_actions_secret" "aws_access_key" {
  repository      = var.github_repository
  secret_name     = "AWS_ACCESS_KEY_ID_${upper(replace(var.agent_name, "-", "_"))}"
  plaintext_value = aws_iam_access_key.github_actions.id
}

resource "github_actions_secret" "aws_secret_key" {
  repository      = var.github_repository
  secret_name     = "AWS_SECRET_ACCESS_KEY_${upper(replace(var.agent_name, "-", "_"))}"
  plaintext_value = aws_iam_access_key.github_actions.secret
}

resource "github_actions_secret" "agent_role_arn" {
  repository      = var.github_repository
  secret_name     = "AGENT_ROLE_ARN_${upper(replace(var.agent_name, "-", "_"))}"
  plaintext_value = aws_iam_role.agent_role.arn
}

# IAM user for GitHub Actions
resource "aws_iam_user" "github_actions" {
  name = "${var.agent_name}-github-actions"
  path = "/ci-cd/"

  tags = merge(
    var.tags,
    {
      Name    = "${var.agent_name}-github-actions"
      Purpose = "GitHub Actions CI/CD"
    }
  )
}

resource "aws_iam_access_key" "github_actions" {
  user = aws_iam_user.github_actions.name
}

# Policy allowing GitHub Actions to assume agent role
resource "aws_iam_user_policy" "github_actions_assume_role" {
  name = "${var.agent_name}-assume-agent-role"
  user = aws_iam_user.github_actions.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = aws_iam_role.agent_role.arn
      }
    ]
  })
}

# GitHub Actions workflow file
resource "github_repository_file" "agent_workflow" {
  repository          = var.github_repository
  branch              = "main"
  file                = ".github/workflows/${var.github_workflow_file}"
  commit_message      = "Add AI ops agent workflow (${var.agent_name})"
  commit_author       = "Terraform"
  commit_email        = "terraform@suhlabs.com"
  overwrite_on_create = true

  content = templatefile("${path.module}/templates/github-workflow.yml.tpl", {
    agent_name              = var.agent_name
    agent_tier              = var.agent_tier
    aws_region              = var.aws_region
    agent_role_arn          = aws_iam_role.agent_role.arn
    llm_model_provider      = var.llm_model_provider
    llm_model_version       = var.llm_model_version
    daily_cost_budget       = var.daily_cost_budget
    monthly_cost_budget     = var.monthly_cost_budget
    human_review_percentage = var.human_review_percentage
    enable_audit_trail      = var.enable_audit_trail
    enable_observability    = var.enable_observability
    audit_table_name        = var.enable_audit_trail ? aws_dynamodb_table.audit_trail[0].name : ""
    log_group_name          = aws_cloudwatch_log_group.agent_logs.name
  })
}

# GitHub repository webhook for agent events
resource "github_repository_webhook" "agent_events" {
  repository = var.github_repository

  configuration {
    url          = aws_api_gateway_deployment.agent_webhook.invoke_url
    content_type = "json"
    insecure_ssl = false
    secret       = random_password.webhook_secret.result
  }

  active = true

  events = [
    "push",
    "pull_request",
    "issues",
    "issue_comment",
    "deployment",
    "deployment_status"
  ]
}

resource "random_password" "webhook_secret" {
  length  = 32
  special = true
}

# Store webhook secret in AWS Secrets Manager
resource "aws_secretsmanager_secret" "webhook_secret" {
  name        = "${var.agent_name}-github-webhook-secret"
  description = "GitHub webhook secret for ${var.agent_name}"

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-github-webhook-secret"
    }
  )
}

resource "aws_secretsmanager_secret_version" "webhook_secret" {
  secret_id     = aws_secretsmanager_secret.webhook_secret.id
  secret_string = random_password.webhook_secret.result
}

# API Gateway for GitHub webhook receiver
resource "aws_api_gateway_rest_api" "agent_webhook" {
  name        = "${var.agent_name}-github-webhook"
  description = "GitHub webhook receiver for ${var.agent_name}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-github-webhook"
    }
  )
}

resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.agent_webhook.id
  parent_id   = aws_api_gateway_rest_api.agent_webhook.root_resource_id
  path_part   = "webhook"
}

resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.agent_webhook.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "webhook_lambda" {
  rest_api_id = aws_api_gateway_rest_api.agent_webhook.id
  resource_id = aws_api_gateway_resource.webhook.id
  http_method = aws_api_gateway_method.webhook_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.webhook_handler.invoke_arn
}

resource "aws_api_gateway_deployment" "agent_webhook" {
  depends_on = [
    aws_api_gateway_integration.webhook_lambda
  ]

  rest_api_id = aws_api_gateway_rest_api.agent_webhook.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# Lambda function for webhook processing
resource "aws_lambda_function" "webhook_handler" {
  filename      = "${path.module}/lambda/webhook-handler.zip"
  function_name = "${var.agent_name}-webhook-handler"
  role          = aws_iam_role.webhook_handler_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30

  environment {
    variables = {
      AGENT_NAME            = var.agent_name
      AGENT_TIER            = var.agent_tier
      WEBHOOK_SECRET_ARN    = aws_secretsmanager_secret.webhook_secret.arn
      AUDIT_TABLE_NAME      = var.enable_audit_trail ? aws_dynamodb_table.audit_trail[0].name : ""
      LOG_GROUP_NAME        = aws_cloudwatch_log_group.agent_logs.name
      ENABLE_AUDIT_TRAIL    = var.enable_audit_trail
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-webhook-handler"
    }
  )
}

resource "aws_iam_role" "webhook_handler_role" {
  name = "${var.agent_name}-webhook-handler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-webhook-handler-role"
    }
  )
}

resource "aws_iam_policy" "webhook_handler_policy" {
  name = "${var.agent_name}-webhook-handler-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.webhook_secret.arn
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem"
        ]
        Resource = var.enable_audit_trail ? aws_dynamodb_table.audit_trail[0].arn : "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-webhook-handler-policy"
    }
  )
}

resource "aws_iam_role_policy_attachment" "webhook_handler_policy" {
  role       = aws_iam_role.webhook_handler_role.name
  policy_arn = aws_iam_policy.webhook_handler_policy.arn
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.agent_webhook.execution_arn}/*/*"
}
