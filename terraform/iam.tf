# IAM Roles and Policies for AI Ops Agent
# Implements: MI-006 (Access Controls), MI-020 (Tier Enforcement)
# Addresses: RI-012 (Unauthorized Actions)

# IAM role for the AI ops agent
resource "aws_iam_role" "agent_role" {
  name        = "${var.agent_name}-execution-role"
  description = "Execution role for ${var.agent_name} (${var.agent_tier})"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "lambda.aws.amazon.com",
            "ecs-tasks.amazonaws.com",
            "states.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  max_session_duration = 3600 # 1 hour max

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-execution-role"
      AgentTier     = var.agent_tier
      ControlID     = "MI-006,MI-020"
      RiskAddresses = "RI-012"
      Principle     = "Least-Privilege"
    }
  )
}

# Policy for tier-based permissions (SEC-003: Least Privilege)
resource "aws_iam_policy" "tier_permissions" {
  name        = "${var.agent_name}-tier-permissions"
  description = "Tier-based permissions for ${var.agent_tier}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      # Read-only permissions (all tiers)
      [
        {
          Sid    = "ReadOnlyAccess"
          Effect = "Allow"
          Action = [
            "s3:GetObject",
            "s3:ListBucket",
            "dynamodb:GetItem",
            "dynamodb:Query",
            "dynamodb:Scan",
            "logs:GetLogEvents",
            "cloudwatch:GetMetricData",
            "cloudwatch:GetMetricStatistics"
          ]
          Resource = "*"
          Condition = {
            StringEquals = {
              "aws:ResourceTag/AgentAccessible" = "true"
            }
          }
        }
      ],
      # Tier 3+ specific permissions (deployment)
      var.agent_tier == "tier3-operations" ? [
        {
          Sid    = "Tier3DeploymentAccess"
          Effect = "Allow"
          Action = [
            "ecs:UpdateService",
            "ecs:DescribeServices",
            "lambda:UpdateFunctionCode",
            "lambda:PublishVersion",
            "s3:PutObject",
            "ecr:PutImage"
          ]
          Resource = "*"
          Condition = {
            StringEquals = {
              "aws:ResourceTag/Environment" = var.environment
            }
          }
        }
      ] : [],
      # Explicit denies for security-critical actions (all tiers)
      [
        {
          Sid    = "DenySecurityModifications"
          Effect = "Deny"
          Action = [
            "iam:*",
            "kms:*",
            "secretsmanager:DeleteSecret",
            "secretsmanager:PutSecretValue",
            "organizations:*",
            "account:*"
          ]
          Resource = "*"
        }
      ]
    )
  })

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-tier-permissions"
      AgentTier = var.agent_tier
      ControlID = "MI-020"
    }
  )
}

# Attach tier permissions to role
resource "aws_iam_role_policy_attachment" "tier_permissions" {
  role       = aws_iam_role.agent_role.name
  policy_arn = aws_iam_policy.tier_permissions.arn
}

# Attach secrets access policy
resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = aws_iam_role.agent_role.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# CloudWatch Logs policy (MI-004: Observability)
resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "${var.agent_name}-cloudwatch-logs"
  description = "Allow ${var.agent_name} to write logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/ai-agents/${var.agent_name}:*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-cloudwatch-logs"
      ControlID = "MI-004"
    }
  )
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  role       = aws_iam_role.agent_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

# X-Ray tracing policy (MI-004: Observability)
resource "aws_iam_policy" "xray_tracing" {
  count = var.enable_observability ? 1 : 0

  name        = "${var.agent_name}-xray-tracing"
  description = "Allow ${var.agent_name} to send traces to X-Ray"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-xray-tracing"
      ControlID = "MI-004"
    }
  )
}

resource "aws_iam_role_policy_attachment" "xray_tracing" {
  count = var.enable_observability ? 1 : 0

  role       = aws_iam_role.agent_role.name
  policy_arn = aws_iam_policy.xray_tracing[0].arn
}

# DynamoDB access for audit trails (MI-019)
resource "aws_iam_policy" "audit_trail_access" {
  count = var.enable_audit_trail ? 1 : 0

  name        = "${var.agent_name}-audit-trail-access"
  description = "Allow ${var.agent_name} to write audit trails"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.audit_trail[0].arn
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-audit-trail-access"
      ControlID = "MI-019"
    }
  )
}

resource "aws_iam_role_policy_attachment" "audit_trail_access" {
  count = var.enable_audit_trail ? 1 : 0

  role       = aws_iam_role.agent_role.name
  policy_arn = aws_iam_policy.audit_trail_access[0].arn
}
