# AI Agent Governance Framework - Internal v2.1 - Quick Reference

> **Print and keep handy for daily agent operations**

---

## 🎯 What's New in v2.0

| Enhancement | What It Does | When to Use |
|------------|--------------|-------------|
| **Risk Catalog** | 18 AI-specific risks | Before any deployment |
| **Threat Modeling** | STRIDE-based assessment | Required for Tier 3/4 |
| **Observability** | OpenTelemetry + metrics | All agents |
| **Mitigation Catalog** | 17+ controls | When risks identified |

---

## 📋 18 AI Risks (Must Know)

### 🔴 Critical Risks (Always Address)
- **RI-001**: Hallucination - Agent generates false information
- **RI-014**: Prompt Injection - Malicious input hijacks agent
- **RI-015**: Data to Hosted LLM - Secrets sent to provider
- **RI-018**: Cost Overrun - Runaway spending

### 🟡 High Risks (Address for Tier 3+)
- **RI-002**: Model Versioning - Unexpected behavior changes
- **RI-006**: Bias & Discrimination - Unfair outputs
- **RI-011**: Vector Store Leak - Sensitive data in RAG
- **RI-016**: Regulatory Compliance - Legal violations

### 🟢 Medium Risks (Monitor)
- **RI-003**: Non-Deterministic - Inconsistent outputs
- **RI-009**: Data Drift - Stale data degrades performance

**See full catalog**: `policies/risk-catalog.md`

---

## 🛡️ Top 10 Mitigations (Quick Action)

| ID | Mitigation | Quick Fix | Cost |
|----|-----------|-----------|------|
| **MI-001** | Data Leakage Prevention | PII redaction script | Low |
| **MI-002** | Input Filtering | Injection pattern scanner | Low |
| **MI-004** | Observability | OpenTelemetry setup | $300/mo |
| **MI-009** | Cost Monitoring | Budget alerts | Free |
| **MI-010** | Version Pinning | Lock model version | Free |
| **MI-013** | Citations | Add source links | +10% tokens |
| **MI-015** | LLM-as-Judge | Validation LLM call | 2x cost |
| **MI-017** | AI Firewall | `llm_guard` library | $0.01/req |
| **MI-020** | Tier Enforcement | Check decision matrix | Free |
| **MI-021** | Budget Limits | Hard caps | Free |

---

## 🔄 Enhanced PAR Cycle

```
┌─────────────────────────────────────────────┐
│ PROBLEM                                     │
│ ├─ Define requirements                      │
│ ├─ ⭐ Run threat model (NEW for Tier 3/4)  │
│ └─ Get approval                             │
├─────────────────────────────────────────────┤
│ ACTION                                      │
│ ├─ Build with AI assistance                │
│ ├─ Log iterations                           │
│ ├─ ⭐ Monitor with OpenTelemetry (NEW)     │
│ └─ Test thoroughly                          │
├─────────────────────────────────────────────┤
│ RESULTS                                     │
│ ├─ Generate handoff summary                │
│ ├─ ⭐ Professional validation (NEW)        │
│ ├─ Validate quality                         │
│ └─ Archive with audit trail                │
└─────────────────────────────────────────────┘
```

---

## 🎯 Threat Modeling in 5 Minutes

### STRIDE Checklist

Quick questions to ask:

- [ ] **S**poofing: Can someone impersonate user/agent?
- [ ] **T**ampering: Can data/model be modified?
- [ ] **R**epudiation: Can actions be unaudited?
- [ ] **I**nfo Disclosure: Can sensitive data leak?
- [ ] **D**enial of Service: Can agent be made unavailable?
- [ ] **E**levation: Can agent exceed permissions?

**Tool**: `./workflows/threat-modeling/scripts/run-threat-model.sh --agent <name> --tier <1-4>`

---

## 📊 Risk Scoring Formula

```
Risk Score = Likelihood (1-5) × Impact (1-5)

Priority:
🔴 Critical (15-25): Must fix before deploy
🟡 High (8-14):     Fix soon, monitor closely
🟢 Low (1-7):       Accept or monitor

Example:
RI-015 (Data to LLM): 5 × 5 = 25 🔴
RI-018 (Cost): 3 × 2 = 6 🟢
```

---

## 🔧 Quick Commands

### Setup New Agent
```bash
# 1. Create agent
./scripts/setup-agent.sh --tier 3 --name my-agent

# 2. Run threat model (if Tier 3/4)
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent my-agent --tier 3

# 3. Configure observability
cp frameworks/observability-config.yml \
   agents/my-agent/observability.yml

# 4. Deploy
# (after approvals)
```

### Check Agent Health
```bash
# Cost check
./scripts/cost-report.sh --agent my-agent

# Compliance check
./scripts/compliance-check.sh --agent my-agent

# View metrics
# http://localhost:9090/metrics (Prometheus)
```

### Emergency Response
```bash
# If agent misbehaving
./scripts/pause-agent.sh --agent my-agent --reason "policy-violation"

# Review logs
tail -f /var/log/ai-agents/my-agent/agent.log

# Check budget
./scripts/cost-report.sh --agent my-agent --today
```

