---
name: governance-policy-review
description: >
  Dual-persona Governance Policy & Feature Proposal Review. Invoked when evaluating
  new governance guardrails, agent policy changes, or system enhancement proposals.
  Produces a PM + System Architect technical validation backed by live code evidence,
  and updates NEXT_RELEASE_TODO.md with approved items.
---

# Governance Policy & Feature Review Skill

## Trigger Phrases
- "review this governance proposal"
- "evaluate policy change"
- "PM and architect review"
- "review this feature proposal"

---

## Workflow

### Phase 1 — Codebase Research
1. Cites exact file locations in `app/`, `policies/`, `deploy/`, and `agents/`.
2. Verifies schema compliance against `policies/schemas/audit-trail.json`.
3. Checks NIST 800-53 control mappings in `policies/control-mappings.md`.

### Phase 2 — Dual-Persona Review Artifact
Produce `governance_review_<version>.md` in the artifacts directory evaluating:
- **Product / Compliance Manager Review**: NIST alignment, FedRAMP posture, business risk assessment.
- **System Architect Review**: PDP logic impact, JWT token claims, K8s NetworkPolicy impact, token router efficiency impact.

### Phase 3 — Standing Guards
- **Patent Integrity Guard**: `audit-trail.json` structure must remain intact.
- **Token Efficiency Guard**: Ensure new policy rules are added to `simple_rules.yml` to preserve zero-token evaluation.
- **Zero Secrets Guard**: Verify no secrets or credentials are hardcoded.

### Phase 4 — NEXT_RELEASE_TODO.md Update
Update the backlog with prioritized, actionable execution steps.
