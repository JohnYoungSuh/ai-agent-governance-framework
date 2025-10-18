# Security Policies

> Aligned to NIST 800-53 Rev 5 and DISA CCI standards

---

## IA-5: Authenticator Management (Credential Management)
**NIST Control**: IA-5 | **CCI**: CCI-000195
**AI Extension**: IA-5(7) - No Embedded Unencrypted Static Authenticators | **CCI**: CCI-004062

**Policy**: AI agents never handle credentials directly; all authenticators stored in approved vaults

### Control Implementation

**IA-5(a)**: Verify identity before issuing authenticators
- Agents assigned dedicated service account identities
- Human administrator provisions initial credentials
- All credential issuance logged (AU-3)

**IA-5(b)**: Establish initial content for authenticators
- Secrets stored in approved vaults (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
- Agents reference secret paths/ARNs, never raw values
- Secrets Manager API calls logged with agent ID

**IA-5(c)**: Ensure sufficient strength
- Minimum 32-character randomly generated secrets
- Rotate every 90 days or on-demand
- Use cryptographic key-based authentication where possible (IA-5(2))

**IA-5(7) - AI-Specific**: No embedded credentials in code, prompts, or context
- Pre-processing filter scans all LLM inputs for secrets (regex patterns)
- Reject prompts containing: API keys, tokens, private keys, passwords
- Log rejection events for security review

### Implementation Examples

```yaml
# ✅ CORRECT - Reference by path
agent:
  secrets:
    - path: "aws/secretsmanager/prod/api-key"
      permission: read-only
```

```python
# ❌ INCORRECT - Embedded credential
api_key = "sk-abc123..."  # NEVER DO THIS

# ✅ CORRECT - Vault integration
from aws_secretsmanager import get_secret
api_key = get_secret("prod/api-key")
```

**Violation Response**: Immediate agent suspension, credential rotation, security incident review

---

## SC-4: Information in Shared System Resources (Data Classification)
**NIST Control**: SC-4 | **CCI**: CCI-001414
**Supporting Controls**: SC-28 (Protection at Rest), SC-28(1) (Cryptographic Protection)
**AI Extension**: SC-4-AI-1 - Data Leakage to LLM Providers | **CCI**: CCI-AI-003

**Policy**: Prevent unauthorized information leakage between data classification boundaries

### Data Classification Matrix

| Classification | Tier Access | LLM Provider | Logging Level | Retention | Encryption |
|----------------|-------------|--------------|---------------|-----------|------------|
| **Public** | All (1-4) | Allowed | Standard (AU-2) | Indefinite | Optional |
| **Internal** | Tier 2+ | Redacted/On-Prem Only | Enhanced (AU-3) | Per policy | At rest (SC-28) |
| **Confidential** | Tier 3+ with approval | Prohibited | Full audit (AU-3(1)) | 7 years | At rest + transit (SC-28(1)) |
| **Restricted** | Human only | Prohibited | Complete (AU-9) | Max security | All states (SC-28(1)) |

### SC-4-AI-1 Implementation: Data Leakage Prevention

**Control Statement**: Prevent sensitive data from being transmitted to hosted LLM providers

**Implementation**:
1. **Pre-processing Filters** (before LLM API call):
   - PII detection (Microsoft Presidio, AWS Macie)
   - Secrets scanning (detect-secrets, gitleaks)
   - Custom regex for proprietary data markers

2. **Classification Enforcement**:
   - Tag all data with classification label
   - Block Confidential/Restricted data to external APIs
   - Route Internal data to on-premise LLMs or redact

3. **Audit Trail** (AU-3):
   - Log classification level of each request
   - Log redaction/blocking events
   - Alert on classification violations

```python
# Example implementation
from data_classifier import classify, redact

def safe_llm_call(prompt: str, context: str):
    classification = classify(prompt + context)

    if classification in ["CONFIDENTIAL", "RESTRICTED"]:
        raise SecurityError("Cannot send classified data to hosted LLM")

    if classification == "INTERNAL":
        prompt = redact(prompt, ["PII", "IP_ADDRESS", "SSN"])

    # Log the request
    audit_log(classification=classification, redacted=True)

    return llm_api.call(prompt)
```

---

## AC-6: Least Privilege
**NIST Control**: AC-6 | **CCI**: CCI-002220
**Supporting Controls**: AC-6(1) - Authorize Access to Security Functions | **CCI**: CCI-002233
**Supporting Controls**: AC-6(9) - Log Use of Privileged Functions | **CCI**: CCI-002235
**AI Extension**: AC-6-AI-1 - AI Agent Tier Enforcement | **CCI**: CCI-AI-005

**Policy**: AI agents operate with minimum required permissions based on tier level

### Control Implementation

**AC-6(a)**: Authorize access based on duties
- Define explicit permission sets per agent tier (see `frameworks/decision-matrix.yml`)
- No default permissions; all access explicitly granted
- Service accounts dedicated per agent (AC-2)

**AC-6(b)**: Separation of duties
- Development agents (Tier 1-2): Read-only production access
- Production agents (Tier 3): Write with human approval
- Strategic agents (Tier 4): Planning only, execution requires Tier 3

**AC-6(1)**: Security function authorization
- Only Tier 3+ can modify security configurations
- Require multi-person approval (separate developer + security admin)
- All security function calls logged (AU-6(9))

**AC-6(9)**: Audit privileged functions
- Log every use of elevated permissions
- Include: agent ID, tier, action, approver, timestamp
- Alert on privilege escalation attempts

### AC-6-AI-1 Implementation: Tier Enforcement

**Control Statement**: Enforce tier-based privilege boundaries for AI agents

| Tier | Scope | Write Access | Approval Required | Example Permissions |
|------|-------|--------------|-------------------|---------------------|
| **Tier 1** | Development | No | N/A | Read code, suggest changes |
| **Tier 2** | Staging | Limited | For deployments | Read/write dev, read prod |
| **Tier 3** | Production | Yes | For all writes | Execute approved changes |
| **Tier 4** | Strategic | No (plans only) | For initiated workflows | Read-only analysis |

**Implementation**:
```yaml
# IAM policy example - Tier 2 agent
agents/tier2/dev-agent:
  permissions:
    - resource: "repositories/*"
      actions: ["read", "write"]
    - resource: "production/*"
      actions: ["read"]  # Read-only production
    - resource: "deployments/staging"
      actions: ["deploy"]
      conditions:
        require_approval: true
```

**Quarterly Review** (AC-2(3)):
- Review all service account permissions
- Remove unused accounts (dormant >90 days)
- Validate tier assignments
- Document review in audit trail (AU-11)
