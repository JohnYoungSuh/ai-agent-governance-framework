# SCAP Compliance for AI Agent Governance Framework

**Version:** 2.1
**Last Updated:** 2025-11-06

---

## Overview

This directory contains SCAP (Security Content Automation Protocol) compliance content for automated security scanning of AI agent deployments.

**Components**:
- **XCCDF Benchmark** (`ai-agent-benchmark.xml`): Security checklist with AI-specific controls
- **OVAL Definitions** (`ai-agent-oval.xml`): Automated compliance tests

---

## What is SCAP?

SCAP is a suite of specifications for automated security compliance checking:

- **XCCDF**: Extensible Configuration Checklist Description Format
- **OVAL**: Open Vulnerability and Assessment Language
- **CCE**: Common Configuration Enumeration
- **CPE**: Common Platform Enumeration
- **CCI**: Control Correlation Identifiers

Used by: DISA STIGs, FedRAMP, NIST, DoD, Federal agencies

---

## AI-Specific STIG Rules

| Rule ID | NIST Control | CCI | Title | CAT |
|---------|--------------|-----|-------|-----|
| SV-AI-001 | AC-6-AI-1 | CCI-AI-005 | AI Agent Tier Enforcement | II |
| SV-AI-002 | AC-6-AI-2 | CCI-AI-006 | Human-in-the-Loop Authorization | II |
| SV-AI-003 | SC-4-AI-1 | CCI-AI-003 | PII/Secrets Leakage Prevention | I |
| SV-AI-004 | SC-4-AI-2 | CCI-AI-004 | Vector Store Data Isolation | II |
| SV-AI-007 | AU-3-AI-1 | CCI-AI-008 | AI Decision Audit Trail | II |
| SV-AI-013 | SA-15-AI-1 | CCI-AI-013 | Cost and Budget Controls | II |
| SV-AI-017 | CA-7-AI-2 | CCI-AI-017 | Non-Deterministic Problem Detection | II |

**CAT Levels**:
- **CAT I**: Critical/High risk
- **CAT II**: Medium risk
- **CAT III**: Low risk

---

## Running SCAP Scans

### Option 1: OpenSCAP (Recommended)

```bash
# Install OpenSCAP
sudo apt-get install libopenscap8 openscap-utils  # Ubuntu/Debian
sudo yum install openscap-scanner openscap-utils  # RHEL/CentOS

# Run compliance scan
oscap xccdf eval \
    --profile xccdf_gov.nist.ai-agent-governance_profile_fedramp-moderate-ai \
    --results results.xml \
    --report report.html \
    --oval-results \
    compliance/scap/ai-agent-benchmark.xml

# View report
firefox report.html
```

### Option 2: SCAP Workbench (GUI)

```bash
# Install SCAP Workbench
sudo apt-get install scap-workbench

# Launch GUI
scap-workbench compliance/scap/ai-agent-benchmark.xml
```

### Option 3: Nessus/Tenable

Import `ai-agent-benchmark.xml` into Nessus:
1. Navigate to Policies → SCAP
2. Upload XCCDF benchmark
3. Run audit scan

---

## Compliance Profiles

### FedRAMP Moderate + AI Extensions

Includes all FedRAMP Moderate controls plus AI-specific extensions:

```xml
<Profile id="xccdf_gov.nist.ai-agent-governance_profile_fedramp-moderate-ai">
```

**Use Cases**:
- Tier 3-4 agents in production
- Agents handling sensitive data
- Cloud-hosted AI services (FedRAMP)

### Development/Testing Profile

Baseline security for Tier 1-2 agents:

```xml
<Profile id="xccdf_gov.nist.ai-agent-governance_profile_dev">
```

**Use Cases**:
- Development environments
- Testing and QA
- Non-production agents

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: SCAP Compliance Scan

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  scap-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install OpenSCAP
        run: sudo apt-get install -y libopenscap8 openscap-utils

      - name: Run SCAP Scan
        run: |
          oscap xccdf eval \
            --profile xccdf_gov.nist.ai-agent-governance_profile_fedramp-moderate-ai \
            --results results.xml \
            --report report.html \
            --oval-results \
            compliance/scap/ai-agent-benchmark.xml || true

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: scap-results
          path: |
            results.xml
            report.html

      - name: Check Compliance
        run: |
          # Fail if any CAT I findings
          cat results.xml | grep -q "severity=\"high\".*result=\"fail\"" && exit 1 || exit 0
```

### Pre-Deployment Check

```bash
#!/bin/bash
# pre-deploy-scap.sh

echo "Running SCAP compliance check..."

oscap xccdf eval \
    --profile xccdf_gov.nist.ai-agent-governance_profile_fedramp-moderate-ai \
    --results results.xml \
    compliance/scap/ai-agent-benchmark.xml

# Check for failures
if grep -q 'result="fail"' results.xml; then
    echo "❌ SCAP compliance FAILED"
    echo "View detailed report: oscap xccdf generate report results.xml > report.html"
    exit 1
else
    echo "✅ SCAP compliance PASSED"
    exit 0
