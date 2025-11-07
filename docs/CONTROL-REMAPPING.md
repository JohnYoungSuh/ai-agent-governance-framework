# Control ID Remapping to NIST 800-53 Rev 5

**Version:** 2.1
**Date:** 2025-11-06
**Purpose:** Standardize all control IDs to NIST 800-53 Rev 5 and AI RMF conventions

---

## Executive Summary

This document provides the authoritative mapping from **legacy custom control IDs** to **NIST 800-53 Rev 5 standard controls** with AI extensions. All future references should use the NIST-compliant names.

**Naming Convention**:
- **Standard controls**: `{FAMILY}-{NUMBER}` (e.g., `AC-6`, `AU-2`)
- **Control enhancements**: `{FAMILY}-{NUMBER}({ENHANCEMENT})` (e.g., `AC-6(2)`, `AU-3(1)`)
- **AI extensions**: `{FAMILY}-{NUMBER}-AI-{EXT}` (e.g., `AC-6-AI-1`, `SA-15-AI-2`)

---

## Complete Control Remapping Table

### Access Control (AC) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| SEC-003 | **AC-6** | Base | CCI-002220 | Least Privilege | Base access control |
| SEC-003 | **AC-6(1)** | Enhancement | CCI-002233 | Authorize Access to Security Functions | Security function access |
| SEC-003 | **AC-6(2)** | Enhancement | CCI-002234 | Non-Privileged Access for Nonsecurity Functions | Privilege separation |
| SEC-003 | **AC-6(9)** | Enhancement | CCI-002235 | Log Use of Privileged Functions | Privileged action logging |
| AC-003 | **AC-6** | Base | CCI-002220 | Least Privilege | Duplicate of SEC-003 |
| AC-004 | **AC-4** | Base | CCI-001368 | Information Flow Enforcement | Network segmentation |
| MI-006 | **AC-6** | Base | CCI-002220 | Least Privilege | Access Controls |
| MI-020 | **AC-6-AI-1** | **AI Extension** | CCI-AI-005 | **AI Agent Tier Enforcement** | Tier-based privilege separation |
| MI-007 | **AC-6-AI-2** | **AI Extension** | CCI-AI-006 | **Human-in-the-Loop Authorization** | Human approval for Tier 3+ |
| APP-001 | **AC-6-AI-2** | **AI Extension** | CCI-AI-006 | **Human Primacy** | Same as MI-007 |
| - | **AC-2** | Base | CCI-000015 | Account Management | Service account management |
| - | **AC-2(7)** | Enhancement | CCI-000016 | Role-Based Schemes | RBAC for agents |

### Audit and Accountability (AU) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| COMP-001 | **AU-2** | Base | CCI-000130 | Event Logging | Audit event logging |
| AU-002 | **AU-2** | Base | CCI-000130 | Event Logging | Duplicate of COMP-001 |
| MI-019 | **AU-2** | Base | CCI-000130 | Audit Trails | Same as AU-002 |
| G-07 | **AU-2** | Base | CCI-000130 | Jira Integration & Audit | Audit trails |
| - | **AU-3** | Base | CCI-000131 | Content of Audit Records | Audit record content |
| - | **AU-3(1)** | Enhancement | CCI-000133 | Additional Audit Information | Extended audit data |
| AU-003 | **AU-3** | Base | CCI-000131 | Content of Audit Records | Duplicate |
| - | **AU-3-AI-1** | **AI Extension** | CCI-AI-008 | **AI Decision Auditability** | Log AI reasoning & decisions |
| AU-006 | **AU-6** | Base | CCI-000134 | Audit Record Review, Analysis, and Reporting | Audit analysis |
| - | **AU-8** | Base | CCI-000159 | Time Stamps | UTC timestamps |
| - | **AU-9** | Base | CCI-000162 | Protection of Audit Information | Audit protection |
| - | **AU-9(2)** | Enhancement | CCI-001350 | Store on Separate Physical Systems | Audit separation |
| - | **AU-9(3)** | Enhancement | CCI-001351 | Cryptographic Protection | Encrypt audit logs |
| AU-009 | **AU-9** | Base | CCI-000162 | Protection of Audit Information | Duplicate |
| - | **AU-11** | Base | CCI-001849 | Audit Record Retention | 7-year retention |
| AU-012 | **AU-12** | Base | CCI-000169 | Audit Record Generation | Generate audit records |

