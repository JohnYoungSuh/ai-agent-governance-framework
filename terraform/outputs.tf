# Terraform Outputs

output "agent_name" {
  description = "Name of the AI ops agent"
  value       = var.agent_name
}

output "agent_tier" {
  description = "Agent tier classification"
  value       = var.agent_tier
}

output "agent_role_arn" {
  description = "IAM role ARN for the agent"
  value       = aws_iam_role.agent_role.arn
}

output "agent_role_name" {
  description = "IAM role name for the agent"
  value       = aws_iam_role.agent_role.name
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.agent_logs.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.agent_logs.arn
}

output "audit_trail_table_name" {
  description = "DynamoDB audit trail table name"
  value       = var.enable_audit_trail ? aws_dynamodb_table.audit_trail[0].name : "N/A - audit trail not enabled"
}

output "audit_archive_bucket" {
  description = "S3 bucket for audit trail archive"
  value       = var.enable_audit_trail ? aws_s3_bucket.audit_archive[0].id : "N/A - audit trail not enabled"
}

output "governance_records_table_name" {
  description = "DynamoDB governance records table name"
  value       = aws_dynamodb_table.governance_records.name
}

output "governance_evidence_bucket" {
  description = "S3 bucket for governance evidence"
  value       = aws_s3_bucket.governance_evidence.id
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.agent_alerts.arn
}

output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.agent_dashboard.dashboard_name}"
}

output "webhook_url" {
  description = "GitHub webhook URL"
  value       = "${aws_api_gateway_deployment.agent_webhook.invoke_url}/webhook"
}

output "kms_key_id" {
  description = "KMS key ID for encryption"
  value       = aws_kms_key.agent_encryption.id
}

output "kms_key_arn" {
  description = "KMS key ARN for encryption"
  value       = aws_kms_key.agent_encryption.arn
}

output "llm_api_key_secret_arn" {
  description = "ARN of the LLM API key secret"
  value       = aws_secretsmanager_secret.llm_api_key.arn
  sensitive   = true
}

output "github_token_secret_arn" {
  description = "ARN of the GitHub token secret"
  value       = aws_secretsmanager_secret.github_token.arn
  sensitive   = true
}

output "compliance_mapping_file" {
  description = "Path to compliance mapping YAML file"
  value       = local_file.compliance_mapping.filename
}

output "governance_validation_report" {
  description = "Path to governance validation report"
  value       = local_file.governance_validation_report.filename
}

output "cost_budgets" {
  description = "Configured cost budgets"
  value = {
    daily_budget   = var.daily_cost_budget
    monthly_budget = var.monthly_cost_budget
  }
}

output "human_review_percentage" {
  description = "Configured human review percentage"
  value       = "${var.human_review_percentage * 100}%"
}

output "risk_controls_implemented" {
  description = "List of risk controls implemented"
  value       = var.risk_controls_required
}

output "compliance_regulations" {
  description = "Applicable compliance regulations"
  value       = var.compliance_regulations
}

output "security_summary" {
  description = "Security configuration summary"
  value = {
    encryption_at_rest         = "KMS-encrypted"
    encryption_in_transit      = "TLS/HTTPS"
    secrets_management         = "AWS Secrets Manager"
    pii_redaction_enabled      = var.enable_pii_redaction
    secrets_scanning_enabled   = var.enable_secrets_scanning
    prompt_injection_detection = var.enable_prompt_injection_detection
    audit_trail_enabled        = var.enable_audit_trail
    observability_enabled      = var.enable_observability
  }
}

output "next_steps" {
  description = "Next steps for agent deployment"
  value = <<-EOT

    ✅ Terraform Infrastructure Deployed Successfully!

    Next Steps:

    1. Store Secrets in AWS Secrets Manager:
       - LLM API Key: aws secretsmanager put-secret-value --secret-id ${aws_secretsmanager_secret.llm_api_key.name} --secret-string "YOUR_API_KEY"
       - GitHub Token: aws secretsmanager put-secret-value --secret-id ${aws_secretsmanager_secret.github_token.name} --secret-string "YOUR_GITHUB_TOKEN"

    2. Initialize Governance Records:
       - Run: aws lambda invoke --function-name ${aws_lambda_function.governance_initializer.function_name} response.json

    3. Configure GitHub Webhook:
       - Webhook URL: ${aws_api_gateway_deployment.agent_webhook.invoke_url}/webhook
       - Secret is stored in: ${aws_secretsmanager_secret.webhook_secret.name}

    4. Review Governance Validation Report:
       - File: ${local_file.governance_validation_report.filename}
       - Review and complete approval sign-off

    5. Review Compliance Mapping:
       - File: ${local_file.compliance_mapping.filename}
       - Ensure all required controls are documented

    6. Set Up Monitoring:
       - Dashboard: ${aws_cloudwatch_dashboard.agent_dashboard.dashboard_name}
       - Subscribe to SNS topic: ${aws_sns_topic.agent_alerts.arn}

    7. Test Agent Deployment:
       - Trigger GitHub workflow: ${var.github_workflow_file}
       - Monitor logs: ${aws_cloudwatch_log_group.agent_logs.name}

    8. Review Security Controls:
       ${var.enable_audit_trail ? "✅" : "❌"} Audit Trail
       ${var.enable_observability ? "✅" : "❌"} Observability
       ${var.enable_pii_redaction ? "✅" : "❌"} PII Redaction
       ${var.enable_prompt_injection_detection ? "✅" : "❌"} Prompt Injection Detection

    For support: https://github.com/suhlabs/ai-agent-governance-framework
  EOT
}
