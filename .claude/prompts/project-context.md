# AI Agent Governance Framework - Project Context

## Project Overview
This is an internal AI Agent Governance Framework (v2.1) for deploying, governing, and managing AI agents as autonomous team members using the Problem → Action → Results (PAR) model.

## Key Capabilities
- **Risk Management**: 18 AI-specific risks with 21 mitigation controls
- **Compliance**: NIST 800-53 Rev 5 (88% complete, 298/339 controls), FedRAMP ready
- **Threat Modeling**: STRIDE-based assessment for Tier 3/4 agents
- **Observability**: OpenTelemetry integration with SIEM event emission (OCSF-compliant)
- **Infrastructure**: Terraform modules, Kubernetes/Helm charts, AWS Lambda deployment
- **Jira Integration**: PKI-signed change request approvals
- **Game Theory**: Cooperative improvement proposals with Pareto efficiency

## Agent Tiers
- **Tier 1 (Observer)**: Read-only, docs/analysis ($0.10-$0.50/task)
- **Tier 2 (Developer)**: Dev environment only ($0.50-$5.00/task)
- **Tier 3 (Operations)**: Production with approvals ($1.00-$10.00/task)
- **Tier 4 (Architect)**: Design & research ($5.00-$50.00/task)

## Key Documentation Paths
- Quick Reference: `docs/QUICK-REFERENCE.md`
- Governance Policy: `docs/GOVERNANCE-POLICY.md`
- Risk Catalog: `policies/risk-catalog.md`
- Mitigation Catalog: `policies/mitigation-catalog.md`
- Control Mappings: `policies/control-mappings.md`
- SSP Controls: `compliance/ssp/control-implementation.md`
- Threat Modeling: `workflows/threat-modeling/guide.md`
- Kubernetes Deployment: `docs/KUBERNETES-DEPLOYMENT-GUIDE.md`
- OpenTelemetry SIEM: `docs/OPENTELEMETRY-SIEM-INTEGRATION.md`

## Key Scripts
- Setup agent: `./scripts/setup-agent.sh`
- Compliance checks: `./scripts/compliance-check-enhanced.sh`
- SIEM emitter: `./scripts/otel-siem-emitter.py`
- Jira validation: `./scripts/validate-jira-approval.py`
- Threat modeling: `./workflows/threat-modeling/scripts/run-threat-model.sh`

## Important Schemas
- Audit trail: `policies/schemas/audit-trail.json`
- SIEM events: `policies/schemas/siem-event.json`
- Cost tracking: `policies/schemas/agent-cost-record.json`

## Governance Principles
1. Human Primacy - Humans have final authority
2. Transparency - All actions are auditable
3. Accountability - Clear ownership and responsibility
4. Safety - Risk-based controls and approvals
5. Cost Efficiency - ROI tracking and optimization

## Common Tasks
- Deploy Tier 1/2 agent: Use `setup-agent.sh`, implement MI-001, MI-009, MI-021
- Deploy Tier 3/4 agent: Requires threat model + Jira CR approval
- Run compliance checks: Use `compliance-check-enhanced.sh` with SIEM integration
- Validate Jira approval: Use `validate-jira-approval.py` for PKI verification
- Monitor costs: Use `cost-report.sh` with OpenTelemetry metrics

## Project Structure Highlights
- `/docs` - Core documentation
- `/policies` - Policy documents and schemas
- `/compliance` - SSP, assessments, continuous monitoring
- `/workflows` - Threat modeling and PAR-PROTO patterns
- `/frameworks` - Agent tiers, decision matrix, observability config
- `/templates` - Deployment, cost tracking, review templates
- `/examples` - Real-world tier-based examples
- `/scripts` - Automation scripts
- `/terraform` - IaC modules for AWS
- `/deploy` - Kubernetes/Helm charts

## Git Status
- Branch: master
- Recent commits focus on governance policy, token accountability, guardrails
- Multiple untracked files for new features (policies, schemas, workflows)