### Configuration Management (CM) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| COMP-002 | **CM-3** | Base | CCI-000066 | Configuration Change Control | Change management |
| CM-002 | **CM-3** | Base | CCI-000066 | Configuration Change Control | Duplicate |
| - | **CM-3(2)** | Enhancement | CCI-001813 | Test / Validate / Document Changes | Change testing |
| - | **CM-4** | Base | CCI-001812 | Impact Analyses | Change impact analysis |
| - | **CM-5(1)** | Enhancement | CCI-001814 | Automated Access Enforcement / Auditing | Rollback automation |
| - | **CM-7** | Base | CCI-000381 | Least Functionality | Minimal services |
| MI-010 | **CM-7** | Base | CCI-000381 | Version Pinning | Model version pinning |
| - | **CM-3-AI-1** | **AI Extension** | CCI-AI-007 | **Model Version Control** | LLM version management |
| MI-016 | **CM-3-AI-1** | **AI Extension** | CCI-AI-007 | Change Monitoring | Model change detection |
| MI-022 | **CM-3-AI-1** | **AI Extension** | CCI-AI-007 | Model Version Tracking | Version audit trail |

### Identification and Authentication (IA) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| SEC-001 | **IA-5** | Base | CCI-000195 | Authenticator Management | Credential management |
| IA-002 | **IA-5** | Base | CCI-000195 | Authenticator Management | Duplicate |
| MI-003 | **IA-5** | Base | CCI-000195 | Secrets Management | Same as SEC-001 |
| IA-005 | **IA-5** | Base | CCI-000195 | Authenticator Management | Duplicate |
| - | **IA-5(1)** | Enhancement | CCI-000196 | Password-Based Authentication | Password policies |
| - | **IA-5(2)** | Enhancement | CCI-004063 | Public Key-Based Authentication | PKI authentication |
| - | **IA-5(7)** | Enhancement | CCI-004062 | No Embedded Unencrypted Static Authenticators | No hardcoded secrets |

### System and Communications Protection (SC) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| SEC-002 | **SC-4** | Base | CCI-001414 | Information in Shared System Resources | Data classification |
| - | **SC-7** | Base | CCI-000382 | Boundary Protection | Network boundaries |
| - | **SC-7(21)** | Enhancement | CCI-003748 | Isolation of System Components | Component isolation |
| COMP-003 | **SC-7(21)** | Enhancement | CCI-003748 | Data Residency | Geographic isolation |
| SC-028 | **SC-28** | Base | CCI-001199 | Protection of Information at Rest | Encryption at rest |
| - | **SC-28(1)** | Enhancement | CCI-002475 | Cryptographic Protection | KMS encryption |
| MI-001 | **SC-4-AI-1** | **AI Extension** | CCI-AI-003 | **Data Leakage Prevention** | PII/secrets redaction |
| - | **SC-4-AI-2** | **AI Extension** | CCI-AI-004 | **Vector Store Data Isolation** | RAG data separation |
| MI-014 | **SC-4-AI-2** | **AI Extension** | CCI-AI-004 | RAG Security | Vector store security |
| MI-011 | **SC-4-AI-3** | **AI Extension** | CCI-AI-015 | **On-Premise LLM** | Self-hosted models |

### System and Information Integrity (SI) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| MI-002 | **SI-10** | Base | CCI-002754 | Input Filtering | Input validation |
| MI-017 | **SI-10-AI-1** | **AI Extension** | CCI-AI-016 | **AI Firewall** | Prompt injection defense |
| MI-013 | **SI-7-AI-1** | **AI Extension** | CCI-AI-009 | **Citations & Fact-Checking** | Output validation |
| MI-015 | **SI-7-AI-2** | **AI Extension** | CCI-AI-010 | **LLM-as-Judge** | Secondary verification |
| - | **SI-3** | Base | CCI-001233 | Malicious Code Protection | Security scanning |

### Risk Assessment (RA) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| - | **RA-3** | Base | CCI-001484 | Risk Assessment | Threat modeling |
| - | **RA-3(1)** | Enhancement | CCI-001666 | Supply Chain Risk Assessment | Supply chain risks |
| - | **RA-9** | Base | CCI-002239 | Criticality Analysis | Criticality assessment |
| - | **RA-9-AI-1** | **AI Extension** | CCI-AI-001 | **Model Hallucination Risk** | Hallucination mitigation |
| - | **RA-9-AI-2** | **AI Extension** | CCI-AI-002 | **Prompt Injection Risk** | Injection attack risk |
| - | **RA-5-AI-1** | **AI Extension** | CCI-AI-011 | **Bias and Fairness Testing** | Bias detection |
| MI-012 | **RA-5-AI-1** | **AI Extension** | CCI-AI-011 | Bias Testing | Same as above |

