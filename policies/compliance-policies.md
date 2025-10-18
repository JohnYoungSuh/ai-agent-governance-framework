# Compliance Policies

> Aligned to NIST 800-53 Rev 5, DISA CCI, and regulatory frameworks

---

## AU-2 / AU-3: Audit Events and Content of Audit Records
**NIST Controls**: AU-2, AU-3, AU-3(1) | **CCI**: CCI-000130, CCI-000131, CCI-000133
**AI Extension**: AU-3-AI-1 - AI Decision Auditability | **CCI**: CCI-AI-008
**Supporting Controls**: AU-8 (Time Stamps), AU-9 (Protection), AU-11 (Retention)

**Policy**: All AI agent actions must generate auditable records with sufficient detail for compliance and forensic analysis

### AU-2: Audit Events

**Control Statement**: Identify and audit organizationally-defined events

**Auditable Events for AI Agents**:
1. **Authentication Events** (IA-5)
   - Agent service account authentication
   - Secrets Manager access (checkout/checkin)
   - Credential rotation events

2. **Authorization Events** (AC-6)
   - Permission grants/revocations
   - Privilege escalation attempts
   - Tier boundary violations

3. **Agent Actions** (AU-3-AI-1)
   - All create/read/update/delete operations
   - Code modifications and deployments
   - Infrastructure changes
   - JIRA ticket creation/updates

4. **Data Access** (SC-4)
   - Classification level of accessed data
   - PII/sensitive data redaction events
   - Cross-classification boundary access

5. **Cost Events** (SA-15-AI-1)
   - LLM API token consumption
   - Budget threshold exceedances
   - Cost per task/operation

6. **Security Events** (SI-4)
   - Prompt injection detection
   - Output validation failures
   - Hallucination alerts

### AU-3: Content of Audit Records

**Required Fields** (per CCI-000131):
```json
{
  "siem_event_id": "uuid-v4",
  "timestamp": "2025-10-18T14:32:01.123Z",  // AU-8: UTC with milliseconds
  "event_type": "agent_action",
  "agent_id": "tier3-prod-deploy-agent-001",
  "agent_tier": 3,
  "action": "deploy_application",
  "target": "production/web-app-v2.1.0",
  "approver_id": "user@example.com",
  "approval_ticket": "JIRA-12345",
  "classification": "INTERNAL",
  "input_params": {
    "version": "2.1.0",
    "environment": "production"
  },
  "output_summary": "Deployment successful, 3 pods updated",
  "outcome": "success",
  "cost_tokens": 15420,
  "cost_usd": 0.23,
  "model_version": "gpt-4-2024-11-20"
}
```

### AU-3(1): Additional Audit Information

**AI-Specific Additional Fields** (CCI-000133):
- `reasoning_chain`: Steps in agent's decision process
- `confidence_score`: Model confidence in output
- `citations`: Sources used for decision
- `hallucination_check`: Result of validation
- `bias_score`: If applicable for decision-making agents

### AU-3-AI-1: AI Decision Auditability

**Control Statement**: Log sufficient information to reproduce AI agent reasoning and validate decisions

**Implementation**:
```python
# Example audit logging
def audit_agent_decision(action, input_data, output, metadata):
    audit_record = {
        # Standard AU-3 fields
        "siem_event_id": uuid.uuid4(),
        "timestamp": datetime.utcnow().isoformat(),
        "agent_id": get_agent_id(),
        "action": action,

        # AU-3-AI-1 extensions
        "prompt_template": metadata.get("prompt_template"),
        "context_included": metadata.get("context_docs"),
        "model_params": {
            "temperature": metadata.get("temperature"),
            "max_tokens": metadata.get("max_tokens")
        },
        "reasoning_chain": output.get("chain_of_thought"),
        "validation_result": validate_output(output),
        "citations": extract_citations(output)
    }

    append_to_audit_log(audit_record)
```

### AU-9: Protection of Audit Information

**Control Implementation** (CCI-000162):
- **Append-only storage**: S3 Object Lock, WORM storage
- **Immutability**: Object versioning enabled, deletion disabled
- **Encryption**: AES-256 at rest (SC-28(1))
- **Access Control**: AI Auditor Agent has append-only write; humans have read-only
- **Integrity**: Merkle tree hash published daily for external verification

### AU-11: Audit Record Retention

**Retention Policy** (CCI-001849):
- **Minimum Retention**: 2 years in active storage
- **Archive Retention**: 5 additional years in cold storage (Glacier)
- **Compliance Extensions**:
  - SOX: 7 years
  - HIPAA: 6 years
  - PCI-DSS: 1 year online, 3 years archive

---

## CM-3 / CM-4: Configuration Change Control
**NIST Controls**: CM-3, CM-3(2), CM-4 | **CCI**: CCI-000066, CCI-001813, CCI-001812
**AI Extension**: CM-3-AI-1 - Model Version Control | **CCI**: CCI-AI-007

**Policy**: All changes must follow documented approval process with impact analysis

### CM-3: Configuration Change Control

**Control Implementation**:

