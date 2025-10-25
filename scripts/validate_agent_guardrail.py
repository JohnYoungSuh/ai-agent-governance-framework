#!/usr/bin/env python3
"""
validate_agent_guardrail.py
Purpose:
    Validate AI agent actions, prompts, and outputs against
    defined guardrails in config/agent-guardrail.yaml.
    Generates audit-trail entries for compliance verification.

Location:
    /agents/<agent_name>/src/config/validate_agent_guardrail.py

Usage:
    python validate_agent_guardrail.py --agent security --action scan --output report.txt
"""

import argparse
import yaml
import json
import os
import datetime
import hashlib
from pathlib import Path

AUDIT_LOG = Path("audit_trail_entry.json")


def load_guardrails(config_path: str):
    """Load guardrail YAML policy configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pre_validate_action(agent_name: str, action: str, target_resources: list, config: dict, namespace: str):
    """
    PRE-EXECUTION validation - validates BEFORE action executes.
    Prevents damage by blocking unauthorized actions upfront.

    Args:
        agent_name: Name of the agent requesting action
        action: Action to be performed
        target_resources: List of resource paths/identifiers that will be affected
        config: Loaded guardrail configuration
        namespace: Expected project namespace (e.g., 'project-a')

    Returns:
        tuple: (bool, str) - (is_valid, reason)

    Raises:
        ValueError: If validation fails (prevents action execution)
    """
    agent_rules = config.get("agents", {}).get(agent_name, {})

    if not agent_rules:
        return False, f"No guardrails found for agent: {agent_name}"

    # 1. Validate action is allowed
    allowed_actions = agent_rules.get("allowed_actions", [])
    if action not in allowed_actions:
        return False, f"Action '{action}' is not permitted for agent '{agent_name}'"

    # 2. Validate namespace boundary - ensure all resources are within namespace
    base_path = config.get("scope", {}).get("base_directory", f"~/projects/{namespace}")
    base_path_expanded = os.path.expanduser(base_path.replace("%project_name$", namespace))

    for resource in target_resources:
        resource_abs = os.path.abspath(os.path.expanduser(resource))
        base_abs = os.path.abspath(base_path_expanded)

        # Check if resource is within namespace directory
        if not resource_abs.startswith(base_abs):
            return False, f"Resource '{resource}' is outside namespace '{namespace}' (expected under {base_abs})"

    # 3. Check for destructive actions requiring explicit confirmation
    destructive_actions = agent_rules.get("destructive_actions", [])
    if action in destructive_actions:
        # In production, this should check for human approval token/flag
        # For now, we log that confirmation is required
        print(f"[WARNING] Destructive action '{action}' requires explicit human confirmation")

    return True, "Pre-execution validation passed"


def validate_action(agent_name: str, action: str, output_file: str, config: dict):
    """
    Validate agent's action and output against its guardrails.
    Returns a validation result and reasons for failure if any.
    """
    agent_rules = config.get("agents", {}).get(agent_name, {})

    if not agent_rules:
        return False, f"No guardrails found for agent: {agent_name}"

    allowed_actions = agent_rules.get("allowed_actions", [])
    restricted_keywords = agent_rules.get("restricted_keywords", [])

    if action not in allowed_actions:
        return False, f"Action '{action}' is not permitted for agent '{agent_name}'"

    # Check output content for restricted terms
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            for keyword in restricted_keywords:
                if keyword.lower() in content.lower():
                    return False, f"Output contains restricted keyword: {keyword}"

    return True, "Validation passed"


def generate_audit_entry(agent_name: str, action: str, result: bool, reason: str):
    """Create or append an audit trail JSON entry."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent": agent_name,
        "action": action,
        "result": "PASS" if result else "FAIL",
        "reason": reason,
        "record_hash": hashlib.sha256(
            f"{agent_name}{action}{reason}{datetime.datetime.utcnow()}".encode()
        ).hexdigest(),
    }

    existing_entries = []
    if AUDIT_LOG.exists():
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            try:
                existing_entries = json.load(f)
            except json.JSONDecodeError:
                existing_entries = []

    existing_entries.append(entry)
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(existing_entries, f, indent=2)

    print(f"[{'PASS' if result else 'FAIL'}] Audit entry logged for {agent_name}/{action}")


def main():
    parser = argparse.ArgumentParser(description="Validate AI agent actions against governance guardrails.")
    parser.add_argument("--agent", required=True, help="Name of the agent (e.g., ai, architect, security)")
    parser.add_argument("--action", required=True, help="Action performed by the agent (e.g., scan, train, deploy)")
    parser.add_argument("--output", required=True, help="Path to agent output file")
    parser.add_argument("--config", default="frameworks/agent-guardrail.yaml", help="Path to guardrail config file")
    parser.add_argument("--namespace", required=True, help="Project namespace (e.g., project-a)")
    parser.add_argument("--resources", nargs="+", help="Target resources for pre-execution validation")
    parser.add_argument("--pre-validate-only", action="store_true", help="Only run pre-execution validation, skip post-validation")
    args = parser.parse_args()

    config = load_guardrails(args.config)

    # PRE-EXECUTION VALIDATION (if resources provided)
    if args.resources:
        pre_result, pre_reason = pre_validate_action(
            args.agent, args.action, args.resources, config, args.namespace
        )
        if not pre_result:
            print(f"[BLOCKED] Pre-execution validation failed: {pre_reason}")
            generate_audit_entry(args.agent, args.action, False, f"PRE-EXEC BLOCK: {pre_reason}")
            exit(1)
        else:
            print(f"[APPROVED] Pre-execution validation passed: {pre_reason}")
            generate_audit_entry(args.agent, args.action, True, f"PRE-EXEC PASS: {pre_reason}")

        if args.pre_validate_only:
            exit(0)

    # POST-EXECUTION VALIDATION (original behavior)
    result, reason = validate_action(args.agent, args.action, args.output, config)
    generate_audit_entry(args.agent, args.action, result, reason)


if __name__ == "__main__":
    main()
