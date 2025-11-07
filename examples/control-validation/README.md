# Control Validation Examples

This folder contains worked examples of MVP control validation, based on the template in:
`frameworks/control-validation-template.md`.

All examples use **NIST 800-53 Rev 5** control IDs. For legacy ID mapping, see `docs/CONTROL-REMAPPING.md`.

## How to Contribute

1. Copy the template from `frameworks/control-validation-template.md`.
2. Create a new file in this folder named `<NIST-CONTROL-ID>-<short-name>.md`.
   - Example: `IA-5-aws-secrets-manager.md` (for Authenticator Management)
   - Example: `AC-6-AI-2-jira-approval.md` (for Human-in-the-Loop Authorization)
3. Fill in:
   - NIST 800-53 Rev 5 control reference with CCI
   - Implementation snippet
   - Governance record JSON
   - Audit trail JSON (conforming to `policies/schemas/audit-trail.json`)
   - Auditor Agent checks
   - MVP test steps
4. Submit a pull request.

## Current Examples

| File | NIST Control | CCI | Description |
|------|--------------|-----|-------------|
| `SEC-001-aws-secrets-manager.md` | **IA-5, IA-5(7)** | CCI-000195, CCI-004062 | Credential lifecycle management with AWS Secrets Manager |
| `APP-001-jira-approval.md` | **AC-6-AI-2** | CCI-AI-006 | Human-in-the-loop authorization via Jira CR |

## Planned Examples
- **SC-4-AI-1**: PII redaction and data leakage prevention
- **SA-15-AI-1**: Cost monitoring and budget enforcement
- **CA-7-AI-1**: Model performance monitoring and drift detection
- **SI-7-AI-1**: Output validation and fact-checking

## File Naming Convention

Use NIST 800-53 Rev 5 control IDs:
- Base controls: `IA-5-description.md`, `AC-6-description.md`
- Control enhancements: `IA-5-7-description.md` (for IA-5(7))
- AI extensions: `AC-6-AI-2-description.md`, `CA-7-AI-1-description.md`

**Legacy files** (`SEC-001-*.md`, `APP-001-*.md`) are retained for backwards compatibility but reference the new NIST control IDs in their content.