**CM-3(a)**: Determine types of changes that are configuration-controlled
- All production infrastructure changes
- AI model version updates (CM-3-AI-1)
- Agent tier escalations
- Security configuration changes
- Data classification policy changes

**CM-3(b)**: Review and approve configuration changes
- **Tier 3+ Changes**: Require JIRA change ticket
- **Approval Authority**:
  - Infrastructure: DevOps Lead + Security
  - Model Updates: ML Engineering + Security
  - Security Policies: CISO or designee
- **Multi-person rule**: No self-approval for production

**CM-3(d)**: Document configuration changes
```yaml
# Example change record
change_id: "CHG-2025-10-001"
type: "model_version_update"
requested_by: "tier3-agent-prod-001"
approved_by: ["ml-eng@example.com", "security@example.com"]
description: "Update GPT-4 model from 2024-09-01 to 2024-11-20"
impact_analysis:
  affected_systems: ["prod-deploy-agent", "code-review-agent"]
  risk_level: "medium"
  rollback_plan: "Revert model_version in config to 2024-09-01"
  testing_evidence: "SAT regression passed 98.5% (acceptable)"
implementation_date: "2025-10-18T20:00:00Z"
validation_result: "success"
```

### CM-3(2): Test / Validate / Document Changes

**Requirements** (CCI-001813):
1. **Pre-Implementation Testing**:
   - Run Standard Acceptance Test (SAT) suite
   - Compare output quality vs. baseline
   - Verify no regressions in critical workflows

2. **Rollback Plan**:
   - Document exact steps to revert
   - Test rollback in staging first
   - Keep previous version available for 30 days

3. **Post-Implementation Validation**:
   - Monitor error rates for 24 hours
   - Verify cost metrics within expected range
   - Human spot-check on sample outputs

### CM-4: Impact Analysis

**Control Statement** (CCI-001812): Analyze changes for potential security and privacy impacts

**Required Analysis**:
```markdown
## Change Impact Analysis - CHG-2025-10-001

### Security Impact
- [ ] New permissions required? No
- [ ] Data classification changes? No
- [ ] Authentication/authorization changes? No
- [ ] Audit logging adequate? Yes

### Privacy Impact
- [ ] New PII processing? No
- [ ] Cross-border data transfer? No
- [ ] Consent requirements? N/A

### Operational Impact
- [ ] Performance degradation? Tested: +50ms avg (acceptable)
- [ ] Cost increase? Estimated +12% token cost
- [ ] Dependency changes? New model version only

### Risk Level: MEDIUM
Justification: No security/privacy changes, cost increase within budget
```

### CM-3-AI-1: Model Version Control

**Control Statement**: Control and document all LLM model version changes

**Implementation**:
1. **Version Pinning**: Specify exact model version in configuration
   ```yaml
   llm:
     provider: "openai"
     model: "gpt-4-2024-11-20"  # Exact version, not "gpt-4" alias
   ```

2. **Change Detection**: Monitor for provider version deprecation notices
3. **Regression Testing**: Automated SAT suite on every version change
4. **Audit Trail**: Log all model version changes (AU-3)

---

## PL-8: Security and Privacy Architectures (Data Residency)
**NIST Control**: PL-8, PL-8(1) | **CCI**: CCI-000352, CCI-003505
**Supporting Controls**: SC-7(21) - Isolation of System Components

**Policy**: AI systems must comply with geographic data residency and sovereignty requirements

### Control Implementation

**PL-8(a)**: Develop security and privacy architectures
- **Data Classification Mapping**: Identify which data is subject to residency laws
  - EU GDPR: Personal data of EU residents
  - China PIPL: Personal information processed in China
  - Russia Data Localization: Russian citizen data
  - US ITAR: Defense-related technical data

**PL-8(b)**: Describe architecture in system security plan
```yaml
# AI Agent Data Residency Architecture
training_data:
  location: "us-east-1"  # AWS region
  classification: "INTERNAL"
  compliance: ["US-CLOUD-ACT", "FedRAMP"]

processing:
  llm_provider: "OpenAI"
  api_endpoint: "api.openai.com"
  data_residency: "United States"
  certifications: ["SOC 2 Type II"]

storage:
  vector_db: "Pinecone"
  region: "us-east-1"
  encryption: "AES-256"

cross_border_transfers:
  eu_to_us:
    mechanism: "Standard Contractual Clauses (SCCs)"
    approval_required: true
    dpia_completed: true  # Data Protection Impact Assessment
```

**PL-8(1)**: Defense in Depth
- Multiple layers of data residency enforcement:
  1. Regional LLM endpoint selection
  2. Network-level geo-blocking
  3. Application-level classification checks
  4. Audit trail for cross-border transfers (AU-3)

### Implementation Checklist

- [ ] Document training data origin and location
- [ ] Verify LLM provider data processing locations
- [ ] Obtain legal approval for cross-border transfers
- [ ] Maintain current certifications (ISO 27001, SOC 2)
- [ ] Update privacy notices to reflect data transfers
- [ ] Conduct DPIA for high-risk processing (GDPR Article 35)