---

## 🚨 Alert Response Guide

### Budget Alert (75% consumed)
1. Check `cost-report.sh` for breakdown
2. Review if usage is expected
3. If normal: Increase budget
4. If abnormal: Investigate + pause if needed

### Policy Violation
1. **STOP**: Pause agent immediately
2. Review audit logs for details
3. Assess severity (security incident?)
4. Fix issue + update policies
5. Resume only after approval

### Hallucination Detected
1. Review LLM-as-Judge reports
2. Check input data quality
3. Add validation rules (MI-015)
4. Consider model version change
5. Increase human review %

### Model Version Change
1. **BEFORE ACCEPTING**: Run full SAT
2. Compare outputs with old version
3. Check for regressions
4. Update version pin in config
5. Document change in git

---

## 📐 Decision Matrix (Tier-Based)

| Action | T1 | T2 | T3 | T4 | Human? |
|--------|----|----|----|----|--------|
| Read data | ✅ | ✅ | ✅ | ✅ | No |
| Modify dev | ❌ | ✅ | ✅ | POC | Post-review |
| Deploy staging | ❌ | ❌ | ✅ | ❌ | Pre-approve |
| Deploy prod | ❌ | ❌ | ✅ | ❌ | Pre + Dual |
| Change arch | ❌ | ❌ | ❌ | Propose | Approve |
| Modify security | ❌ | ❌ | ❌ | ❌ | **ALWAYS** |

---

## 💰 Cost Tracking Cheat Sheet

### Token Costs (Claude Sonnet 4.5)
```
Input:  $0.003 per 1K tokens
Output: $0.015 per 1K tokens

Example task:
- Input: 15K tokens × $0.003 = $0.045
- Output: 5K tokens × $0.015 = $0.075
- Total: $0.12
```

### Budget Defaults
```yaml
Tier 1: $10/day, $200/month
Tier 2: $100/day, $2000/month
Tier 3: $250/day, $5000/month
Tier 4: $500/task (strategic)
```

### ROI Targets
```
Tier 1: 10:1 (save $10 for every $1 spent)
Tier 2: 5:1
Tier 3: 3:1
Tier 4: Strategic value (not time-based)
```

---

## 🎓 Best Practices Reminder

### DO ✅
- Run threat model for Tier 3/4 agents
- Monitor cost daily
- Pin model versions
- Log all decisions
- Test before production
- Review quarterly

### DON'T ❌
- Skip threat modeling for production
- Ignore cost alerts
- Auto-upgrade models without testing
- Deploy without approvals
- Use agent for untested use cases
- Hardcode secrets

---

## 📚 Essential Files to Know

```
Your Framework/
├── policies/
│   ├── risk-catalog.md           ⭐ Read first
│   └── mitigation-catalog.md     ⭐ Solutions here
│
├── workflows/
│   ├── PAR-PROTO/               # Prototyping
│   └── threat-modeling/         ⭐ Required for Tier 3/4
│
├── frameworks/
│   ├── agent-tiers.yml          # Tier definitions
│   ├── decision-matrix.yml      # What each tier can do
│   └── observability-config.yml ⭐ Monitoring setup
│
└── templates/
    └── [all your templates]
```

---

## 🔗 Quick Links

| Resource | Location |
|----------|----------|
| Risk Catalog | `policies/risk-catalog.md` |
| Mitigation Catalog | `policies/mitigation-catalog.md` |
| Threat Modeling | `workflows/threat-modeling/guide.md` |
| Observability | `frameworks/observability-config.yml` |
| Enhancement Summary | `ENHANCEMENTS.md` |
| Original Framework | `docs/PAR-WORKFLOW-FRAMEWORK.md` |

---

## 🆘 Quick Help

**Question**: Which risks apply to my agent?
→ Check tier + use case in Risk Catalog

**Question**: How do I threat model?
→ `./workflows/threat-modeling/scripts/run-threat-model.sh`

**Question**: Budget exceeded, now what?
→ Check cost-report.sh, approve increase or pause

**Question**: How to add observability?
→ Copy observability-config.yml, configure exporters

**Question**: Need to compare before/after?
→ See framework-comparison artifact or ENHANCEMENTS.md

---

## 📞 Emergency Contacts

```
Security Incident: security-team@suhlabs.com
Budget Issues: finance-team@suhlabs.com
Governance Questions: governance-team@suhlabs.com
Technical Issues: [GitHub Issues]
```

---

## ✅ Pre-Deployment Checklist

Before deploying **any** Tier 3/4 agent:

- [ ] Threat model completed
- [ ] All Critical risks (15-25) mitigated
- [ ] Observability configured
- [ ] Budget limits set
- [ ] Approvals obtained
- [ ] Rollback plan documented
- [ ] Tests passing (SAT)
- [ ] Audit trail enabled

---

**Framework v2.0 - Enhanced with FINOS + Microsoft + Industry Best Practices**

**Remember**: Good governance enables innovation, not blocks it! 🚀
