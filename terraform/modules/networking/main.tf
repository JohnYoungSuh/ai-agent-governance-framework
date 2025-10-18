# Networking Module
# Control: SEC-002, MI-011 (Network Isolation)
# Purpose: VPC and network security configuration for AI agents

variable "agent_id" {
  description = "Agent identifier"
  type        = string
}

variable "agent_tier" {
  description = "Agent tier (tier1-observer, tier2-developer, tier3-operations, tier4-architect)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for outbound internet access"
  type        = bool
  default     = true
}

variable "control_id" {
  description = "Governance control IDs this module implements"
  type        = list(string)
  default     = ["SEC-002", "MI-011"]
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# ============================================================================
# VPC
# ============================================================================
resource "aws_vpc" "agent_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name       = "${var.agent_id}-vpc"
      AgentID    = var.agent_id
      AgentTier  = var.agent_tier
      ControlID  = join(",", var.control_id)
      ManagedBy  = "Terraform"
      Framework  = "AI-Agent-Governance-v2.0"
      Purpose    = "Network isolation for AI agent"
    }
  )
}

# ============================================================================
# Internet Gateway
# ============================================================================
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.agent_vpc.id

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-igw"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
    }
  )
}

# ============================================================================
# Subnets
# ============================================================================
data "aws_availability_zones" "available" {
  state = "available"
}

# Private subnets for Lambda functions
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.agent_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-private-${count.index + 1}"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
      Type      = "private"
    }
  )
}

# Public subnets for NAT Gateway
resource "aws_subnet" "public" {
  count                   = var.enable_nat_gateway ? 2 : 0
  vpc_id                  = aws_vpc.agent_vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-public-${count.index + 1}"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
      Type      = "public"
    }
  )
}

# ============================================================================
# NAT Gateway (for private subnet outbound internet access)
# ============================================================================
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-nat-eip"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
    }
  )

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-nat"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
    }
  )

  depends_on = [aws_internet_gateway.igw]
}

# ============================================================================
# Route Tables
# ============================================================================

# Private route table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.agent_vpc.id

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-private-rt"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
      Type      = "private"
    }
  )
}

# Private route to NAT Gateway (if enabled)
resource "aws_route" "private_nat" {
  count                  = var.enable_nat_gateway ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat[0].id
}

# Private subnet associations
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Public route table
resource "aws_route_table" "public" {
  count  = var.enable_nat_gateway ? 1 : 0
  vpc_id = aws_vpc.agent_vpc.id

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-public-rt"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
      Type      = "public"
    }
  )
}

# Public route to Internet Gateway
resource "aws_route" "public_igw" {
  count                  = var.enable_nat_gateway ? 1 : 0
  route_table_id         = aws_route_table.public[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

# Public subnet associations
resource "aws_route_table_association" "public" {
  count          = var.enable_nat_gateway ? 2 : 0
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# ============================================================================
# Security Groups
# ============================================================================

# Lambda security group (restrictive egress)
resource "aws_security_group" "lambda" {
  name        = "${var.agent_id}-lambda-sg"
  description = "Security group for ${var.agent_id} Lambda functions with least-privilege egress"
  vpc_id      = aws_vpc.agent_vpc.id

  # No ingress rules - Lambda doesn't need inbound

  # Egress: HTTPS only (for LLM API calls, AWS API calls)
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound for API calls (LLM, AWS services)"
  }

  # Egress: DynamoDB endpoint (if using VPC endpoint)
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "DynamoDB VPC endpoint access"
  }

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-lambda-sg"
      AgentID   = var.agent_id
      AgentTier = var.agent_tier
      ControlID = join(",", var.control_id)
      Purpose   = "Lambda function security group with least-privilege egress"
    }
  )
}

# ============================================================================
# VPC Endpoints (for private AWS service access)
# ============================================================================

