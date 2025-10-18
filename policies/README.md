# Policies Directory

> NIST 800-53 Rev 5 aligned security, compliance, and governance policies for AI agent operations

## Overview

This directory contains comprehensive policies and controls for governing AI agents, aligned to **NIST 800-53 Revision 5** security controls, **DISA CCI (Control Correlation Identifiers)**, and industry compliance frameworks (FedRAMP, SOC 2, PCI-DSS, HIPAA, EU AI Act).

### Why NIST 800-53?

NIST 800-53 is the authoritative control catalog for U.S. federal systems and is widely adopted across industries. It provides:
- **800+ security and privacy controls** organized into 20 families
- **Control enhancements** for additional rigor
- **CCI mappings** to DISA STIGs for compliance verification
- **Control overlays** for specific compliance frameworks (FedRAMP, HIPAA, etc.)

For AI-specific requirements not directly covered by standard NIST controls, we use **AI control extensions** following the convention: `{FAMILY}-{NUMBER}-AI-{EXT}` (e.g., `SC-4-AI-1` for AI data leakage prevention).

---

## Document Structure

### Core Policy Documents

| Document | NIST Control Family | Description |
|----------|---------------------|-------------|
| **[control-mappings.md](control-mappings.md)** | All families | **START HERE**: Master mapping of policies to NIST 800-53 controls and CCIs |
| **[security-policies.md](security-policies.md)** | AC, IA, SC | Access control, authentication, and system protection policies |
| **[compliance-policies.md](compliance-policies.md)** | AU, CM, PL | Audit, change management, and architecture policies |
| **[logging-policy.md](logging-policy.md)** | AU family | Comprehensive audit and accountability implementation |
| **[risk-catalog.md](risk-catalog.md)** | RA family | 18 AI-specific risks with NIST control mappings |
| **[mitigation-catalog.md](mitigation-catalog.md)** | Multiple | 21 mitigations mapped to NIST controls |
| **[ethical-policies.md](ethical-policies.md)** | SI, RA | Bias, fairness, and responsible AI guidelines |

### Supporting Artifacts

```
policies/
├── schemas/                    # JSON schemas for audit logs
│   ├── audit-trail.json       # AI agent decision logs (AU-3-AI-1)
│   ├── siem-event.json        # Generic security events (AU-2, AU-3)
│   └── agent-cost-record.json # Cost tracking (SA-15-AI-1)
├── control-mappings.md        # 📋 MASTER CONTROL MAPPING
├── security-policies.md       # IA-5, SC-4, AC-6 implementations
├── compliance-policies.md     # AU-2/3, CM-3, PL-8 implementations
├── logging-policy.md          # AU family comprehensive guide
├── risk-catalog.md            # RA-3 risk assessment catalog
└── mitigation-catalog.md      # Control implementation guidance
```

---

## Quick Reference: NIST Control Families

| Family Code | Family Name | Policies Coverage |
|-------------|-------------|-------------------|
| **AC** | Access Control | Least privilege (AC-6), tier enforcement (AC-6-AI-1), service accounts (AC-2) |
| **AU** | Audit and Accountability | Logging (AU-2/3), retention (AU-11), protection (AU-9), AI auditability (AU-3-AI-1) |
| **CM** | Configuration Management | Change control (CM-3), model versioning (CM-3-AI-1), impact analysis (CM-4) |
| **IA** | Identification and Authentication | Credential management (IA-5), no embedded secrets (IA-5(7)), vault integration |
| **PL** | Planning | Data residency (PL-8), architecture documentation, compliance mapping |
| **RA** | Risk Assessment | Threat modeling (RA-3), hallucination risk (RA-9-AI-1), prompt injection (RA-9-AI-2) |
| **SC** | System and Communications Protection | Data classification (SC-4), encryption (SC-28), data leakage prevention (SC-4-AI-1) |
| **SI** | System and Information Integrity | Output validation (SI-7-AI-1), LLM-as-Judge (SI-7-AI-2), input filtering (SI-10) |
| **SA** | System and Services Acquisition | Cost controls (SA-15-AI-1) |
| **CA** | Assessment, Authorization, and Monitoring | Performance monitoring (CA-7-AI-1), continuous monitoring |

---

## AI-Specific Control Extensions

These extensions address AI/ML risks not directly covered by baseline NIST controls:

