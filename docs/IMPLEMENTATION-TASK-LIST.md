# AI Agent Governance Framework - Implementation Task List

**Purpose:** Token-efficient governance system implementation
**Target:** 70% token reduction via small model (3B) cache/routing + large model (70B+) complex decisions
**Framework Focus:** CREATE/MODIFY/DELETE/ACCESS/COMPLY actions
**Date:** 2025-10-25
**Status:** Ready for implementation

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Component 1: Cache Classifier Prompt](#component-1-cache-classifier-prompt)
3. [Component 2: Intent Router Prompt](#component-2-intent-router-prompt)
4. [Component 3: Distillation Prompt](#component-3-distillation-prompt)
5. [Component 4: Implementation Task List](#component-4-implementation-task-list)
6. [Component 5: Project Templates](#component-5-project-templates)
7. [Token Savings Analysis](#token-savings-analysis)
8. [Integration Plan](#integration-plan)

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Governance Request Incoming                   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
                  ┌──────────────────────┐
                  │  Cache Classifier    │ ← 3B Model (100 tokens)
                  │  (Small Model)       │   JSON output
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌────────┐   ┌─────────┐   ┌──────────┐
         │ CACHE  │   │ ROUTE   │   │ ESCALATE │
         │  HIT   │   │ SIMPLE  │   │ COMPLEX  │
         └────┬───┘   └────┬────┘   └────┬─────┘
              │            │              │
              │            ▼              │
              │   ┌──────────────┐       │
              │   │ Intent Router│←──────┘
              │   │ (Small Model)│  3B (200 tokens)
              │   └──────┬───────┘
              │          │
              │    5 Categories:
              │    CREATE/MODIFY/DELETE/ACCESS/COMPLY
              │          │
              └──────────┼──────────────┐
                         ▼              ▼
                  ┌──────────┐   ┌─────────────┐
                  │ Simple   │   │  Complex    │
                  │ Rules    │   │ 70B Model   │
                  │ (Cached) │   │ (500 tokens)│
                  └──────────┘   └─────────────┘
                   0 tokens        Only 5% cases
```

**Token Savings Calculation:**
- **Before:** Every request → 70B model (avg 2000 tokens/request)
- **After:**
  - 60% cache hits → 100 tokens (cache classifier only)
  - 35% simple routing → 300 tokens (classifier + router + rules)
  - 5% complex → 600 tokens (classifier + router + 70B)
- **Weighted Average:** (0.60 × 100) + (0.35 × 300) + (0.05 × 600) = **195 tokens/request**
- **Savings:** (2000 - 195) / 2000 = **90.25% reduction** 🎯 (exceeds 70% target!)

---

## Component 1: Cache Classifier Prompt

**Purpose:** Small model (3B) determines if request is cacheable
**Output:** Structured JSON for fast decision-making
**Token Budget:** ~100 tokens

### Prompt Template

```markdown
You are a cache classifier for AI governance requests. Analyze the request and output ONLY valid JSON.

RULES:
- Output ONLY the JSON object, no explanations
- Use exact field names shown below
- Keep reasoning under 20 words

REQUEST: {user_request}

CONTEXT:
- Agent: {agent_name}
- Namespace: {namespace}
- Action: {action_type}

OUTPUT FORMAT:
{
  "cacheable": true|false,
  "cache_key": "string|null",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "route_to": "cache|router|escalate"
}

DECISION LOGIC:
1. cacheable=true IF:
   - Exact same agent+namespace+action seen before
   - No context-dependent variables (timestamps, dynamic paths)
   - Policy hasn't changed recently

2. route_to values:
   - "cache": High-confidence cached result exists
   - "router": Need intent classification (not in cache)
   - "escalate": Complex/ambiguous case needs large model

EXAMPLES:

Input: "Can cleanup-agent delete temp files in my-project?"
Output: {"cacheable": true, "cache_key": "cleanup-agent:my-project:delete:temp", "confidence": 0.95, "reasoning": "Standard cleanup pattern", "route_to": "cache"}

Input: "Should architect-agent modify production DB schema?"
Output: {"cacheable": false, "cache_key": null, "confidence": 0.80, "reasoning": "Complex decision needed", "route_to": "escalate"}

Input: "Can deploy-agent create k8s resources in dev namespace?"
Output: {"cacheable": true, "cache_key": "deploy-agent:dev:create:k8s", "confidence": 0.90, "reasoning": "Common deployment action", "route_to": "cache"}

NOW PROCESS THE REQUEST ABOVE. OUTPUT ONLY JSON:
```

### Implementation Notes

**File Location:** `scripts/prompts/cache_classifier.txt`

**Integration:**
```python
# scripts/governance_router.py
def classify_for_cache(request, agent, namespace, action):
    prompt = load_prompt("cache_classifier.txt").format(
        user_request=request,
        agent_name=agent,
        namespace=namespace,
        action_type=action
    )

    # Use small model (gemini-flash, llama-3b, phi-3)
    response = small_model.generate(prompt, max_tokens=150, temperature=0.1)
    result = json.loads(response)

    if result["route_to"] == "cache":
        return get_cached_decision(result["cache_key"])
    elif result["route_to"] == "router":
        return route_intent(request, agent, namespace, action)
    else:
        return escalate_to_large_model(request, agent, namespace, action)
```

**Cache Storage:**
```python
# Simple in-memory cache (use Redis for production)
GOVERNANCE_CACHE = {
    "cleanup-agent:my-project:delete:temp": {
        "decision": "ALLOW",
        "conditions": ["must_be_in_temp_dir", "no_hidden_files"],
        "ttl": 86400,  # 24 hours
        "last_updated": "2025-10-25T10:00:00Z"
    }
}
```

---

## Component 2: Intent Router Prompt

**Purpose:** Classify governance action into 5 categories
**Output:** Route to appropriate policy handler
**Token Budget:** ~200 tokens

### Prompt Template

```markdown
You are an intent router for AI agent governance. Classify the action into exactly ONE category.

REQUEST: {user_request}
AGENT: {agent_name}
NAMESPACE: {namespace}
ACTION: {action_type}

OUTPUT ONLY THIS JSON:
{
  "category": "CREATE|MODIFY|DELETE|ACCESS|COMPLY",
  "subcategory": "string",
  "risk_level": "low|medium|high|critical",
  "requires_approval": true|false,
  "policy_refs": ["policy_id1", "policy_id2"]
}

CATEGORY DEFINITIONS:

1. CREATE
   - Scope: New resources, files, configs, deployments
   - Examples: mkdir, kubectl apply, terraform apply, git init
   - Risk factors: Namespace, resource quotas, cost
   - Policies: resource-limits, cost-controls, namespace-isolation

2. MODIFY
   - Scope: Editing existing resources
   - Examples: config changes, file edits, scaling, updates
   - Risk factors: Change magnitude, production vs dev, rollback ability
   - Policies: change-management, approval-workflow, backup-required

3. DELETE
   - Scope: Removing resources, data, configs
   - Examples: rm -rf, kubectl delete, DROP TABLE, S3 delete
   - Risk factors: Irreversibility, data loss, dependencies
   - Policies: deletion-safeguards, backup-verification, multi-approval

4. ACCESS
   - Scope: Reading data, credentials, logs, configs
   - Examples: cat secrets.yml, kubectl get, database queries
   - Risk factors: PII exposure, credential leakage, compliance
   - Policies: data-classification, pii-protection, need-to-know

5. COMPLY
   - Scope: Audit, reporting, policy validation
   - Examples: Generate audit report, validate NIST compliance
   - Risk factors: Accuracy, completeness, timeliness
   - Policies: audit-trail, retention-policy, evidence-collection

RISK LEVEL LOGIC:
- low: Dev namespace, read-only, reversible, <$10 cost
- medium: Staging, limited blast radius, <$100 cost
- high: Production, write operations, >$100 cost
- critical: DELETE in prod, PII access, >$1000 cost, compliance violation

APPROVAL LOGIC:
requires_approval = true IF:
- risk_level >= high
- category = DELETE (always)
- Production namespace
- Cost > $50
- Policy violation detected

EXAMPLES:

Input: "Create temp directory in my-project namespace"
Output: {"category": "CREATE", "subcategory": "filesystem", "risk_level": "low", "requires_approval": false, "policy_refs": ["namespace-isolation"]}

Input: "Delete all pods in production namespace"
Output: {"category": "DELETE", "subcategory": "kubernetes", "risk_level": "critical", "requires_approval": true, "policy_refs": ["deletion-safeguards", "multi-approval", "production-protection"]}

Input: "Read database credentials from secrets manager"
Output: {"category": "ACCESS", "subcategory": "credentials", "risk_level": "high", "requires_approval": true, "policy_refs": ["credential-management", "need-to-know", "audit-trail"]}

NOW CLASSIFY THE REQUEST. OUTPUT ONLY JSON:
```

### Implementation

**File Location:** `scripts/prompts/intent_router.txt`

**Router Logic:**
```python
# scripts/intent_router.py
def route_intent(request, agent, namespace, action):
    prompt = load_prompt("intent_router.txt").format(
        user_request=request,
        agent_name=agent,
        namespace=namespace,
        action_type=action
    )

    response = small_model.generate(prompt, max_tokens=200, temperature=0.0)
    intent = json.loads(response)

    # Route to appropriate handler
    if intent["requires_approval"]:
        return require_human_approval(intent)

    if intent["risk_level"] in ["low", "medium"]:
        return apply_simple_rules(intent)
    else:
        return escalate_to_large_model(request, intent)
```

**Simple Rules Engine:**
```python
# Pre-computed rules for common cases (no LLM needed!)
SIMPLE_RULES = {
    "CREATE:filesystem:low": lambda ctx: ctx["namespace"] in ctx["allowed_namespaces"],
    "ACCESS:logs:low": lambda ctx: True,  # Always allow log reads in own namespace
    "DELETE:temp:low": lambda ctx: "/tmp/" in ctx["target_path"],
    "MODIFY:config:medium": lambda ctx: ctx["has_backup"] and ctx["namespace"] != "prod"
}

def apply_simple_rules(intent):
    rule_key = f"{intent['category']}:{intent['subcategory']}:{intent['risk_level']}"
    if rule_key in SIMPLE_RULES:
        return SIMPLE_RULES[rule_key](current_context)
    else:
        return escalate_to_large_model(...)
```

---

## Component 3: Distillation Prompt

**Purpose:** Convert large model complex decisions into simple cacheable rules
**Output:** Python/YAML rules that can be executed without LLM
**Token Budget:** ~500 tokens (large model)

### Prompt Template

```markdown
You are a policy distillation expert. Convert the complex governance decision below into a simple, executable rule.

COMPLEX DECISION EXAMPLE:
---
Request: "Can deploy-agent create a LoadBalancer service in production namespace?"

Large Model Decision:
"This request should be ALLOWED with conditions:
1. The agent has deploy:services permission in the namespace
2. The LoadBalancer has cost tags and budget alerts configured
3. A change ticket exists in the tracking system
4. The deployment happens during approved change window (not 9am-5pm EST)
5. Production namespace has <5 existing LoadBalancers (quota limit)

If any condition fails, DENY and require human approval."
---

YOUR TASK: Distill this into:
1. A Python function (executable rule)
2. A YAML policy entry (for version control)
3. A cache key pattern (for future hits)

OUTPUT FORMAT:
```python
# File: policies/distilled_rules/loadbalancer_create.py
def can_create_loadbalancer(agent, namespace, context):
    """
    Distilled from: Large model decision 2025-10-25
    Decision confidence: 0.95
    Applicable to: deploy-agent, CREATE, LoadBalancer
    """

    # Check 1: Permission
    if not has_permission(agent, namespace, "deploy:services"):
        return {"decision": "DENY", "reason": "Missing deploy:services permission"}

    # Check 2: Cost controls
    if not context.get("has_cost_tags") or not context.get("has_budget_alerts"):
        return {"decision": "DENY", "reason": "Missing cost controls"}

    # Check 3: Change ticket
    if not context.get("change_ticket_id"):
        return {"decision": "DENY", "reason": "No change ticket"}

    # Check 4: Change window
    current_hour = datetime.now(tz='EST').hour
    if 9 <= current_hour <= 17:
        return {"decision": "DENY", "reason": "Outside approved change window"}

    # Check 5: Quota
    existing_lb_count = count_resources(namespace, "LoadBalancer")
    if existing_lb_count >= 5:
        return {"decision": "DENY", "reason": "LoadBalancer quota exceeded"}

    return {
        "decision": "ALLOW",
        "reason": "All conditions met",
        "audit_trail": {
            "policy": "loadbalancer_create_v1",
            "timestamp": datetime.utcnow().isoformat(),
            "conditions_checked": 5
        }
    }
```

```yaml
# File: policies/distilled_rules/loadbalancer_create.yml
policy_id: loadbalancer_create_v1
distilled_from: large_model_decision_2025_10_25
category: CREATE
subcategory: kubernetes_loadbalancer
risk_level: high
cache_pattern: "{agent}:*:create:loadbalancer"

conditions:
  - permission: deploy:services
  - cost_tags: required
  - budget_alerts: required
  - change_ticket: required
  - change_window: outside_business_hours
  - quota: max_5_per_namespace

decision_logic:
  type: all_conditions_must_pass
  on_failure: DENY
  on_success: ALLOW

metadata:
  created: 2025-10-25
  confidence: 0.95
  test_cases: 12
  last_validated: 2025-10-25
```

```python
# Cache key pattern
cache_key = f"{agent}:production:create:loadbalancer"
cache_value = {
    "rule_file": "loadbalancer_create.py",
    "function": "can_create_loadbalancer",
    "ttl": 3600,  # Re-validate hourly
    "requires_context": ["has_cost_tags", "has_budget_alerts", "change_ticket_id"]
}
```

NOW DISTILL THIS DECISION:
---
Request: {complex_request}
Large Model Decision: {large_model_output}
---

OUTPUT THE THREE CODE BLOCKS ABOVE (Python function, YAML policy, Cache entry):
```

### Distillation Workflow

```python
# scripts/distill_policy.py
def distill_complex_decision(request, large_model_decision):
    """
    Converts one-time large model decision into reusable rule
    """
    prompt = load_prompt("distillation.txt").format(
        complex_request=request,
        large_model_output=large_model_decision
    )

    distilled = large_model.generate(prompt, max_tokens=800)

    # Parse the three components
    python_code = extract_code_block(distilled, "python")
    yaml_policy = extract_code_block(distilled, "yaml")
    cache_entry = extract_code_block(distilled, "python", index=1)

    # Save to repository
    save_distilled_rule(python_code, yaml_policy, cache_entry)

    # Run test cases
    validate_rule(python_code)

    # Add to cache
    update_cache(cache_entry)

    return {
        "status": "distilled",
        "rule_file": "loadbalancer_create.py",
        "cache_hit_rate_expected": 0.85
    }
```

**Token Savings from Distillation:**
- First request: 600 tokens (large model)
- Distillation: 500 tokens (one-time cost)
- Next 100 requests: 0 tokens (cached rule execution)
- **Savings:** (100 × 600) - 500 = 59,500 tokens saved per pattern

---

## Component 4: Implementation Task List

### Task Categorization System

Tasks are tagged with:
- **[LLM]**: Can be done by LLM (prompts, docs, configs)
- **[CODE]**: Requires coding skills (Python, integration, testing)
- **[HYBRID]**: LLM drafts, human validates/refines

### Phase 1: Foundation (Week 1) - 🎯 70% Token Savings Achieved Here

| # | Task | Type | Effort | Priority | Token Impact |
|---|------|------|--------|----------|--------------|
| 1.1 | Create cache classifier prompt | [LLM] | 1h | P0 | 60% savings |
| 1.2 | Create intent router prompt (5 categories) | [LLM] | 2h | P0 | 30% savings |
| 1.3 | Build simple rules engine (Python) | [CODE] | 4h | P0 | 5% savings |
| 1.4 | Set up in-memory cache (dict-based) | [CODE] | 2h | P0 | Enables 1.1 |
| 1.5 | Create distillation prompt template | [LLM] | 2h | P1 | Future savings |
| 1.6 | Write integration script (router.py) | [CODE] | 3h | P0 | Core logic |
| 1.7 | Test with 10 sample governance requests | [HYBRID] | 2h | P0 | Validation |

**Deliverables:**
- ✅ Cache classifier prompt: `scripts/prompts/cache_classifier.txt`
- ✅ Intent router prompt: `scripts/prompts/intent_router.txt`
- ✅ Router script: `scripts/governance_router.py`
- ✅ Test results showing token reduction

---

### Phase 2: Distillation & Rules (Week 2) - 🎯 Push to 90% Savings

| # | Task | Type | Effort | Priority | Token Impact |
|---|------|------|--------|----------|--------------|
| 2.1 | Distill 10 most common governance decisions | [HYBRID] | 6h | P0 | 20% additional |
| 2.2 | Create YAML policy schema | [LLM] | 1h | P1 | Documentation |
| 2.3 | Build policy validator (YAML → Python) | [CODE] | 3h | P1 | Quality |
| 2.4 | Generate test cases for each distilled rule | [LLM] | 2h | P1 | Validation |
| 2.5 | Implement rule versioning system | [CODE] | 2h | P2 | Maintainability |
| 2.6 | Create policy update workflow | [HYBRID] | 2h | P1 | Governance |
| 2.7 | Set up A/B testing (cached vs large model) | [CODE] | 4h | P1 | Validation |

**Deliverables:**
- ✅ 10 distilled rules in `policies/distilled_rules/`
- ✅ Rule validator: `scripts/validate_distilled_rule.py`
- ✅ A/B test results report

---

### Phase 3: Production Readiness (Week 3-4)

| # | Task | Type | Effort | Priority | Token Impact |
|---|------|------|--------|----------|--------------|
| 3.1 | Replace in-memory cache with Redis | [CODE] | 4h | P1 | Scale |
| 3.2 | Add monitoring (token usage, cache hit rate) | [CODE] | 3h | P0 | Observability |
| 3.3 | Create admin dashboard (cache stats, rules) | [CODE] | 6h | P2 | Operations |
| 3.4 | Write operational runbook | [LLM] | 2h | P1 | Maintenance |
| 3.5 | Security audit (prompt injection, cache poisoning) | [HYBRID] | 4h | P0 | Security |
| 3.6 | Load testing (1000 req/sec) | [CODE] | 3h | P1 | Performance |
| 3.7 | Documentation (API, deployment, troubleshooting) | [LLM] | 4h | P1 | Adoption |

**Deliverables:**
- ✅ Production deployment guide
- ✅ Monitoring dashboard
- ✅ Security audit report

---

### Phase 4: Advanced Features (Month 2+)

| # | Task | Type | Effort | Priority | Token Impact |
|---|------|------|--------|----------|--------------|
| 4.1 | Auto-distillation pipeline (scheduled job) | [CODE] | 6h | P2 | Automation |
| 4.2 | Multi-tenant support (per-org caches) | [CODE] | 8h | P2 | Scale |
| 4.3 | Policy conflict detection | [HYBRID] | 4h | P2 | Quality |
| 4.4 | Machine learning for cache key prediction | [CODE] | 12h | P3 | Optimization |
| 4.5 | GraphQL API for policy queries | [CODE] | 8h | P3 | Integration |

---

## Component 5: Project Templates

### Template 1: Minimal Viable Setup (Copy-Paste Ready)

**File: `templates/token-efficient-governance/minimal/`**

#### Directory Structure
```
minimal/
├── prompts/
│   ├── cache_classifier.txt       # Component 1
│   ├── intent_router.txt          # Component 2
│   └── distillation.txt           # Component 3
├── scripts/
│   ├── router.py                  # Main integration
│   ├── cache.py                   # Simple cache
│   └── rules.py                   # Rules engine
├── policies/
│   ├── simple_rules.yml           # Pre-approved patterns
│   └── distilled_rules/           # Generated rules
├── tests/
│   ├── test_router.py
│   └── test_data.json             # 50 sample requests
├── config.yml                      # Model endpoints, thresholds
├── requirements.txt
└── README.md                       # Quick start guide
```

#### config.yml
```yaml
models:
  small:
    provider: google
    model: gemini-2.0-flash-thinking-exp-1219
    max_tokens: 200
    temperature: 0.0
    cost_per_1k_tokens: 0.0001

  large:
    provider: anthropic
    model: claude-opus-4
    max_tokens: 800
    temperature: 0.2
    cost_per_1k_tokens: 0.015

cache:
  type: memory  # Switch to redis for production
  ttl: 3600
  max_size: 10000

routing:
  cache_confidence_threshold: 0.85
  escalation_risk_levels: [high, critical]

monitoring:
  log_all_requests: true
  track_token_usage: true
  alert_on_cache_miss_rate: 0.5  # Alert if <50% cache hits
```

#### scripts/router.py (Complete Implementation)

```python
#!/usr/bin/env python3
"""
Token-Efficient Governance Router
Implements: Cache → Intent Router → Simple Rules → Large Model escalation
Target: 70%+ token reduction
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# Mock LLM clients (replace with actual SDK)
from llm_client import SmallModel, LargeModel

class GovernanceRouter:
    def __init__(self, config_path: str = "config.yml"):
        self.config = yaml.safe_load(Path(config_path).read_text())
        self.small_model = SmallModel(self.config["models"]["small"])
        self.large_model = LargeModel(self.config["models"]["large"])
        self.cache = {}  # Simple in-memory cache
        self.metrics = {"cache_hits": 0, "small_model_calls": 0, "large_model_calls": 0}

        # Load prompts
        self.prompts = {
            "cache_classifier": Path("prompts/cache_classifier.txt").read_text(),
            "intent_router": Path("prompts/intent_router.txt").read_text(),
            "distillation": Path("prompts/distillation.txt").read_text()
        }

        # Load simple rules
        self.simple_rules = yaml.safe_load(Path("policies/simple_rules.yml").read_text())

    def process_request(self, request: str, agent: str, namespace: str, action: str) -> Dict[str, Any]:
        """
        Main entry point for governance decisions
        Returns: {decision: ALLOW|DENY, reason: str, tokens_used: int, route: str}
        """
        start_time = datetime.now()

        # Step 1: Cache Classification (Small Model - ~100 tokens)
        cache_result = self._classify_for_cache(request, agent, namespace, action)
        tokens_used = 100

        if cache_result["route_to"] == "cache":
            # Cache hit - 0 additional tokens!
            self.metrics["cache_hits"] += 1
            decision = self._get_cached_decision(cache_result["cache_key"])
            return {
                **decision,
                "tokens_used": tokens_used,
                "route": "cache_hit",
                "latency_ms": (datetime.now() - start_time).total_seconds() * 1000
            }

        # Step 2: Intent Routing (Small Model - ~200 tokens)
        self.metrics["small_model_calls"] += 1
        intent = self._route_intent(request, agent, namespace, action)
        tokens_used += 200

        # Step 3: Try Simple Rules (0 tokens!)
        if intent["risk_level"] in ["low", "medium"]:
            rule_result = self._apply_simple_rules(intent, agent, namespace, action)
            if rule_result:
                self._cache_decision(cache_result.get("cache_key"), rule_result)
                return {
                    **rule_result,
                    "tokens_used": tokens_used,
                    "route": "simple_rules"
                }

        # Step 4: Escalate to Large Model (~500 tokens)
        self.metrics["large_model_calls"] += 1
        decision = self._escalate_to_large_model(request, intent, agent, namespace, action)
        tokens_used += 500

        # Step 5: Distill the decision for future use
        self._distill_decision(request, decision)

        return {
            **decision,
            "tokens_used": tokens_used,
            "route": "large_model",
            "latency_ms": (datetime.now() - start_time).total_seconds() * 1000
        }

    def _classify_for_cache(self, request: str, agent: str, namespace: str, action: str) -> Dict:
        """Step 1: Cache classifier"""
        prompt = self.prompts["cache_classifier"].format(
            user_request=request,
            agent_name=agent,
            namespace=namespace,
            action_type=action
        )

        response = self.small_model.generate(prompt, max_tokens=150)
        return json.loads(response)

    def _route_intent(self, request: str, agent: str, namespace: str, action: str) -> Dict:
        """Step 2: Intent router"""
        prompt = self.prompts["intent_router"].format(
            user_request=request,
            agent_name=agent,
            namespace=namespace,
            action_type=action
        )

        response = self.small_model.generate(prompt, max_tokens=200)
        return json.loads(response)

    def _apply_simple_rules(self, intent: Dict, agent: str, namespace: str, action: str) -> Optional[Dict]:
        """Step 3: Simple rules engine (no LLM)"""
        rule_key = f"{intent['category']}:{intent['subcategory']}:{intent['risk_level']}"

        if rule_key in self.simple_rules:
            rule = self.simple_rules[rule_key]
            # Execute rule logic (simplified example)
            if eval(rule["condition"]):  # In production, use safe eval or AST
                return {
                    "decision": rule["decision"],
                    "reason": rule["reason"],
                    "policy_refs": rule["policies"]
                }

        return None

    def _escalate_to_large_model(self, request: str, intent: Dict, agent: str, namespace: str, action: str) -> Dict:
        """Step 4: Large model for complex decisions"""
        prompt = f"""
        Governance decision required for complex case.

        Request: {request}
        Agent: {agent}
        Namespace: {namespace}
        Action: {action}
        Intent Classification: {json.dumps(intent, indent=2)}

        Policies to consider: {intent['policy_refs']}

        Provide decision in JSON format:
        {{
            "decision": "ALLOW|DENY",
            "reason": "detailed explanation",
            "conditions": ["condition1", "condition2"],
            "requires_approval": true|false,
            "approval_tier": "tier1|tier2|tier3|tier4"
        }}
        """

        response = self.large_model.generate(prompt, max_tokens=500)
        return json.loads(response)

    def _distill_decision(self, request: str, decision: Dict):
        """Step 5: Convert complex decision to simple rule"""
        # Only distill high-confidence, reusable decisions
        if decision.get("confidence", 0) < 0.85:
            return

        prompt = self.prompts["distillation"].format(
            complex_request=request,
            large_model_output=json.dumps(decision, indent=2)
        )

        distilled = self.large_model.generate(prompt, max_tokens=800)

        # Save distilled rule (simplified)
        rule_id = f"distilled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        Path(f"policies/distilled_rules/{rule_id}.py").write_text(distilled)

    def _get_cached_decision(self, cache_key: str) -> Dict:
        """Retrieve from cache"""
        return self.cache.get(cache_key, {"decision": "DENY", "reason": "Cache miss"})

    def _cache_decision(self, cache_key: str, decision: Dict):
        """Store in cache"""
        if cache_key:
            self.cache[cache_key] = decision

    def get_metrics(self) -> Dict:
        """Return token usage statistics"""
        total_requests = sum(self.metrics.values())
        if total_requests == 0:
            return self.metrics

        cache_hit_rate = self.metrics["cache_hits"] / total_requests

        # Calculate token savings
        baseline_tokens = total_requests * 2000  # All requests to large model
        actual_tokens = (
            self.metrics["cache_hits"] * 100 +
            self.metrics["small_model_calls"] * 300 +
            self.metrics["large_model_calls"] * 600
        )
        savings_pct = (baseline_tokens - actual_tokens) / baseline_tokens * 100

        return {
            **self.metrics,
            "cache_hit_rate": f"{cache_hit_rate:.2%}",
            "token_savings": f"{savings_pct:.1f}%",
            "baseline_tokens": baseline_tokens,
            "actual_tokens": actual_tokens
        }


# Example usage
if __name__ == "__main__":
    router = GovernanceRouter()

    # Test cases
    test_requests = [
        ("Can cleanup-agent delete temp files?", "cleanup-agent", "my-project", "delete"),
        ("Should deploy-agent create LoadBalancer in prod?", "deploy-agent", "production", "create"),
        ("Can read database logs?", "observer-agent", "staging", "access"),
    ]

    for req, agent, ns, action in test_requests:
        result = router.process_request(req, agent, ns, action)
        print(f"\nRequest: {req}")
        print(f"Decision: {result['decision']}")
        print(f"Route: {result['route']}")
        print(f"Tokens: {result['tokens_used']}")

    print(f"\n\nMetrics: {json.dumps(router.get_metrics(), indent=2)}")
```

#### policies/simple_rules.yml

```yaml
# Simple rules that can be executed without LLM calls
# Format: "CATEGORY:SUBCATEGORY:RISK_LEVEL": {condition, decision, reason}

CREATE:filesystem:low:
  condition: "namespace in ['dev', 'test'] and '/tmp/' in target_path"
  decision: ALLOW
  reason: "Low-risk temp file creation in dev/test namespace"
  policies: [namespace-isolation]

DELETE:temp:low:
  condition: "'/tmp/' in target_path and namespace != 'production'"
  decision: ALLOW
  reason: "Safe temp file deletion"
  policies: [deletion-safeguards]

ACCESS:logs:low:
  condition: "action == 'read' and 'logs/' in target_path"
  decision: ALLOW
  reason: "Log access within namespace"
  policies: [audit-trail]

ACCESS:secrets:high:
  condition: "False"  # Always deny, require large model decision
  decision: DENY
  reason: "Secrets access requires manual approval"
  policies: [credential-management, need-to-know]

DELETE:production:critical:
  condition: "False"  # Always deny simple rules
  decision: DENY
  reason: "Production deletions require large model review"
  policies: [deletion-safeguards, multi-approval, production-protection]

MODIFY:config:medium:
  condition: "has_backup and namespace in ['dev', 'staging']"
  decision: ALLOW
  reason: "Config modification with backup in non-prod"
  policies: [change-management, backup-required]

CREATE:kubernetes:medium:
  condition: "resource_type in ['Deployment', 'Service'] and namespace != 'production'"
  decision: ALLOW
  reason: "Standard k8s resource creation in non-prod"
  policies: [resource-limits, namespace-isolation]

COMPLY:audit:low:
  condition: "True"  # Always allow audit/compliance queries
  decision: ALLOW
  reason: "Compliance queries are read-only"
  policies: [audit-trail]
```

#### tests/test_router.py

```python
import pytest
from scripts.router import GovernanceRouter

def test_cache_hit():
    router = GovernanceRouter()

    # First request - cache miss
    result1 = router.process_request(
        "Can cleanup-agent delete temp files?",
        "cleanup-agent", "dev", "delete"
    )

    # Second identical request - should hit cache
    result2 = router.process_request(
        "Can cleanup-agent delete temp files?",
        "cleanup-agent", "dev", "delete"
    )

    assert result2["route"] == "cache_hit"
    assert result2["tokens_used"] == 100

def test_simple_rules():
    router = GovernanceRouter()

    result = router.process_request(
        "Create temp directory",
        "test-agent", "dev", "create"
    )

    assert result["route"] == "simple_rules"
    assert result["tokens_used"] <= 300  # No large model call

def test_large_model_escalation():
    router = GovernanceRouter()

    result = router.process_request(
        "Delete all production databases",
        "admin-agent", "production", "delete"
    )

    assert result["route"] == "large_model"
    assert result["decision"] == "DENY"

def test_token_savings():
    router = GovernanceRouter()

    # Run 100 requests (mix of cache hits and new)
    for i in range(100):
        router.process_request(
            f"Request {i % 10}",  # 10 unique patterns
            "test-agent", "dev", "read"
        )

    metrics = router.get_metrics()

    # Should achieve >70% token savings
    savings_pct = float(metrics["token_savings"].rstrip("%"))
    assert savings_pct > 70.0
```

---

### Template 2: Production-Ready Setup

**File: `templates/token-efficient-governance/production/`**

Includes:
- Redis cache integration
- Prometheus metrics export
- Distributed tracing (OpenTelemetry)
- Multi-tenant support
- Admin API (FastAPI)
- Kubernetes deployment manifests
- CI/CD pipeline (.github/workflows)

*(Full template available in separate file due to size)*

---

## Token Savings Analysis

### Baseline (No Optimization)

```
Scenario: 1000 governance requests/day
Model: Claude Opus 4 (70B equivalent)
Avg tokens per request: 2000
Daily tokens: 1000 × 2000 = 2,000,000 tokens
Monthly cost: 2M × 30 × $0.015/1k = $900/month
```

### Optimized System

```
Request Distribution:
- 60% cache hits → 100 tokens each
- 35% simple routing → 300 tokens each
- 5% large model → 600 tokens each

Daily tokens:
- Cache: 600 × 100 = 60,000
- Simple: 350 × 300 = 105,000
- Large: 50 × 600 = 30,000
Total: 195,000 tokens/day

Monthly cost: 195k × 30 × mixed pricing ≈ $90/month

SAVINGS: $810/month (90% reduction) 🎯
```

### ROI Calculation

**Implementation costs:**
- Week 1 setup: 16 hours × $100/hr = $1,600
- Week 2 distillation: 20 hours × $100/hr = $2,000
- Week 3 production: 26 hours × $100/hr = $2,600
- **Total:** $6,200

**Payback period:** $6,200 / $810/month = **7.6 months**

**3-year savings:** ($810 × 36) - $6,200 = **$23,000**

---

## Integration Plan

### Step 1: Proof of Concept (Days 1-3)

1. **Day 1:**
   - Copy `minimal/` template to your repo
   - Customize `config.yml` with your model endpoints
   - Update prompts with your specific governance policies
   - Run `python scripts/router.py` with 10 test requests

2. **Day 2:**
   - Add your 10 most common governance patterns to `simple_rules.yml`
   - Test cache hit rate with repeated requests
   - Measure token usage vs baseline

3. **Day 3:**
   - Run A/B test: 50 requests with optimization, 50 without
   - Calculate actual token savings
   - Present results to stakeholders

**Success Criteria:**
- ✅ Cache hit rate >50%
- ✅ Token reduction >60%
- ✅ No false positives (incorrect ALLOW decisions)

---

### Step 2: Production Deployment (Week 2)

1. Replace in-memory cache with Redis
2. Add monitoring (Prometheus/Grafana)
3. Set up CI/CD pipeline
4. Load test (1000 req/sec)
5. Security audit
6. Documentation

---

### Step 3: Continuous Improvement (Ongoing)

1. **Weekly:** Review large model escalations, identify patterns to distill
2. **Monthly:** Update simple rules based on new use cases
3. **Quarterly:** Re-evaluate model selection (new small models may be better)

---

## Next Steps

1. **Choose a starting point:**
   - Quick proof of concept → Use `minimal/` template
   - Production deployment → Use `production/` template

2. **Customize for your environment:**
   - Update `config.yml` with your model endpoints
   - Modify prompts to reference your specific policies
   - Add your governance rules to `simple_rules.yml`

3. **Measure and iterate:**
   - Run A/B tests to validate token savings
   - Distill high-frequency decisions
   - Monitor cache hit rate and adjust thresholds

---

## Files Created by This Implementation

```
docs/IMPLEMENTATION-TASK-LIST.md                  ← This file

templates/token-efficient-governance/
├── minimal/                                      ← Copy this to get started
│   ├── prompts/
│   │   ├── cache_classifier.txt
│   │   ├── intent_router.txt
│   │   └── distillation.txt
│   ├── scripts/
│   │   ├── router.py                            ← Main implementation
│   │   ├── cache.py
│   │   └── rules.py
│   ├── policies/
│   │   ├── simple_rules.yml                     ← Add your rules here
│   │   └── distilled_rules/
│   ├── tests/
│   │   ├── test_router.py
│   │   └── test_data.json
│   ├── config.yml                                ← Configure your models
│   ├── requirements.txt
│   └── README.md

└── production/                                   ← For production deployment
    ├── (same structure as minimal)
    ├── kubernetes/
    ├── monitoring/
    └── .github/workflows/
```

---

## Questions & Support

**Q: Which small model should I use?**
A: Recommended options (as of Oct 2025):
- Google Gemini 2.0 Flash Thinking (best price/performance)
- Meta Llama 3.2 3B (self-hosted option)
- Anthropic Claude Haiku (if using Anthropic stack)

**Q: What if my cache hit rate is low (<40%)?**
A:
1. Review your `cache_classifier` prompt - may be too conservative
2. Add more patterns to `simple_rules.yml`
3. Lower confidence threshold in `config.yml`

**Q: How do I handle policy updates?**
A:
1. Update the policy file
2. Clear cache for affected patterns
3. Re-run distillation for impacted rules
4. Deploy new rules with version number

**Q: Is this secure against prompt injection?**
A:
1. Input validation before prompts
2. Structured JSON output (not free text)
3. Simple rules don't use LLM (immune to injection)
4. Audit all large model decisions

---

**End of Implementation Task List**
**Last Updated:** 2025-10-25
**Next Review:** After Phase 1 completion (Week 1)
