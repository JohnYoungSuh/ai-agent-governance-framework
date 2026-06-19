# AI Agent Governance Framework - Internal v2.1

A comprehensive, risk-based framework for deploying, governing, and managing AI agents as autonomous team members using the **Problem → Action → Results (PAR)** model.

**Internal Repository**: This is a private fork customized for internal use.

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
- **Structured Logging**: JSON schemas for audit trails, SIEM events, and cost tracking with OCSF mapping
- **OpenTelemetry SIEM Integration**: Real-time security event emission to Splunk, Datadog, CloudWatch
- **Jira Integration**: PKI-signed CR approvals with webhook receiver and CI/CD enforcement
- **Cooperative Game Theory**: AI agent improvement proposals with Pareto efficiency and review validation
- **Terraform Modules**: 7 modular IaC components with control_id tags and audit correlation
- **AWS Compliance Checks**: 12 automated checks for KMS, IAM, Secrets Manager, CloudTrail, S3
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
- **[Unified AI Agent Governance Framework v3.0](UNIFIED-AI-AGENT-GOVERNANCE-FRAMEWORK-v3.0.md)** ⭐ - Complete framework specification (SINGLE SOURCE OF TRUTH)

### Governance Kernel (Patent Pending) ⭐ **NEW**
- **[US Patent Application](docs/US-PATENT-APPLICATION.md)** ⭐ - Full USPTO-compliant utility patent application draft.
- **[Patent Technical Disclosure](docs/PATENT-DISCLOSURE.md)** ⭐ - The authoritative technical specification for the Atomic Governance Transaction system.
- *[DEPRECATED] GPIS Requirements & Gap Analysis* - See `docs/` for historical reference.

### Architecture & Deployment (NEW in v2.1)
- **[Kubernetes Deployment Guide](docs/KUBERNETES-DEPLOYMENT-GUIDE.md)** ⭐ - Complete K8s deployment with Helm charts and monitoring
- **[Multi-Repo vs Monorepo Architecture](docs/MULTI-REPO-VS-MONOREPO-ARCHITECTURE.md)** ⭐ - Complete guide for extending framework to specialized agent services

### DevContainer Patterns
- **[Devcontainer Vendor Image Workflow](docs/DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md)** - Using vendor images for efficiency
- **[Devcontainer Governance Integration](docs/DEVCONTAINER-GOVERNANCE-INTEGRATION.md)** - Governance alignment and token accountability
- **[Devcontainer Quick Start](docs/DEVCONTAINER-QUICKSTART.md)** - Quick setup guide
- **[Devcontainer Debugging Patterns](docs/DEVCONTAINER-DEBUGGING-PATTERNS.md)** ⭐ **NEW** - AI agent patterns for debugging vendor image issues

### Risk Management (v2.0)
- **[Risk Catalog](policies/risk-catalog.md)** ⭐ - 18 AI-specific risks with scoring
- **[Mitigation Catalog](policies/mitigation-catalog.md)** ⭐ - 21 controls with implementation code
- **[Threat Modeling Guide](workflows/threat-modeling/guide.md)** ⭐ - STRIDE-based security assessment

### Compliance & Security (NEW in v2.1)
- **[Compliance Documentation](compliance/README.md)** ⭐ - Authority to Operate (ATO) and regulatory compliance
- **[System Security Plan (SSP)](compliance/ssp/README.md)** ⭐ - NIST 800-53 Rev 5 control implementation (88% complete)
- **[AI Agent Safety Policies](policies/agent-safety-policies.md)** ⭐ **NEW** - Mandatory safety protocols for destructive operations
- **[Control Mappings](policies/control-mappings.md)** - NIST 800-53 → CCI → Framework mappings (FedRAMP, SOC 2, ISO 27001)
- **[Logging Policy](policies/logging-policy.md)** - Complete AU family implementation with SIEM integration
- **[Schemas](policies/schemas/)** - JSON schemas for audit trails, SIEM events, and cost records
- **[OpenTelemetry SIEM Integration](docs/OPENTELEMETRY-SIEM-INTEGRATION.md)** ⭐ - Real-time security event emission with OCSF mapping
- **[Jira Integration Guide](docs/JIRA-INTEGRATION-GUIDE.md)** ⭐ - PKI-signed approvals with webhook integration
- **[Cooperative Game Theory](docs/COOPERATIVE-GAME-THEORY.md)** ⭐ - AI improvement proposals with Pareto efficiency

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
│   ├── agent-safety-policies.md   # ⭐ AI agent safety protocols (NEW)
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
│   ├── compliance-check.sh        # Run compliance checks
│   ├── otel-siem-emitter.py       # ⭐ OpenTelemetry SIEM event emitter (NEW)
│   ├── test-siem-emitter.sh       # ⭐ SIEM emitter test suite (NEW)
│   ├── validate-jira-approval.py  # ⭐ Jira CR validation with PKI (NEW)
│   ├── jira-webhook-receiver.py   # ⭐ Real-time Jira webhook handler (NEW)
│   └── game_theory/               # ⭐ Game theory validators (NEW)
│       ├── cooperative_improvement_validator.py  # Pareto improvements
│       └── raci_game_validator.py                # Stackelberg model
├── terraform/                     # ⭐ Infrastructure as Code (NEW)
│   ├── README.md                  # AWS deployment guide
│   ├── main.tf                    # Terraform configuration
│   ├── main-modular-v2.tf         # ⭐ Modular architecture (NEW)
│   ├── modules/                   # ⭐ Reusable modules (NEW)
│   │   ├── secrets_manager/       # Secrets with audit correlation
│   │   ├── cloudtrail/            # Multi-region trail
│   │   ├── kms/                   # KMS key management
│   │   └── s3_audit_logs/         # Audit log storage
│   └── lambda/                    # Lambda functions
├── test-output/                   # ⭐ Test artifacts (NEW)
│   └── siem-events/               # SIEM event test output
└── docs/ENHANCEMENTS.md           # ⭐ v2.0 enhancements
```

## 🚀 Quick Start

### 1. Start with the Quick Reference (5 minutes)

```bash
# Clone the repository
git clone https://github.com/JohnYoungSuh/ai-agent-governance-framework-internal.git
cd ai-agent-governance-framework-internal

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
# Set up a new Tier 3 agent (requires Jira CR for prod)
./scripts/setup-agent.sh --tier 3 --name "customer-support-bot" \
  --environment prod --jira-cr-id CR-2025-1042

