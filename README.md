# AI Agent Governance Framework v2.0

A comprehensive, risk-based framework for deploying, governing, and managing AI agents as autonomous team members using the **Problem → Action → Results (PAR)** model.

## 🎯 Overview

This framework enables organizations to:
- Deploy AI agents with clear governance and accountability
- **Identify and mitigate 18 AI-specific risks systematically**
- **Conduct STRIDE-based threat modeling for production agents**
- Manage costs and ROI with real-time monitoring
- Maintain security, compliance, and comprehensive audit trails
- **Monitor agent operations with OpenTelemetry observability**
- Scale AI operations with human oversight

## 🆕 What's New in v2.0

Version 2.0 introduces major security and risk management enhancements:

- **Risk Catalog**: 18 AI-specific risks with scoring and detection methods
- **Mitigation Catalog**: 21 implementation-ready controls with code samples
- **Threat Modeling**: STRIDE-based assessment tool (required for Tier 3/4)
- **Observability Framework**: OpenTelemetry configuration for comprehensive monitoring
- **Enhanced PAR Cycle**: Security and observability built into workflow
- **Quick Reference Guide**: Printable daily operations reference

**See [ENHANCEMENTS.md](ENHANCEMENTS.md) for complete details.**

## 📚 Documentation

### Quick Start
- **[Quick Reference Guide](docs/QUICK-REFERENCE.md)** ⭐ - Daily operations reference (print and keep handy!)
- **[Quick Start Guide](docs/QUICK-START.md)** - Get started in 15 minutes
- **[What's New in v2.0](ENHANCEMENTS.md)** - Complete list of enhancements

### Core Framework
- **[Workflow Framework](docs/PAR-WORKFLOW-FRAMEWORK.md)** - Enhanced PAR cycle with security gates
- **[Governance & Policy](docs/GOVERNANCE-POLICY.md)** - Security, compliance, and ethical guidelines

### Risk Management (NEW in v2.0)
- **[Risk Catalog](policies/risk-catalog.md)** ⭐ - 18 AI-specific risks with scoring
- **[Mitigation Catalog](policies/mitigation-catalog.md)** ⭐ - 21 controls with implementation code
- **[Threat Modeling Guide](workflows/threat-modeling/guide.md)** ⭐ - STRIDE-based security assessment

## 🏗️ Project Structure

```
ai-agent-governance-framework/
├── docs/                          # Core documentation
│   ├── QUICK-REFERENCE.md         # ⭐ Daily operations guide (NEW)
│   ├── PAR-WORKFLOW-FRAMEWORK.md  # Enhanced workflow patterns
│   ├── GOVERNANCE-POLICY.md       # Governance framework
│   └── QUICK-START.md             # Getting started guide
├── policies/                      # Policy documents
│   ├── risk-catalog.md            # ⭐ 18 AI-specific risks (NEW)
│   ├── mitigation-catalog.md      # ⭐ 21 controls with code (NEW)
│   ├── security-policies.md       # Security requirements
│   ├── compliance-policies.md     # Compliance requirements
│   └── ethical-policies.md        # Ethical guidelines
├── workflows/                     # ⭐ Workflows (NEW)
│   ├── threat-modeling/           # ⭐ STRIDE-based assessment (NEW)
│   │   ├── guide.md              # Comprehensive guide
│   │   ├── scripts/
│   │   │   └── run-threat-model.sh  # Interactive tool
│   │   └── reports/              # Generated threat models
│   └── PAR-PROTO/                # Prototyping workflow
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
└── ENHANCEMENTS.md                # ⭐ v2.0 what's new (NEW)
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

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This framework is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

This framework (v2.0) aligns with and incorporates best practices from:
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