| Control ID | CCI | Purpose | Document |
|------------|-----|---------|----------|
| **RA-9-AI-1** | CCI-AI-001 | Model Hallucination Risk Assessment | `risk-catalog.md` |
| **RA-9-AI-2** | CCI-AI-002 | Prompt Injection Risk Assessment | `risk-catalog.md` |
| **SC-4-AI-1** | CCI-AI-003 | Data Leakage to LLM Providers Prevention | `security-policies.md` |
| **SC-4-AI-2** | CCI-AI-004 | Vector Store Data Isolation | `security-policies.md` |
| **AC-6-AI-1** | CCI-AI-005 | AI Agent Tier Enforcement | `security-policies.md` |
| **AC-6-AI-2** | CCI-AI-006 | Human-in-the-Loop Authorization | `compliance-policies.md` |
| **CM-3-AI-1** | CCI-AI-007 | Model Version Control | `compliance-policies.md` |
| **AU-3-AI-1** | CCI-AI-008 | AI Decision Auditability | `logging-policy.md` |
| **SI-7-AI-1** | CCI-AI-009 | Output Validation & Fact-Checking | `mitigation-catalog.md` |
| **SI-7-AI-2** | CCI-AI-010 | LLM-as-Judge Verification | `mitigation-catalog.md` |
| **RA-5-AI-1** | CCI-AI-011 | Bias and Fairness Testing | `ethical-policies.md` |
| **CA-7-AI-1** | CCI-AI-012 | Model Performance Monitoring | `logging-policy.md` |
| **SA-15-AI-1** | CCI-AI-013 | Cost and Budget Controls | `compliance-policies.md` |
| **IR-5-AI-1** | CCI-AI-014 | AI Incident Response | `risk-catalog.md` |

**See `control-mappings.md` for complete details and implementation guidance.**

---

## How to Use This Framework

### For Security Engineers

1. **Start**: Read `control-mappings.md` to understand the NIST → Policy mapping
2. **Implement**: Use `security-policies.md` and `compliance-policies.md` for technical controls
3. **Monitor**: Configure logging per `logging-policy.md` (AU family)
4. **Verify**: Use schemas in `policies/schemas/` for audit log compliance

### For Compliance Teams

1. **Map Requirements**: Use `control-mappings.md` → Control Overlays section
   - FedRAMP Moderate → Baseline + AI extensions
   - PCI-DSS 4.0 → SC-4-AI-1, AU-3-AI-1, AC-6-AI-2
   - HIPAA → SC-4-AI-1, AU-3-AI-1, SI-7-AI-1
   - EU AI Act → All RA-AI and SI-AI controls

2. **Evidence Collection**: Audit logs in `schemas/` are compliance-ready
3. **Gap Analysis**: Compare implemented controls vs. required overlays

### For Risk Management

1. **Assess**: Use `risk-catalog.md` for AI-specific threat identification (RA-3)
2. **Mitigate**: Apply controls from `mitigation-catalog.md`
3. **Monitor**: Track risk indicators via AU-3-AI-1 logs

### For Developers

1. **Credential Handling**: Follow IA-5 and IA-5(7) in `security-policies.md`
2. **Data Classification**: Implement SC-4-AI-1 data leakage prevention
3. **Logging**: Emit AU-3-AI-1 compliant logs (see `schemas/audit-trail.json`)
4. **Change Control**: Follow CM-3 and CM-3-AI-1 for model updates

---

## Control Implementation Priority

### 🔴 Critical (Must Implement Before Production)

| Control | Policy | Rationale |
|---------|--------|-----------|
| **IA-5, IA-5(7)** | `security-policies.md` | Prevent credential leakage (RI-015) |
| **SC-4-AI-1** | `security-policies.md` | Block sensitive data to LLM APIs (RI-015) |
| **AC-6, AC-6-AI-1** | `security-policies.md` | Enforce least privilege and tier boundaries (RI-012) |
| **AU-2, AU-3, AU-3-AI-1** | `logging-policy.md` | Required for all compliance frameworks |
| **CM-3, CM-3-AI-1** | `compliance-policies.md` | Prevent unauthorized production changes (RI-016) |
| **SA-15-AI-1** | `compliance-policies.md` | Prevent cost overruns (RI-018) |

