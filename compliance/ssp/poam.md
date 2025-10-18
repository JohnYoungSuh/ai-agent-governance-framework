# Plan of Action & Milestones (POA&M)

> Remediation plan for control weaknesses and security gaps
> AI Agent Governance Framework (AAGF)

**System**: AAGF-PROD-001
**Document Version**: 1.0
**Last Updated**: 2025-10-18
**Review Frequency**: Monthly
**Next Review**: 2025-11-18

---

## POA&M Overview

| Metric | Value |
|--------|-------|
| **Total Open Items** | 11 |
| **High Priority** | 4 |
| **Medium Priority** | 7 |
| **Low Priority** | 0 |
| **Overdue Items** | 0 |
| **On Track** | 11 (100%) |

**Authorization Impact**: All items have compensating controls. System remains in acceptable risk posture for ATO.

---

## POA&M Items

### POA&M #1: Vector Store Data Isolation (SC-4-AI-2)

**Control**: SC-4-AI-2 - Vector Store Data Isolation | **CCI**: CCI-AI-004
**Priority**: 🔴 **HIGH**
**Status**: 🟡 Partially Implemented
**Risk Level**: MEDIUM

#### Weakness Description

Current vector store (Pinecone/Chroma) access controls do not enforce per-user data isolation for RAG (Retrieval-Augmented Generation) implementations. Agent can potentially retrieve documents outside authorized scope through crafted similarity queries.

**Specific Gaps**:
- Namespace isolation configured, but not enforced at query time
- Metadata filtering relies on application layer, not database ACLs
- No cryptographic separation between user data partitions

#### Impact Assessment

**Confidentiality**: MODERATE - Potential for cross-user data leakage via vector search
**Integrity**: LOW - Data cannot be modified, only read
**Availability**: NONE

**Affected Systems**:
- Tier 3 agents using RAG functionality
- Vector databases: Pinecone (production), Chroma (development)

#### Current Compensating Controls

1. **Application-Layer Filtering**: Agents filter by metadata before query execution
```python
# Current implementation
def query_vector_store(query_embedding, user_id):
    results = vector_db.query(
        vector=query_embedding,
        filter={"user_id": user_id},  # App-level filter
        top_k=10
    )
    return results
```

2. **Audit Logging** (AU-3-AI-1): All vector queries logged with agent ID and filters
3. **Agent Tier Restrictions** (AC-6-AI-1): Only Tier 3+ agents have vector store access

**Current Risk**: **ACCEPTABLE** (Low likelihood due to compensating controls)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 1.1 | Evaluate database-native RBAC capabilities (Pinecone Teams vs. Weaviate) | ML Engineering | 2025-11-15 | ⏳ In Progress |
| 1.2 | Design cryptographic isolation scheme (per-user encryption keys) | Security Engineering | 2025-11-30 | 📅 Scheduled |
| 1.3 | Implement database-native ACLs in development | ML Engineering | 2025-12-20 | 📅 Scheduled |
| 1.4 | Conduct penetration testing of isolation (attempt cross-user query) | Security Team | 2026-01-15 | 📅 Scheduled |
| 1.5 | Deploy to production with monitoring | DevOps | 2026-01-31 | 📅 Scheduled |

**Target Completion**: 2026-01-31

#### Cost and Resources

- **Engineering**: 120 hours (ML + Security)
- **Budget**: $0 (existing licenses support RBAC)
- **Testing**: Included in annual penetration test budget

#### Evidence of Completion

- [ ] Updated architecture diagram showing cryptographic isolation
- [ ] Penetration test report: no cross-user data leakage
- [ ] Audit logs showing ACL enforcement at database layer
- [ ] Updated `control-implementation.md` § SC-4-AI-2

---

### POA&M #3: Change Management Automation (CM-3(2))

**Control**: CM-3(2) - Test / Validate / Document Changes | **CCI**: CCI-001813
**Priority**: 🔴 **HIGH**
**Status**: 🟡 Partially Implemented
**Risk Level**: MEDIUM

#### Weakness Description