# DynamoDB VPC Endpoint (Gateway endpoint, no cost)
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id          = aws_vpc.agent_vpc.id
  service_name    = "com.amazonaws.${data.aws_region.current.name}.dynamodb"
  route_table_ids = [aws_route_table.private.id]

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-dynamodb-endpoint"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
      Service   = "DynamoDB"
    }
  )
}

# S3 VPC Endpoint (Gateway endpoint, no cost)
resource "aws_vpc_endpoint" "s3" {
  vpc_id          = aws_vpc.agent_vpc.id
  service_name    = "com.amazonaws.${data.aws_region.current.name}.s3"
  route_table_ids = [aws_route_table.private.id]

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-s3-endpoint"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
      Service   = "S3"
    }
  )
}

# Secrets Manager VPC Endpoint (Interface endpoint, incurs cost)
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.agent_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-secretsmanager-endpoint"
      AgentID   = var.agent_id
      ControlID = "SEC-001,MI-003"
      Service   = "SecretsManager"
    }
  )
}

# CloudWatch Logs VPC Endpoint (Interface endpoint)
resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.agent_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-logs-endpoint"
      AgentID   = var.agent_id
      ControlID = "MI-004,MI-019"
      Service   = "CloudWatch Logs"
    }
  )
}

# Security group for VPC endpoints
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.agent_id}-vpc-endpoints-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.agent_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-vpc-endpoints-sg"
      AgentID   = var.agent_id
      ControlID = join(",", var.control_id)
    }
  )
}

# ============================================================================
# VPC Flow Logs (for network monitoring and compliance)
# ============================================================================
resource "aws_flow_log" "vpc" {
  count                = var.enable_vpc_flow_logs ? 1 : 0
  vpc_id               = aws_vpc.agent_vpc.id
  traffic_type         = "ALL"
  iam_role_arn         = aws_iam_role.flow_logs[0].arn
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.flow_logs[0].arn

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-vpc-flow-logs"
      AgentID   = var.agent_id
      ControlID = "MI-004,MI-011"
      Purpose   = "Network traffic monitoring and compliance"
    }
  )
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count             = var.enable_vpc_flow_logs ? 1 : 0
  name              = "/aws/vpc/${var.agent_id}-flow-logs"
  retention_in_days = 90

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-flow-logs"
      AgentID   = var.agent_id
      ControlID = "MI-004,MI-019"
    }
  )
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0
  name  = "${var.agent_id}-vpc-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-flow-logs-role"
      AgentID   = var.agent_id
      ControlID = "MI-011"
    }
  )
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0
  name  = "${var.agent_id}-flow-logs-policy"
  role  = aws_iam_role.flow_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = aws_cloudwatch_log_group.flow_logs[0].arn
      }
    ]
  })
}

# ============================================================================
# Data sources
# ============================================================================
data "aws_region" "current" {}

# ============================================================================
# Outputs
# ============================================================================
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.agent_vpc.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.agent_vpc.cidr_block
}

output "private_subnet_ids" {
  description = "Private subnet IDs for Lambda deployment"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = var.enable_nat_gateway ? aws_subnet.public[*].id : []
}

output "lambda_security_group_id" {
  description = "Security group ID for Lambda functions"
  value       = aws_security_group.lambda.id
}

output "nat_gateway_id" {
  description = "NAT Gateway ID (if enabled)"
  value       = var.enable_nat_gateway ? aws_nat_gateway.nat[0].id : null
}

output "vpc_endpoint_dynamodb_id" {
  description = "DynamoDB VPC endpoint ID"
  value       = aws_vpc_endpoint.dynamodb.id
}

output "vpc_endpoint_s3_id" {
  description = "S3 VPC endpoint ID"
  value       = aws_vpc_endpoint.s3.id
}

output "vpc_endpoint_secretsmanager_id" {
  description = "Secrets Manager VPC endpoint ID"
  value       = aws_vpc_endpoint.secretsmanager.id
}

output "vpc_flow_logs_group_name" {
  description = "CloudWatch log group name for VPC flow logs"
  value       = var.enable_vpc_flow_logs ? aws_cloudwatch_log_group.flow_logs[0].name : null
}