### Continuous Monitoring (CA) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| MI-004 | **CA-7** | Base | CCI-000366 | Continuous Monitoring | Observability |
| - | **CA-7-AI-1** | **AI Extension** | CCI-AI-012 | **Model Performance Monitoring** | Drift detection |
| MI-009 | **CA-7-AI-1** | **AI Extension** | CCI-AI-012 | Cost Monitoring | Token/cost tracking |
| MI-024 | **CA-7-AI-2** | **AI Extension** | CCI-AI-017 | **Interaction Monitoring** | Non-deterministic detection |

### System and Services Acquisition (SA) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| MI-021 | **SA-15-AI-1** | **AI Extension** | CCI-AI-013 | **Cost and Budget Controls** | Budget limits & circuit breakers |
| MI-009 | **SA-15-AI-1** | **AI Extension** | CCI-AI-013 | Cost Monitoring | Overlaps with CA-7-AI-1 |

### Incident Response (IR) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| - | **IR-5-AI-1** | **AI Extension** | CCI-AI-014 | **AI Incident Response** | AI-specific incidents |

### Planning (PL) Family

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| COMP-003 | **PL-8** | Base | CCI-000352 | Security and Privacy Architectures | Architecture |
| - | **PL-8(1)** | Enhancement | CCI-003505 | Defense in Depth | Layered defenses |

### Governance Controls (Custom G- prefix)

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| G-001 | **AC-6-AI-1** | AI Extension | CCI-AI-005 | Agent Tier Enforcement | Tier governance |
| G-02 | **AC-6-AI-2** | AI Extension | CCI-AI-006 | Human Approval Required | Approval workflow |
| G-05 | **CM-3** | Base | CCI-000066 | Infrastructure Change Control | Change governance |
| G-07 | **AU-2** | Base | CCI-000130 | Jira Integration | Audit integration |
| G-101 | **AC-6-AI-1** | AI Extension | CCI-AI-005 | Tier 1 Enforcement | Observer tier |
| G-102 | **AC-6-AI-1** | AI Extension | CCI-AI-005 | Tier 2 Enforcement | Developer tier |
| G-103 | **AC-6-AI-1** | AI Extension | CCI-AI-005 | Tier 3 Enforcement | Operations tier |
| G-202 | **CM-3(2)** | Enhancement | CCI-001813 | Deployment Testing | Pre-deployment validation |

### Additional Mitigations

| Legacy ID | New NIST ID | Enhancement | CCI | Control Name | Notes |
|-----------|-------------|-------------|-----|--------------|-------|
| MI-005 | **AC-7** | Base | CCI-000044 | Rate Limiting | Unsuccessful logon attempts |
| MI-008 | **SC-7(21)** | Enhancement | CCI-003748 | Sandboxing | Environment isolation |
| MI-018 | **Multiple** | - | Multiple | Compliance Mapping | See overlay tables |
| MI-023 | **CA-7-AI-1** | AI Extension | CCI-AI-012 | Model Drift Detection | Performance monitoring |

---

## Risk ID Alignment

Risks already follow industry naming patterns:

| Risk ID | Aligned Framework | Notes |
|---------|-------------------|-------|
| RI-001 through RI-019 | NIST AI RMF Risk Categories | Already compliant |

**Format**: `RI-{NUMBER}` (Risk Identifier)
- RI-001: Hallucination (NIST AI RMF: Trust & Safety)
- RI-014: Prompt Injection (OWASP LLM01)
- RI-015: Data Leakage (OWASP LLM02, NIST Privacy)
- RI-018: Cost Overruns (Custom, maps to SA-15-AI-1)
- RI-019: Non-Deterministic Problems (Custom, maps to CA-7-AI-2)

---

## New AI-Specific CCIs

These Common Control Identifiers (CCIs) extend DISA's CCI list for AI systems:

