#!/usr/bin/env python3
"""
Token-Efficient Governance Router for AI Agent Governance Framework
Implements: Cache → Intent Router → Simple Rules → Large Model escalation
Also manages: Stateful memory broker (Redis/local), Tool Registry enforcement,
and CyberArk secretless token checkout.
"""

import os
import json
import yaml
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class GovernanceRouter:
    """
    Main router for token-efficient governance decisions, stateful memory, and tool enforcement
    """

    def __init__(self, config_path: str = "config/token_router.yml"):
        """Initialize router with config and load prompts/rules"""
        self.project_root = Path(__file__).parent.parent
        
        # Load configuration
        conf_file = self.project_root / config_path
        if conf_file.exists():
            self.config = yaml.safe_load(conf_file.read_text())
        else:
            self.config = {
                "models": {
                    "small": {"model": "gemini-2.0-flash-thinking-exp-1219"},
                    "large": {"model": "claude-opus-4-20250514"}
                }
            }

        # Initialize LLM clients with graceful fallback
        self.small_model = None
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.small_model = genai.GenerativeModel(self.config["models"]["small"]["model"])
            except Exception:
                pass

        self.large_model = None
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                from anthropic import Anthropic
                self.large_model = Anthropic(api_key=anthropic_key)
            except Exception:
                pass

        # Redis connection setup
        self.redis_client = None
        self.local_memory = {}
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        try:
            import redis
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=1)
            self.redis_client.ping()
        except Exception:
            self.redis_client = None

        self.metrics = {
            "cache_hits": 0,
            "small_model_calls": 0,
            "large_model_calls": 0,
            "total_tokens": 0
        }

        # Load prompts
        prompt_dir = self.project_root / "scripts" / "prompts"
        self.prompts = {}
        for p_name in ["cache_classifier", "intent_router", "distillation"]:
            p_file = prompt_dir / f"{p_name}.txt"
            if p_file.exists():
                self.prompts[p_name] = p_file.read_text()
            else:
                self.prompts[p_name] = "Mock prompt for {user_request}"

        # Load simple rules
        rules_path = self.project_root / "policies" / "simple_rules.yml"
        self.simple_rules = yaml.safe_load(rules_path.read_text()) if rules_path.exists() else {}

        # Load tool registry
        tool_reg_path = self.project_root / "policies" / "tool-registry.yml"
        self.tool_registry = yaml.safe_load(tool_reg_path.read_text()) if tool_reg_path.exists() else {"tools": {}}

    def process_request(
        self,
        request: str,
        agent_name: str,
        namespace: str,
        action_type: str,
        agent_tier: str = "tier1"
    ) -> Dict[str, Any]:
        """
        Main entry point for governance decisions
        """
        start_time = datetime.now()
        tokens_used = 0

        # Validate input for prompt injection
        try:
            self._validate_input_safety(request)
        except ValueError as e:
            return {
                "decision": "DENY",
                "reason": f"Input validation failed: {str(e)}",
                "tokens_used": 0,
                "route": "validation_error",
                "guardrails_checked": ["8"]
            }

        # Step 1: Cache Classification (Small Model - ~100 tokens)
        cache_result = self._classify_for_cache(
            request, agent_name, namespace, action_type
        )
        tokens_used += 100

        if cache_result.get("route_to") == "cache":
            # Cache hit - no additional tokens!
            self.metrics["cache_hits"] += 1
            decision = self._get_cached_decision(cache_result["cache_key"])
            if decision.get("decision"):
                return {
                    **decision,
                    "tokens_used": tokens_used,
                    "route": "cache_hit",
                    "latency_ms": (datetime.now() - start_time).total_seconds() * 1000
                }

        # Step 2: Intent Routing (Small Model - ~200 tokens)
        self.metrics["small_model_calls"] += 1
        intent = self._route_intent(
            request, agent_name, namespace, action_type, agent_tier
        )
        tokens_used += 200

        # Step 3: Try Simple Rules (0 tokens!)
        if intent.get("risk_level") in ["low", "medium"] and not intent.get("agent_tier_violation"):
            rule_result = self._apply_simple_rules(intent, namespace, agent_tier)
            if rule_result:
                if cache_result.get("cache_key"):
                    self._cache_decision(cache_result["cache_key"], rule_result)
                self.metrics["total_tokens"] += tokens_used
                return {
                    **rule_result,
                    "tokens_used": tokens_used,
                    "route": "simple_rules",
                    "latency_ms": (datetime.now() - start_time).total_seconds() * 1000
                }

        # Step 4: Escalate to Large Model (~500 tokens)
        self.metrics["large_model_calls"] += 1
        decision = self._escalate_to_large_model(
            request, intent, agent_name, namespace, action_type, agent_tier
        )
        tokens_used += 500

        # Step 5: Log for potential distillation
        if decision.get("confidence", 0) > 0.85:
            self._queue_for_distillation(request, decision)

        self.metrics["total_tokens"] += tokens_used
        return {
            **decision,
            "tokens_used": tokens_used,
            "route": "large_model",
            "latency_ms": (datetime.now() - start_time).total_seconds() * 1000
        }

    def _validate_input_safety(self, request: str):
        """Validates request against injection patterns (Guardrail #8)"""
        max_len = self.config.get("security", {}).get("input_validation", {}).get("max_request_length", 500)
        if len(request) > max_len:
            raise ValueError(f"Request exceeds maximum length of {max_len} characters")
        
        block_patterns = self.config.get("security", {}).get("input_validation", {}).get("block_patterns", [
            "(?i)ignore (previous|above|all) instructions",
            "(?i)you are now",
            "(?i)forget your",
            "(?i)system prompt"
        ])
        for pattern in block_patterns:
            if re.search(pattern, request):
                raise ValueError("Potential prompt injection pattern detected")

    def _classify_for_cache(
        self, request: str, agent_name: str, namespace: str, action_type: str
    ) -> Dict:
        """Step 1: Cache classifier using small model"""
        if self.small_model:
            prompt = self.prompts["cache_classifier"].format(
                user_request=request,
                agent_name=agent_name,
                namespace=namespace,
                action_type=action_type
            )
            try:
                response = self.small_model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.0, "max_output_tokens": 150}
                )
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception:
                pass
        
        # Fallback / mock cache classification
        import hashlib
        cache_key = hashlib.sha256(f"{agent_name}:{namespace}:{action_type}:{request}".encode()).hexdigest()
        cacheable = action_type in ["read", "get", "list", "query"] or "read" in request.lower()
        return {
            "cacheable": cacheable,
            "cache_key": cache_key if cacheable else None,
            "confidence": 0.9,
            "reasoning": "Fallback classification",
            "route_to": "cache" if (cacheable and cache_key in self.cache) else "router"
        }

    def _route_intent(
        self,
        request: str,
        agent_name: str,
        namespace: str,
        action_type: str,
        agent_tier: str
    ) -> Dict:
        """Step 2: Intent router using small model"""
        if self.small_model:
            prompt = self.prompts["intent_router"].format(
                user_request=request,
                agent_name=agent_name,
                namespace=namespace,
                action_type=action_type,
                agent_tier=agent_tier
            )
            try:
                response = self.small_model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.0, "max_output_tokens": 300}
                )
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception:
                pass

        # Fallback / mock intent classification based on keywords
        category = "ACCESS"
        subcategory = "logs"
        risk_level = "low"
        requires_approval = False
        requires_confirmation = False
        
        req_lower = request.lower()
        if "delete" in req_lower or action_type == "delete":
            category = "DELETE"
            risk_level = "critical" if namespace in ["production", "prod"] else "high"
        elif "deploy" in req_lower or "create" in req_lower or action_type == "create":
            category = "CREATE"
            risk_level = "medium"
            if "deployment" in req_lower:
                subcategory = "kubernetes_deployment"
            elif "service" in req_lower:
                subcategory = "kubernetes_service"
            elif "infrastructure" in req_lower:
                subcategory = "infrastructure"
        elif "modify" in req_lower or "update" in req_lower or action_type == "modify":
            category = "MODIFY"
            risk_level = "medium"
            if "config" in req_lower:
                subcategory = "config_file"
        elif "cve" in req_lower or "vulnerability" in req_lower:
            category = "ACCESS"
            subcategory = "cve_lookup"
        elif "comply" in req_lower or "audit" in req_lower:
            category = "COMPLY"
            subcategory = "audit_report"
            
        tier_num = int(agent_tier[-1]) if agent_tier[-1].isdigit() else 1
        agent_tier_violation = False
        if category in ["DELETE", "CREATE", "MODIFY"]:
            if tier_num < 2:
                agent_tier_violation = True
            if category == "DELETE" and tier_num < 3:
                agent_tier_violation = True

        return {
            "category": category,
            "subcategory": subcategory,
            "risk_level": risk_level,
            "requires_approval": requires_approval,
            "requires_confirmation": requires_confirmation,
            "simulation_mode_required": category == "DELETE",
            "guardrail_refs": ["1", "6"],
            "policy_refs": ["audit-trail"],
            "agent_tier_violation": agent_tier_violation
        }

    def _apply_simple_rules(
        self, intent: Dict, namespace: str, agent_tier: str
    ) -> Optional[Dict]:
        """Step 3: Apply cached simple rules (NO LLM)"""
        rule_key = f"{intent['category']}:{intent['subcategory']}:{intent['risk_level']}"

        if rule_key in self.simple_rules:
            rule = self.simple_rules[rule_key]
            return {
                "decision": rule["decision"],
                "reason": rule["reason"],
                "guardrails_checked": intent.get("guardrail_refs", []),
                "policy_refs": rule.get("policies", [])
            }

        return None

    def _escalate_to_large_model(
        self,
        request: str,
        intent: Dict,
        agent_name: str,
        namespace: str,
        action_type: str,
        agent_tier: str
    ) -> Dict:
        """Step 4: Large model for complex decisions"""
        if self.large_model:
            prompt = f"""
You are the AI Agent Governance Framework decision engine.

REQUEST: {request}
AGENT: {agent_name} (Tier: {agent_tier})
NAMESPACE: {namespace}
ACTION: {action_type}

INTENT CLASSIFICATION:
{json.dumps(intent, indent=2)}

FRAMEWORK RULES:
- 16 Guardrail Rules (namespace isolation, safety, audit, secrets, etc.)
- Agent Tier System (Tier 1: read-only → Tier 4: autonomous)
- Risk Levels: low, medium, high, critical
- Simulation mode required for DELETE operations
- Audit trail required for all decisions

YOUR TASK:
Provide a governance decision in JSON format:

{{
  "decision": "ALLOW" or "DENY",
  "reason": "detailed explanation",
  "guardrails_enforced": ["1", "2", ...],
  "requires_confirmation": true|false,
  "simulation_required": true|false,
  "conditions": ["condition 1", "condition 2", ...],
  "confidence": 0.0-1.0
}}

OUTPUT JSON ONLY:
"""
            try:
                response = self.large_model.messages.create(
                    model=self.config["models"]["large"]["model"],
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception:
                pass

        # Fallback / mock large model decision
        decision = "ALLOW"
        reason = "Request authorized by policy."
        
        if intent.get("agent_tier_violation"):
            decision = "DENY"
            reason = f"Agent tier insufficient for operation."
        elif namespace in ["production", "prod"] and intent.get("risk_level") in ["high", "critical"]:
            decision = "DENY"
            reason = f"Direct modification of production denied. Human review required."

        return {
            "decision": decision,
            "reason": reason,
            "guardrails_enforced": ["1", "6"],
            "requires_confirmation": False,
            "simulation_required": False,
            "conditions": [],
            "confidence": 0.95
        }

    def _get_cached_decision(self, cache_key: str) -> Dict:
        """Retrieve decision from cache"""
        if self.redis_client:
            try:
                val = self.redis_client.get(f"governance_cache:{cache_key}")
                if val:
                    return json.loads(val.decode("utf-8"))
            except Exception:
                pass
        return self.local_memory.get(f"governance_cache:{cache_key}", {
            "decision": "DENY",
            "reason": "Cache miss",
            "guardrails_checked": []
        })

    def _cache_decision(self, cache_key: str, decision: Dict):
        """Store decision in cache"""
        if cache_key:
            if self.redis_client:
                try:
                    self.redis_client.setex(f"governance_cache:{cache_key}", 3600, json.dumps(decision))
                    return
                except Exception:
                    pass
            self.local_memory[f"governance_cache:{cache_key}"] = decision

    def _queue_for_distillation(self, request: str, decision: Dict):
        """Queue high-confidence decisions for distillation"""
        distill_queue = self.project_root / "logs" / "distillation_queue.jsonl"
        try:
            distill_queue.parent.mkdir(exist_ok=True)
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "request": request,
                "decision": decision
            }
            with open(distill_queue, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def get_metrics(self) -> Dict:
        """Return token usage statistics"""
        total_requests = sum([
            self.metrics["cache_hits"],
            self.metrics["small_model_calls"],
            self.metrics["large_model_calls"]
        ])

        if total_requests == 0:
            return self.metrics

        cache_hit_rate = self.metrics["cache_hits"] / total_requests
        baseline_tokens = total_requests * 2000
        savings_pct = (baseline_tokens - self.metrics["total_tokens"]) / baseline_tokens * 100

        return {
            **self.metrics,
            "total_requests": total_requests,
            "cache_hit_rate": f"{cache_hit_rate:.2%}",
            "token_savings": f"{savings_pct:.1f}%",
            "baseline_tokens": baseline_tokens,
            "actual_tokens": self.metrics["total_tokens"]
        }

    # ─── Ephemeral Credential Lifecycle (CyberArk Conjur) ────────────────────
    def _fetch_ephemeral_credential(self, conjur_url: str, policy_path: str) -> str:
        """Fetch short-lived ephemeral token from Conjur (Guardrail #8)"""
        # Conjur sidecar token mount path
        token_path = Path("/run/conjur/access-token")
        if token_path.exists():
            try:
                return token_path.read_text().strip()
            except Exception:
                pass
        
        # Projected ServiceAccount token volume path
        sa_token_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
        if sa_token_path.exists():
            try:
                return sa_token_path.read_text().strip()
            except Exception:
                pass

        return "mock-ephemeral-conjur-token-value"

    # ─── Stateful Agent Memory Broker (ZT-compliant Redis backend) ──────────
    def memory_read(self, agent_id: str, key: str) -> Optional[str]:
        """Read a key from isolated agent memory (SC-28 / ZT)"""
        redis_key = f"agent_memory:{agent_id}:{key}"
        if self.redis_client:
            try:
                val = self.redis_client.get(redis_key)
                return val.decode("utf-8") if val else None
            except Exception:
                pass
        return self.local_memory.get(redis_key)

    def memory_write(self, agent_id: str, key: str, value: str) -> bool:
        """Write a key to isolated agent memory (SC-28 / ZT)"""
        redis_key = f"agent_memory:{agent_id}:{key}"
        if self.redis_client:
            try:
                self.redis_client.set(redis_key, value)
                return True
            except Exception:
                pass
        self.local_memory[redis_key] = value
        return True

    def memory_checkpoint(self, agent_id: str) -> str:
        """Create a checkpoint of all agent keys (HITL Suspension Checkpoint)"""
        checkpoint_id = str(uuid.uuid4())
        agent_keys = {}
        prefix = f"agent_memory:{agent_id}:"
        if self.redis_client:
            try:
                # Find keys in Redis
                for k in self.redis_client.keys(f"{prefix}*"):
                    val = self.redis_client.get(k)
                    if val:
                        stripped_key = k.decode("utf-8")[len(prefix):]
                        agent_keys[stripped_key] = val.decode("utf-8")
            except Exception:
                pass
        if not agent_keys:
            # Fallback to local memory
            for k, val in self.local_memory.items():
                if k.startswith(prefix):
                    stripped_key = k[len(prefix):]
                    agent_keys[stripped_key] = val

        # Store checkpoint serialized
        checkpoint_key = f"agent_checkpoint:{agent_id}:{checkpoint_id}"
        checkpoint_data = json.dumps(agent_keys)
        if self.redis_client:
            try:
                # Store with 25-hour TTL
                self.redis_client.setex(checkpoint_key, 90000, checkpoint_data)
                return checkpoint_id
            except Exception:
                pass
        self.local_memory[checkpoint_key] = checkpoint_data
        return checkpoint_id

    def memory_restore(self, agent_id: str, checkpoint_id: str) -> bool:
        """Restore memory keys from a checkpoint (HITL Resume)"""
        checkpoint_key = f"agent_checkpoint:{agent_id}:{checkpoint_id}"
        data_str = None
        if self.redis_client:
            try:
                data_str = self.redis_client.get(checkpoint_key)
                if data_str:
                    data_str = data_str.decode("utf-8")
            except Exception:
                pass
        if not data_str:
            data_str = self.local_memory.get(checkpoint_key)

        if not data_str:
            return False

        data = json.loads(data_str)
        for k, v in data.items():
            self.memory_write(agent_id, k, v)
        return True

    # ─── Tool Registry Enforcement (L7 App-layer - NIST SP 800-207) ──────────
    def execute_tool(self, agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and check authorization to execute a tool (excessive agency blocker)
        """
        tools = self.tool_registry.get("tools", {})
        if tool_name not in tools:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' is not registered in the Tool Registry (excessive agency protection)."
            }

        tool_config = tools[tool_name]

        # Check authorized agents
        authorized = tool_config.get("authorized_agents", [])
        if authorized != "ALL" and agent_id not in authorized:
            return {
                "allowed": False,
                "reason": f"Agent '{agent_id}' is not authorized to use tool '{tool_name}'."
            }

        # Check FQDN egress constraint if destination is in arguments (e.g. host, url, endpoint)
        allowed_fqdns = tool_config.get("allowed_fqdns", [])
        if allowed_fqdns:
            dest = arguments.get("host") or arguments.get("url") or arguments.get("endpoint") or arguments.get("fqdn")
            if dest:
                # strip schema/port
                host = dest.replace("https://", "").replace("http://", "").split(":")[0].split("/")[0]
                if host not in allowed_fqdns:
                    return {
                        "allowed": False,
                        "reason": f"Destination host '{host}' is not in the allowed FQDN list for tool '{tool_name}'."
                    }

        # Check allowed methods if any
        allowed_methods = tool_config.get("allowed_methods", [])
        if allowed_methods:
            method = arguments.get("method", "GET").upper()
            if method not in [m.upper() for m in allowed_methods]:
                return {
                    "allowed": False,
                    "reason": f"HTTP method '{method}' is not allowed for tool '{tool_name}'. Allowed: {allowed_methods}."
                }

        # Validate arguments against request_schema (prevent injection)
        schema = tool_config.get("request_schema", {})
        for param, spec in schema.items():
            if param in arguments:
                # Basic injection check for string params
                if "string" in str(spec).lower() and isinstance(arguments[param], str):
                    if "alphanumeric" in str(spec).lower():
                        val = arguments[param]
                        # permit space, dash, underscore
                        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", val):
                            return {
                                "allowed": False,
                                "reason": f"Parameter '{param}' contains potentially unsafe characters violating schema restrictions."
                            }

        return {
            "allowed": True,
            "reason": f"Tool '{tool_name}' execution authorized."
        }
