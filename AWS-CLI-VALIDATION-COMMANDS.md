# AWS CLI Validation Commands Reference

**Purpose:** Quick reference for validating deployed AI agent infrastructure
**Framework Version:** v2.0
**Last Updated:** 2025-10-17

---

## Quick Validation Script

```bash
#!/bin/bash
# Run all validations for an agent
AGENT_NAME="security-agent"

echo "=== Validating $AGENT_NAME Infrastructure ==="

# 1. KMS Encryption
echo "✓ KMS Encryption..."
aws kms list-aliases --query "Aliases[?contains(AliasName, '$AGENT_NAME')]" --output table

# 2. Secrets Manager
echo "✓ Secrets Manager..."
aws secretsmanager describe-secret \
  --secret-id $AGENT_NAME/llm-api-key \
  --query '{Name:Name,KMS:KmsKeyId,LastRotated:LastRotatedDate}' \
  --output table

# 3. DynamoDB
echo "✓ DynamoDB Audit Trail..."
aws dynamodb describe-table \
  --table-name $AGENT_NAME-audit-trail \
  --query 'Table.{Name:TableName,Status:TableStatus,Encryption:SSEDescription.Status,StreamEnabled:StreamSpecification.StreamEnabled}' \
  --output table

# 4. S3 Archive
echo "✓ S3 Archive Bucket..."
aws s3api get-bucket-encryption \
  --bucket $AGENT_NAME-audit-archive-$(aws sts get-caller-identity --query Account --output text) \
  --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm'

# 5. IAM Role
echo "✓ IAM Role..."
aws iam get-role --role-name $AGENT_NAME-role \
  --query 'Role.{RoleName:RoleName,Created:CreateDate}' \
  --output table

# 6. CloudWatch Logs
echo "✓ CloudWatch Logs..."
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/lambda/$AGENT_NAME" \
  --query 'logGroups[0].{Name:logGroupName,Retention:retentionInDays,KMS:kmsKeyId}' \
  --output table

# 7. Cost Alarms
echo "✓ Cost Alarms..."
aws cloudwatch describe-alarms \
  --alarm-name-prefix "$AGENT_NAME-daily-cost" \
  --query 'MetricAlarms[].{Name:AlarmName,Threshold:Threshold,State:StateValue}' \
  --output table

echo "=== Validation Complete ==="
```

---

## Individual Validation Commands

### 1. KMS Encryption (SEC-001, MI-003)

#### List KMS Keys for Agent
```bash
aws kms list-aliases \
  --query "Aliases[?contains(AliasName, 'security-agent')]" \
  --output table
```

#### Get Key Details
```bash
aws kms describe-key \
  --key-id alias/security-agent-encryption \
  --query 'KeyMetadata.{KeyId:KeyId,State:KeyState,Enabled:Enabled,CreationDate:CreationDate}'
```

#### Verify Key Rotation
```bash
aws kms get-key-rotation-status \
  --key-id alias/security-agent-encryption \
  --query 'KeyRotationEnabled'
```

**Expected:** `true`

#### Get Key Policy
```bash
aws kms get-key-policy \
  --key-id alias/security-agent-encryption \
  --policy-name default \
  --output json | jq .
```

---

### 2. Secrets Manager (SEC-001, MI-003)

#### List Secrets
```bash
aws secretsmanager list-secrets \
  --query "SecretList[?contains(Name, 'security-agent')].[Name,ARN]" \
  --output table
```

#### Describe Secret (No Value)
```bash
aws secretsmanager describe-secret \
  --secret-id security-agent/llm-api-key \
  --query '{Name:Name,KMS:KmsKeyId,Rotation:RotationEnabled,LastAccessed:LastAccessedDate}'
```

#### Verify KMS Encryption
```bash
aws secretsmanager describe-secret \
  --secret-id security-agent/llm-api-key \
  --query 'KmsKeyId' \
  --output text | grep -q '^arn:aws:kms:' && echo "✅ KMS Encrypted" || echo "❌ NOT Encrypted"
```

