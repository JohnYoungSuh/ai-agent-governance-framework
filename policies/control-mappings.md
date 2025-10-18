# NIST RMF Control Mappings for AI Agent Governance

> Maps AI Agent policies to NIST 800-53 Rev 5 controls and CCI identifiers

## Overview

This document provides authoritative mappings between:
- **NIST 800-53 Rev 5** controls (e.g., AC-2, AU-3, IA-5)
- **CCI (Control Correlation Identifiers)** from DISA STIG
- **AI-specific control extensions** using the convention `{FAMILY}-{NUMBER}-AI-{EXT}`

## Control Mapping Table

| Policy Area | Legacy ID | NIST 800-53 Control | CCI | Control Title |
|-------------|-----------|---------------------|-----|---------------|
| **ACCESS CONTROL** |
| Least Privilege | SEC-003 | AC-6 | CCI-002220 | Least Privilege |
| Least Privilege | SEC-003 | AC-6(1) | CCI-002233 | Authorize Access to Security Functions |
| Least Privilege | SEC-003 | AC-6(9) | CCI-002235 | Log Use of Privileged Functions |
| Service Accounts | SEC-003 | AC-2 | CCI-000015 | Account Management |
| Service Accounts | SEC-003 | AC-2(7) | CCI-000016 | Role-Based Schemes |
| Access Reviews | SEC-003 | AC-2(3) | CCI-000017 | Disable Accounts |
| **AUDIT AND ACCOUNTABILITY** |
| Audit Trail | COMP-001 | AU-2 | CCI-000130 | Event Logging |
| Audit Trail | COMP-001 | AU-3 | CCI-000131 | Content of Audit Records |
| Audit Trail | COMP-001 | AU-3(1) | CCI-000133 | Additional Audit Information |
| Audit Trail | COMP-001 | AU-8 | CCI-000159 | Time Stamps |
| Audit Trail | COMP-001 | AU-9 | CCI-000162 | Protection of Audit Information |
| Audit Trail | COMP-001 | AU-9(2) | CCI-001350 | Store on Separate Physical Systems |
| Audit Trail | COMP-001 | AU-11 | CCI-001849 | Audit Record Retention |
| Logging Protection | - | AU-9(3) | CCI-001351 | Cryptographic Protection |
| **IDENTIFICATION AND AUTHENTICATION** |
| Credential Management | SEC-001 | IA-5 | CCI-000195 | Authenticator Management |
| Credential Management | SEC-001 | IA-5(1) | CCI-000196 | Password-Based Authentication |
| Credential Management | SEC-001 | IA-5(7) | CCI-004062 | No Embedded Unencrypted Static Authenticators |
| Secrets Vault | SEC-001 | IA-5(2) | CCI-004063 | Public Key-Based Authentication |
| **SYSTEM AND COMMUNICATIONS PROTECTION** |
| Data Classification | SEC-002 | SC-4 | CCI-001414 | Information in Shared System Resources |
| Data Classification | SEC-002 | SC-28 | CCI-001199 | Protection of Information at Rest |
| Data Classification | SEC-002 | SC-28(1) | CCI-002475 | Cryptographic Protection |
| Data Residency | COMP-003 | SC-7(21) | CCI-003748 | Isolation of System Components |
| **CONFIGURATION MANAGEMENT** |
| Change Management | COMP-002 | CM-3 | CCI-000066 | Configuration Change Control |
| Change Management | COMP-002 | CM-3(2) | CCI-001813 | Test / Validate / Document Changes |
| Change Management | COMP-002 | CM-4 | CCI-001812 | Impact Analyses |
| Rollback Plan | COMP-002 | CM-5(1) | CCI-001814 | Automated Access Enforcement / Auditing |
| Version Pinning | - | CM-7 | CCI-000381 | Least Functionality |
| **PLANNING** |
| Data Residency | COMP-003 | PL-8 | CCI-000352 | Security and Privacy Architectures |
| Data Residency | COMP-003 | PL-8(1) | CCI-003505 | Defense in Depth |
| **RISK ASSESSMENT** |
| Threat Modeling | - | RA-3 | CCI-001484 | Risk Assessment |
| Threat Modeling | - | RA-3(1) | CCI-001666 | Supply Chain Risk Assessment |
| Bias Testing | - | RA-9 | CCI-002239 | Criticality Analysis |

---

## AI-Specific Control Extensions

