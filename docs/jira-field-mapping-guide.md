# Jira Field Mapping Guide for AI Agent Governance Framework

**Version:** 2.1
**Last Updated:** 2025-11-06
**Purpose:** Map governance framework fields to Jira custom fields across different instances

---

## Overview

This guide provides field mapping configurations for integrating the AI Agent Governance Framework with various Jira instances. Different organizations may have different field names, types, and configurations.

---

## Standard Field Mapping

### Core Governance Fields

| Framework Field | Jira Field Type | Required | Default Value | Example |
|----------------|----------------|----------|---------------|---------|
| `cr_id` | Text (Single line) | ✅ Yes | Auto-generated | CR-2024-0001 |
| `agent_id` | Text (Single line) | ✅ Yes | - | ops-agent-01 |
| `tier` | Number | ✅ Yes | 1 | 1-4 |
| `control_id` | Text (Single line) | ✅ Yes | - | SEC-001 |
| `approver_role` | Text (Single line) | ✅ Yes | - | Security Lead |
| `budget_tokens` | Number | ⚠️ Recommended | 0 | 1000000 |
| `cost_usd` | Number (Decimal) | ⚠️ Recommended | 0.00 | 125.50 |
| `compliance_result` | Select List | ✅ Yes | - | pass/fail/warning |

### Extended Governance Fields

| Framework Field | Jira Field Type | Required | Default Value | Example |
|----------------|----------------|----------|---------------|---------|
| `threat_model_ref` | URL | ❌ Optional | - | https://... |
| `siem_event_id` | Text (Single line) | ⚠️ Recommended | Auto-generated | audit-1730900000-a1b2c3d4 |
| `workflow_step` | Select List | ⚠️ Recommended | - | G-07 |
| `pki_signature` | Text (Multi-line) | ❌ Optional | - | Base64 signature |
| `risk_level` | Select List | ⚠️ Recommended | Medium | Low/Medium/High/Critical |
| `deployment_environment` | Select List | ⚠️ Recommended | dev | dev/staging/prod |

---

## Jira Cloud Configuration

### Custom Field IDs (Example)

```json
{
  "jira_cloud_mapping": {
    "cr_id": "customfield_10050",
    "agent_id": "customfield_10051",
    "tier": "customfield_10052",
    "control_id": "customfield_10053",
    "approver_role": "customfield_10054",
    "budget_tokens": "customfield_10055",
    "cost_usd": "customfield_10056",
    "compliance_result": "customfield_10057",
    "threat_model_ref": "customfield_10058",
    "siem_event_id": "customfield_10059",
    "workflow_step": "customfield_10060",
    "pki_signature": "customfield_10061",
    "risk_level": "customfield_10062",
    "deployment_environment": "customfield_10063"
  }
}
```

### Creating Custom Fields in Jira Cloud

```bash
# Use Jira REST API to create custom fields
curl -X POST https://your-domain.atlassian.net/rest/api/3/field \
  -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agent ID",
    "description": "Unique identifier for the AI agent",
    "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
    "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
  }'
```

### Select List Options

```json
{
  "compliance_result": {
    "options": [
      {"value": "pass", "color": "#14892C"},
      {"value": "fail", "color": "#D04437"},
      {"value": "warning", "color": "#F6C342"}
    ]
  },
  "tier": {
    "options": [
      {"value": 1, "label": "Tier 1: Observer"},
      {"value": 2, "label": "Tier 2: Developer"},
      {"value": 3, "label": "Tier 3: Operations"},
      {"value": 4, "label": "Tier 4: Architect"}
    ]
  },
  "risk_level": {
    "options": [
      {"value": "Low", "color": "#14892C"},
      {"value": "Medium", "color": "#F6C342"},
      {"value": "High", "color": "#FF991F"},
      {"value": "Critical", "color": "#D04437"}
    ]
  },
  "deployment_environment": {
    "options": [
      {"value": "dev", "label": "Development"},
      {"value": "staging", "label": "Staging"},
      {"value": "prod", "label": "Production"}
    ]
  }
}
```

---

## Jira Server/Data Center Configuration

### Custom Field Mapping

For self-hosted Jira instances, field IDs may differ:

```json
{
  "jira_server_mapping": {
    "cr_id": "customfield_11001",
    "agent_id": "customfield_11002",
    "tier": "customfield_11003",
    "control_id": "customfield_11004",
    "approver_role": "customfield_11005",
    "budget_tokens": "customfield_11006",
    "cost_usd": "customfield_11007",
    "compliance_result": "customfield_11008",
    "threat_model_ref": "customfield_11009",
    "siem_event_id": "customfield_11010",
    "workflow_step": "customfield_11011",
    "pki_signature": "customfield_11012",
    "risk_level": "customfield_11013",
    "deployment_environment": "customfield_11014"
  }
}
```

