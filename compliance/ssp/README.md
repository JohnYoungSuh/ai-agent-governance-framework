# System Security Plan (SSP) for AI Agent Governance Framework

> NIST SP 800-18 Rev 1 compliant System Security Plan
> FedRAMP and FISMA ready

## Document Control

| Field | Value |
|-------|-------|
| **System Name** | AI Agent Governance Framework (AAGF) |
| **System Abbreviation** | AAGF |
| **Document Version** | 1.0 |
| **Date** | 2025-10-18 |
| **Classification** | CONTROLLED UNCLASSIFIED INFORMATION (CUI) |
| **Security Categorization** | FIPS 199 Moderate (pending) |
| **Authorization Boundary** | AI OPS agents, audit infrastructure, control plane |
| **Prepared By** | Security & Compliance Team |
| **Review Cycle** | Annual or on significant change |

---

## Table of Contents

1. [System Identification](#1-system-identification)
2. [System Categorization](#2-system-categorization)
3. [System Owner](#3-system-owner)
4. [Authorization Boundary](#4-authorization-boundary)
5. [System Description](#5-system-description)
6. [Information Types](#6-information-types)
7. [Security Controls](#7-security-controls)
8. [Interconnections](#8-interconnections)
9. [Laws and Regulations](#9-laws-and-regulations)
10. [Attachments](#10-attachments)

---

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[system-description.md](system-description.md)** | Architecture and components | Architects, Assessors |
| **[control-implementation.md](control-implementation.md)** | Detailed control statements | Auditors, Security |
| **[control-summary.md](control-summary.md)** | At-a-glance control status | Management |
| **[poam.md](poam.md)** | Plan of Action & Milestones | Program Managers |
| **[fedramp-appendices.md](appendices/fedramp-appendices.md)** | FedRAMP-specific docs | FedRAMP reviewers |

---

## SSP Structure

```
compliance/ssp/
├── README.md                          # This file - SSP overview
├── system-description.md              # Section 5: System architecture
├── control-implementation.md          # Section 7: Control statements
├── control-summary.md                 # Executive summary of controls
├── poam.md                            # Plan of Action & Milestones
│
├── appendices/
│   ├── fedramp-appendices.md         # FedRAMP required appendices
│   ├── fips-199-categorization.md    # Security categorization worksheet
│   ├── laws-regulations.md           # Section 9: Applicable laws
│   ├── interconnections.md           # Section 8: System connections
│   └── acronyms.md                   # Acronyms and abbreviations
│
├── diagrams/
│   ├── authorization-boundary.md     # System boundary diagram
│   ├── network-architecture.md       # Network topology
│   ├── data-flow.md                  # Data flow diagrams
│   └── component-inventory.md        # Hardware/software inventory
│
└── attachments/
    ├── policies/                     # Link to ../policies/
    ├── procedures/                   # SOPs and runbooks
    └── evidence/                     # Screenshots, scan results
```

---

## 1. System Identification

### 1.1 System Name and Identifier

**Official System Name**: AI Agent Governance Framework (AAGF)

**System Identifier**: AAGF-PROD-001

**System Type**: Platform as a Service (PaaS) - AI Operations Platform

**Hosting Model**:
- Cloud-hosted (AWS/Azure/GCP) for production
- On-premise option available for restricted environments

### 1.2 System Purpose

The AI Agent Governance Framework provides a secure, auditable platform for deploying and managing autonomous AI agents across development, operations, and security workflows. The system enforces:

- **Tiered access controls** (AC-6-AI-1) limiting agent capabilities by risk level
- **Comprehensive audit trails** (AU-3-AI-1) for all AI decisions
- **Data leakage prevention** (SC-4-AI-1) protecting sensitive data from LLM providers
- **Human-in-the-loop approvals** (AC-6-AI-2) for high-risk actions
- **Cost controls** (SA-15-AI-1) preventing runaway LLM expenses

**Mission**: Enable safe, compliant deployment of AI agents in production environments while maintaining security, auditability, and regulatory compliance.

---

## 2. System Categorization

**FIPS 199 Security Categorization**: MODERATE

**Rationale**: System processes Internal and Confidential data, manages production infrastructure, and requires compliance with multiple regulatory frameworks. Loss of confidentiality, integrity, or availability could result in:
- **Confidentiality**: MODERATE - Exposure of proprietary code or internal processes
- **Integrity**: MODERATE - Unauthorized production changes could impact business operations
- **Availability**: MODERATE - System downtime delays development/deployment workflows

**See**: `appendices/fips-199-categorization.md` for detailed FIPS 199 worksheet

---

## 3. System Owner

| Role | Name | Contact | Responsibilities |
|------|------|---------|------------------|
| **System Owner** | [TO BE COMPLETED] | owner@example.com | Overall system authority and risk acceptance |
| **Authorizing Official (AO)** | [TO BE COMPLETED] | ao@example.com | Authorization to operate decision |
| **Information System Security Officer (ISSO)** | [TO BE COMPLETED] | isso@example.com | Day-to-day security operations |
| **Privacy Officer** | [TO BE COMPLETED] | privacy@example.com | PII/PHI protection (SC-4-AI-1) |
| **System Administrator** | [TO BE COMPLETED] | admin@example.com | Infrastructure management |

**Organizational Affiliation**: [Your Organization Name]

---

## 4. Authorization Boundary

### 4.1 Boundary Description

The authorization boundary encompasses:

**IN SCOPE**:
- ✅ AI OPS Agent runtime infrastructure (Tier 1-4 agents)
- ✅ AI Auditor Agent and audit log storage (AU-9)
- ✅ Control plane (JIRA integration, approval workflows)
- ✅ Secrets management vault integration (IA-5)
- ✅ SIEM integration and alerting (SI-4)
- ✅ Cost monitoring and budget controls (SA-15-AI-1)

**OUT OF SCOPE** (External Dependencies):
- ❌ Hosted LLM providers (OpenAI, Anthropic, etc.) - assessed separately
- ❌ JIRA SaaS platform - covered by vendor SOC 2
- ❌ AWS/Azure/GCP cloud infrastructure - FedRAMP authorized
- ❌ Developer workstations - covered by corporate security policies

**See**: `diagrams/authorization-boundary.md` for visual diagram

### 4.2 Boundary Justification

External LLM providers are outside the boundary because:
1. They are third-party SaaS platforms with independent security certifications
2. Data leakage prevention controls (SC-4-AI-1) protect sensitive data before transmission
3. Vendor assessments are maintained per SA-9 (External Information System Services)

---

## 5. System Description

**See**: `system-description.md` for complete architecture documentation

### High-Level Architecture

The system consists of four primary layers:

1. **Agent Runtime Layer** (Tier 1-4 agents)
   - Enforces AC-6-AI-1 (tier-based privilege separation)
   - Implements SC-4-AI-1 (data leakage prevention)
   - Logs all actions to AU-3-AI-1 compliant audit trail

2. **Control Plane** (Authorization & Orchestration)
   - JIRA integration for change control (CM-3, CM-3-AI-1)
   - Human approval workflows (AC-6-AI-2)
   - Secrets Manager integration (IA-5, IA-5(7))

3. **Audit & Compliance Layer**
   - AI Auditor Agent validates control effectiveness
   - Append-only audit log storage (AU-9)
   - SIEM integration for real-time monitoring (SI-4)

4. **Monitoring & Cost Control**
   - Token usage tracking (SA-15-AI-1)
   - Performance monitoring (CA-7-AI-1)
   - Budget alerts and circuit breakers

**Technology Stack**:
- **Compute**: Kubernetes (EKS/AKS/GKE)
- **Storage**: S3/Blob Storage with Object Lock (AU-9)
- **Secrets**: AWS Secrets Manager / HashiCorp Vault (IA-5)
- **Monitoring**: Prometheus + Grafana (CA-7)
- **SIEM**: Splunk / Elastic Security (SI-4)

---

## 6. Information Types

**Based on NIST SP 800-60 and SC-4 Data Classification**

| Classification | Description | FIPS 199 Impact | Controls |
|----------------|-------------|-----------------|----------|
| **Public** | Open-source code, public docs | LOW | Standard logging |
| **Internal** | Proprietary code, internal processes | MODERATE | SC-4, AU-3, encryption at rest |
| **Confidential** | Customer data, financial info | MODERATE | SC-4-AI-1, SC-28(1), AU-9 |
| **Restricted** | PII, PHI, credentials | HIGH | No AI processing, human-only |

**PII Processing**: System may process developer names and email addresses (AU-3 logs)
- **Authority**: Privacy Officer approval required
- **Protection**: SC-4-AI-1 prevents PII transmission to LLM providers
- **Retention**: Per AU-11 and organizational privacy policy

---

## 7. Security Controls

### Control Baseline

**Selected Baseline**: NIST 800-53 Rev 5 MODERATE Baseline + AI Extensions

**Control Summary**:
- **Total Controls**: 325 baseline controls + 14 AI extensions = 339 controls
- **Implemented**: [TO BE COMPLETED after control assessment]
- **Partially Implemented**: [TO BE COMPLETED]
- **Planned**: See POA&M

### Control Families

| Family | Controls | Implementation Status | Document Reference |
|--------|----------|----------------------|---------------------|
| **AC** (Access Control) | 25 controls + AC-6-AI-1, AC-6-AI-2 | ✅ Implemented | `control-implementation.md` |
| **AU** (Audit) | 16 controls + AU-3-AI-1 | ✅ Implemented | `control-implementation.md` |
| **CM** (Config Mgmt) | 14 controls + CM-3-AI-1 | 🟡 Partial | `poam.md` Item #3 |
| **IA** (Identification) | 11 controls + IA-5(7) | ✅ Implemented | `control-implementation.md` |
| **SC** (System Protection) | 51 controls + SC-4-AI-1, SC-4-AI-2 | 🟡 Partial | `poam.md` Item #1 |
| **SI** (System Integrity) | 23 controls + SI-7-AI-1, SI-7-AI-2 | 🟡 Partial | `poam.md` Item #5 |
| **RA** (Risk Assessment) | 10 controls + RA-9-AI-1, RA-9-AI-2, RA-5-AI-1 | ✅ Implemented | `control-implementation.md` |
| **CA** (Assessment) | 9 controls + CA-7-AI-1 | 🟡 Partial | `poam.md` Item #7 |
| **SA** (Acquisition) | 22 controls + SA-15-AI-1 | ✅ Implemented | `control-implementation.md` |

**Detailed Implementation Statements**: See `control-implementation.md`

**At-a-Glance Summary**: See `control-summary.md`

### Tailoring Actions

**Controls Not Applicable**:
- **PE Family** (Physical and Environmental Protection): Not applicable to cloud-hosted SaaS
  - PE-1 through PE-20 marked N/A
  - Inherited from AWS/Azure/GCP FedRAMP authorization

- **MA Family** (Maintenance): Limited applicability for PaaS
  - MA-2, MA-3 inherited from cloud provider
  - MA-4, MA-6 implemented for application-layer maintenance

**See**: `appendices/fedramp-appendices.md` for complete tailoring rationale

---

## 8. Interconnections

**See**: `appendices/interconnections.md` for detailed interconnection security agreements (ISAs)

| External System | Purpose | Data Exchanged | Security Controls |
|-----------------|---------|----------------|-------------------|
| **OpenAI API** | LLM inference | Redacted prompts (SC-4-AI-1) | TLS 1.3, DLP, audit logging |
| **Anthropic API** | LLM inference | Redacted prompts (SC-4-AI-1) | TLS 1.3, DLP, audit logging |
| **JIRA Cloud** | Change management | Ticket metadata (CM-3) | OAuth 2.0, API tokens (IA-5) |
| **AWS Secrets Manager** | Credential storage | Secret references (IA-5(7)) | IAM roles, KMS encryption |
| **Splunk Cloud** | SIEM | Audit logs (AU-3) | TLS 1.3, append-only, immutable |

**Interconnection Agreements**: Required per CA-3 (System Interconnections)

---

## 9. Laws and Regulations

**See**: `appendices/laws-regulations.md` for complete list

### Applicable Frameworks

| Framework | Applicability | Relevant Controls |
|-----------|--------------|-------------------|
| **FISMA** | Federal systems | All MODERATE baseline controls |
| **FedRAMP** | Cloud services for federal | MODERATE + CRM + Agency-specific |
| **NIST AI RMF** | AI systems | RA-9-AI-1, SI-7-AI-1, all AI extensions |
| **SOX** | Financial systems (if applicable) | AU-9, AU-11 (7-year retention), CM-3 |
| **HIPAA** | Healthcare PHI (if applicable) | SC-4-AI-1, AU-3-AI-1, IA-5 |
| **PCI-DSS** | Payment data (if applicable) | SC-4-AI-1, AU-9, AC-6-AI-2 |
| **EU GDPR** | EU citizen data | SC-4-AI-1, PL-8, AU-11 |
| **EU AI Act** | High-risk AI systems | AU-3-AI-1, RA-5-AI-1, SI-7-AI-1 |

---

## 10. Attachments

### 10.1 Required Attachments

- [x] **Attachment 1**: System Authorization Boundary Diagram → `diagrams/authorization-boundary.md`
- [x] **Attachment 2**: Network Architecture Diagram → `diagrams/network-architecture.md`
- [x] **Attachment 3**: Data Flow Diagram → `diagrams/data-flow.md`
- [x] **Attachment 4**: Policies and Procedures → `../policies/`
- [ ] **Attachment 5**: Contingency Plan (CP) → `attachments/contingency-plan.md` [PENDING]
- [ ] **Attachment 6**: Incident Response Plan (IR) → `attachments/incident-response-plan.md` [PENDING]
- [ ] **Attachment 7**: Configuration Management Plan → `attachments/cm-plan.md` [PENDING]
- [x] **Attachment 8**: Control Implementation Evidence → `control-implementation.md`
- [x] **Attachment 9**: POA&M → `poam.md`
- [ ] **Attachment 10**: Privacy Impact Assessment (PIA) → `attachments/pia.md` [PENDING]

### 10.2 FedRAMP-Specific Attachments

For FedRAMP authorization, additional appendices required:
- [x] **Appendix A**: FedRAMP Security Controls → `appendices/fedramp-appendices.md`
- [ ] **Appendix B**: FIPS 199 Categorization → `appendices/fips-199-categorization.md` [PENDING]
- [x] **Appendix C**: Laws and Regulations → `appendices/laws-regulations.md`
- [x] **Appendix D**: Acronyms → `appendices/acronyms.md`
- [ ] **Appendix E**: Security Assessment Plan (SAP) → `appendices/security-assessment-plan.md` [PENDING]
- [ ] **Appendix F**: Continuous Monitoring Strategy → `appendices/continuous-monitoring.md` [PENDING]

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **System Owner** | [TO BE COMPLETED] | _______________ | ________ |
| **ISSO** | [TO BE COMPLETED] | _______________ | ________ |
| **Privacy Officer** | [TO BE COMPLETED] | _______________ | ________ |
| **Authorizing Official** | [TO BE COMPLETED] | _______________ | ________ |

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-10-18 | Security Team | Initial draft |
| 1.0 | [PENDING] | [TO BE COMPLETED] | Approved for ATO submission |

---

## Next Steps

### For Initial ATO (Authorization to Operate)

1. ✅ Complete this SSP template with organization-specific details
2. ⏳ Conduct FIPS 199 categorization (see `appendices/fips-199-categorization.md`)
3. ⏳ Complete control implementation statements (see `control-implementation.md`)
4. ⏳ Address all POA&M items (see `poam.md`)
5. ⏳ Engage 3PAO (Third-Party Assessment Organization) for security assessment
6. ⏳ Remediate findings and update POA&M
7. ⏳ Submit authorization package to AO
8. ⏳ Receive ATO decision

### For Annual Review

1. Review all control implementation statements for accuracy
2. Update POA&M with progress and new items
3. Refresh interconnection agreements (CA-3)
4. Update system description for any architecture changes
5. Conduct annual security assessment
6. Submit annual assessment report to AO

---

**Questions?** Contact the ISSO or Security Team
**Document Location**: `compliance/ssp/`
**Related Documents**: `../policies/` (security policies and controls)
