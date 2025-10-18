# Game-Theoretic RACI Validation

**AI Agent Governance Framework v2.1**
**Control: APP-001, G-02, RACI-001**

## Overview

This module applies game theory to validate RACI (Responsible, Accountable, Consulted, Informed) assignments for AI agents, ensuring optimal governance through mathematical proof of equilibrium states.

---

## Table of Contents

1. [Theoretical Foundation](#theoretical-foundation)
2. [Why Game Theory for RACI?](#why-game-theory-for-raci)
3. [Model Architecture](#model-architecture)
4. [RAND Corp Flaws Addressed](#rand-corp-flaws-addressed)
5. [Usage Guide](#usage-guide)
6. [Examples](#examples)
7. [Integration with Framework](#integration-with-framework)

---

## Theoretical Foundation

### Stackelberg Leadership Game

**Definition:** A sequential game where a leader moves first, and followers observe and respond optimally.

**Applied to AI Agents:**
- **Leader:** Tier 4 (Architect) - Sets strategic direction
- **Followers:** Tier 3 (Ops), Tier 2 (Dev), Tier 1 (Observer) - Respond optimally

**Solution Concept:** Backward induction to find Subgame Perfect Nash Equilibrium (SPNE)

```
Leader (Tier 4) → Follower 1 (Tier 3) → Follower 2 (Tier 2) → Follower 3 (Tier 1)
     ↓                  ↓                      ↓                      ↓
  Strategy          Best Response        Best Response         Best Response
```

### Nash Equilibrium

**Definition:** A strategy profile where no agent can improve their payoff by unilaterally deviating.

**Verification:**
For each agent `i` and their chosen action `a_i`:
```
Payoff(a_i, a_{-i}) ≥ Payoff(a'_i, a_{-i})  ∀ alternative actions a'_i
```

Where `a_{-i}` = actions of all other agents

### Payoff Function

```
Payoff = Compliance_Value - Cost - Risk_Penalty + Cooperation_Bonus

Where:
- Compliance_Value: Value of satisfying control requirements
- Cost: Resource cost × agent's cost factor
- Risk_Penalty: Risk level × (1 - risk tolerance)
- Cooperation_Bonus: Mechanism design incentive for following RACI
```

**Mechanism Design:**
- Responsible role: +2.0 bonus (incentivizes doing assigned work)
- Consulted role: +0.5 bonus (incentivizes collaboration)
- Accountable role: Oversight authority (implicit power)

---

## Why Game Theory for RACI?

### Traditional RACI Problems

1. **Ambiguous Accountability** - Multiple agents claim authority
2. **Responsibility Shirking** - Agents avoid difficult tasks
3. **Coordination Failures** - Conflicting actions
4. **Tier Violations** - Lower tiers overriding higher tiers

### Game Theory Solutions

| Problem | Game Theory Solution |
|---------|---------------------|
| Ambiguous Accountability | Nash equilibrium ensures unique stable assignment |
| Responsibility Shirking | Payoff function incentivizes Responsible agents |
| Coordination Failures | Stackelberg model enforces sequential rationality |
| Tier Violations | Backward induction respects hierarchy |

### Mathematical Guarantees

✅ **Existence**: Nash equilibrium exists (proven for finite games)
✅ **Uniqueness**: Stackelberg equilibrium typically unique
✅ **Optimality**: SPNE is dynamically consistent
✅ **Verifiability**: Computationally checkable

---

## Model Architecture

### Components

```
┌──────────────────────────────────────────────────────┐
│              RACI Game Validator                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  1. RACI Constraint Validation             │    │
│  │     - One Accountable per control          │    │
│  │     - At least one Responsible             │    │
│  │     - No R=A for same agent                │    │
│  │     - Tier hierarchy enforcement           │    │
│  └────────────────────────────────────────────┘    │
│                      ↓                               │
│  ┌────────────────────────────────────────────┐    │
│  │  2. Conflict Detection                     │    │
│  │     - Overlapping responsibilities         │    │
│  │     - Tier violations                      │    │
│  │     - Misaligned incentives                │    │
│  └────────────────────────────────────────────┘    │
│                      ↓                               │
│  ┌────────────────────────────────────────────┐    │
│  │  3. Stackelberg Equilibrium Solving        │    │
│  │     - Sequential moves (Tier 4→3→2→1)      │    │
│  │     - Backward induction                   │    │
│  │     - Best response calculation            │    │
│  └────────────────────────────────────────────┘    │
│                      ↓                               │
│  ┌────────────────────────────────────────────┐    │
│  │  4. Nash Equilibrium Verification          │    │
│  │     - Check no profitable deviation        │    │
│  │     - Epsilon tolerance (0.01)             │    │
│  │     - Report violations if any             │    │
│  └────────────────────────────────────────────┘    │
│                      ↓                               │
│  ┌────────────────────────────────────────────┐    │
│  │  5. Audit Trail Generation                 │    │
│  │     - Game state snapshot                  │    │
│  │     - Equilibrium actions                  │    │
│  │     - Compliance/cost/risk metrics         │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Data Structures

**Agent:**
```python
@dataclass
class Agent:
    agent_id: str
    tier: AgentTier  # 1-4
    controls: List[str]
    cost_per_action: float
    risk_tolerance: float  # 0.0-1.0
```

**RACI Assignment:**
```python
@dataclass
class RACIAssignment:
    control_id: str
    responsible: Agent
    accountable: Agent
    consulted: List[Agent]
    informed: List[Agent]
```

**Payoff Matrix:**
```python
@dataclass
class PayoffMatrix:
    agent: Agent
    action: Action
    payoff: float
    breakdown: Dict[str, float]  # Components
```

---

## RAND Corp Flaws Addressed

### 1. Nash Equilibrium Assumption Flaw

**RAND Problem:** Assumes perfect information and rationality

**Our Fix:**
- Sequential information revelation (Stackelberg)
- Bounded rationality via epsilon tolerance
- Observable game state (audit trails)

### 2. Zero-Sum Fallacy

**RAND Problem:** Treats agent interactions as zero-sum (tic-tac-toe model)

**Our Fix:**
- **Positive-sum game:** Cooperation bonus incentivizes collaboration
- **Pareto improvements:** Multiple agents can increase payoffs simultaneously
- **Long-term vs. short-term:** Compliance value rewards sustained cooperation

### 3. Static Game Limitation

**RAND Problem:** One-shot games don't capture evolving relationships

**Our Fix:**
- **Dynamic RACI:** Assignments can be updated
- **Repeated game potential:** Framework supports multi-round analysis
- **Contextual adaptation:** Risk tolerance and costs can vary by scenario

### 4. Incomplete Contracts

**RAND Problem:** Cannot specify all contingencies

**Our Fix:**
- **Mechanism design:** Cooperation bonuses fill contractual gaps
- **Jira CR approval:** Explicit approval for edge cases
- **Escalation paths:** Consulted/Informed roles provide flexibility

### 5. Enforcement Assumption

**RAND Problem:** Assumes costless enforcement

**Our Fix:**
- **Audit trails:** Cryptographic evidence (hash)
- **CI/CD integration:** Automated enforcement gates
- **PKI signatures:** Non-repudiation of commitments

---

## Usage Guide

### Basic Usage

```bash
# Run with default test scenario
python3 scripts/game_theory/raci_game_validator.py

# Output:
# ✅ All RACI constraints satisfied
# ✅ No conflicts detected
# ✓ Nash equilibrium verified
```

### Programmatic Usage

```python
from scripts.game_theory.raci_game_validator import (
    Agent, AgentTier, RACIAssignment, RACIGameValidator
)

# Define agents
agents = [
    Agent("architect", AgentTier.TIER4_ARCHITECT, ["APP-001"]),
    Agent("security", AgentTier.TIER3_OPERATIONS, ["SEC-001"]),
    Agent("ops", AgentTier.TIER3_OPERATIONS, ["AU-002"]),
]

# Define RACI
raci = [
    RACIAssignment(
        control_id="SEC-001",
        responsible=agents[1],  # security
        accountable=agents[0],  # architect
        consulted=[agents[2]],  # ops
        informed=[]
    )
]

# Validate
validator = RACIGameValidator(agents, raci)

# Check constraints
is_valid, violations = validator.validate_raci_constraints()

# Detect conflicts
conflicts = validator.detect_raci_conflicts()

# Find equilibrium
actions = {agent: validator._get_agent_actions(agent) for agent in agents}
equilibrium = validator.stackelberg_equilibrium(actions)

# Verify Nash
game_state = GameState(agents=agents, raci_assignments=raci)
is_nash, _ = validator.check_nash_equilibrium(game_state, equilibrium)

print(f"RACI Valid: {is_valid}")
print(f"Nash Equilibrium: {is_nash}")
```

### Integration with CI/CD

```yaml
# .github/workflows/validate-raci.yml
name: Validate RACI with Game Theory

on:
  push:
    paths:
      - 'config/raci-assignments.json'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate RACI Equilibrium
        run: |
          python3 scripts/game_theory/raci_game_validator.py \
            --config config/raci-assignments.json \
            --output /tmp/raci-validation.json

      - name: Check Nash Equilibrium
        run: |
          if ! grep -q '"nash_equilibrium": true' /tmp/raci-validation.json; then
            echo "❌ RACI assignment is not a Nash equilibrium"
            exit 1
          fi
```

---

## Examples

### Example 1: Valid Stackelberg Equilibrium

```python
# Tier 4 (Architect) leads
architect = Agent("architect", AgentTier.TIER4_ARCHITECT, ["G-02"])

# Tier 3 (Security) follows
security = Agent("security", AgentTier.TIER3_OPERATIONS, ["SEC-001"])

# RACI: Architect accountable, Security responsible
raci = RACIAssignment(
    control_id="SEC-001",
    responsible=security,
    accountable=architect,
    consulted=[],
    informed=[]
)

# Result: ✅ Nash equilibrium
# Architect sets policy (leader move)
# Security executes optimally (best response)
```

### Example 2: Conflict Detection

```python
# Two agents competing for same Responsible role
security = Agent("security", AgentTier.TIER3_OPERATIONS, ["SEC-001"])
ops = Agent("ops", AgentTier.TIER3_OPERATIONS, ["SEC-001"])

raci1 = RACIAssignment(control_id="SEC-001", responsible=security, ...)
raci2 = RACIAssignment(control_id="SEC-001", responsible=ops, ...)

# Result: ❌ Conflict detected
# Type: overlapping_responsible
# Agents: [security, ops]
```

### Example 3: Tier Violation

```python
# Lower tier as Accountable (violation)
dev = Agent("dev", AgentTier.TIER2_DEVELOPER, ["MI-009"])
architect = Agent("architect", AgentTier.TIER4_ARCHITECT, ["G-02"])

raci = RACIAssignment(
    control_id="G-02",
    responsible=architect,
    accountable=dev,  # ❌ Tier 2 cannot be Accountable
    consulted=[],
    informed=[]
)

# Result: ❌ Tier hierarchy violation
```

---

## Integration with Framework

### 1. Setup Agent Script

```bash
# scripts/setup-agent.sh now validates RACI
./scripts/setup-agent.sh \
  --tier 3 \
  --name security-agent \
  --validate-raci \
  --raci-config config/raci.json
```

### 2. Jira CR Approval

RACI validation runs during Jira approval:
```python
# scripts/validate-jira-approval.py
def validate_cr(cr_id):
    # ... existing validation ...

    # Validate RACI equilibrium
    validator = RACIGameValidator(...)
    is_nash, violations = validator.check_nash_equilibrium(...)

    if not is_nash:
        raise ValidationError("RACI assignment not in Nash equilibrium")
```

### 3. Terraform Integration

```hcl
# terraform/main-modular-v2.tf
resource "null_resource" "raci_validation" {
  provisioner "local-exec" {
    command = <<-EOT
      python3 scripts/game_theory/raci_game_validator.py \
        --agents config/agents.json \
        --raci config/raci.json \
        --output audit-trails/raci-${var.audit_id}.json
    EOT
  }
}
```

### 4. Audit Trail Schema

RACI validation conforms to `audit-trail.json`:

```json
{
  "audit_id": "audit-1729274400-xyz789",
  "timestamp": "2025-10-18T12:00:00Z",
  "actor": "raci-game-validator",
  "action": "game_theoretic_validation",
  "outputs": {
    "nash_equilibrium": true,
    "stackelberg_equilibrium": true,
    "compliance_score": 15.0,
    "conflicts_detected": 0
  },
  "compliance_result": "pass"
}
```

---

## Advanced Topics

### Evolutionary Stability

**Definition:** A strategy is evolutionarily stable if no mutant strategy can invade

**Application:** Ensure RACI assignments resist "mutations" (agent defections)

### Repeated Games

**Extension:** Model long-term agent interactions with reputation

**Implementation:** Track cooperation history in audit trails

### Mechanism Design

**Optimal Incentives:** Design cooperation bonuses to align agent incentives with governance goals

**Current Implementation:**
- Responsible: +2.0 (strong incentive)
- Consulted: +0.5 (weak incentive)
- Can be tuned based on control criticality

---

## References

### Game Theory
- **Nash, J. (1950)** - "Equilibrium Points in N-Person Games", PNAS
- **Von Stackelberg, H. (1934)** - "Market Structure and Equilibrium"
- **Fudenberg & Tirole (1991)** - "Game Theory", MIT Press

### Mechanism Design
- **Hurwicz, L., Maskin, E., Myerson, R. (2007)** - Nobel Prize in Economics
- **Myerson, R. (1981)** - "Optimal Auction Design", Mathematics of Operations Research

### RAND Corp Critiques
- **Schelling, T. (1960)** - "The Strategy of Conflict" (critiques of classical game theory)
- **Simon, H. (1955)** - "A Behavioral Model of Rational Choice" (bounded rationality)

---

## Conclusion

Game-theoretic RACI validation provides **mathematical proof** of optimal governance:

✅ **RACI constraints** → Validated automatically
✅ **Conflicts** → Detected via overlapping strategies
✅ **Equilibrium** → Proven via Nash/Stackelberg analysis
✅ **Audit trail** → Cryptographic evidence

**Result:** Enforceable, optimal, and provably stable AI agent governance.

---

**Version:** 2.1
**Last Updated:** 2025-10-18
**Control Coverage:** APP-001, G-02, RACI-001