| CCI ID | Title | Description |
|--------|-------|-------------|
| CCI-AI-001 | Model Hallucination Risk Assessment | Assess risks from AI hallucinations |
| CCI-AI-002 | Prompt Injection Risk Assessment | Assess prompt injection vectors |
| CCI-AI-003 | Data Leakage Prevention | Prevent sensitive data to LLM APIs |
| CCI-AI-004 | Vector Store Isolation | Enforce RAG data separation |
| CCI-AI-005 | AI Agent Tier Enforcement | Tier-based privilege separation |
| CCI-AI-006 | Human-in-the-Loop | Require human approval for high-risk |
| CCI-AI-007 | Model Version Control | Control LLM version changes |
| CCI-AI-008 | AI Decision Auditability | Log AI reasoning and decisions |
| CCI-AI-009 | Output Validation | Validate AI outputs against sources |
| CCI-AI-010 | LLM-as-Judge Verification | Secondary model verification |
| CCI-AI-011 | Bias and Fairness Testing | Test for demographic bias |
| CCI-AI-012 | Model Performance Monitoring | Monitor for drift and degradation |
| CCI-AI-013 | Cost and Budget Controls | Hard limits for AI API costs |
| CCI-AI-014 | AI Incident Response | AI-specific incident procedures |
| CCI-AI-015 | On-Premise LLM Deployment | Self-hosted model requirements |
| CCI-AI-016 | AI Firewall Protection | Prompt injection filtering |
| CCI-AI-017 | Interaction Monitoring | Non-deterministic problem detection |

---

## Migration Strategy

### Phase 1: Documentation Update (Immediate)
1. Update all markdown files with new control IDs
2. Add legacy ID references for backwards compatibility
3. Update control-mappings.md

### Phase 2: Code Update (Week 1)
1. Update all Python scripts to use new IDs
2. Update Terraform tags with new control IDs
3. Update audit trail schemas

### Phase 3: Validation (Week 2)
1. Run governance-check.sh with new IDs
2. Validate SIEM events use new format
3. Update Jira custom fields

### Phase 4: Deprecation (Month 2)
1. Mark legacy IDs as deprecated
2. Add warnings for legacy ID usage
3. Final migration deadline

---

## Backwards Compatibility

During migration, support both formats:

```python
# Control ID normalization
LEGACY_TO_NIST = {
    'SEC-001': 'IA-5',
    'SEC-002': 'SC-4',
    'SEC-003': 'AC-6',
    'MI-001': 'SC-4-AI-1',
    'MI-002': 'SI-10',
    'MI-003': 'IA-5',
    'MI-006': 'AC-6',
    'MI-007': 'AC-6-AI-2',
    'MI-009': 'SA-15-AI-1',
    'MI-020': 'AC-6-AI-1',
    'MI-021': 'SA-15-AI-1',
    'MI-024': 'CA-7-AI-2',
    'APP-001': 'AC-6-AI-2',
    'AU-002': 'AU-2',
    'G-07': 'AU-2',
    # ... complete mapping
}

def normalize_control_id(control_id: str) -> str:
    """Convert legacy ID to NIST format"""
    return LEGACY_TO_NIST.get(control_id, control_id)
```

---

## Examples

### Before (Legacy)
```python
control_ids = ["SEC-001", "MI-003", "APP-001"]
# Unclear what these mean to external auditors
```

### After (NIST-Compliant)
```python
control_ids = ["IA-5", "IA-5(7)", "AC-6-AI-2"]
# Immediately recognizable by InfoSec teams
# Maps to NIST 800-53 Rev 5
# Compatible with STIG, FedRAMP, etc.
```

### Terraform Tags
```hcl
# Before
tags = {
  ControlIDs = "SEC-001,MI-003,G-07"
}

# After
tags = {
  NIST_Controls = "IA-5,IA-5(7),AU-2"
  AI_Extensions = "SC-4-AI-1,AC-6-AI-2"
  CCI = "CCI-000195,CCI-004062,CCI-000130"
}
```

---

## References

### Primary Standards
- **NIST SP 800-53 Rev 5**: Security and Privacy Controls for Information Systems
- **NIST AI 100-1**: AI Risk Management Framework (AI RMF)
- **DISA CCI**: Control Correlation Identifiers
- **FedRAMP**: Control Baselines and Overlays

### AI-Specific Guidance
- **NIST AI RMF Playbook**: AI Risk Management Practices
- **OWASP LLM Top 10**: LLM Application Security Risks
- **MITRE ATLAS**: Adversarial Threat Landscape for AI Systems
- **ISO/IEC 42001:2023**: AI Management System

### Zero Trust Architecture
- **NIST SP 800-207**: Zero Trust Architecture
- **CISA Zero Trust Maturity Model**
- **DoD Zero Trust Reference Architecture**

---

**Approved By**: Security & Compliance Team
**Effective Date**: 2025-11-06
**Review Cycle**: Quarterly

