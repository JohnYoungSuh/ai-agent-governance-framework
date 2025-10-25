# Pre-Execution Validation — Usage Guide

## Overview
Gap #1 fix implemented: Pre-execution validation prevents AI agents from damaging resources by validating actions BEFORE they execute.

## What Changed
- **Before:** Validator ran AFTER action completed → damage already done
- **After:** Validator runs BEFORE action executes → blocks unauthorized actions upfront

## Usage Examples

### Example 1: Validate Before Deleting Files
```bash
# BEFORE executing deletion, check if resources are within namespace
python scripts/validate_agent_guardrail.py \
  --agent cleanup-agent \
  --action delete \
  --namespace my-project \
  --resources ~/projects/my-project/temp/file1.txt ~/projects/my-project/logs/old.log \
  --output /tmp/cleanup-result.txt \
  --pre-validate-only
```

**Result:**
- ✅ If resources are within `~/projects/my-project/` → Validation PASSES, agent can proceed
- ❌ If any resource is outside namespace → Validation BLOCKS, agent cannot execute

### Example 2: Validate Container Modification
```bash
# Check if agent can modify Docker containers in project namespace
python scripts/validate_agent_guardrail.py \
  --agent docker-agent \
  --action modify \
  --namespace project-a \
  --resources /var/lib/docker/containers/project-a-web /var/lib/docker/containers/project-a-db \
  --output /tmp/docker-result.txt \
  --config frameworks/agent-guardrail.yaml \
  --pre-validate-only
```

### Example 3: Full Workflow (Pre + Post Validation)
```bash
# 1. Pre-validate BEFORE action
python scripts/validate_agent_guardrail.py \
  --agent deployment-agent \
  --action deploy \
  --namespace prod-service \
  --resources ~/projects/prod-service/deploy.yaml \
  --output /tmp/deploy-output.txt \
  --pre-validate-only

# 2. If pre-validation passes, execute agent action
if [ $? -eq 0 ]; then
  ./run-deployment-agent.sh

  # 3. Post-validate output
  python scripts/validate_agent_guardrail.py \
    --agent deployment-agent \
    --action deploy \
    --namespace prod-service \
    --output /tmp/deploy-output.txt
fi
```

## Integration with Agent Workflows

### Python Agent Integration
```python
import subprocess
import sys

def safe_agent_action(agent_name, action, namespace, target_resources):
    """Wrapper that pre-validates before executing agent action"""

    # Pre-execution validation
    result = subprocess.run([
        "python", "scripts/validate_agent_guardrail.py",
        "--agent", agent_name,
        "--action", action,
        "--namespace", namespace,
        "--resources", *target_resources,
        "--output", "/tmp/dummy.txt",  # Not used in pre-validation
        "--pre-validate-only"
    ])

    if result.returncode != 0:
        print(f"[BLOCKED] Action '{action}' rejected by pre-execution validation")
        sys.exit(1)

    # If validation passed, execute actual agent logic
    print(f"[APPROVED] Proceeding with action '{action}'")
    # ... your agent code here ...
```

### Bash Script Integration
```bash
#!/bin/bash
# safe_deploy.sh - Deployment with pre-execution validation

AGENT="deploy-agent"
ACTION="deploy"
NAMESPACE="$1"
RESOURCES="$2"

# Pre-validate
python scripts/validate_agent_guardrail.py \
  --agent "$AGENT" \
  --action "$ACTION" \
  --namespace "$NAMESPACE" \
  --resources $RESOURCES \
  --output /tmp/deploy.log \
  --pre-validate-only

if [ $? -ne 0 ]; then
  echo "Deployment blocked by governance policy"
  exit 1
fi

# Execute deployment
kubectl apply -f "$RESOURCES"
```

## Configuration Requirements

### Agent Guardrail YAML
Ensure your `frameworks/agent-guardrail.yaml` includes:
```yaml
scope:
  base_directory: "~/projects/%project_name$"

agents:
  cleanup-agent:
    allowed_actions:
      - delete
      - cleanup
    destructive_actions:
      - delete

  deploy-agent:
    allowed_actions:
      - deploy
      - rollback
    destructive_actions:
      - deploy
```

## Audit Trail
All pre-execution validations are logged to `audit_trail_entry.json`:
```json
{
  "timestamp": "2025-10-24T10:30:00Z",
  "agent": "cleanup-agent",
  "action": "delete",
  "result": "PASS",
  "reason": "PRE-EXEC PASS: Pre-execution validation passed",
  "record_hash": "abc123..."
}
```

## Next Steps
See remaining critical gaps in todo list:
- Gap #2: JWT namespace validation
- Gap #3: Immutable audit logs
- Gap #4: Policy hash verification
- Gap #5: Emergency kill switch