For AI/ML-specific requirements not directly covered by NIST 800-53, we use the following convention:

**Format**: `{FAMILY}-{NUMBER}-AI-{EXTENSION}`

Example: `SC-42-AI-1` = System and Communications Protection - Sensor Capability and Data (AI Extension 1)

### Defined AI Extensions

| Control ID | CCI | Title | Description |
|------------|-----|-------|-------------|
| **RA-9-AI-1** | CCI-AI-001 | Model Hallucination Risk | Assess and mitigate risks from AI model hallucinations and false information generation |
| **RA-9-AI-2** | CCI-AI-002 | Prompt Injection Risk | Assess and mitigate prompt injection and jailbreak attack vectors |
| **SC-4-AI-1** | CCI-AI-003 | Data Leakage to LLM Providers | Prevent sensitive data leakage to hosted LLM provider APIs |
| **SC-4-AI-2** | CCI-AI-004 | Vector Store Data Isolation | Enforce access controls and data isolation in RAG vector stores |
| **AC-6-AI-1** | CCI-AI-005 | AI Agent Tier Enforcement | Enforce tier-based privilege separation for AI agents |
| **AC-6-AI-2** | CCI-AI-006 | Human-in-the-Loop Authorization | Require human approval for high-privilege agent actions |
| **CM-3-AI-1** | CCI-AI-007 | Model Version Control | Control and document LLM model version changes and updates |
| **AU-3-AI-1** | CCI-AI-008 | AI Decision Auditability | Log sufficient detail to reproduce AI agent reasoning and decisions |
| **SI-7-AI-1** | CCI-AI-009 | Output Validation & Fact-Checking | Validate AI outputs against known truth sources |
| **SI-7-AI-2** | CCI-AI-010 | LLM-as-Judge Verification | Use secondary AI models for output quality verification |
| **RA-5-AI-1** | CCI-AI-011 | Bias and Fairness Testing | Test for demographic bias and unfair outputs |
| **CA-7-AI-1** | CCI-AI-012 | Model Performance Monitoring | Continuously monitor for model drift, degradation, and stale data |
| **SA-15-AI-1** | CCI-AI-013 | Cost and Budget Controls | Implement hard limits and monitoring for AI API consumption costs |
| **IR-5-AI-1** | CCI-AI-014 | AI Incident Response | Establish procedures for AI-specific incidents (hallucinations, bias, etc.) |

---

## Control Overlays by Compliance Framework

### FedRAMP Moderate Baseline
All FedRAMP Moderate controls apply, with additional AI extensions:
- RA-9-AI-1, RA-9-AI-2 (AI Risk Assessment)
- SC-4-AI-1 (Data Leakage Prevention)
- AC-6-AI-2 (Human Approval for High-Risk Actions)
- AU-3-AI-1 (AI Decision Auditability)

### PCI-DSS 4.0 (for payment data)
- SC-4-AI-1 (Critical): Prevent cardholder data leakage to LLM APIs
- SC-4-AI-2 (Critical): Isolate payment data in vector stores
- AU-3-AI-1 (Required): Audit all AI agent access to payment systems
- AC-6-AI-2 (Required): Human approval for any payment-related agent actions

### HIPAA (for healthcare PHI)
- SC-4-AI-1 (Critical): Prevent PHI leakage to hosted LLM providers
- AU-3-AI-1 (Required): Log all AI access to PHI with patient identifiers
- AC-6-AI-2 (Required): Human approval for clinical decisions
- SI-7-AI-1 (Required): Validate medical information accuracy

### EU AI Act - High-Risk Systems
- RA-9-AI-1 (Required): Hallucination risk assessment for high-risk AI
- RA-5-AI-1 (Required): Bias testing for protected characteristics
- AU-3-AI-1 (Required): Full transparency and explainability logging
- AC-6-AI-2 (Required): Human oversight for all high-risk decisions
- SI-7-AI-1 (Required): Output validation for safety-critical systems

### SOC 2 Type II
- AU-2, AU-3, AU-3-AI-1 (Required): Comprehensive audit logging
- AC-6, AC-6-AI-1, AC-6-AI-2 (Required): Tier enforcement and approvals
- CM-3, CM-3-AI-1 (Required): Change control for model versions
- CA-7-AI-1 (Required): Continuous monitoring of AI operations

---

## Risk-to-Control Mapping