#### Get Secret Value (Sensitive!)
```bash
# Only use for testing, logs sensitive data
aws secretsmanager get-secret-value \
  --secret-id security-agent/llm-api-key \
  --query 'SecretString' \
  --output text
```

#### Test Secret Retrieval from Lambda
```bash
# Simulate Lambda retrieving secret
aws secretsmanager get-secret-value \
  --secret-id security-agent/llm-api-key \
  --query 'SecretString' \
  --output text | head -c 20
# Should show first 20 characters
```

---

### 3. DynamoDB Audit Trail (MI-019)

#### Describe Table
```bash
aws dynamodb describe-table \
  --table-name security-agent-audit-trail \
  --query 'Table.{Name:TableName,Status:TableStatus,ItemCount:ItemCount,SizeBytes:TableSizeBytes}'
```

#### Verify Encryption
```bash
aws dynamodb describe-table \
  --table-name security-agent-audit-trail \
  --query 'Table.SSEDescription.{Status:Status,KMSKeyArn:KMSMasterKeyArn}'
```

**Expected:** `{"Status": "ENABLED", "KMSKeyArn": "arn:aws:kms:..."}`

#### Check Point-in-Time Recovery
```bash
aws dynamodb describe-continuous-backups \
  --table-name security-agent-audit-trail \
  --query 'ContinuousBackupsDescription.PointInTimeRecoveryDescription.PointInTimeRecoveryStatus'
```

**Expected:** `"ENABLED"` (production) or `"DISABLED"` (dev)

#### Verify Streams (for SIEM Integration)
```bash
aws dynamodb describe-table \
  --table-name security-agent-audit-trail \
  --query 'Table.{StreamEnabled:StreamSpecification.StreamEnabled,StreamARN:LatestStreamArn}'
```

**Expected:** `{"StreamEnabled": true, "StreamARN": "arn:aws:dynamodb:..."}`

#### List Global Secondary Indexes
```bash
aws dynamodb describe-table \
  --table-name security-agent-audit-trail \
  --query 'Table.GlobalSecondaryIndexes[].{Name:IndexName,Status:IndexStatus}' \
  --output table
```

**Expected:** ActorIndex, ActionIndex, ComplianceIndex

#### Query Audit Trail
```bash
# Get latest audit entries
aws dynamodb scan \
  --table-name security-agent-audit-trail \
  --limit 5 \
  --query 'Items[].{AuditID:audit_id.S,Timestamp:timestamp.S,Action:action.S,Result:compliance_result.S}' \
  --output table
```

---

### 4. S3 Archive Bucket (MI-019)

#### List Archive Buckets
```bash
aws s3 ls | grep audit-archive
```

#### Verify Encryption
```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3api get-bucket-encryption \
  --bucket security-agent-audit-archive-$ACCOUNT_ID \
  --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault'
```

**Expected:** `{"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "arn:aws:kms:..."}`

#### Verify Versioning
```bash
aws s3api get-bucket-versioning \
  --bucket security-agent-audit-archive-$ACCOUNT_ID
```

**Expected:** `{"Status": "Enabled"}`

#### Check Lifecycle Policy
```bash
aws s3api get-bucket-lifecycle-configuration \
  --bucket security-agent-audit-archive-$ACCOUNT_ID \
  --query 'Rules[0].{ID:ID,Status:Status,Transitions:Transitions,Expiration:Expiration}'
```

**Expected:** Transition to Glacier at 90 days, Deep Archive at 365 days, expiration at 2555 days (7 years)

#### Verify Public Access Blocked
```bash
aws s3api get-public-access-block \
  --bucket security-agent-audit-archive-$ACCOUNT_ID
```

**Expected:** All values should be `true`

---

### 5. IAM Role & Policies (MI-006, MI-020)

