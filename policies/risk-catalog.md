# AI Agent Risk Catalog v2.0

> Comprehensive catalog of 18 AI-specific risks for agent governance
> **Aligned to NIST 800-53 Rev 5 Risk Assessment (RA) controls**

## Overview

This catalog identifies and categorizes risks specific to AI agent operations per NIST RA-3 (Risk Assessment). Each risk includes:
- **Risk ID**: Unique identifier (RI-XXX)
- **NIST Control**: Applicable NIST 800-53 control family
- **Severity**: Critical, High, Medium, Low
- **Likelihood**: Probability of occurrence (1-5)
- **Impact**: Consequence if realized (1-5)
- **Risk Score**: Likelihood × Impact
- **Applicable Tiers**: Which agent tiers are affected
- **Related Mitigations**: Controls to address the risk (see `control-mappings.md`)

## Risk Scoring Matrix

```
Risk Score = Likelihood (1-5) × Impact (1-5)

Priority Levels:
🔴 Critical (15-25): Must fix before deployment
🟡 High (8-14):     Fix soon, monitor closely
🟢 Medium/Low (1-7): Accept or monitor
```

---

## 🔴 Critical Risks (Always Address)

### RI-001: Hallucination & False Information Generation

**NIST Controls**: SI-7-AI-1, SI-7-AI-2, RA-9-AI-1 | **CCI**: CCI-AI-009, CCI-AI-010, CCI-AI-001
**Severity**: 🔴 Critical
**Likelihood**: 5 (Very High)
**Impact**: 5 (Severe)
**Risk Score**: 25

**Description**: Agent generates plausible but factually incorrect information, leading to incorrect decisions or outputs.

**Scenarios**:
- Agent provides false technical documentation
- Agent creates incorrect code based on misunderstood requirements
- Agent reports non-existent system status or metrics
- Agent fabricates data sources or citations

**Applicable Tiers**: All (1-4)

**Related Mitigations**: MI-013 (Citations), MI-015 (LLM-as-Judge), MI-007 (Human Review)
**NIST Mitigations**: SI-7-AI-1 (Output Validation), SI-7-AI-2 (LLM-as-Judge), AC-6-AI-2 (Human Review)

**Detection Methods**:
- Output validation against known sources
- LLM-as-Judge verification
- Human spot-checks on random samples
- Automated fact-checking for quantitative claims

---

### RI-014: Prompt Injection & Manipulation

**NIST Controls**: SI-10, RA-9-AI-2, AC-6 | **CCI**: CCI-002754, CCI-AI-002, CCI-002220
**Severity**: 🔴 Critical
**Likelihood**: 4 (High)
**Impact**: 5 (Severe)
**Risk Score**: 20

**Description**: Malicious input hijacks agent behavior, causing it to ignore instructions or perform unauthorized actions.

**Scenarios**:
- User input overrides system prompts
- Agent processes malicious documents containing hidden instructions
- Chained prompt attacks through multiple agent interactions
- Jailbreak attempts to bypass safety controls

**Applicable Tiers**: All (1-4), especially Tier 3-4 with production access

**Related Mitigations**: MI-002 (Input Filtering), MI-017 (AI Firewall), MI-008 (Sandboxing)
**NIST Mitigations**: SI-10 (Input Validation), RA-9-AI-2 (Prompt Injection Risk Assessment), AC-6 (Least Privilege)

**Detection Methods**:
- Pattern matching for injection keywords
- Input validation and sanitization
- Behavioral anomaly detection
- Audit log analysis for unusual command sequences

---

### RI-015: Data Leakage to Hosted LLM Providers

**NIST Controls**: SC-4-AI-1, IA-5(7), SC-28 | **CCI**: CCI-AI-003, CCI-004062, CCI-001199
**Severity**: 🔴 Critical
**Likelihood**: 5 (Very High)
**Impact**: 5 (Severe)
**Risk Score**: 25

**Description**: Sensitive data (secrets, PII, proprietary information) sent to external LLM providers during agent operations.

**Scenarios**:
- API keys or credentials in code snippets sent to LLM
- Customer PII in prompts for analysis
- Proprietary algorithms or trade secrets in context
- Compliance-regulated data (HIPAA, PCI-DSS) leaving environment

**Applicable Tiers**: All (1-4)

**Related Mitigations**: MI-001 (Data Leakage Prevention), MI-003 (Secrets Management), MI-011 (On-Premise LLM)
**NIST Mitigations**: SC-4-AI-1 (Data Leakage Prevention), IA-5(7) (No Embedded Secrets), SC-4 (Information Isolation)

**Detection Methods**:
- PII detection in outbound requests
- Secrets scanning before LLM calls
- DLP (Data Loss Prevention) tools
- Network traffic analysis

---

### RI-018: Runaway Cost & Budget Overruns

