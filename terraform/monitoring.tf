# Monitoring and Observability Infrastructure
# Implements: MI-004 (Observability), MI-009 (Cost Monitoring)
# Addresses: All risks (monitoring foundation)

# CloudWatch Log Group for agent logs
resource "aws_cloudwatch_log_group" "agent_logs" {
  name              = "/ai-agents/${var.agent_name}"
  retention_in_days = 90 # Per MI-019: 90 days hot storage

  kms_key_id = aws_kms_key.agent_encryption.arn

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-logs"
      ControlID     = "MI-004,MI-019"
      RetentionDays = "90"
    }
  )
}

# CloudWatch Metric Alarm for cost budget (MI-009, MI-021)
resource "aws_cloudwatch_metric_alarm" "daily_cost_alert_50pct" {
  alarm_name          = "${var.agent_name}-daily-cost-50pct"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 86400 # 1 day
  statistic           = "Maximum"
  threshold           = var.daily_cost_budget * 0.50
  alarm_description   = "Alert when ${var.agent_name} reaches 50% of daily budget"
  alarm_actions       = [aws_sns_topic.agent_alerts.arn]

  dimensions = {
    AgentName = var.agent_name
  }

  tags = merge(
    var.tags,
    {
      Name           = "${var.agent_name}-daily-cost-50pct"
      ControlID      = "MI-009"
      AlertSeverity  = "Informational"
      BudgetThreshold = "50%"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "daily_cost_alert_75pct" {
  alarm_name          = "${var.agent_name}-daily-cost-75pct"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 86400
  statistic           = "Maximum"
  threshold           = var.daily_cost_budget * 0.75
  alarm_description   = "Warning: ${var.agent_name} at 75% of daily budget"
  alarm_actions       = [aws_sns_topic.agent_alerts.arn]

  dimensions = {
    AgentName = var.agent_name
  }

  tags = merge(
    var.tags,
    {
      Name            = "${var.agent_name}-daily-cost-75pct"
      ControlID       = "MI-009"
      AlertSeverity   = "Warning"
      BudgetThreshold = "75%"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "daily_cost_alert_90pct" {
  alarm_name          = "${var.agent_name}-daily-cost-90pct"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 86400
  statistic           = "Maximum"
  threshold           = var.daily_cost_budget * 0.90
  alarm_description   = "CRITICAL: ${var.agent_name} at 90% of daily budget - requires approval to continue"
  alarm_actions       = [aws_sns_topic.agent_alerts.arn]

  dimensions = {
    AgentName = var.agent_name
  }

  tags = merge(
    var.tags,
    {
      Name            = "${var.agent_name}-daily-cost-90pct"
      ControlID       = "MI-009,MI-021"
      AlertSeverity   = "Critical"
      BudgetThreshold = "90%"
    }
  )
}

# SNS Topic for alerts
resource "aws_sns_topic" "agent_alerts" {
  name              = "${var.agent_name}-alerts"
  display_name      = "Alerts for ${var.agent_name}"
  kms_master_key_id = aws_kms_key.agent_encryption.id

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-alerts"
      ControlID = "MI-004,MI-009"
    }
  )
}

# SNS Topic subscription (email or webhook)
resource "aws_sns_topic_subscription" "agent_alerts_email" {
  topic_arn = aws_sns_topic.agent_alerts.arn
  protocol  = "email"
  endpoint  = "ai-ops@suhlabs.com" # Update with actual email
}

# CloudWatch Dashboard for agent monitoring
resource "aws_cloudwatch_dashboard" "agent_dashboard" {
  dashboard_name = "${var.agent_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title  = "Agent Request Rate"
          region = data.aws_region.current.name
          metrics = [
            ["AI/Agent", "RequestCount", { stat = "Sum", label = "Total Requests" }]
          ]
          period = 300
          yAxis = {
            left = { min = 0 }
          }
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Agent Cost Tracking"
          region = data.aws_region.current.name
          metrics = [
            ["AI/Agent", "EstimatedCost", { stat = "Sum", label = "Total Cost ($)" }]
          ]
          period = 3600
          yAxis = {
            left = { min = 0 }
          }
          annotations = {
            horizontal = [
              {
                value = var.daily_cost_budget
                label = "Daily Budget Limit"
                color = "#ff0000"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Token Usage"
          region = data.aws_region.current.name
          metrics = [
            ["AI/Agent", "InputTokens", { stat = "Sum", label = "Input Tokens" }],
            [".", "OutputTokens", { stat = "Sum", label = "Output Tokens" }]
          ]
          period = 300
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Human Review Rate"
          region = data.aws_region.current.name
          metrics = [
            ["AI/Agent", "HumanReviewRate", { stat = "Average", label = "Review Rate %" }]
          ]
          period = 3600
          yAxis = {
            left = { min = 0, max = 100 }
          }
          annotations = {
            horizontal = [
              {
                value = var.human_review_percentage * 100
                label = "Target Review Rate"
                color = "#00ff00"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Policy Violations"
          region = data.aws_region.current.name
          metrics = [
            ["AI/Agent", "PolicyViolations", { stat = "Sum", label = "Violations" }]
          ]
          period = 3600
          yAxis = {
            left = { min = 0 }
          }
        }
      },
      {
        type = "log"
        properties = {
          title  = "Recent Agent Activity"
          region = data.aws_region.current.name
          query  = <<-EOT
            SOURCE '/ai-agents/${var.agent_name}'
            | fields @timestamp, event_type, action, compliance_result, actor
            | sort @timestamp desc
            | limit 100
          EOT
        }
      }
    ]
  })
}

# CloudWatch Insights Query for audit trail analysis (MI-019)
resource "aws_cloudwatch_query_definition" "audit_trail_analysis" {
  name = "${var.agent_name}-audit-trail-analysis"

  log_group_names = [aws_cloudwatch_log_group.agent_logs.name]

  query_string = <<-EOT
    fields @timestamp, audit_id, actor, action, workflow_step, compliance_result, policy_controls_checked
    | filter event_type = "audit_trail"
    | sort @timestamp desc
    | limit 1000
  EOT
}

# CloudWatch Insights Query for cost analysis
resource "aws_cloudwatch_query_definition" "cost_analysis" {
  name = "${var.agent_name}-cost-analysis"

  log_group_names = [aws_cloudwatch_log_group.agent_logs.name]

  query_string = <<-EOT
    fields @timestamp, input_tokens, output_tokens, estimated_cost
    | stats sum(input_tokens) as total_input_tokens,
            sum(output_tokens) as total_output_tokens,
            sum(estimated_cost) as total_cost by bin(5m)
    | sort @timestamp desc
  EOT
}

# CloudWatch Insights Query for security events
resource "aws_cloudwatch_query_definition" "security_events" {
  name = "${var.agent_name}-security-events"

  log_group_names = [aws_cloudwatch_log_group.agent_logs.name]

  query_string = <<-EOT
    fields @timestamp, event_type, actor, action, security_control, violation_reason
    | filter event_type in ["prompt_injection_detected", "pii_detected", "unauthorized_action", "budget_exceeded"]
    | sort @timestamp desc
    | limit 1000
  EOT
}