Automated testing coverage for configuration changes is incomplete. Currently:
- ✅ Infrastructure changes (Terraform) have automated tests
- ✅ Application code has CI/CD with unit/integration tests
- ❌ Security configuration changes lack automated validation
- ❌ Model version changes have manual regression testing only

**Example Gaps**:
- Changing SIEM alert thresholds: Manual review only
- Updating data classification rules: No automated compliance check
- Model version updates: SAT (Standard Acceptance Test) suite exists but requires manual trigger

#### Impact Assessment

**Confidentiality**: LOW - No direct impact
**Integrity**: MODERATE - Untested config changes could break security controls
**Availability**: MODERATE - Misconfiguration could cause agent downtime

**Affected Systems**: All tiers (configuration changes)

#### Current Compensating Controls

1. **Human Review** (CM-3): All changes require multi-person approval
2. **Rollback Plans** (CM-3(d)): Every change includes rollback procedure
3. **Post-Change Validation** (CM-3(e)): Manual spot-checks on 10% random sample

**Current Risk**: **ACCEPTABLE** (Manual processes robust, but not scalable)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 3.1 | Create automated SAT trigger in CI/CD for model version changes | ML Engineering | 2025-12-01 | ⏳ In Progress |
| 3.2 | Build validation pipeline for security config changes | Security Engineering | 2025-12-15 | 📅 Scheduled |
| 3.3 | Implement compliance checker for data classification rules | Security Engineering | 2026-01-10 | 📅 Scheduled |
| 3.4 | Document testing requirements in change templates | DevOps | 2026-01-20 | 📅 Scheduled |
| 3.5 | Training session for all engineers on new validation process | Training | 2026-02-15 | 📅 Scheduled |

**Target Completion**: 2026-02-15

#### Cost and Resources

- **Engineering**: 160 hours (DevOps + Security)
- **Budget**: $5,000 (CI/CD infrastructure expansion)
- **Training**: 4-hour session for 20 engineers

#### Evidence of Completion

- [ ] CI/CD pipeline showing automated model version regression tests
- [ ] Security config validation script + test results
- [ ] Data classification compliance checker code
- [ ] Updated change management templates
- [ ] Training attendance records

---

### POA&M #5: Output Validation Expansion (SI-7-AI-1)

**Control**: SI-7-AI-1 - Output Validation & Fact-Checking | **CCI**: CCI-AI-009
**Priority**: 🟡 **MEDIUM**
**Status**: 🟡 Partially Implemented
**Risk Level**: LOW

#### Weakness Description

AI output validation currently limited to:
- ✅ Basic hallucination detection (citation checking)
- ✅ Format validation (JSON schema compliance)
- ❌ Automated fact-checking against trusted sources
- ❌ Quantitative claim verification
- ❌ Code correctness validation (beyond syntax)

**Impact**: Agents may generate plausible but factually incorrect outputs (Risk RI-001: Hallucination)

#### Impact Assessment

**Confidentiality**: NONE
**Integrity**: MODERATE - Incorrect outputs could lead to bad decisions
**Availability**: NONE

**Affected Systems**: Tier 2-4 agents (all production decision-making)

#### Current Compensating Controls

1. **Human Review** (AC-6-AI-2): High-risk actions require human approval
2. **LLM Temperature**: Set to 0.1 (low randomness) for factual tasks
3. **Citation Requirement** (MI-013): Agents must cite sources for claims
4. **Audit Logging** (AU-3-AI-1): All outputs logged for post-hoc review

**Current Risk**: **ACCEPTABLE** (Low impact due to human oversight)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 5.1 | Integrate fact-checking API (e.g., Google Fact Check Tools) | ML Engineering | 2026-01-15 | 📅 Scheduled |
| 5.2 | Build quantitative claim validator (numerical assertion checker) | ML Engineering | 2026-02-01 | 📅 Scheduled |
| 5.3 | Implement code execution sandbox for code validation | Security Engineering | 2026-02-15 | 📅 Scheduled |
| 5.4 | Deploy validation pipeline with success metrics | DevOps | 2026-03-01 | 📅 Scheduled |

**Target Completion**: 2026-03-01

#### Cost and Resources