### 🟡 High (Implement for Tier 3+ Production Agents)

| Control | Policy | Rationale |
|---------|--------|-----------|
| **SI-10, RA-9-AI-2** | `risk-catalog.md`, `mitigation-catalog.md` | Prompt injection defense (RI-014) |
| **SI-7-AI-1, SI-7-AI-2** | `mitigation-catalog.md` | Hallucination detection (RI-001) |
| **AC-6-AI-2** | `security-policies.md` | Human approval for high-risk actions (RI-008) |
| **AU-9, AU-11** | `logging-policy.md` | Audit log protection and retention (RI-007) |
| **RA-5-AI-1** | `ethical-policies.md` | Bias testing for fairness (RI-006) |

### 🟢 Medium (Recommended for Maturity)

| Control | Policy | Rationale |
|---------|--------|-----------|
| **CM-4** | `compliance-policies.md` | Impact analysis for changes |
| **CA-7-AI-1** | `logging-policy.md` | Performance and drift monitoring (RI-009) |
| **PL-8** | `compliance-policies.md` | Data residency compliance (RI-016) |

---

## Compliance Framework Mappings

### FedRAMP Moderate Baseline

**Required Controls**: All FedRAMP Moderate controls + AI extensions
- **Critical Add-ons**: RA-9-AI-1, RA-9-AI-2, SC-4-AI-1, AC-6-AI-2, AU-3-AI-1
- **Evidence**: Logs per `schemas/audit-trail.json` and `siem-event.json`
- **See**: `control-mappings.md` → FedRAMP Moderate Baseline section

### PCI-DSS 4.0 (Payment Card Data)

**Requirement 10**: Logging and Monitoring
- **Controls**: AU-2, AU-3, AU-3-AI-1, AU-9, AU-11
- **Critical**: SC-4-AI-1 (prevent cardholder data to LLMs), AC-6-AI-2 (human approval)
- **See**: `logging-policy.md` → Compliance-Specific Extensions

### HIPAA (Healthcare PHI)

**Security Rule**: Access Control, Audit, Integrity
- **Controls**: AC-6, AU-2, AU-3-AI-1, SC-4-AI-1, SI-7-AI-1
- **Critical**: Prevent PHI leakage to hosted LLMs (SC-4-AI-1)
- **See**: `control-mappings.md` → HIPAA section

### EU AI Act (High-Risk AI Systems)

**Transparency & Accountability Requirements**
- **Controls**: AU-3-AI-1 (explainability), RA-5-AI-1 (bias testing), SI-7-AI-1 (validation)
- **Documentation**: All controls in `compliance-policies.md` and `risk-catalog.md`
- **See**: `control-mappings.md` → EU AI Act section

### SOC 2 Type II

**Trust Service Criteria**: Security, Availability, Confidentiality
- **CC6.1** (Logical Access): AC-6, AC-6-AI-1
- **CC7.2** (System Monitoring): AU-2, AU-3, CA-7-AI-1
- **CC8.1** (Change Management): CM-3, CM-3-AI-1
- **See**: `control-mappings.md` → SOC 2 Type II section

---

## Schema Compliance

All audit logs MUST conform to approved JSON schemas for automated compliance validation:

| Schema File | Purpose | NIST Controls | Validation |
|-------------|---------|---------------|------------|
| `audit-trail.json` | AI agent decisions and actions | AU-3-AI-1, AC-6-AI-1 | Includes reasoning_chain, model_version |
| `siem-event.json` | Generic security events | AU-2, AU-3, SI-4 | Standard SIEM normalization |
| `agent-cost-record.json` | Token usage and costs | SA-15-AI-1, CA-7-AI-1 | Budget tracking |

**Usage**:
```bash
# Validate logs against schema
jsonschema -i logs/agent-action.json policies/schemas/audit-trail.json
```

---

## Migration from Legacy IDs

If you're using the old custom IDs (`SEC-001`, `COMP-001`, etc.), refer to the mapping table:

