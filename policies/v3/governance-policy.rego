# Unified AI Agent Governance Policy v3.0
# Open Policy Agent (OPA) implementation
# Usage: opa eval -d governance-policy.rego -i request.json "data.governance.v3.decision"

package governance.v3

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

framework_version := "3.0.0"

# Default tier for unmatched actions
default_tier := 2

# Default decision: deny unless explicitly allowed
default allow := false

# Tier definitions
tier_definitions := {
    0: {"name": "auto_approve", "requires_human": false, "audit_level": "info"},
    1: {"name": "auto_approve_with_audit", "requires_human": false, "audit_level": "warn"},
    2: {"name": "human_approval_required", "requires_human": true, "audit_level": "warn"},
    3: {"name": "always_deny", "requires_human": false, "audit_level": "critical"}
}

# =============================================================================
# MAIN DECISION POINT
# =============================================================================

# The primary decision output
decision := {
    "allow": allow,
    "tier": tier,
    "requires_human_approval": requires_human_approval,
    "approval_routing": approval_routing,
    "justification": justification,
    "violations": violations,
    "recommendations": recommendations,
    "audit_level": audit_level,
    "simulation_required": simulation_required
}

# =============================================================================
# ALLOW/DENY LOGIC
# =============================================================================

# Allow if tier is 0 or 1 (auto-approve)
allow if {
    tier in [0, 1]
    count(violations) == 0
}

# Deny if tier is 3
allow := false if {
    tier == 3
}

# Tier 2 requires human approval (don't auto-allow, but don't deny either)
allow := "pending_approval" if {
    tier == 2
}

# =============================================================================
# TIER CALCULATION
# =============================================================================

# Determine the tier for the requested action
tier := calculated_tier if {
    calculated_tier := calculate_tier
}

# Calculate tier based on rules
calculate_tier := tier_value if {
    # Check for Tier 3 violations first (highest priority)
    tier_3_match
    tier_value := 3
} else := tier_value if {
    # Check for Tier 2 conditions
    tier_2_match
    tier_value := 2
} else := tier_value if {
    # Check for Tier 1 conditions
    tier_1_match
    tier_1_conditions_met
    tier_value := 1
} else := tier_value if {
    # Check for Tier 0 conditions
    tier_0_match
    tier_value := 0
} else := default_tier

# =============================================================================
# HELPER FUNCTIONS: Extract data from input
# =============================================================================

# Extract namespace from agent identity (format: namespace-agent-instance)
agent_namespace := ns if {
    parts := split(input.agent_identity, "-")
    count(parts) >= 1
    ns := parts[0]
}

# Get target namespace from input
target_namespace := input.namespace

# Get operation type
operation := input.operation

# Get command being executed
command := input.command

# Get environment
environment := input.environment

# =============================================================================
# TIER 0 RULES: Auto-approve without audit
# =============================================================================

tier_0_match if {
    operation in ["get", "list", "describe", "show", "read", "cat", "head", "tail", "grep", "find"]
    target_namespace == agent_namespace
}

tier_0_match if {
    operation in ["status", "health", "version", "info", "uptime"]
}

tier_0_match if {
    regex.match("^kubectl get .* -n " + agent_namespace + "$", command)
}

tier_0_match if {
    regex.match("^ls .* ~/projects/" + agent_namespace + "/.*$", command)
}

# =============================================================================
# TIER 1 RULES: Auto-approve with audit
# =============================================================================

tier_1_match if {
    operation in ["create", "apply", "patch", "update", "write", "touch", "mkdir"]
    target_namespace == agent_namespace
}

tier_1_match if {
    operation == "delete"
    input.resource_type == "pod"
    target_namespace == agent_namespace
    count(input.affected_resources) <= 5
}

tier_1_match if {
    operation == "scale"
    target_namespace == agent_namespace
    input.target_replicas <= 10
}

tier_1_match if {
    regex.match("^echo .* > /tmp/" + agent_namespace + "-.*$", command)
}