**NIST Controls**: SA-15-AI-1, CA-7-AI-1, AU-2 | **CCI**: CCI-AI-013, CCI-AI-012, CCI-000130
**Severity**: 🔴 Critical (Financial Impact)
**Likelihood**: 4 (High)
**Impact**: 4 (Major)
**Risk Score**: 16

**Description**: Agent generates unexpected costs through excessive LLM calls, token usage, or resource consumption.

**Scenarios**:
- Agent enters infinite loop making repeated API calls
- Extremely large context windows on every request
- Unoptimized prompt engineering multiplying costs
- No budget alerts or circuit breakers configured

**Applicable Tiers**: All (1-4)

**Related Mitigations**: MI-009 (Cost Monitoring), MI-021 (Budget Limits), MI-005 (Rate Limiting)
**NIST Mitigations**: SA-15-AI-1 (Cost and Budget Controls), CA-7-AI-1 (Performance Monitoring), AU-2 (Cost Event Logging)

**Detection Methods**:
- Real-time cost tracking dashboards
- Budget threshold alerts (50%, 75%, 90%)
- Token usage anomaly detection
- Cost-per-task benchmarking

---

## 🟡 High Risks (Address for Tier 3+)

### RI-002: Model Version Drift & Breaking Changes

**Severity**: 🟡 High
**Likelihood**: 4 (High)
**Impact**: 3 (Moderate)
**Risk Score**: 12

**Description**: LLM provider updates model version, causing unexpected behavior changes, regressions, or failures.

**Scenarios**:
- Model update changes output format breaking parsers
- Previously working prompts produce degraded results
- New model has different safety thresholds
- Performance characteristics change (slower/more expensive)

**Applicable Tiers**: All, especially Tier 2-4 with production dependencies

**Related Mitigations**: MI-010 (Version Pinning), MI-016 (Change Monitoring)

**Detection Methods**:
- Automated regression testing (SAT - Standard Acceptance Test)
- Output comparison before/after version changes
- Model version tracking in logs
- Provider API version monitoring

---

### RI-006: Bias, Discrimination & Unfair Outputs

**Severity**: 🟡 High
**Likelihood**: 3 (Moderate)
**Impact**: 4 (Major - Legal/Reputational)
**Risk Score**: 12

**Description**: Agent produces biased outputs affecting protected classes or perpetuating discrimination.

**Scenarios**:
- Resume screening agent discriminates by name/gender
- Code review agent shows bias against non-English comments
- Customer support agent provides unequal service quality
- Decision-making agent exhibits racial or cultural bias

**Applicable Tiers**: All, especially Tier 3-4 with user-facing outputs

**Related Mitigations**: MI-015 (LLM-as-Judge), MI-007 (Human Review), MI-012 (Bias Testing)

**Detection Methods**:
- Demographic parity testing
- Disparate impact analysis
- Bias detection tools (e.g., Fairlearn)
- Regular human audits across demographic groups

---

### RI-011: Vector Store & RAG Data Leakage

**Severity**: 🟡 High
**Likelihood**: 3 (Moderate)
**Impact**: 4 (Major)
**Risk Score**: 12

**Description**: Sensitive information stored in vector databases or RAG systems accessible through prompt engineering or retrieval attacks.

**Scenarios**:
- Agent retrieves other users' data through crafted queries
- Embeddings reveal sensitive information through similarity search
- RAG system includes documents user shouldn't access
- Vector store doesn't enforce access controls

**Applicable Tiers**: Tier 2-4 with RAG implementations

**Related Mitigations**: MI-001 (Data Leakage Prevention), MI-006 (Access Controls), MI-014 (RAG Security)

**Detection Methods**:
- Access control testing on vector stores
- Query analysis for unauthorized data access
- Regular permission audits
- Embedding inspection for sensitive data

---

### RI-016: Regulatory & Compliance Violations

**Severity**: 🟡 High
**Likelihood**: 3 (Moderate)
**Impact**: 5 (Severe - Legal/Financial)
**Risk Score**: 15

**Description**: Agent operations violate regulations (GDPR, HIPAA, SOX, EU AI Act, etc.) through data handling or decision-making.

**Scenarios**:
- PII processing without consent (GDPR violation)
- Healthcare data mishandling (HIPAA violation)
- Financial decisions without audit trail (SOX violation)
- High-risk AI system without required assessments (EU AI Act)

**Applicable Tiers**: All, severity increases with tier

**Related Mitigations**: MI-018 (Compliance Mapping), MI-019 (Audit Trails), MI-001 (Data Leakage Prevention)

**Detection Methods**:
- Automated compliance scanning
- Regular regulatory audits
- Data classification and tracking
- Legal review of agent use cases

---

## 🟢 Medium Risks (Monitor & Manage)

### RI-003: Non-Deterministic Behavior & Inconsistency