# Run threat model (REQUIRED for Tier 3/4)
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent customer-support-bot --tier 3

# Configure observability
cp frameworks/observability-config.yml \
   agents/customer-support-bot/observability.yml

# Validate Jira approval (PKI signature verification)
./scripts/validate-jira-approval.py deployment-agent CR-2025-1042 "Change Manager"

# Run compliance checks with SIEM integration
./scripts/compliance-check-enhanced.sh --agent customer-support-bot \
  --environment prod --jira-cr-id CR-2025-1042

# Deploy (after approvals and mitigations)
```

### 4. Monitor and Track Costs

```bash
# Generate cost report with OpenTelemetry
./scripts/cost-report.sh --agent doc-analyzer

# Check compliance (12 AWS checks + SIEM events)
./scripts/compliance-check-enhanced.sh --agent doc-analyzer

# Test SIEM emitter (validates OCSF mapping)
./scripts/test-siem-emitter.sh

# View SIEM event output
cat test-output/siem-events/test-01-compliance-check.json

# View metrics (if observability configured)
# http://localhost:9090/metrics
```

## 🔑 Key Features in v2.1

### OpenTelemetry SIEM Integration
- **Real-time security event emission** to any OTLP-compatible backend (Splunk, Datadog, CloudWatch)
- **OCSF-compliant** (Open Cybersecurity Schema Framework) event mapping
- **Distributed tracing** with audit correlation via `audit_id` and `jira_cr_id`
- **Fallback mode** - works without OpenTelemetry dependencies
- **10/10 passing tests** with comprehensive validation

```bash
# Emit SIEM event
python3 scripts/otel-siem-emitter.py \
  --agent-id security-agent \
  --control-id SEC-001 \
  --event-type compliance_check \
  --severity info \
  --description "KMS key rotation enabled" \
  --audit-id audit-12345 \
  --jira-cr-id CR-2025-1042
```

### Jira Integration with PKI
- **PKI digital signatures** (RSA-SHA256) on all Tier 3/4 change requests
- **Real-time webhook receiver** with Redis caching and Slack notifications
- **CI/CD enforcement** - deployments halt without approved Jira CR
- **Automatic correlation** - all audit trails include `jira_reference`

```bash
# Validate Jira CR with PKI signature verification
./scripts/validate-jira-approval.py deployment-agent CR-2025-1042 "Change Manager"
```

### Cooperative Game Theory
- **Pareto improvements** - AI agents propose changes where no one is worse off
- **Truthful reporting** - VCG mechanism incentivizes honest proposals
- **Review validation** - Statistical bounds ensure humans don't rubber-stamp
- **Social welfare maximization** - Optimize total value within constraints

```bash
# Validate AI improvement proposal
python3 scripts/game_theory/cooperative_improvement_validator.py \
  --proposal proposals/PROP-2025-001.json \
  --validate-all
```

### AWS Compliance Automation
- **12 automated checks**: KMS, IAM, Secrets Manager, CloudTrail, S3
- **Audit trail generation** conforming to JSON schema
- **SIEM event emission** for every compliance check
- **Control coverage**: SEC-001, SC-028, AU-002, MI-003, IA-002

```bash
# Run compliance checks with SIEM integration
./scripts/compliance-check-enhanced.sh \
  --agent security-agent \
  --environment prod \
  --jira-cr-id CR-2025-1042
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

- **Issues**: Internal issue tracker
- **Discussions**: Internal communications channels
- **Email**: youngs@suhlabs.com
- **Upstream**: [Public Repository](https://github.com/JohnYoungSuh/ai-agent-governance-framework)

## ✅ Verification & Evidence

All features are implemented, tested, and committed to the repository. For verification:

- **[VERIFICATION-EVIDENCE.md](docs/archive/VERIFICATION-EVIDENCE.md)** - Complete evidence with commit hashes, file locations, code samples (archived)
- **[COMMIT-EVIDENCE.txt](COMMIT-EVIDENCE.txt)** - Git commit proof with grep verification commands

**Key Commits:**
- `f26581b` (2025-10-18) - OpenTelemetry SIEM Integration
- `1cd3332` (2025-10-18) - Game Theory + Terraform Modules
- `9bf3af0` (2025-10-18) - Jira Integration + Schemas

**Verification Commands:**
```bash
# View implementation commits
git log --oneline -10

# Verify OCSF mapping
grep -A 10 "ocsf_mapping" policies/schemas/siem-event.json

# Verify PKI signing
grep -A 5 "validate_pki_signature" scripts/validate-jira-approval.py

# Run tests (10/10 pass)
./scripts/test-siem-emitter.sh

# View working SIEM event
cat test-output/siem-events/test-01-compliance-check.json
```

---

**Built for teams who want AI agents to be accountable, cost-effective team members.**