#### Get Role
```bash
aws iam get-role \
  --role-name security-agent-role \
  --query 'Role.{RoleName:RoleName,Created:CreateDate,ARN:Arn}'
```

#### List Role Policies
```bash
aws iam list-role-policies \
  --role-name security-agent-role
```

**Expected:** security-agent-secrets-policy, security-agent-audit-policy

#### Get Secrets Policy
```bash
aws iam get-role-policy \
  --role-name security-agent-role \
  --policy-name security-agent-secrets-policy \
  --query 'PolicyDocument.Statement[].{Effect:Effect,Action:Action,Resource:Resource}' \
  --output json | jq .
```

#### Check for Wildcard Actions (Least-Privilege Violation)
```bash
aws iam get-role-policy \
  --role-name security-agent-role \
  --policy-name security-agent-secrets-policy \
  --query 'PolicyDocument.Statement[].Action' \
  --output json | grep -q '\*' && echo "❌ Wildcard actions found (least-privilege violation)" || echo "✅ Least-privilege policy"
```

#### List Attached Managed Policies
```bash
aws iam list-attached-role-policies \
  --role-name security-agent-role \
  --query 'AttachedPolicies[].{Name:PolicyName,ARN:PolicyArn}' \
  --output table
```

**Expected:** AWSLambdaBasicExecutionRole

---

### 6. Lambda Function

#### Describe Function
```bash
aws lambda get-function \
  --function-name security-agent \
  --query 'Configuration.{Name:FunctionName,Runtime:Runtime,Memory:MemorySize,Timeout:Timeout,Role:Role}'
```

#### Get Environment Variables (Redacted)
```bash
aws lambda get-function-configuration \
  --function-name security-agent \
  --query 'Environment.Variables' \
  --output json | jq 'to_entries | map({key: .key, value: (if .key | contains("SECRET") then "***REDACTED***" else .value end)}) | from_entries'
```

#### Check Dead Letter Queue
```bash
aws lambda get-function-configuration \
  --function-name security-agent \
  --query 'DeadLetterConfig.TargetArn'
```

**Expected:** `"arn:aws:sqs:us-east-1:...:security-agent-dlq"`

---

### 7. CloudWatch Logs (MI-004, MI-019)

#### List Log Groups
```bash
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/lambda/security-agent" \
  --query 'logGroups[].{Name:logGroupName,Retention:retentionInDays,KMS:kmsKeyId,SizeMB:storedBytes}' \
  --output table
```

#### Get Recent Log Streams
```bash
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/security-agent" \
  --order-by LastEventTime \
  --descending \
  --max-items 5 \
  --query 'logStreams[].{Name:logStreamName,LastEvent:lastEventTimestamp}' \
  --output table
```

#### Tail Logs (Live)
```bash
aws logs tail /aws/lambda/security-agent --follow
```

---

### 8. CloudWatch Alarms (MI-009, MI-021)

#### List Cost Alarms
```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "security-agent-daily-cost" \
  --query 'MetricAlarms[].{Name:AlarmName,Threshold:Threshold,State:StateValue,ActionsEnabled:ActionsEnabled}' \
  --output table
```

#### Get Alarm Details
```bash
aws cloudwatch describe-alarms \
  --alarm-names security-agent-daily-cost-90pct \
  --query 'MetricAlarms[0].{Name:AlarmName,Metric:MetricName,Threshold:Threshold,Actions:AlarmActions}'
```

#### Test Alarm
```bash
# Set alarm to test state
aws cloudwatch set-alarm-state \
  --alarm-name security-agent-daily-cost-50pct \
  --state-value ALARM \
  --state-reason "Testing alarm notification"
```

---

### 9. SNS Topics (Notifications)

#### List Topics
```bash
aws sns list-topics \
  --query "Topics[?contains(TopicArn, 'security-agent')]" \
  --output table
```