fi
```

---

## OVAL Automated Checks

OVAL definitions provide automated compliance testing:

### Example: Tier Enforcement Check

```xml
<definition id="oval:gov.nist.ai:def:1001" class="compliance">
  <title>AI Agent Tier Enforcement</title>
  <criteria operator="AND">
    <criterion comment="Agent config file exists" test_ref="oval:gov.nist.ai:tst:1001"/>
    <criterion comment="Agent tier is valid (1-4)" test_ref="oval:gov.nist.ai:tst:1002"/>
    <criterion comment="Governance check script exists" test_ref="oval:gov.nist.ai:tst:1003"/>
  </criteria>
</definition>
```

**Checks**:
1. `/etc/ai-agent/agent_config.yaml` exists
2. `tier` field contains value 1-4
3. `governance-check.sh` script is present

---

## Fixing Non-Compliant Findings

### CAT I: Critical

**Finding**: SV-AI-003 - Data leakage prevention not configured

**Fix**:
```bash
# Implement MI-001 control
# Add PII redaction before LLM calls
# See: policies/mitigation-catalog.md MI-001
```

### CAT II: Medium

**Finding**: SV-AI-001 - Agent tier not configured

**Fix**:
```yaml
# /etc/ai-agent/agent_config.yaml
agent_id: "ops-agent-01"
tier: 3

# Validate
./scripts/governance-check.sh --agent ops-agent-01 --tier 3
```

**Finding**: SV-AI-013 - Budget limits not configured

**Fix**:
```yaml
# /etc/ai-agent/agent_config.yaml
budget_limit_daily: 100.00
budget_limit_monthly: 2000.00

# Implement circuit breaker (MI-021)
# See: policies/mitigation-catalog.md MI-021
```

---

## Customizing for Your Environment

### Update OVAL File Paths

Edit `ai-agent-oval.xml` to match your installation:

```xml
<!-- Default path -->
<ind-def:filepath>/etc/ai-agent/agent_config.yaml</ind-def:filepath>

<!-- Custom path -->
<ind-def:filepath>/opt/mycompany/ai-agent/config.yaml</ind-def:filepath>
```

### Add Custom Rules

1. Create new `<Rule>` in `ai-agent-benchmark.xml`
2. Create corresponding OVAL `<definition>` in `ai-agent-oval.xml`
3. Assign new STIG ID: `SV-AI-0XX`
4. Map to control and CCI

---

## Validation

### Validate XCCDF Syntax

```bash
oscap xccdf validate compliance/scap/ai-agent-benchmark.xml
```

### Validate OVAL Syntax

```bash
oscap oval validate compliance/scap/ai-agent-oval.xml
```

### Test OVAL Definitions

```bash
oscap oval eval compliance/scap/ai-agent-oval.xml
```

---

## STIG Viewer

View checklist in DISA STIG Viewer:

1. Download: https://public.cyber.mil/stigs/srg-stig-tools/
2. Import `ai-agent-benchmark.xml`
3. Review findings by CAT level

---

## Reporting

### Generate HTML Report

```bash
oscap xccdf generate report results.xml > report.html
```

### Generate Guide

```bash
oscap xccdf generate guide ai-agent-benchmark.xml > guide.html
```

### Export to CSV

```bash
oscap xccdf export-oval-variables results.xml > findings.csv
```

---

## Compliance Mapping

| Framework | Profile | Notes |
|-----------|---------|-------|
| **FedRAMP Moderate** | fedramp-moderate-ai | Baseline + AI extensions |
| **NIST 800-53 Rev 5** | fedramp-moderate-ai | Full control set |
| **NIST AI RMF** | fedramp-moderate-ai | AI-specific controls |
| **HIPAA** | fedramp-moderate-ai | Add SC-4-AI-1 (critical) |
| **PCI-DSS** | fedramp-moderate-ai | Add SC-4-AI-1, SC-4-AI-2 |
| **SOC 2** | fedramp-moderate-ai | AU-2, AU-3-AI-1, AC-6-AI-2 |

---

## Troubleshooting

### Issue: "Profile not found"

**Solution**: Check profile ID matches exactly:
```bash
oscap info ai-agent-benchmark.xml  # List available profiles
```

### Issue: "OVAL definition not found"

**Solution**: Ensure `ai-agent-oval.xml` is in same directory or specify path:
```bash
oscap xccdf eval --check-engine-results --oval-results ai-agent-benchmark.xml
```

### Issue: "Permission denied" on file checks

**Solution**: Run with appropriate privileges:
```bash
sudo oscap xccdf eval ...
```

---

## References

### Standards
- **NIST SP 800-126 Rev 3**: SCAP Specification
- **NIST SP 800-53 Rev 5**: Security Controls
- **XCCDF 1.2**: Checklist Specification
- **OVAL 5.11**: Assessment Language

### Tools
- **OpenSCAP**: https://www.open-scap.org/
- **SCAP Workbench**: https://www.open-scap.org/tools/scap-workbench/
- **DISA STIG Viewer**: https://public.cyber.mil/stigs/

### Documentation
- SCAP Content Guide: https://static.open-scap.org/
- NIST SCAP: https://csrc.nist.gov/Projects/scap
- CCI List: https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/u_cci_list.zip

---

**Questions? Issues?**

File an issue: https://github.com/ai-agent-governance-framework/issues