- **Engineering**: 80 hours (ML + Security)
- **Budget**: $2,500 (fact-checking API subscriptions)
- **Infrastructure**: Sandbox environment for code execution

#### Evidence of Completion

- [ ] Fact-checking integration code + test results
- [ ] Quantitative validator accuracy report (>95% target)
- [ ] Code execution sandbox documentation
- [ ] Updated `control-implementation.md` § SI-7-AI-1

---

### POA&M #6: LLM-as-Judge Implementation (SI-7-AI-2)

**Control**: SI-7-AI-2 - LLM-as-Judge Verification | **CCI**: CCI-AI-010
**Priority**: 🟡 **MEDIUM**
**Status**: 📅 Planned (Not Yet Started)
**Risk Level**: LOW

#### Weakness Description

No secondary LLM deployed to validate primary agent outputs. LLM-as-Judge pattern provides:
- Quality scoring of agent outputs
- Detection of reasoning errors or logical fallacies
- Bias detection in decision-making
- Hallucination cross-check

**Current State**: Relying solely on single-model outputs

#### Impact Assessment

**Confidentiality**: NONE
**Integrity**: MODERATE - Reduced confidence in output correctness
**Availability**: NONE

**Affected Systems**: Tier 3-4 agents (production decision-making)

#### Current Compensating Controls

1. **Human Review** (AC-6-AI-2): Required for all Tier 3 production changes
2. **Citation Checking**: Validate sources exist and are relevant
3. **Deterministic Validation**: Where possible (e.g., schema compliance)

**Current Risk**: **ACCEPTABLE** (Human review provides final check)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 6.1 | Select judge model (e.g., Claude 3 Opus, GPT-4 Turbo) | ML Engineering | 2026-02-01 | 📅 Scheduled |
| 6.2 | Design judge prompts and scoring rubrics | ML Engineering | 2026-02-15 | 📅 Scheduled |
| 6.3 | Build judgment pipeline (parallel to primary agent) | ML Engineering | 2026-03-15 | 📅 Scheduled |
| 6.4 | Calibrate scoring thresholds (what score blocks execution?) | ML Engineering + Security | 2026-04-01 | 📅 Scheduled |
| 6.5 | Deploy to production with monitoring | DevOps | 2026-04-15 | 📅 Scheduled |

**Target Completion**: 2026-04-15

#### Cost and Resources

- **Engineering**: 100 hours (ML)
- **Budget**: $15,000/year (additional LLM API costs for judge model)
- **Performance Impact**: +500ms latency per agent action

#### Evidence of Completion

- [ ] Judge model deployment documentation
- [ ] Scoring rubric and threshold calibration report
- [ ] Production metrics: judge score distribution, blocked actions
- [ ] Cost analysis: judge model vs. primary model
- [ ] Updated `control-implementation.md` § SI-7-AI-2

---

### POA&M #7: Performance Monitoring Enhancement (CA-7-AI-1)

**Control**: CA-7-AI-1 - Model Performance Monitoring | **CCI**: CCI-AI-012
**Priority**: 🟡 **MEDIUM**
**Status**: 🟡 Partially Implemented
**Risk Level**: LOW

#### Weakness Description

Current monitoring provides basic metrics only:
- ✅ API latency and error rates
- ✅ Cost tracking (SA-15-AI-1)
- ❌ Model drift detection (output quality degradation over time)
- ❌ Hallucination rate trending
- ❌ Confidence score distribution analysis
- ❌ Automated alerting on quality degradation

#### Impact Assessment

**Confidentiality**: NONE
**Integrity**: LOW - May not detect gradual quality degradation
**Availability**: NONE

**Affected Systems**: All agent tiers

#### Current Compensating Controls

1. **Human Spot-Checks**: Weekly review of random agent outputs (10% sample)
2. **User Feedback**: Engineers report quality issues manually
3. **Model Version Pinning** (CM-3-AI-1): Prevents unexpected model changes