### Field Configuration XML (for Jira Server)

```xml
<customfield>
  <id>customfield_11002</id>
  <name>Agent ID</name>
  <description>Unique identifier for the AI agent</description>
  <type>com.atlassian.jira.plugin.system.customfieldtypes:textfield</type>
  <searcher>com.atlassian.jira.plugin.system.customfieldtypes:textsearcher</searcher>
</customfield>
```

---

## Alternative Field Names

Some organizations may use different field names. Here are common alternatives:

| Standard Name | Alternative Names |
|--------------|-------------------|
| `cr_id` | Change Request ID, CR Number, Request ID, Change ID |
| `agent_id` | Agent Name, Bot ID, Service Account, Agent Identifier |
| `tier` | Agent Tier, Permission Level, Access Level, Capability Level |
| `control_id` | Governance Control, Control Number, Policy ID |
| `approver_role` | Approver, Authorized By, Reviewer Role |
| `budget_tokens` | Token Budget, Token Limit, Token Allocation |
| `cost_usd` | Cost, Expense, Total Cost, Actual Cost |
| `compliance_result` | Compliance Status, Audit Result, Policy Check |

---

## Python Integration Example

### Reading Field Mapping from Config

```python
#!/usr/bin/env python3
"""
Jira Field Mapper
Dynamically map framework fields to Jira custom fields
"""

import json
import os
from typing import Dict, Any

class JiraFieldMapper:
    """Map governance framework fields to Jira custom fields"""

    def __init__(self, config_path: str = None):
        """Initialize mapper with config file"""
        if config_path is None:
            config_path = os.getenv('JIRA_FIELD_MAPPING_CONFIG',
                                   './config/jira-field-mapping.json')

        with open(config_path, 'r') as f:
            self.mapping = json.load(f)

    def map_to_jira(self, framework_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map framework fields to Jira custom fields

        Args:
            framework_fields: Dict with framework field names as keys

        Returns:
            Dict with Jira custom field IDs as keys
        """
        jira_fields = {}

        for framework_key, value in framework_fields.items():
            jira_key = self.mapping.get(framework_key)

            if jira_key:
                jira_fields[jira_key] = value
            else:
                print(f"Warning: No mapping for field '{framework_key}'")

        return jira_fields

    def map_from_jira(self, jira_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Jira custom fields back to framework fields

        Args:
            jira_fields: Dict with Jira custom field IDs as keys

        Returns:
            Dict with framework field names as keys
        """
        # Create reverse mapping
        reverse_mapping = {v: k for k, v in self.mapping.items()}

        framework_fields = {}

        for jira_key, value in jira_fields.items():
            framework_key = reverse_mapping.get(jira_key)

            if framework_key:
                framework_fields[framework_key] = value

        return framework_fields


# Example usage
if __name__ == '__main__':
    # Load mapper
    mapper = JiraFieldMapper('./config/jira-field-mapping.json')

    # Framework data
    framework_data = {
        'cr_id': 'CR-2024-0001',
        'agent_id': 'ops-agent-01',
        'tier': 3,
        'control_id': 'SEC-001',
        'approver_role': 'Security Lead',
        'budget_tokens': 1000000,
        'cost_usd': 125.50,
        'compliance_result': 'pass'
    }

    # Map to Jira format
    jira_data = mapper.map_to_jira(framework_data)
    print("Jira Custom Fields:")
    print(json.dumps(jira_data, indent=2))

    # Map back from Jira
    framework_data_back = mapper.map_from_jira(jira_data)
    print("\nFramework Fields:")
    print(json.dumps(framework_data_back, indent=2))
```

---

## Jira REST API Examples

### Creating an Issue with Custom Fields

```python
import requests
import json

JIRA_URL = "https://your-domain.atlassian.net"
JIRA_API_TOKEN = "your-api-token"

headers = {
    "Authorization": f"Bearer {JIRA_API_TOKEN}",
    "Content-Type": "application/json"
}

# Create CR issue
issue_data = {
    "fields": {
        "project": {"key": "AIOPS"},
        "summary": "Tier 3 Agent Deployment Request",
        "description": "Request approval for ops-agent-01 deployment",
        "issuetype": {"name": "Change Request"},

        # Standard fields
        "priority": {"name": "High"},

        # Custom fields (using field mapping)
        "customfield_10050": "CR-2024-0001",  # cr_id
        "customfield_10051": "ops-agent-01",   # agent_id
        "customfield_10052": 3,                # tier
        "customfield_10053": "SEC-001",        # control_id
        "customfield_10054": "Security Lead",  # approver_role
        "customfield_10055": 1000000,          # budget_tokens
        "customfield_10056": 125.50,           # cost_usd
        "customfield_10057": {"value": "pass"} # compliance_result
    }
}

response = requests.post(
    f"{JIRA_URL}/rest/api/3/issue",
    headers=headers,
    json=issue_data
)

if response.status_code == 201:
    issue_key = response.json()['key']
    print(f"✅ Issue created: {issue_key}")
else:
    print(f"❌ Error: {response.text}")
```

