# NIST SP 800-207 Zero Trust Architecture Components Mapping

This document provides a formal mapping of the six logical components of a Zero Trust Architecture (ZTA) as defined in NIST SP 800-207, mapping each component to its implementation in the AI Agent Governance Framework.

## Component Mapping Table

| ZT Component | System / Implementation | Primary File(s) | NIST 800-53 Control(s) |
| :--- | :--- | :--- | :--- |
| **Policy Decision Point (PDP)** | Governance Policy Inquiry Service (GPIS) FastAPI Server | [main.py](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/app/main.py) | AC-3, AC-6, AU-2, IA-3 |
| **Policy Enforcement Point (PEP)** | K8s NetworkPolicy + JWT Middleware validation | [networkpolicy.yaml](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/deploy/helm/ai-agent/templates/networkpolicy.yaml) | SC-7, AC-17, SC-8 |
| **Policy Information Point (PIP)** | CMDB, agent manifests, Prometheus metrics, and Budget check | [policy_engine.py](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/app/policy_engine.py), [simple_rules.yml](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/policies/simple_rules.yml) | AU-2, RA-5, SI-4 |
| **Policy Administration Point (PAP)** | GPIS Admin API + simple rules registry storage | [admin_api.py](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/app/admin_api.py), `simple_rules.yml` | CM-3, CM-6, AC-2, AU-12 |
| **Policy Engine (PE)** | GovernanceRouter execution flow (Cache -> Router -> Rules -> LLM) | [governance_router.py](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/scripts/governance_router.py) | SI-2, AC-24, SI-3 |
| **Policy Administrator (PA)** | Human Operators, Jira Webhook verification | [validate-jira-approval.py](file:///home/suhlabs/projects/suhlabs/ai-agent-governance-framework/scripts/validate-jira-approval.py) | AC-5, PE-2, CM-3 |

---

## Detailed ZTA Component Implementations

### 1. Policy Decision Point (PDP)
The **PDP** is the central authority that makes decisions to grant, deny, or suspend access to resources.
* **Implementation:** The GPIS FastAPI server processes requests containing the `agent_id`, `category`, and `payload`. It resolves policies by evaluating simple rules and checking system state.
* **Sovereignty:** Single point of truth. Agents never self-authorize.

### 2. Policy Enforcement Point (PEP)
The **PEP** is responsible for establishing, monitoring, and terminating connections between subjects and resources.
* **Implementation:** 
  1. **L4 Layer:** Kubernetes `NetworkPolicy` objects enforce namespace-isolation and restrict port-to-port communication.
  2. **L7 Layer:** Downstream service endpoints and the `GovernanceRouter` validate GPIS-signed JWTs, ensuring the agent holds a valid "permission slip."

### 3. Policy Information Point (PIP)
The **PIP** provides external context (attribute data, logs, budget info) required by the PDP to make decisions.
* **Implementation:**
  1. **CMDB/Manifests:** Defines metadata quotas, tiers, and isolated namespace mappings.
  2. **Budget PIP:** Querying rolling 24h token metrics in Redis to enforce financial limits.

### 4. Policy Administration Point (PAP)
The **PAP** is the interface used to define, edit, and publish access policies.
* **Implementation:** Policies are stored as code (`simple_rules.yml`). Modifications flow through Git change management. The `/admin` API on GPIS serves as the runtime interface to suspend or revoke active policy bindings.

### 5. Policy Engine (PE)
The **PE** is the core cognitive engine that evaluates intent, risk, and heuristics to propose decisions.
* **Implementation:** The `GovernanceRouter` runs the token-efficient pipeline: caching decisions, determining request intent, performing fast rules lookup, and escalating to LLMs when necessary.

### 6. Policy Administrator (PA)
The **PA** represents the human-in-the-loop governance role.
* **Implementation:** Enforces approval constraints for Tier 3 and 4 actions. Integrates with enterprise change control systems (Jira CR verification) and handles manual revocation decisions.