**Current Risk**: **ACCEPTABLE** (Manual monitoring catches major issues)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 7.1 | Define quality metrics baseline (hallucination rate, confidence, etc.) | ML Engineering | 2025-12-15 | ⏳ In Progress |
| 7.2 | Build automated quality scoring pipeline | ML Engineering | 2026-01-15 | 📅 Scheduled |
| 7.3 | Configure Grafana dashboards for quality trends | DevOps | 2026-01-31 | 📅 Scheduled |
| 7.4 | Set up SIEM alerts for quality degradation (>10% drop) | Security Operations | 2026-02-15 | 📅 Scheduled |
| 7.5 | Document response procedures for quality alerts | DevOps | 2026-02-28 | 📅 Scheduled |

**Target Completion**: 2026-02-28

#### Cost and Resources

- **Engineering**: 60 hours (ML + DevOps)
- **Budget**: $0 (existing Grafana/SIEM infrastructure)
- **Ongoing**: 4 hours/month reviewing quality reports

#### Evidence of Completion

- [ ] Quality metrics baseline documentation
- [ ] Automated scoring pipeline code + tests
- [ ] Grafana dashboard screenshots
- [ ] SIEM alert rules configuration
- [ ] Response runbook documentation

---

### POA&M #8: Bias Testing Automation (RA-5-AI-1)

**Control**: RA-5-AI-1 - Bias and Fairness Testing | **CCI**: CCI-AI-011
**Priority**: 🟡 **MEDIUM**
**Status**: 🟡 Partially Implemented
**Risk Level**: LOW

#### Weakness Description

Bias and fairness testing currently manual:
- ✅ Initial bias assessment completed (demographic parity tested)
- ❌ No automated continuous bias monitoring
- ❌ Limited demographic coverage (gender, race only - no age, disability, etc.)
- ❌ No regression testing on model version updates

**Risk**: Agents may produce biased outputs affecting protected classes (Risk RI-006)

#### Impact Assessment

**Confidentiality**: NONE
**Integrity**: MODERATE - Reputational and legal risk if bias detected
**Availability**: NONE

**Affected Systems**: Tier 3-4 agents (production user-facing)

#### Current Compensating Controls

1. **Human Review** (AC-6-AI-2): Required for user-facing decisions
2. **Initial Assessment**: One-time bias testing completed 2025-09-01
3. **Audit Logging** (AU-3-AI-1): All decisions logged for post-hoc analysis

**Current Risk**: **ACCEPTABLE** (Initial testing passed, human oversight active)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 8.1 | Expand test dataset with diverse demographics | ML Engineering | 2026-02-01 | 📅 Scheduled |
| 8.2 | Integrate bias testing library (e.g., Fairlearn, AIF360) | ML Engineering | 2026-03-01 | 📅 Scheduled |
| 8.3 | Build automated bias testing in CI/CD for model updates | ML Engineering | 2026-04-01 | 📅 Scheduled |
| 8.4 | Configure monthly automated bias reports | ML Engineering | 2026-04-15 | 📅 Scheduled |
| 8.5 | Document bias thresholds and remediation procedures | ML Engineering + Legal | 2026-05-01 | 📅 Scheduled |

**Target Completion**: 2026-05-01

#### Cost and Resources

- **Engineering**: 120 hours (ML)
- **Budget**: $10,000 (diverse test dataset creation)
- **Legal Review**: 8 hours (bias threshold approval)

#### Evidence of Completion

- [ ] Expanded test dataset documentation (demographics breakdown)
- [ ] Automated bias testing pipeline code
- [ ] Monthly bias report samples (3 months minimum)
- [ ] Bias remediation procedures documentation
- [ ] Legal approval of bias thresholds

---

### POA&M #9: Annual Security Assessment (CA-2)

**Control**: CA-2 - Control Assessments | **CCI**: CCI-002065
**Priority**: 🔴 **HIGH**
**Status**: 📅 Planned (Scheduled)
**Risk Level**: NONE (Timing issue, not weakness)

#### Weakness Description

Annual security assessment not yet conducted. Required for:
- FedRAMP continuous monitoring
- SOC 2 Type II attestation
- Internal audit requirements

**Current State**: System deployed 2025-10-01, first annual assessment due Q1 2026

#### Impact Assessment

**Confidentiality**: NONE (No technical weakness)
**Integrity**: NONE
**Availability**: NONE

