---
trigger: always_on
---

# Hard Constraints: Systems & Security Rules

## Governance & Security Invariants
- **NEVER bypass GPIS PDP** (`app/main.py`) — no agent may self-authorize or bypass policy evaluation.
- **NEVER hardcode secrets, passwords, or JWT keys** in source code or tests — always use `os.getenv("VAR")`.
- **NEVER issue Tier 3/4 JWTs without validating `jira_cr_id`** via PKI verification.
- **NEVER mutate `policies/schemas/audit-trail.json`** without patent counsel review — this schema is a core patent anchor.
- **NEVER alter `simple_rules.yml` rules to fail-open** — governance must remain fail-closed.

## Kubernetes & Deployment Constraints
- **NEVER allow containers to run as root** (`runAsUser: 65534` mandatory).
- **NEVER mount `hostPath` volumes** in agent Helm charts or pod manifests.
- **NEVER remove `automountServiceAccountToken: false`** from pod default templates.
- **NEVER skip `NetworkPolicy` isolation** — all agent namespaces require default-deny ingress/egress policies.

## Code Quality & Dependencies
- **NEVER delete `requirements.txt` entries** without running `pip-audit` to verify vulnerability status.
- **NEVER import unvalidated third-party packages** in FedRAMP Moderate / DoD IL5 pipelines.
- **NEVER resolve errors by swallowing exceptions**, returning dummy fallbacks, or commenting out failing tests.
- **NEVER push changes without running pytest** and validating all 3 JSON schemas (`audit-trail`, `siem-event`, `agent-cost-record`).

## Execution & Environment Rules
- **NEVER use PowerShell or Windows CMD** — all terminal actions run strictly in WSL2/bash with UNIX paths.
- **NEVER retry a failing command more than 3 consecutive times** — stop and consult the user on the 3rd failure.
- **NEVER leave dangling Docker containers, volumes, or build caches** after testing — always run `docker builder prune -f` and remove temporary test containers.
- **NEVER consider a task complete** until the automated test suite passes with 0 errors.
