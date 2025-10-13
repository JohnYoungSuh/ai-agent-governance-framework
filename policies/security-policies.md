# Security Policies

## SEC-001: Credential Management
**Policy**: Agents never handle credentials directly

**Implementation**:
- Reference secret paths, not values
- Use approved vault (HashiCorp Vault, AWS Secrets Manager)
- Log usage, not content
- Human configures access

**Violation**: Immediate suspension, security review

## SEC-002: Data Classification
**Policy**: Respect data classification levels

| Level | Access | Logging | Retention |
|-------|--------|---------|-----------|
| Public | All tiers | Standard | Indefinite |
| Internal | Tier 2+ | Enhanced | Per policy |
| Confidential | Tier 3+ with approval | Full audit | Encrypted |
| Restricted | Human only | Complete | Maximum security |

## SEC-003: Least Privilege
**Policy**: Minimum required permissions

**Implementation**:
- Dedicated service accounts
- Quarterly reviews
- Justified elevation
- All actions logged