**Impact**: Authorization renewal at risk if not completed on schedule

#### Current Compensating Controls

1. **Continuous Monitoring** (CA-7): Real-time SIEM alerts and dashboards
2. **Quarterly Internal Reviews**: DevOps + Security self-assessments
3. **Initial SSP** (This Document): Comprehensive control documentation

**Current Risk**: **LOW** (Scheduled within required timeframe)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 9.1 | Engage 3PAO (Third-Party Assessment Organization) | ISSO | 2026-01-15 | 📅 Scheduled |
| 9.2 | Prepare assessment evidence packages | Security Team | 2026-02-15 | 📅 Scheduled |
| 9.3 | Conduct on-site (virtual) assessment | 3PAO | 2026-03-01 - 2026-03-15 | 📅 Scheduled |
| 9.4 | Remediate findings and update POA&M | Security Team | 2026-03-25 | 📅 Scheduled |
| 9.5 | Submit Security Assessment Report (SAR) to AO | ISSO | 2026-03-31 | 📅 Scheduled |

**Target Completion**: 2026-03-31

#### Cost and Resources

- **3PAO Fee**: $50,000 - $75,000 (depending on scope)
- **Internal Effort**: 200 hours (evidence preparation + remediation)
- **Schedule**: 3 months (January - March 2026)

#### Evidence of Completion

- [ ] 3PAO engagement letter
- [ ] Security Assessment Plan (SAP)
- [ ] Security Assessment Report (SAR)
- [ ] Updated POA&M with any new findings
- [ ] AO acceptance letter

---

### POA&M #10: Penetration Testing (CA-8)

**Control**: CA-8 - Penetration Testing | **CCI**: CCI-001429
**Priority**: 🔴 **HIGH**
**Status**: 📅 Planned (Not Yet Started)
**Risk Level**: LOW

#### Weakness Description

No penetration testing conducted yet. Required for:
- FedRAMP: Annual penetration test
- PCI-DSS (if applicable): Quarterly external scans + annual penetration test
- Industry best practice: Annual offensive security assessment

**Specific Test Areas Needed**:
- Prompt injection attacks (RA-9-AI-2)
- Vector store data isolation bypass (SC-4-AI-2)
- Agent tier escalation attempts (AC-6-AI-1)
- Audit log tampering (AU-9)
- Credential extraction (IA-5(7))

#### Impact Assessment

**Confidentiality**: NONE (Preventative control gap, not active vulnerability)
**Integrity**: NONE
**Availability**: NONE

**Impact**: Unknown vulnerabilities may exist until testing conducted

#### Current Compensating Controls

1. **Vulnerability Scanning** (RA-5): Weekly automated scans (Trivy, Snyk)
2. **Code Review**: Manual security reviews on all PRs
3. **Bug Bounty**: Private bug bounty program active (HackerOne)

**Current Risk**: **LOW** (Multiple compensating controls, no known vulnerabilities)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 10.1 | Select penetration testing vendor (RFP process) | ISSO | 2026-03-01 | 📅 Scheduled |
| 10.2 | Define test scope and rules of engagement | Security Team | 2026-03-15 | 📅 Scheduled |
| 10.3 | Conduct penetration test (2-week engagement) | Vendor | 2026-06-01 - 2026-06-15 | 📅 Scheduled |
| 10.4 | Remediate critical and high findings | Engineering | 2026-06-30 | 📅 Scheduled |
| 10.5 | Retest critical findings | Vendor | 2026-07-15 | 📅 Scheduled |

**Target Completion**: 2026-06-30 (Initial test), 2026-07-15 (Retest)

#### Cost and Resources

- **Penetration Test**: $25,000 - $35,000 (2-week engagement)
- **Remediation**: 160 hours (estimated, depends on findings)
- **Retest**: $5,000

#### Evidence of Completion

- [ ] Vendor engagement letter
- [ ] Rules of Engagement document
- [ ] Penetration Test Report (PTR)
- [ ] Remediation evidence for all findings
- [ ] Retest verification report

---

### POA&M #11: AI Incident Response Playbook (IR-5-AI-1)