| Risk ID | Risk Name | Primary Controls | Supporting Controls |
|---------|-----------|------------------|---------------------|
| RI-001 | Hallucination & False Information | SI-7-AI-1, SI-7-AI-2 | AU-3-AI-1, AC-6-AI-2 |
| RI-002 | Model Version Drift | CM-3-AI-1, CA-7-AI-1 | CM-3, CM-4 |
| RI-006 | Bias & Discrimination | RA-5-AI-1, SI-7-AI-2 | AC-6-AI-2, AU-3-AI-1 |
| RI-014 | Prompt Injection | RA-9-AI-2, SI-10 | SI-3, AC-6 |
| RI-015 | Data Leakage to LLM | SC-4-AI-1, IA-5(7) | AU-3, SC-28 |
| RI-016 | Regulatory Violations | All applicable controls | AU-11, AU-9 |
| RI-018 | Cost Overruns | SA-15-AI-1 | CA-7-AI-1, AU-2 |

---

## Mitigation-to-Control Mapping

| Mitigation ID | Mitigation Name | Primary Controls | CCI References |
|---------------|-----------------|------------------|----------------|
| MI-001 | Data Leakage Prevention | SC-4-AI-1, IA-5(7) | CCI-AI-003, CCI-004062 |
| MI-002 | Input Filtering | SI-10, RA-9-AI-2 | CCI-002754, CCI-AI-002 |
| MI-003 | Secrets Management | IA-5, IA-5(7) | CCI-000195, CCI-004062 |
| MI-004 | Observability | AU-2, AU-3, CA-7 | CCI-000130, CCI-000131 |
| MI-006 | Access Controls | AC-6, AC-6-AI-1 | CCI-002220, CCI-AI-005 |
| MI-007 | Human Review | AC-6-AI-2 | CCI-AI-006 |
| MI-009 | Cost Monitoring | SA-15-AI-1, CA-7-AI-1 | CCI-AI-013, CCI-AI-012 |
| MI-010 | Version Pinning | CM-3-AI-1, CM-7 | CCI-AI-007, CCI-000381 |
| MI-012 | Bias Testing | RA-5-AI-1 | CCI-AI-011 |
| MI-013 | Citations | SI-7-AI-1 | CCI-AI-009 |
| MI-015 | LLM-as-Judge | SI-7-AI-2 | CCI-AI-010 |
| MI-018 | Compliance Mapping | See overlay tables above | Multiple |
| MI-019 | Audit Trails | AU-2, AU-3, AU-3-AI-1 | CCI-000130, CCI-AI-008 |
| MI-020 | Tier Enforcement | AC-6-AI-1 | CCI-AI-005 |
| MI-021 | Budget Limits | SA-15-AI-1 | CCI-AI-013 |

---

## Control Implementation Responsibility

| Control Family | Development Team | Operations Team | Security Team | Compliance Team |
|----------------|------------------|-----------------|---------------|-----------------|
| AC (Access Control) | Configure RBAC | Monitor access | Review permissions | Audit compliance |
| AU (Audit) | Implement logging | Maintain SIEM | Analyze logs | Retention compliance |
| CM (Configuration Mgmt) | Version control | Deploy changes | Approve changes | Document changes |
| IA (Identification/Auth) | Integrate vault | Rotate secrets | Monitor auth | Audit credentials |
| RA (Risk Assessment) | Run bias tests | Monitor drift | Threat modeling | Risk acceptance |
| SC (System Protection) | Implement DLP | Monitor traffic | Review incidents | Data classification |
| SI (System Integrity) | Validate outputs | Monitor quality | Investigate issues | Report incidents |

---

## References

### Standards
- **NIST SP 800-53 Rev 5**: Security and Privacy Controls for Information Systems
- **NIST AI RMF**: AI Risk Management Framework (NIST AI 100-1)
- **DISA CCI**: Control Correlation Identifiers
- **FedRAMP**: Federal Risk and Authorization Management Program
- **PCI-DSS 4.0**: Payment Card Industry Data Security Standard
- **EU AI Act**: Regulation on Artificial Intelligence

### Control Catalogs
- NIST 800-53B: Control Baselines for Information Systems
- NIST SP 800-171: Protecting CUI in Nonfederal Systems
- ISO/IEC 27001:2022: Information Security Management
- ISO/IEC 42001:2023: AI Management System

---

**Version**: 1.0
**Last Updated**: 2025-10-18
**Maintained By**: Security & Compliance Team
