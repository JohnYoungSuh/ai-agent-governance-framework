# Multi-Repo vs Monorepo Architecture Comparison
## AI Agent Governance Framework Extension

**Version:** 1.0
**Date:** October 2025
**Status:** Architecture Decision Document

---

## Executive Summary

This document compares two architectural approaches for extending the **ai-agent-governance-framework** to support four specialized agent services:

1. **Security Agent** - Security scanning, vulnerability detection, compliance monitoring
2. **IT-Ops Agent** - Infrastructure operations, deployment automation, incident response
3. **AI Agent** - AI/ML model operations, training pipelines, model governance
4. **Architect Agent** - System design, technical evaluation, architectural decisions

Both approaches leverage the existing **AWS serverless architecture** (Lambda, DynamoDB, S3, CloudWatch) with **Terraform IaC** and **GitHub Actions CI/CD**.

**Recommendation:** For a small cross-functional team, use **Monorepo with Per-Agent Folders** (see section 7).

---

## Table of Contents

1. [Current Framework State](#1-current-framework-state)
2. [Approach 1: Multi-Repo Architecture](#2-approach-1-multi-repo-architecture)
3. [Approach 2: Monorepo Architecture](#3-approach-2-monorepo-architecture)
4. [CI/CD Pipeline Comparison](#4-cicd-pipeline-comparison)
5. [Versioning & Dependency Management](#5-versioning--dependency-management)
6. [Secrets Management](#6-secrets-management)
7. [Pros & Cons Comparison](#7-pros--cons-comparison)
8. [Recommendation](#8-recommendation)
9. [Migration Path](#9-migration-path)

---

## 1. Current Framework State

### Infrastructure
- **Cloud Platform:** AWS (Lambda, DynamoDB, S3, CloudWatch, Secrets Manager)
- **IaC:** Terraform (29 input variables, 24 outputs)
- **CI/CD:** GitHub Actions (validation, security scanning, deployment)
- **Monitoring:** OpenTelemetry + CloudWatch
- **Audit:** DynamoDB audit trail + S3 Glacier (7-year retention)

### Repository Structure
```
ai-agent-governance-framework/
├── docs/                    # Framework documentation
├── policies/                # Risk catalog, mitigations (18 risks, 21 controls)
├── frameworks/              # YAML configs (tiers, approval workflows, observability)
├── workflows/               # Threat modeling, PAR-PROTO patterns
├── templates/               # Agent deployment, cost tracking templates
├── examples/                # Tier 1-4 agent examples
├── scripts/                 # Setup, cost reporting, compliance scripts
├── terraform/               # AWS infrastructure (Lambda, DynamoDB, S3, IAM, monitoring)
└── .github/workflows/       # GitHub Actions (validate.yml)
```

### Agent Tier System
| Tier | Role | Autonomy | Avg Cost/Task | Example Use Cases |
|------|------|----------|---------------|-------------------|
| 1 | Observer | Read-only | $0.10-$0.50 | Docs, log analysis, code review |
| 2 | Developer | Dev env | $0.50-$5.00 | Code generation, testing, PRs |
| 3 | Operations | Production | $1.00-$10.00 | Deployments, incident response, scaling |
| 4 | Architect | Design | $5.00-$50.00 | System design, POCs, technical evaluation |

---

## 2. Approach 1: Multi-Repo Architecture

### 2.1 Repository Layout

```
┌─────────────────────────────────────────────────────────────┐
│  CENTRAL FRAMEWORK REPO                                     │
│  Repository: ai-agent-governance-framework                  │
│  Purpose: Shared policies, templates, Terraform modules    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (imported as Git submodule or NPM package)
                            │
        ┌───────────────────┼───────────────────┬───────────────────┐
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ security-agent│   │ it-ops-agent  │   │   ai-agent    │   │architect-agent│
│  Repository   │   │  Repository   │   │  Repository   │   │  Repository   │
└───────────────┘   └───────────────┘   └───────────────┘   └───────────────┘
```

### 2.2 Central Framework Repository Structure

**Repository:** `ai-agent-governance-framework`

```
ai-agent-governance-framework/
├── docs/                           # Documentation
├── policies/                       # Risk catalog, mitigations
├── frameworks/                     # YAML configs
├── workflows/                      # Threat modeling, PAR-PROTO
├── templates/                      # Reusable templates
├── terraform/
│   ├── modules/                    # Reusable Terraform modules
│   │   ├── agent-lambda/           # Lambda function module
│   │   ├── audit-trail/            # DynamoDB audit module
│   │   ├── monitoring/             # CloudWatch monitoring module
│   │   ├── secrets/                # Secrets Manager module
│   │   └── governance-gate/        # Governance check module
│   ├── main.tf                     # Core infrastructure
│   ├── variables.tf
│   └── outputs.tf
├── scripts/
│   ├── setup-agent.sh
│   ├── cost-report.sh
│   └── compliance-check.sh
├── .github/workflows/
│   ├── validate.yml                # Framework validation
│   └── release.yml                 # Versioned releases (tags)
├── package.json                    # NPM package metadata (optional)
├── VERSION                         # Semantic versioning (e.g., 2.1.0)
└── README.md
```

**Key Changes:**
- Add `terraform/modules/` for reusable Terraform modules
- Add `.github/workflows/release.yml` for automated versioning
- Add `VERSION` file for semantic versioning
- Optional: Publish as NPM package or Git tags

### 2.3 Agent Repository Structure (Example: Security Agent)

**Repository:** `security-agent`

```
security-agent/
├── src/
│   ├── handlers/
│   │   ├── vulnerability-scanner.py      # Lambda handler
│   │   ├── compliance-checker.py         # Lambda handler
│   │   └── security-audit.py             # Lambda handler
│   ├── lib/
│   │   ├── scanner-engines/              # Trivy, Grype, etc.
│   │   └── reporting/
│   ├── config/
│   │   ├── agent-config.yml              # Agent-specific config
│   │   └── scan-policies.yml             # Scanning rules
│   └── tests/
│       ├── unit/
│       └── integration/
├── terraform/
│   ├── main.tf                           # Agent-specific infrastructure
│   ├── variables.tf
│   ├── backend.tf                        # S3 backend for state
│   └── terraform.tfvars.example
├── framework/                            # Git submodule
│   └── @ai-agent-governance-framework -> (submodule link)
├── docker/
│   ├── Dockerfile                        # Lambda container image
│   ├── requirements.txt                  # Python dependencies
│   └── .dockerignore
├── deploy/
│   ├── lambda-config.json                # Lambda environment config
│   └── event-triggers.json               # EventBridge rules
├── .github/workflows/
│   ├── ci.yml                            # Build, test, scan
│   ├── deploy-dev.yml                    # Deploy to dev
│   ├── deploy-prod.yml                   # Deploy to prod (with approval)
│   └── governance-check.yml              # Framework compliance check
├── docs/
│   ├── README.md                         # Agent documentation
│   ├── RUNBOOK.md                        # Operations guide
│   └── THREAT-MODEL.md                   # STRIDE assessment
├── .framework-version                    # Tracks framework version (e.g., v2.1.0)
├── package.json                          # Framework version dependency
└── README.md
```

**Framework Version Management:**
```json
// package.json
{
  "name": "security-agent",
  "version": "1.0.0",
  "dependencies": {
    "@ai-governance/framework": "^2.1.0"  // Framework version
  }
}
```

**Or using Git Submodules:**
```bash
# Add framework as submodule
git submodule add https://github.com/org/ai-agent-governance-framework.git framework

# Pin to specific version
cd framework
git checkout v2.1.0
cd ..
git add framework
git commit -m "Pin framework to v2.1.0"
```

### 2.4 Agent-Specific Terraform Configuration

**File:** `security-agent/terraform/main.tf`

```hcl
# Import framework modules
module "governance_framework" {
  source = "../framework/terraform/modules"
}

module "security_agent_lambda" {
  source = "../framework/terraform/modules/agent-lambda"

  agent_name          = "security-agent"
  agent_tier          = 3  # Tier 3 - Operations
  handler             = "handlers/vulnerability-scanner.handler"
  runtime             = "python3.11"
  memory_size         = 1024
  timeout             = 300

  # Use framework's IAM policies
  iam_policy_arns = [
    module.governance_framework.tier3_policy_arn
  ]

  # Environment variables
  environment_variables = {
    FRAMEWORK_VERSION     = "v2.1.0"
    AGENT_TIER            = "3"
    AUDIT_TRAIL_TABLE     = module.governance_framework.audit_trail_table
    SECRETS_PREFIX        = "security-agent/"
    COST_BUDGET_MONTHLY   = "100"
  }

  # EventBridge triggers
  event_rules = [
    {
      name        = "daily-vulnerability-scan"
      schedule    = "cron(0 2 * * ? *)"  # 2 AM daily
      description = "Daily security vulnerability scan"
    },
    {
      name        = "code-commit-scan"
      event_pattern = jsonencode({
        source      = ["aws.codecommit"]
        detail-type = ["CodeCommit Repository State Change"]
      })
    }
  ]
}

module "security_monitoring" {
  source = "../framework/terraform/modules/monitoring"

  agent_name     = "security-agent"
  log_group_name = "/aws/lambda/security-agent"

  alarms = [
    {
      name      = "security-scan-failures"
      metric    = "Errors"
      threshold = 5
      period    = 300
    },
    {
      name      = "critical-vulnerabilities-found"
      metric    = "CriticalVulnerabilities"
      threshold = 1
      period    = 60
    }
  ]
}

module "audit_trail" {
  source = "../framework/terraform/modules/audit-trail"

  agent_name = "security-agent"
  tier       = 3
}

# Agent-specific resources
resource "aws_s3_bucket" "scan_reports" {
  bucket = "security-agent-scan-reports-${var.environment}"

  tags = {
    Agent     = "security-agent"
    Tier      = "3"
    Framework = "v2.1.0"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "scan_reports_lifecycle" {
  bucket = aws_s3_bucket.scan_reports.id

  rule {
    id     = "archive-old-reports"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555  # 7 years
    }
  }
}

# Secrets for agent
resource "aws_secretsmanager_secret" "security_agent_secrets" {
  name        = "security-agent/api-keys"
  description = "API keys for security scanning tools"

  kms_key_id = module.governance_framework.secrets_kms_key_id
}
```

### 2.5 Dockerfile for Lambda Container

**File:** `security-agent/docker/Dockerfile`

```dockerfile
# Base image with Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements
COPY docker/requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Install security scanning tools
RUN yum install -y wget && \
    wget https://github.com/aquasecurity/trivy/releases/download/v0.45.0/trivy_0.45.0_Linux-64bit.tar.gz && \
    tar zxvf trivy_0.45.0_Linux-64bit.tar.gz && \
    mv trivy /usr/local/bin/ && \
    rm trivy_0.45.0_Linux-64bit.tar.gz

# Copy agent source code
COPY src/ ${LAMBDA_TASK_ROOT}/

# Copy framework policies (from submodule)
COPY framework/policies/ ${LAMBDA_TASK_ROOT}/framework/policies/
COPY framework/frameworks/ ${LAMBDA_TASK_ROOT}/framework/frameworks/

# Set handler
CMD ["handlers.vulnerability-scanner.handler"]
```

**File:** `security-agent/docker/requirements.txt`

```
boto3==1.34.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-aws-lambda==0.42b0
pyyaml==6.0.1
requests==2.31.0
python-json-logger==2.0.7
```

### 2.6 CI/CD Pipeline (GitHub Actions)

**File:** `security-agent/.github/workflows/deploy-prod.yml`

```yaml
name: Deploy Security Agent to Production

on:
  push:
    branches:
      - main
    paths:
      - 'src/**'
      - 'terraform/**'
      - 'docker/**'
      - '.github/workflows/deploy-prod.yml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'prod'
        type: choice
        options:
          - dev
          - staging
          - prod

env:
  AWS_REGION: us-east-1
  FRAMEWORK_VERSION: v2.1.0
  AGENT_TIER: 3

jobs:
  # Job 1: Framework Compliance Check
  governance-check:
    runs-on: ubuntu-latest
    outputs:
      approved: ${{ steps.check.outputs.approved }}
    steps:
      - name: Checkout agent repo
        uses: actions/checkout@v4
        with:
          submodules: recursive  # Pull framework submodule

      - name: Check framework version compatibility
        id: check
        run: |
          CURRENT_VERSION=$(cat .framework-version)
          REQUIRED_VERSION="v2.1.0"

          if [ "$CURRENT_VERSION" != "$REQUIRED_VERSION" ]; then
            echo "❌ Framework version mismatch: $CURRENT_VERSION != $REQUIRED_VERSION"
            exit 1
          fi

          echo "✅ Framework version: $CURRENT_VERSION"
          echo "approved=true" >> $GITHUB_OUTPUT

      - name: Validate agent configuration
        run: |
          cd framework
          python3 scripts/validate-agent-config.py \
            --config ../src/config/agent-config.yml \
            --tier 3

      - name: Check budget compliance
        run: |
          cd framework
          ./scripts/compliance-check.sh \
            --agent security-agent \
            --tier 3 \
            --budget-limit 100

      - name: Validate secrets configuration
        run: |
          aws secretsmanager describe-secret \
            --secret-id security-agent/api-keys \
            --region $AWS_REGION

  # Job 2: Security Scanning
  security-scan:
    runs-on: ubuntu-latest
    needs: governance-check
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Run secret scanning
        run: |
          cd framework/workflows/threat-modeling
          ./scripts/scan-secrets.sh ../../..

      - name: Scan for PII
        run: |
          cd framework
          ./scripts/scan-pii.sh ../src

      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Job 3: Build and Push Docker Image
  build:
    runs-on: ubuntu-latest
    needs: security-scan
    outputs:
      image-tag: ${{ steps.build-image.outputs.image-tag }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: security-agent
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:latest \
            -f docker/Dockerfile .

          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

          echo "image-tag=$IMAGE_TAG" >> $GITHUB_OUTPUT

  # Job 4: Deploy Infrastructure with Terraform
  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: production
      url: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/security-agent
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        working-directory: terraform
        run: terraform init

      - name: Terraform Plan
        working-directory: terraform
        env:
          TF_VAR_image_tag: ${{ needs.build.outputs.image-tag }}
        run: |
          terraform plan \
            -var="environment=prod" \
            -var="image_tag=${{ needs.build.outputs.image-tag }}" \
            -out=tfplan

      - name: Terraform Apply
        working-directory: terraform
        run: terraform apply -auto-approve tfplan

      - name: Update Lambda function code
        run: |
          aws lambda update-function-code \
            --function-name security-agent-prod \
            --image-uri ${{ steps.login-ecr.outputs.registry }}/security-agent:${{ needs.build.outputs.image-tag }}

  # Job 5: Cost Tracking
  cost-tracking:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Record deployment cost
        run: |
          cd framework
          ./scripts/cost-report.sh \
            --agent security-agent \
            --tier 3 \
            --deployment-id ${{ github.sha }} \
            --timestamp $(date -u +"%Y-%m-%dT%H:%M:%SZ")

      - name: Check budget compliance
        run: |
          MONTHLY_BUDGET=100
          CURRENT_SPEND=$(aws ce get-cost-and-usage \
            --time-period Start=2025-10-01,End=2025-10-31 \
            --granularity MONTHLY \
            --metrics UnblendedCost \
            --filter file://filter.json \
            --query 'ResultsByTime[0].Total.UnblendedCost.Amount' \
            --output text)

          if (( $(echo "$CURRENT_SPEND > $MONTHLY_BUDGET" | bc -l) )); then
            echo "❌ Budget exceeded: \$$CURRENT_SPEND > \$$MONTHLY_BUDGET"
            exit 1
          fi

          echo "✅ Budget OK: \$$CURRENT_SPEND / \$$MONTHLY_BUDGET"

  # Job 6: Audit Trail
  audit-trail:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Record audit event
        run: |
          aws dynamodb put-item \
            --table-name governance-audit-trail \
            --item '{
              "agent_id": {"S": "security-agent"},
              "timestamp": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"},
              "event_type": {"S": "DEPLOYMENT"},
              "tier": {"N": "3"},
              "user": {"S": "${{ github.actor }}"},
              "commit_sha": {"S": "${{ github.sha }}"},
              "framework_version": {"S": "'$FRAMEWORK_VERSION'"},
              "status": {"S": "SUCCESS"}
            }'

      - name: Generate compliance report
        run: |
          cd framework
          ./scripts/compliance-check.sh \
            --agent security-agent \
            --generate-report \
            --output ../compliance-report.json

      - name: Upload compliance report
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report
          path: compliance-report.json
          retention-days: 2555  # 7 years
```

### 2.7 Other Agent Repositories

The same structure applies to:

1. **it-ops-agent** - Infrastructure operations (Tier 3)
2. **ai-agent** - AI/ML operations (Tier 3)
3. **architect-agent** - System design and evaluation (Tier 4)

Each repository:
- Imports framework as Git submodule or NPM package
- Maintains `.framework-version` file
- Has agent-specific Dockerfile and Lambda handlers
- Uses framework Terraform modules
- Implements governance checks in CI/CD

---

## 3. Approach 2: Monorepo Architecture

### 3.1 Repository Layout

```
ai-agent-governance-framework/  (SINGLE REPOSITORY)
├── framework/                   # Core framework (existing content)
├── agents/
│   ├── security/                # Security agent
│   ├── it-ops/                  # IT Operations agent
│   ├── ai/                      # AI/ML operations agent
│   └── architect/               # Architect agent
├── deploy/                      # Shared deployment config
└── .github/workflows/           # Unified CI/CD
```

### 3.2 Complete Monorepo Structure

```
ai-agent-governance-framework/
├── framework/                           # Core governance framework
│   ├── docs/
│   ├── policies/
│   ├── frameworks/
│   ├── workflows/
│   ├── templates/
│   ├── scripts/
│   │   ├── setup-agent.sh
│   │   ├── cost-report.sh
│   │   ├── compliance-check.sh
│   │   └── validate-agent-config.py
│   └── terraform/
│       ├── modules/                     # Reusable Terraform modules
│       │   ├── agent-lambda/
│       │   ├── audit-trail/
│       │   ├── monitoring/
│       │   ├── secrets/
│       │   └── governance-gate/
│       ├── main.tf                      # Shared infrastructure
│       ├── variables.tf
│       └── outputs.tf
│
├── agents/
│   ├── security/                        # Security Agent (Tier 3)
│   │   ├── src/
│   │   │   ├── handlers/
│   │   │   │   ├── vulnerability_scanner.py
│   │   │   │   ├── compliance_checker.py
│   │   │   │   └── security_audit.py
│   │   │   ├── lib/
│   │   │   │   ├── scanner_engines/
│   │   │   │   └── reporting/
│   │   │   ├── config/
│   │   │   │   ├── agent-config.yml
│   │   │   │   └── scan-policies.yml
│   │   │   └── tests/
│   │   ├── terraform/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── docker/
│   │   │   ├── Dockerfile
│   │   │   └── requirements.txt
│   │   ├── deploy/
│   │   │   ├── lambda-config.json
│   │   │   └── event-triggers.json
│   │   ├── docs/
│   │   │   ├── README.md
│   │   │   ├── RUNBOOK.md
│   │   │   └── THREAT-MODEL.md
│   │   └── VERSION                      # Agent version (e.g., 1.2.0)
│   │
│   ├── it-ops/                          # IT Operations Agent (Tier 3)
│   │   ├── src/
│   │   │   ├── handlers/
│   │   │   │   ├── deployment_automation.py
│   │   │   │   ├── incident_response.py
│   │   │   │   └── resource_scaling.py
│   │   │   ├── lib/
│   │   │   │   ├── orchestration/
│   │   │   │   └── monitoring/
│   │   │   ├── config/
│   │   │   │   ├── agent-config.yml
│   │   │   │   └── deployment-policies.yml
│   │   │   └── tests/
│   │   ├── terraform/
│   │   ├── docker/
│   │   ├── deploy/
│   │   ├── docs/
│   │   └── VERSION
│   │
│   ├── ai/                              # AI/ML Operations Agent (Tier 3)
│   │   ├── src/
│   │   │   ├── handlers/
│   │   │   │   ├── model_training.py
│   │   │   │   ├── model_deployment.py
│   │   │   │   └── model_monitoring.py
│   │   │   ├── lib/
│   │   │   │   ├── mlops/
│   │   │   │   └── model_registry/
│   │   │   ├── config/
│   │   │   │   ├── agent-config.yml
│   │   │   │   └── training-policies.yml
│   │   │   └── tests/
│   │   ├── terraform/
│   │   ├── docker/
│   │   ├── deploy/
│   │   ├── docs/
│   │   └── VERSION
│   │
│   └── architect/                       # Architect Agent (Tier 4)
│       ├── src/
│       │   ├── handlers/
│       │   │   ├── system_design.py
│       │   │   ├── tech_evaluation.py
│       │   │   └── poc_development.py
│       │   ├── lib/
│       │   │   ├── design_patterns/
│       │   │   └── evaluation_framework/
│       │   ├── config/
│       │   │   ├── agent-config.yml
│       │   │   └── design-policies.yml
│       │   └── tests/
│       ├── terraform/
│       ├── docker/
│       ├── deploy/
│       ├── docs/
│       └── VERSION
│
├── deploy/                              # Shared deployment configurations
│   ├── environments/
│   │   ├── dev.tfvars
│   │   ├── staging.tfvars
│   │   └── prod.tfvars
│   ├── kustomize/                       # (Optional: if using Kubernetes)
│   │   ├── base/
│   │   └── overlays/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   ├── helm/                            # (Optional: if using Kubernetes)
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── scripts/
│       ├── deploy-agent.sh
│       └── rollback-agent.sh
│
├── .github/
│   └── workflows/
│       ├── validate-framework.yml       # Framework validation
│       ├── validate-agents.yml          # All agents validation
│       ├── build-security-agent.yml     # Security agent CI/CD
│       ├── build-itops-agent.yml        # IT-Ops agent CI/CD
│       ├── build-ai-agent.yml           # AI agent CI/CD
│       ├── build-architect-agent.yml    # Architect agent CI/CD
│       ├── deploy-all-dev.yml           # Deploy all to dev
│       ├── deploy-all-staging.yml       # Deploy all to staging
│       └── deploy-all-prod.yml          # Deploy all to prod (with approval)
│
├── docs/
│   ├── ARCHITECTURE.md                  # Architecture overview
│   ├── MULTI-REPO-VS-MONOREPO.md        # This document
│   └── AGENT-DEVELOPMENT-GUIDE.md       # Guide for agent development
│
├── scripts/
│   ├── bootstrap.sh                     # Initial setup
│   ├── create-new-agent.sh              # Scaffold new agent
│   └── update-framework-version.sh      # Bump framework version
│
├── FRAMEWORK-VERSION                    # Framework version (e.g., 2.1.0)
├── CHANGELOG.md                         # Changelog for all components
├── package.json                         # Workspace configuration
└── README.md                            # Updated with agent info
```

### 3.3 Agent-Specific Terraform (Monorepo)

**File:** `agents/security/terraform/main.tf`

```hcl
# Reference shared framework modules using relative paths
module "security_agent_lambda" {
  source = "../../../framework/terraform/modules/agent-lambda"

  agent_name          = "security-agent"
  agent_tier          = 3
  handler             = "handlers.vulnerability_scanner.handler"
  runtime             = "python3.11"
  memory_size         = 1024
  timeout             = 300

  # Use framework's IAM policies
  iam_policy_arns = [
    data.terraform_remote_state.framework.outputs.tier3_policy_arn
  ]

  environment_variables = {
    FRAMEWORK_VERSION     = var.framework_version
    AGENT_TIER            = "3"
    AUDIT_TRAIL_TABLE     = data.terraform_remote_state.framework.outputs.audit_trail_table
    SECRETS_PREFIX        = "security-agent/"
    COST_BUDGET_MONTHLY   = "100"
  }
}

# Reference shared framework infrastructure
data "terraform_remote_state" "framework" {
  backend = "s3"
  config = {
    bucket = "ai-governance-terraform-state"
    key    = "framework/terraform.tfstate"
    region = "us-east-1"
  }
}
```

### 3.4 Dockerfile (Monorepo)

**File:** `agents/security/docker/Dockerfile`

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements
COPY agents/security/docker/requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Install security scanning tools
RUN yum install -y wget && \
    wget https://github.com/aquasecurity/trivy/releases/download/v0.45.0/trivy_0.45.0_Linux-64bit.tar.gz && \
    tar zxvf trivy_0.45.0_Linux-64bit.tar.gz && \
    mv trivy /usr/local/bin/ && \
    rm trivy_0.45.0_Linux-64bit.tar.gz

# Copy agent source code
COPY agents/security/src/ ${LAMBDA_TASK_ROOT}/

# Copy framework policies (from same repo)
COPY framework/policies/ ${LAMBDA_TASK_ROOT}/framework/policies/
COPY framework/frameworks/ ${LAMBDA_TASK_ROOT}/framework/frameworks/

CMD ["handlers.vulnerability_scanner.handler"]
```

### 3.5 CI/CD Pipeline (Monorepo)

**File:** `.github/workflows/build-security-agent.yml`

```yaml
name: Build and Deploy Security Agent

on:
  push:
    branches:
      - main
    paths:
      - 'agents/security/**'
      - 'framework/**'
      - '.github/workflows/build-security-agent.yml'
  pull_request:
    paths:
      - 'agents/security/**'
      - 'framework/**'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod

env:
  AWS_REGION: us-east-1
  AGENT_NAME: security-agent
  AGENT_TIER: 3
  AGENT_PATH: agents/security

jobs:
  # Job 1: Detect Changes
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      framework-changed: ${{ steps.changes.outputs.framework }}
      agent-changed: ${{ steps.changes.outputs.agent }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Detect changes
        id: changes
        run: |
          if git diff --name-only HEAD~1 HEAD | grep -q '^framework/'; then
            echo "framework=true" >> $GITHUB_OUTPUT
          else
            echo "framework=false" >> $GITHUB_OUTPUT
          fi

          if git diff --name-only HEAD~1 HEAD | grep -q '^agents/security/'; then
            echo "agent=true" >> $GITHUB_OUTPUT
          else
            echo "agent=false" >> $GITHUB_OUTPUT
          fi

  # Job 2: Governance Check
  governance-check:
    runs-on: ubuntu-latest
    needs: detect-changes
    if: needs.detect-changes.outputs.agent-changed == 'true' || needs.detect-changes.outputs.framework-changed == 'true'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check framework version
        run: |
          FRAMEWORK_VERSION=$(cat FRAMEWORK-VERSION)
          echo "Framework version: $FRAMEWORK_VERSION"

      - name: Validate agent configuration
        run: |
          python3 framework/scripts/validate-agent-config.py \
            --config ${{ env.AGENT_PATH }}/src/config/agent-config.yml \
            --tier ${{ env.AGENT_TIER }}

      - name: Check budget compliance
        run: |
          ./framework/scripts/compliance-check.sh \
            --agent ${{ env.AGENT_NAME }} \
            --tier ${{ env.AGENT_TIER }} \
            --budget-limit 100

  # Job 3: Security Scan
  security-scan:
    runs-on: ubuntu-latest
    needs: governance-check
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run secret scanning
        run: |
          ./framework/workflows/threat-modeling/scripts/scan-secrets.sh ${{ env.AGENT_PATH }}

      - name: Scan for PII
        run: |
          ./framework/scripts/scan-pii.sh ${{ env.AGENT_PATH }}/src

      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: ${{ env.AGENT_PATH }}
          format: 'sarif'
          output: 'trivy-results.sarif'

  # Job 4: Build and Test
  build:
    runs-on: ubuntu-latest
    needs: security-scan
    outputs:
      image-tag: ${{ steps.build-image.outputs.image-tag }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        working-directory: ${{ env.AGENT_PATH }}
        run: |
          pip install -r docker/requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        working-directory: ${{ env.AGENT_PATH }}
        run: |
          pytest src/tests/unit/ -v --cov=src --cov-report=xml

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ env.AGENT_NAME }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build from repo root to access both framework/ and agents/
          docker build \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:latest \
            -f ${{ env.AGENT_PATH }}/docker/Dockerfile .

          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

          echo "image-tag=$IMAGE_TAG" >> $GITHUB_OUTPUT

  # Job 5: Deploy
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
    environment:
      name: ${{ github.event.inputs.environment || 'dev' }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        working-directory: ${{ env.AGENT_PATH }}/terraform
        run: terraform init

      - name: Terraform Plan
        working-directory: ${{ env.AGENT_PATH }}/terraform
        run: |
          terraform plan \
            -var-file="../../../deploy/environments/${{ github.event.inputs.environment || 'dev' }}.tfvars" \
            -var="image_tag=${{ needs.build.outputs.image-tag }}" \
            -out=tfplan

      - name: Terraform Apply
        working-directory: ${{ env.AGENT_PATH }}/terraform
        run: terraform apply -auto-approve tfplan

  # Job 6: Post-Deployment Validation
  post-deployment:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run smoke tests
        run: |
          aws lambda invoke \
            --function-name ${{ env.AGENT_NAME }}-${{ github.event.inputs.environment || 'dev' }} \
            --payload '{"test": true}' \
            response.json

          cat response.json

          # Check for errors
          if grep -q "errorMessage" response.json; then
            echo "❌ Lambda invocation failed"
            exit 1
          fi

          echo "✅ Smoke test passed"

      - name: Record audit event
        run: |
          aws dynamodb put-item \
            --table-name governance-audit-trail \
            --item '{
              "agent_id": {"S": "${{ env.AGENT_NAME }}"},
              "timestamp": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"},
              "event_type": {"S": "DEPLOYMENT"},
              "tier": {"N": "${{ env.AGENT_TIER }}"},
              "user": {"S": "${{ github.actor }}"},
              "commit_sha": {"S": "${{ github.sha }}"},
              "environment": {"S": "${{ github.event.inputs.environment || 'dev' }}"},
              "status": {"S": "SUCCESS"}
            }'
```

**File:** `.github/workflows/deploy-all-prod.yml`

```yaml
name: Deploy All Agents to Production

on:
  workflow_dispatch:
    inputs:
      agents:
        description: 'Agents to deploy (comma-separated: security,it-ops,ai,architect or "all")'
        required: true
        default: 'all'

jobs:
  # Sequential deployment with approval gates
  deploy-security:
    if: contains(github.event.inputs.agents, 'security') || github.event.inputs.agents == 'all'
    uses: ./.github/workflows/build-security-agent.yml
    with:
      environment: prod
    secrets: inherit

  deploy-itops:
    if: contains(github.event.inputs.agents, 'it-ops') || github.event.inputs.agents == 'all'
    needs: deploy-security
    uses: ./.github/workflows/build-itops-agent.yml
    with:
      environment: prod
    secrets: inherit

  deploy-ai:
    if: contains(github.event.inputs.agents, 'ai') || github.event.inputs.agents == 'all'
    needs: deploy-itops
    uses: ./.github/workflows/build-ai-agent.yml
    with:
      environment: prod
    secrets: inherit

  deploy-architect:
    if: contains(github.event.inputs.agents, 'architect') || github.event.inputs.agents == 'all'
    needs: deploy-ai
    uses: ./.github/workflows/build-architect-agent.yml
    with:
      environment: prod
    secrets: inherit

  post-deployment:
    needs: [deploy-security, deploy-itops, deploy-ai, deploy-architect]
    runs-on: ubuntu-latest
    steps:
      - name: Generate deployment report
        run: |
          echo "# Deployment Report" > report.md
          echo "Timestamp: $(date -u)" >> report.md
          echo "Agents: ${{ github.event.inputs.agents }}" >> report.md
          echo "Environment: prod" >> report.md

      - name: Notify team
        run: |
          # Send Slack notification
          curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
            -H 'Content-Type: application/json' \
            -d '{"text": "🚀 Production deployment completed for agents: ${{ github.event.inputs.agents }}"}'
```

### 3.6 Workspace Configuration

**File:** `package.json` (for NPM workspaces)

```json
{
  "name": "ai-agent-governance-framework",
  "version": "2.1.0",
  "private": true,
  "workspaces": [
    "framework",
    "agents/*"
  ],
  "scripts": {
    "validate:all": "npm run validate --workspaces",
    "test:all": "npm run test --workspaces",
    "build:all": "npm run build --workspaces",
    "deploy:dev": "npm run deploy:dev --workspaces",
    "deploy:prod": "npm run deploy:prod --workspaces"
  },
  "devDependencies": {
    "lerna": "^8.0.0"
  }
}
```

**File:** `agents/security/package.json`

```json
{
  "name": "@ai-governance/security-agent",
  "version": "1.0.0",
  "description": "Security scanning and compliance agent",
  "scripts": {
    "validate": "python3 ../../framework/scripts/validate-agent-config.py --config src/config/agent-config.yml",
    "test": "cd src && pytest tests/",
    "build": "docker build -t security-agent -f docker/Dockerfile ../..",
    "deploy:dev": "cd terraform && terraform apply -var-file=../../deploy/environments/dev.tfvars",
    "deploy:prod": "cd terraform && terraform apply -var-file=../../deploy/environments/prod.tfvars"
  },
  "dependencies": {
    "@ai-governance/framework": "workspace:^2.1.0"
  }
}
```

### 3.7 Framework Version Management

**File:** `scripts/update-framework-version.sh`

```bash
#!/bin/bash
# Update framework version and propagate to all agents

set -e

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
  echo "Usage: $0 <new-version>"
  echo "Example: $0 2.2.0"
  exit 1
fi

echo "Updating framework version to $NEW_VERSION..."

# Update framework version file
echo "$NEW_VERSION" > FRAMEWORK-VERSION

# Update package.json
jq ".version = \"$NEW_VERSION\"" package.json > package.json.tmp
mv package.json.tmp package.json

# Update all agent package.json dependencies
for agent in agents/*/; do
  if [ -f "$agent/package.json" ]; then
    echo "Updating $agent..."
    cd "$agent"
    jq ".dependencies[\"@ai-governance/framework\"] = \"workspace:^$NEW_VERSION\"" package.json > package.json.tmp
    mv package.json.tmp package.json
    cd ../..
  fi
done

echo "✅ Framework version updated to $NEW_VERSION"
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Run tests: npm run test:all"
echo "3. Commit: git commit -am 'Bump framework to v$NEW_VERSION'"
echo "4. Tag: git tag -a v$NEW_VERSION -m 'Release v$NEW_VERSION'"
echo "5. Push: git push && git push --tags"
```

---

## 4. CI/CD Pipeline Comparison

### 4.1 Multi-Repo CI/CD Characteristics

**Pros:**
- ✅ **Independent pipelines** - Each agent has its own CI/CD
- ✅ **Faster builds** - Only builds changed agent
- ✅ **Clear ownership** - Team owns entire repo + pipeline
- ✅ **Independent deployments** - Deploy agents separately
- ✅ **Easier rollbacks** - Roll back single agent without affecting others

**Cons:**
- ❌ **Pipeline duplication** - Similar workflows across repos
- ❌ **Framework updates** - Must update submodule in all repos
- ❌ **Cross-agent testing** - Difficult to test agent interactions
- ❌ **Coordinated releases** - Hard to deploy multiple agents together

**Example: Deploying framework update across all agents**

```bash
# Multi-repo: Update framework in all agent repos
for repo in security-agent it-ops-agent ai-agent architect-agent; do
  cd $repo
  git submodule update --remote framework
  git checkout -b update-framework-v2.2.0
  git add framework
  git commit -m "Update framework to v2.2.0"
  git push origin update-framework-v2.2.0
  gh pr create --title "Update framework to v2.2.0" --body "Updates framework dependency"
  cd ..
done

# Requires 4 separate PRs and approvals
```

### 4.2 Monorepo CI/CD Characteristics

**Pros:**
- ✅ **Single source of truth** - One repo, one version
- ✅ **Atomic changes** - Framework + all agents updated together
- ✅ **Easier cross-agent testing** - Test agent interactions
- ✅ **Coordinated releases** - Deploy multiple agents together
- ✅ **Simplified dependencies** - Framework changes propagate automatically

**Cons:**
- ❌ **Longer CI times** - Must validate all agents (mitigated by path filters)
- ❌ **Larger repo** - More code to clone
- ❌ **Branch conflicts** - Multiple teams working in same repo
- ❌ **Deployment coupling** - One agent bug can block all deployments

**Example: Deploying framework update across all agents**

```bash
# Monorepo: Update framework version
./scripts/update-framework-version.sh 2.2.0

# Creates single PR with all changes
git checkout -b update-framework-v2.2.0
git add .
git commit -m "Bump framework to v2.2.0"
git push origin update-framework-v2.2.0
gh pr create --title "Update framework to v2.2.0" --body "Updates framework and all agent dependencies"

# Single PR, all agents updated atomically
```

### 4.3 Path-Based Triggering (Monorepo Optimization)

```yaml
# Only build security agent when its files change
on:
  push:
    paths:
      - 'agents/security/**'
      - 'framework/**'  # Also trigger on framework changes
```

This prevents unnecessary builds while ensuring agents rebuild when framework changes.

---

## 5. Versioning & Dependency Management

### 5.1 Multi-Repo Versioning

**Framework Versioning:**
```bash
# Framework repo
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
```

**Agent Versioning:**
```json
// security-agent/package.json
{
  "name": "security-agent",
  "version": "1.2.0",
  "dependencies": {
    "@ai-governance/framework": "^2.1.0"
  }
}
```

**Git Submodule Approach:**
```bash
# In security-agent repo
cd framework
git fetch --tags
git checkout v2.1.0
cd ..
git add framework
git commit -m "Update framework to v2.1.0"
```

**Pros:**
- ✅ Agents can pin to specific framework versions
- ✅ Independent versioning (agent v1.2.0 + framework v2.1.0)
- ✅ Gradual rollout of framework updates

**Cons:**
- ❌ Version drift across agents
- ❌ Manual updates required in each repo
- ❌ Difficult to track which agents use which framework version

### 5.2 Monorepo Versioning

**Single Version File:**
```bash
# FRAMEWORK-VERSION
2.1.0
```

**Automatic Propagation:**
```bash
# Update all agents to use new framework version
./scripts/update-framework-version.sh 2.2.0

# All agents updated in single commit
```

**Pros:**
- ✅ All agents always use same framework version
- ✅ No version drift
- ✅ Atomic updates across all components
- ✅ Easy to track version history

**Cons:**
- ❌ All agents must update together
- ❌ No gradual rollout (all-or-nothing)
- ❌ Framework breaking changes affect all agents

### 5.3 Semantic Versioning Strategy

**Framework Version:** `MAJOR.MINOR.PATCH`
- **MAJOR:** Breaking changes (e.g., 2.0.0 → 3.0.0)
- **MINOR:** New features, backward-compatible (e.g., 2.1.0 → 2.2.0)
- **PATCH:** Bug fixes (e.g., 2.1.0 → 2.1.1)

**Agent Version:** `MAJOR.MINOR.PATCH`
- **MAJOR:** Breaking API changes
- **MINOR:** New capabilities
- **PATCH:** Bug fixes

**Dependency Rules:**
- Multi-repo: Agents use `^` (caret) for minor updates: `^2.1.0` (allows 2.1.x and 2.2.0, not 3.0.0)
- Monorepo: Agents use `workspace:^` for local workspace linking

---

## 6. Secrets Management

Both approaches use **AWS Secrets Manager** with KMS encryption.

### 6.1 Secrets Structure

**Framework-Level Secrets:**
```
/governance/shared/
  ├── audit-trail-key         # Audit trail encryption key
  ├── cost-api-key            # Cost tracking API key
  └── compliance-cert         # Compliance certificates
```

**Agent-Specific Secrets:**
```
/agents/security-agent/
  ├── api-keys                # Security scanner API keys
  ├── credentials             # Third-party credentials
  └── tokens                  # Access tokens

/agents/it-ops-agent/
  ├── ssh-keys                # Deployment SSH keys
  ├── k8s-tokens              # Kubernetes tokens
  └── api-keys                # Cloud provider keys

/agents/ai-agent/
  ├── model-registry-key      # Model registry credentials
  ├── training-secrets        # Training job secrets
  └── api-keys                # ML platform API keys

/agents/architect-agent/
  ├── design-tool-keys        # Design tool API keys
  └── research-tokens         # Research API tokens
```

### 6.2 Secrets Access (Multi-Repo)

**Terraform:**
```hcl
# security-agent/terraform/main.tf
data "aws_secretsmanager_secret" "agent_secrets" {
  name = "agents/security-agent/api-keys"
}

resource "aws_lambda_function" "security_agent" {
  environment {
    variables = {
      SECRET_ARN = data.aws_secretsmanager_secret.agent_secrets.arn
    }
  }
}
```

**Lambda Code:**
```python
# security-agent/src/handlers/vulnerability_scanner.py
import boto3
import os

secrets_client = boto3.client('secretsmanager')

def get_secrets():
    secret_arn = os.environ['SECRET_ARN']
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    return json.loads(response['SecretString'])
```

### 6.3 Secrets Access (Monorepo)

Same approach, but secrets paths are more explicit:

```hcl
# agents/security/terraform/main.tf
data "aws_secretsmanager_secret" "agent_secrets" {
  name = "agents/security-agent/api-keys"
}
```

### 6.4 Secrets Rotation

Both approaches use the same rotation strategy:

```hcl
# Framework module: framework/terraform/modules/secrets/main.tf
resource "aws_secretsmanager_secret_rotation" "rotation" {
  secret_id           = aws_secretsmanager_secret.secret.id
  rotation_lambda_arn = aws_lambda_function.rotation_lambda.arn

  rotation_rules {
    automatically_after_days = 30
  }
}
```

---

## 7. Pros & Cons Comparison

### 7.1 Comparison Matrix

| Dimension | Multi-Repo | Monorepo |
|-----------|-----------|----------|
| **Team Ownership** | ✅ Clear (team owns entire repo) | ⚠️ Shared (CODEOWNERS helps) |
| **Release Cadence** | ✅ Independent releases | ⚠️ Coordinated releases |
| **CI/CD Complexity** | ⚠️ Duplicate pipelines | ✅ Centralized, reusable |
| **Dependency Management** | ❌ Manual updates, version drift | ✅ Atomic updates, no drift |
| **Framework Updates** | ❌ Update 4+ repos | ✅ Single update |
| **Cross-Agent Testing** | ❌ Difficult | ✅ Easy |
| **Build Time** | ✅ Fast (only changed agent) | ⚠️ Longer (all agents validated) |
| **Repository Size** | ✅ Small repos | ⚠️ Larger repo |
| **Rollback** | ✅ Independent rollback | ⚠️ All-or-nothing |
| **Onboarding** | ⚠️ Must clone multiple repos | ✅ Single clone |
| **Code Review** | ⚠️ Fragmented across repos | ✅ Centralized |
| **Branching Strategy** | ✅ Simple (per repo) | ⚠️ More conflicts |
| **Secrets Management** | ✅ Same (AWS Secrets Manager) | ✅ Same (AWS Secrets Manager) |
| **Cost Tracking** | ⚠️ Per-repo dashboards | ✅ Unified dashboard |
| **Audit Trail** | ⚠️ Fragmented logs | ✅ Unified audit trail |

### 7.2 Detailed Pros & Cons

#### Multi-Repo

**Pros:**
1. ✅ **Clear ownership** - Each team owns a repo
2. ✅ **Independent releases** - Deploy agents separately
3. ✅ **Isolated failures** - One agent bug doesn't block others
4. ✅ **Smaller blast radius** - Changes affect one agent
5. ✅ **Easier access control** - Repo-level permissions
6. ✅ **Fast CI** - Only builds changed repo
7. ✅ **Technology diversity** - Different languages/tools per agent

**Cons:**
1. ❌ **Framework updates** - Update 4+ repos manually
2. ❌ **Version drift** - Agents on different framework versions
3. ❌ **Duplicate pipelines** - Copy/paste CI/CD configs
4. ❌ **Cross-agent testing** - Difficult to test interactions
5. ❌ **Fragmented audit** - Logs across multiple repos
6. ❌ **Onboarding complexity** - Clone/setup multiple repos
7. ❌ **Coordinated releases** - Hard to deploy all agents together

#### Monorepo

**Pros:**
1. ✅ **Single source of truth** - All code in one place
2. ✅ **Atomic updates** - Framework + all agents updated together
3. ✅ **No version drift** - All agents use same framework
4. ✅ **Simplified CI/CD** - Reusable workflows
5. ✅ **Easy cross-agent testing** - Test agent interactions
6. ✅ **Unified audit trail** - Single commit history
7. ✅ **Fast onboarding** - Clone once, build all
8. ✅ **Refactoring** - Easy to move code between agents
9. ✅ **Code sharing** - Share utilities across agents

**Cons:**
1. ❌ **Larger repo size** - More code to clone
2. ❌ **Longer CI times** - Validate all agents (mitigated by path filters)
3. ❌ **Branch conflicts** - Multiple teams in same repo
4. ❌ **Deployment coupling** - One bug can block all deploys
5. ❌ **Access control** - Need CODEOWNERS for fine-grained permissions
6. ❌ **All-or-nothing updates** - Framework changes affect all agents
7. ❌ **Git performance** - Large repo can slow git operations

### 7.3 Team Size Considerations

**Small Team (3-5 developers):**
- **Monorepo recommended** - Less overhead, easier coordination

**Medium Team (6-15 developers):**
- **Monorepo or Multi-repo** - Depends on team structure

**Large Team (15+ developers):**
- **Multi-repo recommended** - Better isolation, clear ownership

---

## 8. Recommendation

### 8.1 Recommendation: Monorepo with Per-Agent Folders

**For a small cross-functional team, use the Monorepo approach.**

**Rationale:**

1. ✅ **Lower overhead** - Single repo, single CI/CD setup
2. ✅ **Easier framework updates** - Atomic updates, no version drift
3. ✅ **Simplified onboarding** - Clone once, see all code
4. ✅ **Better collaboration** - All code visible, easier code review
5. ✅ **Unified audit trail** - Single commit history for compliance
6. ✅ **Cost efficiency** - Reuse CI/CD infrastructure
7. ✅ **Faster iteration** - Test cross-agent features easily

**When to reconsider:**
- Team grows beyond 15 developers
- Agents need independent release cycles
- Different teams own different agents with minimal coordination
- Security requirements demand strict repo-level access control

### 8.2 Hybrid Approach (Future Option)

If the team grows or requirements change:

**Phase 1:** Start with Monorepo (current recommendation)
**Phase 2:** Extract agents to separate repos if needed

```
ai-agent-governance-framework/     (Core framework)
├── framework/
├── docs/
└── terraform/modules/

security-agent/                    (Extracted repo)
├── src/
├── terraform/
├── docker/
└── framework/ → (submodule)

it-ops-agent/                      (Extracted repo)
├── src/
├── terraform/
├── docker/
└── framework/ → (submodule)
```

The framework Terraform modules are designed to be reusable, making extraction easy.

---

## 9. Migration Path

### 9.1 Immediate Next Steps (Monorepo Approach)

1. **Create agent directories**
```bash
mkdir -p agents/{security,it-ops,ai,architect}
```

2. **Scaffold security agent** (example)
```bash
./framework/scripts/setup-agent.sh \
  --tier 3 \
  --name security-agent \
  --output agents/security
```

3. **Create Terraform modules**
```bash
mkdir -p framework/terraform/modules/{agent-lambda,audit-trail,monitoring,secrets,governance-gate}
```

4. **Implement first agent** (Security Agent)
   - Vulnerability scanning (Trivy, Grype)
   - Compliance checking (CIS benchmarks)
   - Security audit reports

5. **Create CI/CD workflows**
   - `.github/workflows/build-security-agent.yml`
   - Path filters: `agents/security/**` and `framework/**`

6. **Deploy to dev environment**
```bash
cd agents/security/terraform
terraform init
terraform apply -var-file=../../../deploy/environments/dev.tfvars
```

7. **Iterate** on other agents (IT-Ops, AI, Architect)

### 9.2 Implementation Timeline

**Week 1-2: Foundation**
- Create monorepo structure
- Refactor existing terraform into modules
- Set up CI/CD workflows

**Week 3-4: Security Agent**
- Implement vulnerability scanner
- Create compliance checker
- Deploy to dev/staging/prod

**Week 5-6: IT-Ops Agent**
- Implement deployment automation
- Create incident response handlers
- Integrate with monitoring

**Week 7-8: AI Agent**
- Implement model training pipelines
- Create model deployment automation
- Set up model monitoring

**Week 9-10: Architect Agent**
- Implement system design tools
- Create tech evaluation framework
- Build POC automation

**Week 11-12: Integration & Testing**
- Cross-agent testing
- Multi-agent workflows
- Documentation & runbooks

---

## 10. Conclusion

This document provides a comprehensive comparison of **Multi-Repo** and **Monorepo** architectures for extending the AI Agent Governance Framework.

**Key Takeaways:**

1. **Monorepo is recommended** for small cross-functional teams (3-15 developers)
2. Both approaches use the same **AWS serverless infrastructure** (Lambda, DynamoDB, S3, CloudWatch)
3. **Terraform modules** make the framework reusable in both approaches
4. **GitHub Actions** provides CI/CD with path-based filtering for efficiency
5. **AWS Secrets Manager** handles secrets in both approaches
6. **Migration path** is straightforward: start with monorepo, extract repos later if needed

**Next Steps:**
1. Review and approve this architecture
2. Begin implementation with Security Agent
3. Update main README.md with agent information
4. Create agent development guide

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Maintained By:** AI Governance Team