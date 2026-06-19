# Code Map — AI Agent Governance Framework

> **Purpose:** Find the right file instantly. Map of features → source files.

---

## GPIS — Governance Policy Inquiry Service (The PDP)

| Feature | File |
|---------|------|
| FastAPI server + JWT issuance | `app/main.py` |
| Policy evaluation logic (3 categories) | `app/policy_engine.py` |
| Token-efficient router (template) | `scripts/governance_router.py` |
| Simple rules YAML (zero-token decisions) | `policies/simple_rules.yml` |
| Cache classifier prompt | `scripts/prompts/cache_classifier.txt` |
| Intent router prompt | `scripts/prompts/intent_router.txt` |
| Pattern distillation prompt | `scripts/prompts/distillation.txt` |
| Token router config | `config/token_router.yml` |

---

## Agent Implementations

| Agent | Type | Source |
|-------|------|--------|
| Security Agent | CronJob + Deployment | `agents/security/src/handlers/` |
| IT-Ops Agent | Long-running Deployment | `agents/it-ops/src/handlers/` |
| AI Agent | ML Training CronJob | `agents/ai/src/handlers/training_job.py` |
| Architect Agent | Long-running Deployment | `agents/architect/src/handlers/` |

---

## Policies & Schemas

| Policy | File |
|--------|------|
| ⭐ Audit trail schema (patent anchor) | `policies/schemas/audit-trail.json` |
| SIEM event schema | `policies/schemas/siem-event.json` |
| Agent cost record schema | `policies/schemas/agent-cost-record.json` |
| Agent safety policies | `policies/agent-safety-policies.md` |
| 18 AI-specific risks | `policies/risk-catalog.md` |
| 21 mitigation controls | `policies/mitigation-catalog.md` |
| NIST 800-53 control mappings | `policies/control-mappings.md` |
| Simple governance rules | `policies/simple_rules.yml` |

---

## Compliance & Certification

| Topic | File |
|-------|------|
| SSP overview | `compliance/ssp/README.md` |
| 298/339 control implementation | `compliance/ssp/control-implementation.md` |
| POA&M (41 open controls) | `compliance/ssp/poam.md` |
| ATO pathway | `compliance/README.md` |

---

## Infrastructure & Deployment

| Layer | Files |
|-------|-------|
| Helm chart (all agents) | `deploy/helm/ai-agent/` |
| Agent-specific values | `deploy/helm/ai-agent/values-security.yaml` etc. |
| Terraform (AWS Lambda) | `terraform/main-modular-v2.tf` + `terraform/modules/` |
| KMS module | `terraform/modules/kms/` |
| Secrets Manager module | `terraform/modules/secrets_manager/` |
| CloudTrail module | `terraform/modules/cloudtrail/` |
| S3 audit log storage | `terraform/modules/s3_audit_logs/` |

---

## Automation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup-agent.sh` | New agent provisioning |
| `scripts/compliance-check-enhanced.sh` | 12 AWS compliance checks |
| `scripts/otel-siem-emitter.py` | SIEM event emission (OTLP) |
| `scripts/test-siem-emitter.sh` | SIEM test suite (10/10 pass) |
| `scripts/validate-jira-approval.py` | PKI-signed CR validation |
| `scripts/jira-webhook-receiver.py` | Real-time Jira webhook |
| `scripts/benchmark_token_savings.py` | Token efficiency benchmark |
| `scripts/cost-report.sh` | Cost reporting |
| `scripts/game_theory/cooperative_improvement_validator.py` | Pareto proposal validation |

---

## Workflows & Patterns

| Pattern | Files |
|---------|-------|
| Multi-agent PAR-PROTO | `workflows/PAR-PROTO/README.md` |
| STRIDE threat modeling | `workflows/threat-modeling/guide.md` |
| Threat modeling script | `workflows/threat-modeling/scripts/run-threat-model.sh` |
| Jira integration | `workflows/PAR-PROTO/integrations/jira-integration.md` |

---

## Patent & Documentation

| Document | File |
|----------|------|
| ⭐ USPTO patent application | `docs/US-PATENT-APPLICATION.md` |
| ⭐ Technical patent disclosure | `docs/PATENT-DISCLOSURE.md` |
| Governance agent architecture | `docs/GOVERNANCE-AGENT-ARCHITECTURE.md` |
| Token efficiency guide | `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md` |
| Unified framework v3.0 | `UNIFIED-AI-AGENT-GOVERNANCE-FRAMEWORK-v3.0.md` |
| 16 guardrail rules | `docs/GOVERNANCE_GUARDRAILS.md` |


---

## Agent Rules & Knowledge

| Rule | File |
|------|------|
| Agent identity & responsibilities | `.agents/rules/agent-role.md` |
| Development workflow | `.agents/rules/workflow.md` |
| Governance architecture invariants | `.agents/rules/governance-rules.md` |
| Security & compliance standards | `.agents/rules/security-overrides.md` |
| Testing strategy | `.agents/rules/testing.md` |
| Post-session validation checklist | `.agents/rules/post-goal-validation.md` |
| Project source map | `.agents/rules/project-knowledge.md` |
| IDE-agnostic rules | `.agents/rules/ide-rules.md` |
| QA/Tester Agent role | `.agents/rules/qa-tester-role.md` |
| Project context prompt | `.agents/rules/project-context.md` |
| Project context template | `.agents/rules/template-project-context.md` |
| ⭐ Root cause playbooks | `LESSONS_LEARNED.md` |
| ⭐ Current backlog | `NEXT_RELEASE_TODO.md` |
| 60-second orientation | `SESSION_START.md` |
