---
trigger: always_on
---

# Security & Compliance Rules

## Zero-Trust Security Posture

### Secrets Management (Guardrail #8 — NIST IA-5)
- **Absolute rule**: NO secrets, API keys, JWT secrets, passwords, or credentials in source code
- All secrets → Kubernetes `ExternalSecret` objects, backed by AWS Secrets Manager or HashiCorp Vault
- All env var secrets → `os.getenv("VAR")` with startup assertion: `if not VAR: raise RuntimeError(...)`
- Add `detect-secrets` or TruffleHog to pre-commit hooks (see LL-001)
- Any secret ever committed to Git history MUST be rotated — changing the code alone is insufficient

### IP Boundary Protection & Release Sanitization
- **INTERNAL (Trade Secret / Conceptual IP)**: Unproven algorithms (game theory), proprietary distillation prompts (`scripts/prompts/distillation.txt`), pre-patent disclosures (`docs/*PATENT*`), internal engineering backlogs (`NEXT_RELEASE_TODO.md`). Must NEVER be exported to public/client SDKs.
- **EXTERNAL (Proven Framework)**: Standardized schemas (`audit-trail.json`), FastAPI PDP server (`app/main.py`), Helm charts (`deploy/helm/ai-agent/`), OCSF SIEM emitter, and pytest suites.
- **Export Gate**: All releases must run `./scripts/export-external-sdk.sh` with 0 security scanner warnings before distribution.

### Input Validation Rules (OWASP LLM Top 10 — Prompt Injection)
```python
# All GPIS inputs must be validated before processing:
MAX_REQUEST_LENGTH = 500  # characters
ALLOWED_CHARS = re.compile(r'^[a-zA-Z0-9\s\-_/:@.{}[\]"\']+$')

def validate_governance_request(request: str) -> bool:
    if len(request) > MAX_REQUEST_LENGTH:
        raise ValidationError("Request too long")
    if not ALLOWED_CHARS.match(request):
        raise ValidationError("Invalid characters detected")
    # Block prompt injection patterns
    INJECTION_PATTERNS = ["ignore previous", "system prompt", "jailbreak", "DAN"]
    if any(p.lower() in request.lower() for p in INJECTION_PATTERNS):
        raise SecurityViolation("Prompt injection detected")
```

### Container Security Standards (NIST SC-39)
Every agent Docker image must satisfy:
```dockerfile
# Required in all agent Dockerfiles:
FROM python:3.12-slim@sha256:<digest>  # Pin to digest, NOT tag
RUN useradd -u 65534 -r agent && chown -R agent:agent /app
USER 65534
# No curl, wget, git, bash in production images
```

Every Helm `values.yaml` must include:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 65534
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

### Network Policy Rules (NIST SC-7)
Default deny is mandatory in `ai-agents-prod` namespace. Each agent has explicit allow rules:
- **Security Agent** → GPIS (8000), Kubernetes API (6443), image registry (443)
- **IT-Ops Agent** → GPIS (8000), Kubernetes API (6443), SIEM endpoint (4317)
- **AI Agent** → GPIS (8000), S3 endpoint (443), ML platform
- **Architect Agent** → GPIS (8000), internet egress (443 only, approved CIDRs)

## CI/CD Security Pipeline (NIST SA-15, RA-5)

### Required Pipeline Stages (in order):
1. **TruffleHog** — secret scan on every `push` (fail on any verified secret)
2. **pip-audit** — dependency vulnerability scan (fail on CRITICAL CVEs)
3. **Trivy** — container image scan (fail on HIGH+CRITICAL CVEs)
4. **Bandit** — Python SAST (fail on HIGH severity)
5. **pytest** — unit + integration tests (fail if coverage < 80%)
6. **mypy** — type checking (fail on errors)
7. **Helm lint** — K8s manifest validation
8. **Syft** — SBOM generation (attach as artifact)

### AppInspect Equivalent for This Project
Before any release:
```bash
# Validate all manifests
python3 scripts/validate-manifest.py

# Run compliance checks
./scripts/compliance-check-enhanced.sh --environment prod

# Run token benchmark
python3 scripts/benchmark_token_savings.py --format json

# Validate schemas
python3 -m pytest tests/test_schemas.py -v
```
A release is NOT ready until all 4 pass with 0 errors.

## Audit Logging Requirements (NIST AU-2, AU-3, AU-12)

### Every governance decision must emit:
```json
{
  "audit_id": "<UUID>",
  "timestamp": "<ISO 8601>",
  "actor": "<agent_id>",
  "action": "<string>",
  "workflow_step": "<string>",
  "policy_controls_checked": ["<control_id>"],
  "compliance_result": "pass|fail",
  "evidence_hash": "<sha256>",
  "auditor_agent": "GPIS-001"
}
```

### Validation before emission:
```python
import jsonschema, json
from pathlib import Path

SCHEMA = json.loads(Path("policies/schemas/audit-trail.json").read_text())

def emit_audit_event(event: dict):
    jsonschema.validate(event, SCHEMA)  # Raises if invalid
    # ... emit to SIEM
```

## FedRAMP & NIST Compliance Gates

### Before any Tier 3/4 operation is allowed:
1. ✅ Jira CR validated and approved (`validate-jira-approval.py`)
2. ✅ Threat model exists for agent (`workflows/threat-modeling/reports/`)
3. ✅ GPIS JWT issued with `tier3`/`tier4` claim
4. ✅ Audit event emitted before AND after execution
5. ✅ Operation logged to SIEM with OCSF mapping

### STIG Hardening Checklist (DoD IL5 environments)
- [ ] No SUID/SGID binaries in container images
- [ ] No root processes in running containers
- [ ] All inter-service communication over mTLS
- [ ] Kubernetes API server audit logging enabled
- [ ] No `hostPath` mounts in agent pods
- [ ] All ConfigMaps/Secrets encrypted at rest (KMS)
