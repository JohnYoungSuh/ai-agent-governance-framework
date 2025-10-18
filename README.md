# AI Agent Governance Framework v2.1

A comprehensive, risk-based framework for deploying, governing, and managing AI agents as autonomous team members using the **Problem → Action → Results (PAR)** model.

## 🎯 Overview

This framework enables organizations to:
- Deploy AI agents with clear governance and accountability
- **Identify and mitigate 18 AI-specific risks systematically**
- **Conduct STRIDE-based threat modeling for production agents**
- **Achieve regulatory compliance** (FedRAMP, NIST 800-53, SOC 2, ISO 27001)
- Manage costs and ROI with real-time monitoring
- Maintain security, compliance, and comprehensive audit trails
- **Monitor agent operations with OpenTelemetry observability**
- Scale AI operations with human oversight

## 🆕 What's New in v2.1

Version 2.1 introduces enterprise-grade compliance, production deployment options, and structured governance:

### Core Framework (v2.0)
- **Risk Catalog**: 18 AI-specific risks with scoring and detection methods
- **Mitigation Catalog**: 21 implementation-ready controls with code samples
- **Threat Modeling**: STRIDE-based assessment tool (required for Tier 3/4)
- **Observability Framework**: OpenTelemetry configuration for comprehensive monitoring
- **Enhanced PAR Cycle**: Security and observability built into workflow
- **Multi-Agent Workflows**: PAR-PROTO pattern for Copilot → Claude development

### New in v2.1 (Enterprise Compliance & Deployment)
- **Compliance Framework**: Complete ATO pathway with NIST 800-53 Rev 5 SSP (88% complete, 298/339 controls)
- **Control Mappings**: NIST → CCI → FedRAMP/SOC 2/ISO 27001 mappings with 14 AI extensions
- **Structured Logging**: JSON schemas for audit trails, SIEM events, and cost tracking
- **Kubernetes Deployment**: Complete Helm charts, Kustomize overlays, and monitoring stack
- **Terraform/AWS**: Infrastructure as Code for serverless Lambda deployments
- **Logging Policy**: Complete NIST AU family implementation with SIEM integration

**See [ENHANCEMENTS.md](ENHANCEMENTS.md) for v2.0 details.**

## 📚 Documentation