**Severity**: 🟢 Medium
**Likelihood**: 5 (Very High)
**Impact**: 2 (Minor)
**Risk Score**: 10

**Description**: Agent produces different outputs for identical inputs due to LLM stochasticity, causing user confusion or operational issues.

**Scenarios**:
- Same query returns different answers across runs
- Agent provides inconsistent recommendations
- Testing becomes difficult due to output variation
- Users lose trust due to unpredictability

**Applicable Tiers**: All

**Related Mitigations**: MI-010 (Version Pinning), MI-004 (Observability), MI-007 (Human Review)

**Detection Methods**:
- Repeatability testing (same input → similar output)
- Output variance measurement
- User feedback on consistency
- Statistical analysis of response distributions

---

### RI-009: Data Drift & Stale Information

**Severity**: 🟢 Medium
**Likelihood**: 4 (High)
**Impact**: 2 (Minor)
**Risk Score**: 8

**Description**: Agent operates on outdated data, leading to degraded performance or incorrect decisions over time.

**Scenarios**:
- RAG system contains outdated documentation
- Training data becomes stale and unrepresentative
- Agent references deprecated APIs or tools
- Embeddings don't reflect current knowledge

**Applicable Tiers**: Tier 2-4 with data dependencies

**Related Mitigations**: MI-016 (Change Monitoring), MI-004 (Observability), MI-014 (RAG Security)

**Detection Methods**:
- Data freshness monitoring
- Performance degradation tracking
- Regular knowledge base updates
- User feedback on accuracy

---

### RI-004: Context Window Limitations & Information Loss

**Severity**: 🟢 Medium
**Likelihood**: 4 (High)
**Impact**: 2 (Minor)
**Risk Score**: 8

**Description**: Agent loses critical information when context exceeds window size, leading to incomplete or incorrect outputs.

**Scenarios**:
- Long documents truncated, missing key details
- Multi-turn conversations lose early context
- Large codebases can't fit in context
- Agent forgets earlier instructions

**Applicable Tiers**: All

**Related Mitigations**: MI-013 (Citations), MI-014 (RAG Security), MI-004 (Observability)

**Detection Methods**:
- Context length monitoring
- Output quality vs context size analysis
- User reports of "forgotten" information

---

### RI-005: Dependency & Third-Party API Failures

**Severity**: 🟢 Medium
**Likelihood**: 3 (Moderate)
**Impact**: 3 (Moderate)
**Risk Score**: 9

**Description**: Agent failures due to LLM provider outages, API changes, or third-party service unavailability.

**Scenarios**:
- OpenAI/Anthropic API outage halts operations
- Provider changes API contract without notice
- Rate limits or throttling affect availability
- Network issues prevent API access

**Applicable Tiers**: All

**Related Mitigations**: MI-011 (On-Premise LLM), MI-005 (Rate Limiting), MI-008 (Sandboxing)

**Detection Methods**:
- API health monitoring
- Fallback mechanism testing
- Dependency availability dashboards
- SLA tracking

---

### RI-007: Insufficient Audit Trail & Traceability

**Severity**: 🟢 Medium
**Likelihood**: 3 (Moderate)
**Impact**: 3 (Moderate)
**Risk Score**: 9

**Description**: Lack of comprehensive logging makes it impossible to debug issues, prove compliance, or understand agent decisions.

**Scenarios**:
- Can't reproduce agent behavior during incident
- No record of who approved agent actions
- Compliance audit fails due to missing logs
- Unable to trace decision-making chain

**Applicable Tiers**: Tier 2-4, especially Tier 3 (production)

**Related Mitigations**: MI-019 (Audit Trails), MI-004 (Observability)

**Detection Methods**:
- Log completeness audits
- Compliance requirement mapping
- Incident response drills
- Regular audit trail testing

---

### RI-008: Inadequate Human Oversight

**Severity**: 🟢 Medium
**Likelihood**: 3 (Moderate)
**Impact**: 3 (Moderate)
**Risk Score**: 9

**Description**: Insufficient human review or approval mechanisms for agent actions, leading to unchecked errors or policy violations.

**Scenarios**:
- Agent deploys to production without review
- No human spot-checks on agent outputs
- Approval workflows bypassed or ignored
- Alert fatigue causes humans to rubber-stamp reviews

**Applicable Tiers**: All, especially Tier 3-4

**Related Mitigations**: MI-007 (Human Review), MI-020 (Tier Enforcement), MI-004 (Observability)

**Detection Methods**:
- Human review rate monitoring
- Approval workflow compliance audits
- Time-to-approval tracking
- Reviewer engagement metrics

---

### RI-010: Performance Degradation & Latency

**Severity**: 🟢 Medium
**Likelihood**: 3 (Moderate)
**Impact**: 2 (Minor)
**Risk Score**: 6