tier_1_match if {
    regex.match("^mkdir ~/projects/" + agent_namespace + "/.*$", command)
}

# Tier 1 conditions that must be met
tier_1_conditions_met if {
    quota_check_pass
    cost_tags_present
}

# =============================================================================
# TIER 2 RULES: Human approval required
# =============================================================================

tier_2_match if {
    budget_remaining < 0
}

tier_2_match if {
    target_namespace != agent_namespace
}

tier_2_match if {
    regex.match(".*(sudo|su -|chmod \\+s|setuid).*", command)
}

tier_2_match if {
    operation in ["delete", "drop", "truncate"]
    input.resource_type in ["database", "table", "collection", "bucket"]
    environment == "production"
}

tier_2_match if {
    operation == "delete"
    count(input.affected_resources) > 100
}

tier_2_match if {
    operation == "delete"
    input.total_size_gb > 1
}

tier_2_match if {
    regex.match("^kubectl (apply|create|patch|delete) .* (networkpolicy|ingress|egress).*", command)
}

# =============================================================================
# TIER 3 RULES: Always deny
# =============================================================================

tier_3_match if {
    regex.match(".*(echo|cat|print|printf).*(password|api_key|secret|token).*", command)
}

tier_3_match if {
    regex.match(".*(rm|delete|truncate|modify).*(audit|log).*", command)
}

tier_3_match if {
    regex.match(".*(skip|bypass|disable|ignore).*(policy|governance|validation).*", command)
}

tier_3_match if {
    regex.match("^rm -rf /$", command)
}

tier_3_match if {
    regex.match("^rm -rf /\\*$", command)
}

tier_3_match if {
    regex.match("^rm -rf \\*$", command)
}

tier_3_match if {
    regex.match(".*(copy|share|export).*(identity|credential|key).*", command)
}

tier_3_match if {
    regex.match(".*(modify|delete).*(cost_center|project_code).*tag.*", command)
}

# =============================================================================
# CONDITION EVALUATORS
# =============================================================================

# Check if within resource quotas
quota_check_pass if {
    input.current_cpu_usage < input.declared_cpu_quota
    input.current_memory_usage < input.declared_memory_quota
    input.current_storage_usage < input.declared_storage_quota
}

# Check if cost attribution tags are present
cost_tags_present if {
    input.resource_tags.agent_identity
    input.resource_tags.cost_center
    input.resource_tags.project_code
}

# Calculate remaining budget
budget_remaining := remaining if {
    remaining := input.budget_limit_usd - input.current_spending_usd
}

# =============================================================================
# APPROVAL ROUTING
# =============================================================================

approval_routing := routes if {
    tier == 2
    routes := determine_approval_routes
}

determine_approval_routes := ["finops_team", input.budget_owner] if {
    budget_remaining < 0
}

determine_approval_routes := ["security_team"] if {
    regex.match(".*(sudo|su -).*", command)
}

determine_approval_routes := ["namespace_owner", "governance_team"] if {
    target_namespace != agent_namespace
    operation in ["create", "update", "delete", "apply"]
}

determine_approval_routes := [concat("", ["namespace_", target_namespace, "_owner"])] if {
    target_namespace != agent_namespace
    operation in ["get", "list", "describe"]
}

determine_approval_routes := ["data_owner", "dba_team"] if {
    operation in ["delete", "drop", "truncate"]
    environment == "production"
}

determine_approval_routes := ["security_team"] if {
    regex.match(".*networkpolicy.*", command)
}

# Default routing for unmatched Tier 2
determine_approval_routes := ["governance_team"] if {
    true  # Fallback
}

# =============================================================================
# HUMAN APPROVAL REQUIREMENT
# =============================================================================

requires_human_approval if {
    tier == 2
}

requires_human_approval := false if {
    tier in [0, 1]
}

requires_human_approval := false if {
    tier == 3  # Deny, don't ask for approval
}

# =============================================================================
# JUSTIFICATION
# =============================================================================

justification := msg if {
    tier == 0
    msg := "Auto-approved: Read-only operation in own namespace"
}