**Control**: IR-5-AI-1 - AI Incident Response | **CCI**: CCI-AI-014
**Priority**: 🟡 **MEDIUM**
**Status**: 🟡 Partially Implemented
**Risk Level**: LOW

#### Weakness Description

Incident response plan exists but lacks AI-specific scenarios:
- ✅ General IR plan documented and tested
- ❌ No playbook for hallucination incidents
- ❌ No playbook for prompt injection attacks
- ❌ No playbook for model performance degradation
- ❌ No playbook for bias complaints

#### Impact Assessment

**Confidentiality**: NONE
**Integrity**: LOW - Delayed response to AI-specific incidents
**Availability**: LOW - Uncertainty in response procedures

**Affected Systems**: All agent tiers

#### Current Compensating Controls

1. **General IR Plan** (IR-8): Covers all system-level incidents
2. **On-Call Rotation** (IR-7): 24/7 security response team
3. **Escalation Matrix** (IR-6): Clear escalation procedures

**Current Risk**: **LOW** (General procedures applicable, but not optimized for AI)

#### Remediation Plan

**Milestones**:

| Milestone | Description | Owner | Target Date | Status |
|-----------|-------------|-------|-------------|--------|
| 11.1 | Document hallucination incident playbook | ML Engineering | 2026-01-15 | ⏳ In Progress |
| 11.2 | Document prompt injection attack playbook | Security Engineering | 2026-01-30 | 📅 Scheduled |
| 11.3 | Document model degradation playbook | ML Engineering | 2026-02-10 | 📅 Scheduled |
| 11.4 | Conduct tabletop exercise for AI incidents | Security Team | 2026-02-28 | 📅 Scheduled |
| 11.5 | Update IR plan with AI-specific sections | ISSO | 2026-03-15 | 📅 Scheduled |

**Target Completion**: 2026-02-15

#### Cost and Resources

- **Engineering**: 40 hours (ML + Security)
- **Tabletop Exercise**: 4 hours (8 participants)
- **Budget**: $0 (internal effort)

#### Evidence of Completion

- [ ] AI incident playbook documentation (4 scenarios minimum)
- [ ] Tabletop exercise report with lessons learned
- [ ] Updated IR-8 plan incorporating AI sections
- [ ] Training completion records for on-call engineers

---

## POA&M Tracking

### Monthly Review Process

1. **Week 1**: Update milestone statuses and completion percentages
2. **Week 2**: Review budget and resource allocation
3. **Week 3**: Identify blockers and escalate if needed
4. **Week 4**: Generate monthly POA&M report for AO and management

### Reporting

**Monthly Report To**:
- Authorizing Official (AO)
- CISO
- System Owner
- ISSO

**Quarterly Report To**:
- Compliance Team
- External Auditors (if applicable)

### Risk Acceptance

All POA&M items have been reviewed and accepted by:
- **System Owner**: [TO BE SIGNED]
- **ISSO**: [TO BE SIGNED]
- **Date**: [TO BE COMPLETED]

**Risk Acceptance Statement**: The residual risk associated with these POA&M items is **ACCEPTABLE** for Authorization to Operate (ATO) given the presence of compensating controls and planned remediation timelines.

---

## Closed POA&M Items (Historical)

*No closed items yet. This section will track completed POA&M items for audit trail purposes.*

---

## Appendix: POA&M Priority Definitions

| Priority | Definition | Response Time | Approval |
|----------|------------|---------------|----------|
| **Critical** | Active vulnerability or compliance violation | Immediate (24 hours) | CISO approval required |
| **High** | Missing control or significant weakness | 30 days to start, 180 days to complete | ISSO approval required |
| **Medium** | Partial implementation or minor gap | 60 days to start, 365 days to complete | System Owner approval |
| **Low** | Enhancement or optimization | Best effort, no deadline | Self-approved |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-18 | Security Team | Initial POA&M creation |

**Next Update**: 2025-11-18 (Monthly review)
**Document Owner**: ISSO
**Related Documents**:
- `control-summary.md` - Overall control status
- `control-implementation.md` - Detailed control statements
- `README.md` - SSP overview