**Description**: Agent response times degrade due to inefficient prompts, large contexts, or infrastructure issues, impacting user experience.

**Scenarios**:
- Multi-minute response times frustrate users
- Large context windows slow processing
- Network latency adds delays
- Inefficient RAG retrieval

**Applicable Tiers**: All

**Related Mitigations**: MI-004 (Observability), MI-005 (Rate Limiting), MI-009 (Cost Monitoring)

**Detection Methods**:
- Response time monitoring
- SLA compliance tracking
- User satisfaction surveys
- Performance profiling

---

### RI-012: Unauthorized Actions & Privilege Escalation

**Severity**: 🟢 Medium (Can be 🟡 High for Tier 3-4)
**Likelihood**: 2 (Low)
**Impact**: 4 (Major)
**Risk Score**: 8

**Description**: Agent performs actions beyond authorized scope or escalates privileges through vulnerabilities.

**Scenarios**:
- Tier 1 agent modifies production data
- Agent bypasses approval workflows
- Prompt injection escalates permissions
- Agent accesses resources outside allowed scope

**Applicable Tiers**: All, especially Tier 2-4

**Related Mitigations**: MI-006 (Access Controls), MI-020 (Tier Enforcement), MI-008 (Sandboxing)

**Detection Methods**:
- Permission boundary testing
- Audit log analysis for unauthorized actions
- Regular security assessments
- Anomalous behavior detection

---

### RI-013: Knowledge Cutoff & Outdated Information

**Severity**: 🟢 Medium
**Likelihood**: 4 (High)
**Impact**: 2 (Minor)
**Risk Score**: 8

**Description**: Agent operates with outdated knowledge due to model training cutoff date, providing obsolete information.

**Scenarios**:
- Agent references deprecated libraries or APIs
- Unaware of recent security vulnerabilities
- Outdated best practices recommendations
- Missing recent product updates

**Applicable Tiers**: All

**Related Mitigations**: MI-014 (RAG Security), MI-016 (Change Monitoring), MI-013 (Citations)

**Detection Methods**:
- Knowledge freshness testing
- Comparison against current documentation
- User feedback on outdated info
- Regular knowledge base updates

---

### RI-017: Adversarial Attacks & Model Exploitation

**Severity**: 🟢 Medium (Can be 🟡 High for public-facing agents)
**Likelihood**: 2 (Low)
**Impact**: 3 (Moderate)
**Risk Score**: 6

**Description**: Attackers exploit model vulnerabilities through adversarial inputs, jailbreaks, or targeted manipulation.

**Scenarios**:
- Adversarial examples trigger misclassification
- Jailbreak prompts bypass safety controls
- Model inversion attacks extract training data
- Backdoor triggers cause malicious behavior

**Applicable Tiers**: All, especially public-facing Tier 3-4

**Related Mitigations**: MI-017 (AI Firewall), MI-002 (Input Filtering), MI-008 (Sandboxing)

**Detection Methods**:
- Adversarial robustness testing
- Jailbreak attempt detection
- Anomaly detection on inputs
- Regular security assessments

---

## Risk Summary by Tier

| Tier | Critical Risks to Address | High Risks to Monitor | Recommended Actions |
|------|--------------------------|----------------------|---------------------|
| **Tier 1** | RI-001, RI-015, RI-018 | RI-006, RI-016 | Focus on hallucination, data leakage, cost control |
| **Tier 2** | RI-001, RI-015, RI-018 | RI-002, RI-006, RI-016 | Add version pinning, bias testing |
| **Tier 3** | RI-001, RI-014, RI-015, RI-018 | All high risks | **Threat model required**, comprehensive controls |
| **Tier 4** | RI-001, RI-014, RI-015, RI-018 | All high risks | **Threat model required**, strategic risk assessment |

---

## Using This Catalog

### Step 1: Identify Applicable Risks
- Review your agent's tier and use case
- Check which risks apply to your scenario
- Calculate risk scores for your context

### Step 2: Prioritize by Score
- Address all Critical (15-25) risks before deployment
- Plan mitigation for High (8-14) risks
- Monitor Medium/Low (1-7) risks

### Step 3: Apply Mitigations
- Reference the Mitigation Catalog for controls
- Implement mitigations based on cost/benefit
- Document your risk acceptance decisions

### Step 4: Continuous Monitoring
- Track risk indicators in observability platform
- Review and update risk assessments quarterly
- Adjust mitigations based on operational experience

---

## Related Documents

- **Mitigation Catalog**: See `mitigation-catalog.md` for controls
- **Threat Modeling**: See `workflows/threat-modeling/guide.md`
- **Observability**: See `frameworks/observability-config.yml`
- **Decision Matrix**: See `frameworks/decision-matrix.yml`

---

**Framework v2.0** - Built on FINOS AI Risk Catalog + Microsoft Responsible AI + Industry Best Practices