### Querying Issues with Custom Fields

```python
# JQL query with custom fields
jql = """
    project = AIOPS
    AND issuetype = "Change Request"
    AND "Agent Tier" >= 3
    AND "Compliance Result" = "pass"
"""

response = requests.get(
    f"{JIRA_URL}/rest/api/3/search",
    headers=headers,
    params={
        "jql": jql,
        "fields": [
            "summary",
            "customfield_10050",  # cr_id
            "customfield_10051",  # agent_id
            "customfield_10052",  # tier
            "customfield_10057"   # compliance_result
        ]
    }
)

issues = response.json()['issues']
for issue in issues:
    print(f"{issue['key']}: {issue['fields']['summary']}")
    print(f"  Agent ID: {issue['fields']['customfield_10051']}")
    print(f"  Tier: {issue['fields']['customfield_10052']}")
```

---

## Field Discovery Script

Use this script to discover custom field IDs in your Jira instance:

```bash
#!/bin/bash
# discover-jira-fields.sh

JIRA_URL="https://your-domain.atlassian.net"
JIRA_API_TOKEN="your-token"

echo "Discovering Jira custom fields..."
echo "=================================="

curl -s -X GET "${JIRA_URL}/rest/api/3/field" \
  -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
  | jq -r '.[] | select(.custom == true) | "\(.id) - \(.name)"'
```

---

## Best Practices

### DO ✅

1. **Use a configuration file** for field mappings
   - Makes it easy to update when Jira changes
   - Supports multiple Jira instances

2. **Validate field types** before writing
   - Check if field exists
   - Verify data type compatibility

3. **Handle missing fields gracefully**
   - Log warnings for unmapped fields
   - Continue processing with available fields

4. **Document custom field IDs** in your instance
   - Create a field mapping document
   - Keep it in version control

5. **Use JQL to validate field usage**
   - Test queries with custom fields
   - Ensure data is searchable

### DON'T ❌

1. **Don't hardcode field IDs** in application code
   - Use configuration files instead

2. **Don't assume field names are unique**
   - Use field IDs for API calls

3. **Don't skip field validation**
   - Validate before creating/updating issues

4. **Don't mix field types**
   - Number fields need numbers, not strings

---

## Configuration File Template

Create `config/jira-field-mapping.json`:

```json
{
  "jira_instance_type": "cloud",
  "jira_url": "https://your-domain.atlassian.net",
  "project_key": "AIOPS",

  "field_mapping": {
    "cr_id": "customfield_10050",
    "agent_id": "customfield_10051",
    "tier": "customfield_10052",
    "control_id": "customfield_10053",
    "approver_role": "customfield_10054",
    "budget_tokens": "customfield_10055",
    "cost_usd": "customfield_10056",
    "compliance_result": "customfield_10057",
    "threat_model_ref": "customfield_10058",
    "siem_event_id": "customfield_10059",
    "workflow_step": "customfield_10060",
    "pki_signature": "customfield_10061",
    "risk_level": "customfield_10062",
    "deployment_environment": "customfield_10063"
  },

  "select_field_mappings": {
    "compliance_result": {
      "pass": "Pass",
      "fail": "Fail",
      "warning": "Warning"
    },
    "risk_level": {
      "low": "Low",
      "medium": "Medium",
      "high": "High",
      "critical": "Critical"
    }
  }
}
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Field not found | Check field ID with discovery script |
| Type mismatch | Verify field type in Jira admin |
| Permission denied | Ensure API token has correct permissions |
| Value not in list | Check select field options |
| Required field missing | Add field to issue creation payload |

### Debug Mode

Enable debug logging to see field mapping:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

mapper = JiraFieldMapper('./config/jira-field-mapping.json')
jira_data = mapper.map_to_jira(framework_data)
```

---

## Related Documentation

- [Jira Integration Guide](../workflows/PAR-PROTO/integrations/jira-integration.md)
- [PKI Signing for Approvals](../scripts/jira-pki-signing.py)
- [Webhook Receiver](../scripts/jira-webhook-receiver.py)
- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

---

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.1 | 2025-11-06 | Initial field mapping guide with examples | AI Governance Framework |

---

**This guide ensures consistent field mapping across different Jira instances for the AI Agent Governance Framework.**