#### List Subscriptions
```bash
TOPIC_ARN=$(aws sns list-topics --query "Topics[?contains(TopicArn, 'cost-alerts')].TopicArn | [0]" --output text)
aws sns list-subscriptions-by-topic \
  --topic-arn $TOPIC_ARN \
  --query 'Subscriptions[].{Protocol:Protocol,Endpoint:Endpoint,Status:SubscriptionArn}' \
  --output table
```

#### Publish Test Message
```bash
aws sns publish \
  --topic-arn $TOPIC_ARN \
  --subject "Test Alert" \
  --message "This is a test notification from the AI Agent Governance Framework"
```

---

## Batch Validation Scripts

### Validate All Resources for Agent

```bash
#!/bin/bash
AGENT_NAME=$1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Validating: $AGENT_NAME"
echo "AWS Account: $ACCOUNT_ID"
echo ""

# Resource counts
echo "=== Resource Inventory ==="
echo "KMS Keys: $(aws kms list-aliases --query "Aliases[?contains(AliasName, '$AGENT_NAME')] | length(@)")"
echo "Secrets: $(aws secretsmanager list-secrets --query "SecretList[?contains(Name, '$AGENT_NAME')] | length(@)")"
echo "DynamoDB Tables: $(aws dynamodb list-tables --query "TableNames[?contains(@, '$AGENT_NAME')] | length(@)")"
echo "S3 Buckets: $(aws s3 ls | grep -c $AGENT_NAME)"
echo "IAM Roles: $(aws iam list-roles --query "Roles[?contains(RoleName, '$AGENT_NAME')] | length(@)")"
echo "Lambda Functions: $(aws lambda list-functions --query "Functions[?contains(FunctionName, '$AGENT_NAME')] | length(@)")"
echo "Log Groups: $(aws logs describe-log-groups --query "logGroups[?contains(logGroupName, '$AGENT_NAME')] | length(@)")"
echo "Alarms: $(aws cloudwatch describe-alarms --alarm-name-prefix "$AGENT_NAME" --query "length(MetricAlarms)")"
echo ""

# Compliance checks
echo "=== Compliance Checks ==="
aws kms get-key-rotation-status --key-id alias/$AGENT_NAME-encryption --query 'KeyRotationEnabled' --output text | grep -q 'True' && echo "✅ KMS rotation enabled" || echo "❌ KMS rotation disabled"
aws secretsmanager describe-secret --secret-id $AGENT_NAME/llm-api-key --query 'KmsKeyId' --output text | grep -q 'arn:aws:kms:' && echo "✅ Secrets KMS encrypted" || echo "❌ Secrets not encrypted"
aws dynamodb describe-table --table-name $AGENT_NAME-audit-trail --query 'Table.SSEDescription.Status' --output text | grep -q 'ENABLED' && echo "✅ DynamoDB encrypted" || echo "❌ DynamoDB not encrypted"
aws s3api get-bucket-versioning --bucket $AGENT_NAME-audit-archive-$ACCOUNT_ID --query 'Status' --output text | grep -q 'Enabled' && echo "✅ S3 versioning enabled" || echo "❌ S3 versioning disabled"
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/$AGENT_NAME" --query 'logGroups[0].retentionInDays' --output text | grep -q '90' && echo "✅ Log retention 90 days" || echo "⚠️  Log retention not 90 days"
```

---

## Tag-Based Queries

### Find All Resources by Control ID

```bash
# Find all resources implementing SEC-001
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=ControlID,Values=SEC-001 \
  --query 'ResourceTagMappingList[].{ARN:ResourceARN,Tags:Tags}' \
  --output table
```

### Find All Resources by Agent ID

```bash
# Find all resources for security-agent
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=AgentID,Values=security-agent \
  --query 'ResourceTagMappingList[].{Type:ResourceARN,AgentTier:Tags[?Key==`AgentTier`].Value|[0]}' \
  --output table
```

---

## Monitoring & Metrics

### Get DynamoDB Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=security-agent-audit-trail \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

### Get Lambda Invocation Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=security-agent \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-17
**Maintained By:** AI Governance Team