| Legacy ID | NIST Control | Document |
|-----------|--------------|----------|
| SEC-001 | IA-5, IA-5(7) | `security-policies.md` |
| SEC-002 | SC-4, SC-28 | `security-policies.md` |
| SEC-003 | AC-6, AC-6(1) | `security-policies.md` |
| COMP-001 | AU-2, AU-3, AU-3-AI-1 | `compliance-policies.md` |
| COMP-002 | CM-3, CM-4 | `compliance-policies.md` |
| COMP-003 | PL-8 | `compliance-policies.md` |
| MI-001 through MI-021 | See `control-mappings.md` | `mitigation-catalog.md` |
| RI-001 through RI-018 | See risk-to-control table | `risk-catalog.md` |

**Complete mapping available in**: `control-mappings.md` → Risk-to-Control Mapping

---

## Continuous Improvement

### Review Cycle

| Activity | Frequency | Owner | Controls |
|----------|-----------|-------|----------|
| **Control Effectiveness Review** | Quarterly | Security Team | All |
| **Risk Assessment Update** | Quarterly | Risk Management | RA-3, RA-9-AI-1/2 |
| **Compliance Audit** | Annual | Compliance Team | AU, CM, AC |
| **Access Review** | Quarterly | Security + IT | AC-2, AC-6 |
| **Incident Lessons Learned** | Post-incident | Security + DevOps | IR-5-AI-1 |

### Version Control

- **Current Version**: 2.0 (NIST-aligned)
- **Last Updated**: 2025-10-18
- **Change History**: See git log for this directory
- **Control Owner**: Security & Compliance Team

### Feedback and Updates

Report issues or suggest improvements:
1. Open issue in project repository
2. Tag with `policy` or `compliance` label
3. Reference specific NIST control (e.g., "AU-3-AI-1 schema update needed")

---

## References and Standards

### NIST Publications
- **NIST SP 800-53 Rev 5**: Security and Privacy Controls for Information Systems and Organizations
- **NIST SP 800-53B**: Control Baselines for Information Systems and Organizations
- **NIST AI RMF (AI 100-1)**: AI Risk Management Framework
- **NIST SP 800-92**: Guide to Computer Security Log Management
- **NIST SP 800-171**: Protecting Controlled Unclassified Information in Nonfederal Systems

### DISA Resources
- **DISA CCI**: Control Correlation Identifiers (https://public.cyber.mil/stigs/cci/)
- **DISA STIG**: Security Technical Implementation Guides

### Compliance Frameworks
- **FedRAMP**: https://www.fedramp.gov/
- **PCI-DSS 4.0**: https://www.pcisecuritystandards.org/
- **HIPAA Security Rule**: 45 CFR Part 164
- **EU AI Act**: Regulation (EU) 2024/1689
- **SOC 2**: AICPA Trust Service Criteria

### Industry Standards
- **ISO/IEC 27001:2022**: Information Security Management
- **ISO/IEC 27002:2022**: Code of Practice for Information Security Controls
- **ISO/IEC 42001:2023**: Artificial Intelligence Management System
- **ISO/IEC 23894:2023**: AI Risk Management

---

## Quick Start Checklist

### Initial Setup (Day 1)
- [ ] Read `control-mappings.md` to understand framework structure
- [ ] Identify applicable compliance frameworks (FedRAMP, PCI, HIPAA, etc.)
- [ ] Review `risk-catalog.md` for AI-specific threats to your use case
- [ ] Implement critical controls (🔴 priority list above)

### Week 1
- [ ] Deploy credential vault integration (IA-5, IA-5(7))
- [ ] Implement data leakage prevention (SC-4-AI-1)
- [ ] Configure tier-based access control (AC-6-AI-1)
- [ ] Set up audit logging infrastructure (AU-2, AU-3)

### Month 1
- [ ] Complete all critical (🔴) controls
- [ ] Implement high (🟡) priority controls for Tier 3+ agents
- [ ] Configure SIEM integration per `logging-policy.md`
- [ ] Establish change management process (CM-3, CM-3-AI-1)
- [ ] Deploy cost monitoring and budget limits (SA-15-AI-1)

### Ongoing
- [ ] Run quarterly control effectiveness reviews
- [ ] Conduct quarterly access reviews (AC-2(3))
- [ ] Update risk catalog based on incidents (RA-3)
- [ ] Maintain compliance evidence in audit logs

---

**For questions or clarifications, contact**: Security & Compliance Team

**Document Version**: 2.0 (NIST 800-53 Rev 5 aligned)
**Last Updated**: 2025-10-18
**Next Review**: 2026-01-18