### Quick Start
- **[Quick Reference Guide](docs/QUICK-REFERENCE.md)** ⭐ - Daily operations reference (print and keep handy!)
- **[Quick Start Guide](docs/QUICK-START.md)** - Get started in 15 minutes
- **[What's New in v2.0](ENHANCEMENTS.md)** - v2.0 enhancements (risk catalog, threat modeling, observability)

### Core Framework
- **[Workflow Framework](docs/PAR-WORKFLOW-FRAMEWORK.md)** - Enhanced PAR cycle with security gates
- **[Governance & Policy](docs/GOVERNANCE-POLICY.md)** - Security, compliance, and ethical guidelines

### Architecture & Deployment (NEW in v2.1)
- **[Kubernetes Deployment Guide](docs/KUBERNETES-DEPLOYMENT-GUIDE.md)** ⭐ - Complete K8s deployment with Helm charts and monitoring
- **[Multi-Repo vs Monorepo Architecture](docs/MULTI-REPO-VS-MONOREPO-ARCHITECTURE.md)** ⭐ - Complete guide for extending framework to specialized agent services

### Risk Management (v2.0)
- **[Risk Catalog](policies/risk-catalog.md)** ⭐ - 18 AI-specific risks with scoring
- **[Mitigation Catalog](policies/mitigation-catalog.md)** ⭐ - 21 controls with implementation code
- **[Threat Modeling Guide](workflows/threat-modeling/guide.md)** ⭐ - STRIDE-based security assessment

### Compliance & Security (NEW in v2.1)
- **[Compliance Documentation](compliance/README.md)** ⭐ - Authority to Operate (ATO) and regulatory compliance
- **[System Security Plan (SSP)](compliance/ssp/README.md)** ⭐ - NIST 800-53 Rev 5 control implementation (88% complete)
- **[Control Mappings](policies/control-mappings.md)** - NIST 800-53 → CCI → Framework mappings (FedRAMP, SOC 2, ISO 27001)
- **[Logging Policy](policies/logging-policy.md)** - Complete AU family implementation with SIEM integration
- **[Schemas](policies/schemas/)** - JSON schemas for audit trails, SIEM events, and cost records

### Multi-Agent Workflows (v2.0)
- **[PAR-PROTO Workflow](workflows/PAR-PROTO/README.md)** ⭐ - Multi-agent development patterns (Copilot → Claude → Gemini)
- **[Jira Integration](workflows/PAR-PROTO/integrations/jira-integration.md)** - Issue tracking and approvals
- **[Slack Integration](workflows/PAR-PROTO/integrations/slack-integration.md)** - Discussion tracking

## 🏗️ Project Structure

```
ai-agent-governance-framework/
├── docs/                          # Core documentation
│   ├── QUICK-REFERENCE.md         # ⭐ Daily operations guide (NEW)
│   ├── PAR-WORKFLOW-FRAMEWORK.md  # Enhanced workflow patterns
│   ├── GOVERNANCE-POLICY.md       # Governance framework
│   ├── QUICK-START.md             # Getting started guide
│   └── KUBERNETES-DEPLOYMENT-GUIDE.md  # ⭐ K8s deployment (NEW)
├── policies/                      # Policy documents
│   ├── risk-catalog.md            # ⭐ 18 AI-specific risks (NEW)
│   ├── mitigation-catalog.md      # ⭐ 21 controls with code (NEW)
│   ├── control-mappings.md        # ⭐ NIST 800-53 → CCI mappings (NEW)
│   ├── logging-policy.md          # ⭐ AU family implementation (NEW)
│   ├── security-policies.md       # Security requirements
│   ├── compliance-policies.md     # Compliance requirements
│   ├── ethical-policies.md        # Ethical guidelines
│   └── schemas/                   # ⭐ JSON schemas (NEW)
│       ├── audit-trail.json       # Audit log schema
│       ├── siem-event.json        # SIEM event schema
│       └── agent-cost-record.json # Cost tracking schema
├── compliance/                    # ⭐ Compliance documentation (NEW)
│   ├── README.md                  # ATO and compliance overview
│   ├── ssp/                       # System Security Plan
│   │   ├── README.md             # SSP structure and guide
│   │   ├── control-implementation.md  # NIST 800-53 controls (88%)
│   │   ├── control-summary.md    # Control status summary
│   │   ├── poam.md               # Plan of Action & Milestones
│   │   ├── appendices/           # FedRAMP attachments
│   │   ├── diagrams/             # Architecture diagrams
│   │   └── attachments/          # Evidence documents
│   ├── assessments/              # Security assessments
│   └── continuous-monitoring/    # Ongoing compliance evidence
├── workflows/                     # ⭐ Workflows (NEW)
│   ├── threat-modeling/           # ⭐ STRIDE-based assessment (NEW)
│   │   ├── guide.md              # Comprehensive guide
│   │   ├── scripts/
│   │   │   └── run-threat-model.sh  # Interactive tool
│   │   └── reports/              # Generated threat models
│   └── PAR-PROTO/                # ⭐ Multi-agent workflows (NEW)
│       ├── README.md             # Two-agent pattern (Copilot → Claude)
│       ├── three-agent-workflow.md  # Three-agent with Gemini testing
│       ├── integrations/         # Jira & Slack integration guides
│       └── templates/            # Project templates
├── frameworks/                    # Framework definitions
│   ├── observability-config.yml   # ⭐ OpenTelemetry config (NEW)
│   ├── agent-tiers.yml            # Tier definitions
│   ├── decision-matrix.yml        # Authority matrix
│   └── approval-workflows.yml     # Workflow definitions
├── templates/                     # Reusable templates
│   ├── agent-deployment/          # Agent deployment forms
│   ├── cost-tracking/             # Cost tracking templates
│   └── governance-review/         # Review checklists
├── examples/                      # Real-world examples
│   ├── tier1-observer/            # Observer agent examples
│   ├── tier2-developer/           # Developer agent examples
│   ├── tier3-operations/          # Operations agent examples
│   └── tier4-architect/           # Architect agent examples
├── scripts/                       # Automation scripts
│   ├── setup-agent.sh             # New agent setup
│   ├── cost-report.sh             # Generate cost reports
│   └── compliance-check.sh        # Run compliance checks
├── terraform/                     # ⭐ Infrastructure as Code (NEW)
│   ├── README.md                  # AWS deployment guide
│   ├── main.tf                    # Terraform configuration
│   └── lambda/                    # Lambda functions
└── ENHANCEMENTS.md                # ⭐ v2.0 enhancements
```

## 🚀 Quick Start

### 1. Start with the Quick Reference (5 minutes)

```bash
# Clone the repository
git clone https://github.com/JohnYoungSuh/ai-agent-governance-framework.git
cd ai-agent-governance-framework

# Read the quick reference guide
cat docs/QUICK-REFERENCE.md
```

### 2. Deploy Your First Agent (Tier 1/2)

```bash
# Set up a new Tier 1 agent
./scripts/setup-agent.sh --tier 1 --name "doc-analyzer"

# Implement critical mitigations
# - Data leakage prevention (MI-001)
# - Cost monitoring (MI-009)
# - Budget limits (MI-021)

# Review the generated configuration
cat agents/doc-analyzer/config.yml
```

### 3. Deploy a Production Agent (Tier 3) - NEW

```bash
# Set up a new Tier 3 agent
./scripts/setup-agent.sh --tier 3 --name "customer-support-bot"

# Run threat model (REQUIRED for Tier 3/4)
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent customer-support-bot --tier 3

# Configure observability
cp frameworks/observability-config.yml \
   agents/customer-support-bot/observability.yml

# Deploy (after approvals and mitigations)
```

### 4. Monitor and Track Costs

```bash
# Generate cost report
./scripts/cost-report.sh --agent doc-analyzer

# Check compliance
./scripts/compliance-check.sh --agent doc-analyzer

# View metrics (if observability configured)
# http://localhost:9090/metrics
```

## 📦 Deployment Options

### Manual Deployment
Follow the Quick Start guide above for local/manual agent deployment.

### Infrastructure as Code (Terraform - AWS Lambda)
For serverless AWS deployments with full governance controls, see **[Terraform README](terraform/README.md)**:
- AWS infrastructure with Lambda, CloudWatch, DynamoDB, S3
- All 21 mitigation controls implemented
- GitHub Actions integration
- Estimated cost: $50-$575/month

### Kubernetes Deployment
For containerized deployments on Kubernetes clusters, see **[Kubernetes Deployment Guide](docs/KUBERNETES-DEPLOYMENT-GUIDE.md)**:
- Complete Kubernetes manifests for 4 specialized agents
- Helm charts with customizable values
- Kustomize overlays for dev/staging/prod environments
- Prometheus + Grafana monitoring stack
- External Secrets Operator integration
- NetworkPolicy and RBAC security
- Estimated cost: $500-$1,600/month (K8s + AI costs)

### Extending to Specialized Agent Services
Planning to deploy multiple specialized agents (Security, IT-Ops, AI, Architect)? See the **[Multi-Repo vs Monorepo Architecture Guide](docs/MULTI-REPO-VS-MONOREPO-ARCHITECTURE.md)** for:
- Complete comparison of multi-repo vs monorepo approaches
- Detailed folder structures, Dockerfiles, and Kubernetes/Lambda manifests
- CI/CD pipeline designs for GitHub Actions
- Versioning strategy and secrets management
- **Recommendation: Monorepo for small cross-functional teams**

## 📋 Agent Tier Overview

| Tier | Role | Autonomy | Use Cases | Avg Cost/Task |
|------|------|----------|-----------|---------------|
| 1 | Observer | Read-only | Docs, analysis, Q&A | $0.10-$0.50 |
| 2 | Developer | Dev env only | Coding, testing, refactoring | $0.50-$5.00 |
| 3 | Operations | Production (approved) | Deployments, runbooks | $1.00-$10.00 |
| 4 | Architect | Design & research | System design, POCs | $5.00-$50.00 |

## 🔒 Governance Principles

1. **Human Primacy** - Humans always have final authority
2. **Transparency** - All agent actions are auditable
3. **Accountability** - Clear ownership and responsibility
4. **Safety** - Risk-based controls and approvals
5. **Cost Efficiency** - ROI tracking and optimization

## 📊 Success Metrics

- **Overall ROI Target**: >5:1 (time/cost saved vs. spent)
- **Policy Compliance**: <1% violation rate
- **Agent Quality**: <5% defect rate on completed tasks
- **Human Time Saved**: >70% reallocated to strategic work

## 📜 Compliance & Certification Status

| Framework | Status | Documentation |
|-----------|--------|---------------|
| **FedRAMP Moderate** | 📋 Ready for 3PAO | [SSP](compliance/ssp/), [Controls](compliance/ssp/control-implementation.md) |
| **NIST 800-53 Rev 5** | ✅ 88% (298/339) | [Control Summary](compliance/ssp/control-summary.md) |
| **FISMA** | 📋 SSP Complete | [Compliance README](compliance/README.md) |
| **SOC 2 Type II** | 🔄 Scheduled 2026 Q2 | [Control Mappings](policies/control-mappings.md) |
| **ISO 27001:2022** | 📋 Controls Mapped | [Control Mappings](policies/control-mappings.md) |
| **NIST AI RMF** | ✅ Complete | [Risk Catalog](policies/risk-catalog.md), AI Extensions |

**Legend**: ✅ Complete | 📋 Documentation ready | 🔄 In progress

**Path to ATO**: See [compliance/README.md](compliance/README.md) for the complete Authority to Operate pathway, including POA&M status and 3PAO engagement timeline.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This framework is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

This framework (v2.1) aligns with and incorporates best practices from:
- **NIST 800-53 Rev 5** - Federal security control baseline (298/339 controls implemented)
- **FedRAMP** - Federal risk and authorization management program
- **Microsoft Responsible AI** - Fairness, reliability, safety, privacy, security, inclusiveness, transparency, accountability
- **FINOS AI Risk Catalog** - AI-specific risk identification and categorization
- **NIST AI Risk Management Framework** - Risk assessment lifecycle and governance
- **OWASP Top 10 for LLMs** - LLM-specific security vulnerabilities
- **MITRE ATLAS** - Adversarial threat landscape for AI systems
- **STRIDE** (Microsoft) - Threat modeling methodology
- **OECD AI Principles** - International AI governance standards
- **EU AI Act** - Regulatory compliance requirements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JohnYoungSuh/ai-agent-governance-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JohnYoungSuh/ai-agent-governance-framework/discussions)
- **Email**: youngs@suhlabs.com

---

**Built for teams who want AI agents to be accountable, cost-effective team members.**