justification := msg if {
    tier == 1
    msg := "Auto-approved with audit: Write operation within quota and policy"
}

justification := msg if {
    tier == 2
    budget_remaining < 0
    msg := sprintf("Human approval required: Budget exceeded by $%.2f", [abs(budget_remaining)])
}

justification := msg if {
    tier == 2
    target_namespace != agent_namespace
    msg := sprintf("Human approval required: Cross-namespace operation from %s to %s", [agent_namespace, target_namespace])
}

justification := msg if {
    tier == 2
    operation in ["delete", "drop", "truncate"]
    environment == "production"
    msg := "Human approval required: Production data deletion"
}

justification := msg if {
    tier == 3
    regex.match(".*(password|secret|token).*", command)
    msg := "DENIED: Attempted credential exposure - Tier 3 violation"
}

justification := msg if {
    tier == 3
    regex.match(".*audit.*", command)
    msg := "DENIED: Attempted audit log manipulation - Tier 3 violation"
}

justification := msg if {
    tier == 3
    regex.match(".*(skip|bypass).*policy.*", command)
    msg := "DENIED: Attempted policy bypass - Tier 3 violation"
}

justification := msg if {
    tier == 3
    msg := "DENIED: Tier 3 violation - Always deny"
}

# Default justification
justification := "Evaluation complete" if {
    true
}

# =============================================================================
# VIOLATIONS
# =============================================================================

violations contains violation if {
    not quota_check_pass
    tier in [0, 1]
    violation := {
        "rule": "resource_quota_exceeded",
        "severity": "high",
        "message": "Current resource usage exceeds declared quota"
    }
}

violations contains violation if {
    not cost_tags_present
    tier in [0, 1]
    operation in ["create", "apply"]
    violation := {
        "rule": "missing_cost_tags",
        "severity": "high",
        "message": "Resource creation without required cost attribution tags"
    }
}

violations contains violation if {
    tier == 3
    violation := {
        "rule": "tier_3_violation",
        "severity": "critical",
        "message": sprintf("Tier 3 violation detected: %s", [justification])
    }
}

violations contains violation if {
    not input.policy_version == framework_version
    violation := {
        "rule": "policy_version_mismatch",
        "severity": "critical",
        "message": sprintf("Policy version mismatch: agent uses %s, framework requires %s", [input.policy_version, framework_version])
    }
}

violations contains violation if {
    not input.agent_identity
    violation := {
        "rule": "missing_agent_identity",
        "severity": "critical",
        "message": "Agent identity not provided or invalid"
    }
}

# =============================================================================
# RECOMMENDATIONS
# =============================================================================

recommendations contains rec if {
    tier == 2
    budget_remaining < 0
    rec := "Consider optimizing resource usage or requesting budget increase"
}

recommendations contains rec if {
    tier == 2
    target_namespace != agent_namespace
    rec := "Consider adding target namespace to agent manifest privileges if this is a routine operation"
}

recommendations contains rec if {
    input.current_cpu_usage > (input.declared_cpu_quota * 0.8)
    rec := "CPU usage above 80% of quota - consider scaling or increasing quota"
}

recommendations contains rec if {
    tier == 1
    count(input.affected_resources) > 3
    rec := "Consider batching operations to reduce overhead"
}

# =============================================================================
# AUDIT LEVEL
# =============================================================================

audit_level := level if {
    tier == 3
    level := "critical"
}

audit_level := level if {
    tier == 2
    level := "warn"
}

audit_level := level if {
    tier == 1
    level := "info"
}

audit_level := level if {
    tier == 0
    level := "debug"
}

# =============================================================================
# SIMULATION REQUIREMENT
# =============================================================================

simulation_required if {
    tier == 2
    operation in ["delete", "drop", "truncate"]
}

simulation_required if {
    tier == 2
    environment == "production"
    operation in ["update", "patch", "apply"]
}

simulation_required := false if {
    tier in [0, 1]
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

abs(x) := x if { x >= 0 }
abs(x) := -x if { x < 0 }