---

## Appendix: Quick Reference

### Most Common Mappings

| Legacy | NIST | Name |
|--------|------|------|
| SEC-001 | IA-5 | Secrets Management |
| MI-003 | IA-5(7) | No Hardcoded Secrets |
| APP-001 | AC-6-AI-2 | Human Approval |
| MI-020 | AC-6-AI-1 | Tier Enforcement |
| AU-002 | AU-2 | Audit Logging |
| G-07 | AU-2 | Jira Integration |
| MI-009 | SA-15-AI-1 | Cost Monitoring |
| MI-021 | SA-15-AI-1 | Budget Limits |
| MI-024 | CA-7-AI-2 | Interaction Monitoring |

---

## XCCDF/SCAP Schema Extensions

### Overview

For AI-specific controls not covered by existing DISA STIGs, we extend the XCCDF schema with custom benchmarks and OVAL definitions.

**SCAP Components**:
- **XCCDF 1.2**: Checklist format for compliance scanning
- **OVAL**: Automated compliance checks
- **CCE**: Configuration enumeration
- **CPE**: Platform enumeration

### Custom XCCDF Benchmark ID

```
xccdf_gov.nist.ai-agent-governance_benchmark_AI-AGENT-v2.1
```

### XCCDF Rule ID Format for AI Extensions

```
xccdf_gov.nist.ai_rule_SV-AI-{ID}r{REVISION}_rule

Examples:
- xccdf_gov.nist.ai_rule_SV-AI-001r1_rule  (AC-6-AI-1 Tier Enforcement)
- xccdf_gov.nist.ai_rule_SV-AI-006r1_rule  (CA-7-AI-2 Interaction Monitoring)
```

### Control to XCCDF Mapping Table

| NIST Control | CCI | XCCDF Rule ID | STIG ID | Severity | Check Type |
|--------------|-----|---------------|---------|----------|------------|
| **AC-6-AI-1** | CCI-AI-005 | SV-AI-001r1 | V-AI-001 | CAT II (High) | OVAL |
| **AC-6-AI-2** | CCI-AI-006 | SV-AI-002r1 | V-AI-002 | CAT II (High) | OVAL + Manual |
| **AU-3-AI-1** | CCI-AI-008 | SV-AI-007r1 | V-AI-007 | CAT II (Medium) | OVAL |
| **SC-4-AI-1** | CCI-AI-003 | SV-AI-003r1 | V-AI-003 | CAT I (Critical) | OVAL |
| **SC-4-AI-2** | CCI-AI-004 | SV-AI-004r1 | V-AI-004 | CAT II (High) | OVAL |
| **SI-7-AI-1** | CCI-AI-009 | SV-AI-009r1 | V-AI-009 | CAT II (Medium) | OVAL |
| **SI-7-AI-2** | CCI-AI-010 | SV-AI-010r1 | V-AI-010 | CAT II (Medium) | OVAL |
| **SI-10-AI-1** | CCI-AI-016 | SV-AI-016r1 | V-AI-016 | CAT I (Critical) | OVAL |
| **RA-5-AI-1** | CCI-AI-011 | SV-AI-011r1 | V-AI-011 | CAT II (Medium) | Manual |
| **SA-15-AI-1** | CCI-AI-013 | SV-AI-013r1 | V-AI-013 | CAT II (High) | OVAL |
| **CA-7-AI-1** | CCI-AI-012 | SV-AI-012r1 | V-AI-012 | CAT II (Medium) | OVAL |
| **CA-7-AI-2** | CCI-AI-017 | SV-AI-017r1 | V-AI-017 | CAT II (Medium) | OVAL |
| **CM-3-AI-1** | CCI-AI-007 | SV-AI-008r1 | V-AI-008 | CAT II (Medium) | OVAL |
| **IR-5-AI-1** | CCI-AI-014 | SV-AI-014r1 | V-AI-014 | CAT III (Low) | Manual |
| **SC-4-AI-3** | CCI-AI-015 | SV-AI-015r1 | V-AI-015 | CAT II (High) | Manual |

### SCAP Data Stream Example

See `compliance/scap/ai-agent-governance-datastream.xml` for complete SCAP data stream collection.

**Components**:
1. XCCDF Benchmark (`ai-agent-benchmark.xml`)
2. OVAL Definitions (`ai-agent-oval.xml`)
3. CPE Dictionary (`ai-agent-cpe.xml`)
4. OVAL Variables (`ai-agent-variables.xml`)

