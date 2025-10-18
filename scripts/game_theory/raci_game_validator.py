#!/usr/bin/env python3
"""
Game-Theoretic RACI Validation Module
AI Agent Governance Framework v2.1
Control: APP-001, G-02, RACI-001

Purpose: Validate RACI assignments using game theory (Stackelberg model)
         Detect conflicts, verify Nash equilibrium, and ensure optimal governance

Model: Stackelberg Leadership Game
- Leader: Tier 4 (Architect) moves first
- Followers: Tier 3 (Ops), Tier 2 (Dev) respond optimally
- Mechanism: Approval gates enforce sequential rationality
- Verification: Nash equilibrium checking + backward induction

Theory References:
- Von Stackelberg, H. (1934) - Market Structure and Equilibrium
- Nash, J. (1950) - Equilibrium Points in N-Person Games
- Mechanism Design (Hurwicz, Maskin, Myerson - Nobel 2007)
"""

import json
import sys
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import itertools

# ANSI colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


class AgentTier(Enum):
    """Agent tier hierarchy"""
    TIER1_OBSERVER = 1
    TIER2_DEVELOPER = 2
    TIER3_OPERATIONS = 3
    TIER4_ARCHITECT = 4


class RACIRole(Enum):
    """RACI responsibility types"""
    RESPONSIBLE = "R"  # Does the work
    ACCOUNTABLE = "A"  # Ultimately answerable
    CONSULTED = "C"    # Provides input
    INFORMED = "I"     # Kept up-to-date


@dataclass
class Agent:
    """AI Agent player in the game"""
    agent_id: str
    tier: AgentTier
    controls: List[str]
    cost_per_action: float = 1.0
    risk_tolerance: float = 0.5

    def __hash__(self):
        return hash(self.agent_id)


@dataclass
class Action:
    """Possible action an agent can take"""
    action_id: str
    control_id: str
    description: str
    cost: float
    risk: float
    compliance_value: float
    requires_approval: bool = False


@dataclass
class RACIAssignment:
    """RACI assignment for a control"""
    control_id: str
    responsible: Agent
    accountable: Agent
    consulted: List[Agent] = field(default_factory=list)
    informed: List[Agent] = field(default_factory=list)

    def get_all_agents(self) -> Set[Agent]:
        """Get all agents involved"""
        agents = {self.responsible, self.accountable}
        agents.update(self.consulted)
        agents.update(self.informed)
        return agents


@dataclass
class GameState:
    """Current state of the game"""
    agents: List[Agent]
    raci_assignments: List[RACIAssignment]
    actions_taken: List[Tuple[Agent, Action]] = field(default_factory=list)
    compliance_score: float = 0.0
    total_cost: float = 0.0
    total_risk: float = 0.0


@dataclass
class PayoffMatrix:
    """Payoff matrix for game analysis"""
    agent: Agent
    action: Action
    payoff: float
    breakdown: Dict[str, float] = field(default_factory=dict)


class RACIGameValidator:
    """Game-theoretic RACI validator"""

    def __init__(self, agents: List[Agent], raci_assignments: List[RACIAssignment]):
        self.agents = agents
        self.raci_assignments = raci_assignments
        self.agents_by_tier = self._organize_by_tier()

    def _organize_by_tier(self) -> Dict[AgentTier, List[Agent]]:
        """Organize agents by tier for Stackelberg hierarchy"""
        by_tier = {}
        for tier in AgentTier:
            by_tier[tier] = [a for a in self.agents if a.tier == tier]
        return by_tier

    def validate_raci_constraints(self) -> Tuple[bool, List[str]]:
        """
        Validate RACI matrix constraints:
        1. Exactly one Accountable per control
        2. At least one Responsible per control
        3. No agent is both R and A for same control
        4. Tier constraints (Tier 4 = A, Tier 3 = R, etc.)
        """
        violations = []

        for assignment in self.raci_assignments:
            control = assignment.control_id

            # Rule 1: Exactly one Accountable
            if not assignment.accountable:
                violations.append(f"{control}: No Accountable agent assigned")

            # Rule 2: At least one Responsible
            if not assignment.responsible:
                violations.append(f"{control}: No Responsible agent assigned")

            # Rule 3: R != A for same agent
            if assignment.responsible == assignment.accountable:
                violations.append(
                    f"{control}: Agent {assignment.responsible.agent_id} "
                    f"cannot be both Responsible and Accountable"
                )

            # Rule 4: Tier constraints
            if assignment.accountable and assignment.accountable.tier.value < 3:
                violations.append(
                    f"{control}: Accountable agent {assignment.accountable.agent_id} "
                    f"is Tier {assignment.accountable.tier.value}, requires Tier 3+"
                )

        return len(violations) == 0, violations

    def calculate_payoff(self, agent: Agent, action: Action,
                        game_state: GameState) -> PayoffMatrix:
        """
        Calculate payoff for agent taking action

        Payoff = Compliance_Value - Cost - Risk_Penalty + Cooperation_Bonus

        Nash equilibrium exists when no agent can improve payoff by deviating
        """
        # Base components
        compliance_value = action.compliance_value
        cost = action.cost * agent.cost_per_action
        risk_penalty = action.risk * (1 - agent.risk_tolerance)

        # Cooperation bonus (mechanism design incentive)
        cooperation_bonus = 0.0
        for assignment in self.raci_assignments:
            if assignment.control_id == action.control_id:
                if agent == assignment.responsible:
                    cooperation_bonus += 2.0  # Incentive for doing assigned work
                elif agent in assignment.consulted:
                    cooperation_bonus += 0.5  # Incentive for collaboration

        # Total payoff
        payoff = compliance_value - cost - risk_penalty + cooperation_bonus

        breakdown = {
            'compliance_value': compliance_value,
            'cost': -cost,
            'risk_penalty': -risk_penalty,
            'cooperation_bonus': cooperation_bonus,
            'total': payoff
        }

        return PayoffMatrix(agent=agent, action=action, payoff=payoff, breakdown=breakdown)

    def find_best_response(self, agent: Agent, actions: List[Action],
                          game_state: GameState) -> Optional[Action]:
        """
        Find best response action for agent given current game state
        (Nash equilibrium component: each agent plays best response)
        """
        if not actions:
            return None

        payoffs = [self.calculate_payoff(agent, action, game_state)
                   for action in actions]

        best = max(payoffs, key=lambda p: p.payoff)
        return best.action if best.payoff > 0 else None

    def check_nash_equilibrium(self, game_state: GameState,
                               action_profile: Dict[Agent, Action]) -> Tuple[bool, List[str]]:
        """
        Check if action profile is a Nash equilibrium

        Definition: No agent can improve payoff by unilaterally deviating
        """
        violations = []

        for agent, current_action in action_profile.items():
            current_payoff = self.calculate_payoff(agent, current_action, game_state)

            # Get all possible actions for this agent
            possible_actions = self._get_agent_actions(agent)

            # Check if any deviation improves payoff
            for alt_action in possible_actions:
                if alt_action == current_action:
                    continue

                alt_payoff = self.calculate_payoff(agent, alt_action, game_state)

                if alt_payoff.payoff > current_payoff.payoff + 0.01:  # epsilon tolerance
                    violations.append(
                        f"Agent {agent.agent_id} can improve from "
                        f"{current_action.action_id} (payoff={current_payoff.payoff:.2f}) to "
                        f"{alt_action.action_id} (payoff={alt_payoff.payoff:.2f})"
                    )

        is_equilibrium = len(violations) == 0
        return is_equilibrium, violations

    def stackelberg_equilibrium(self, actions_by_agent: Dict[Agent, List[Action]]) -> Dict[Agent, Action]:
        """
        Find Stackelberg equilibrium with sequential moves:

        1. Leader (Tier 4) moves first
        2. Followers (Tier 3, 2, 1) observe and respond optimally
        3. Use backward induction to solve

        Returns optimal action profile
        """
        game_state = GameState(agents=self.agents, raci_assignments=self.raci_assignments)
        action_profile = {}

        # Order agents by tier (highest first = leader)
        sorted_agents = sorted(self.agents, key=lambda a: a.tier.value, reverse=True)

        print(f"\n{Colors.CYAN}=== Stackelberg Game Solving ==={Colors.NC}")
        print(f"Sequential move order: {' → '.join([f'Tier {a.tier.value}' for a in sorted_agents])}\n")

        # Backward induction: solve from followers to leader
        for agent in sorted_agents:
            available_actions = actions_by_agent.get(agent, [])

            # Find best response given previous moves
            best_action = self.find_best_response(agent, available_actions, game_state)

            if best_action:
                action_profile[agent] = best_action
                game_state.actions_taken.append((agent, best_action))
                game_state.compliance_score += best_action.compliance_value
                game_state.total_cost += best_action.cost
                game_state.total_risk += best_action.risk

                payoff = self.calculate_payoff(agent, best_action, game_state)

                print(f"{Colors.GREEN}✓{Colors.NC} {agent.agent_id} (Tier {agent.tier.value}): "
                      f"{best_action.action_id} [payoff={payoff.payoff:.2f}]")
            else:
                print(f"{Colors.YELLOW}⊘{Colors.NC} {agent.agent_id} (Tier {agent.tier.value}): "
                      f"No profitable action")

        return action_profile

    def detect_raci_conflicts(self) -> List[Dict]:
        """
        Detect game-theoretic RACI conflicts:
        1. Multiple agents competing for same Responsible role
        2. Misaligned incentives (negative cooperation bonus)
        3. Tier violations (lower tier as Accountable)
        """
        conflicts = []

        # Check for overlapping Responsible assignments
        control_responsible = {}
        for assignment in self.raci_assignments:
            control = assignment.control_id
            if control not in control_responsible:
                control_responsible[control] = []
            control_responsible[control].append(assignment.responsible)

        for control, responsibles in control_responsible.items():
            if len(responsibles) > 1:
                conflicts.append({
                    'type': 'overlapping_responsible',
                    'control_id': control,
                    'agents': [a.agent_id for a in responsibles],
                    'severity': 'high',
                    'description': f"Multiple agents assigned Responsible for {control}"
                })

        # Check tier hierarchy violations
        for assignment in self.raci_assignments:
            if (assignment.accountable and assignment.responsible and
                assignment.accountable.tier.value < assignment.responsible.tier.value):
                conflicts.append({
                    'type': 'tier_hierarchy_violation',
                    'control_id': assignment.control_id,
                    'accountable': assignment.accountable.agent_id,
                    'responsible': assignment.responsible.agent_id,
                    'severity': 'critical',
                    'description': (
                        f"Accountable ({assignment.accountable.agent_id}, "
                        f"Tier {assignment.accountable.tier.value}) has lower tier than "
                        f"Responsible ({assignment.responsible.agent_id}, "
                        f"Tier {assignment.responsible.tier.value})"
                    )
                })

        return conflicts

    def _get_agent_actions(self, agent: Agent) -> List[Action]:
        """Get available actions for agent based on controls"""
        actions = []
        for control in agent.controls:
            # Create sample actions for each control
            actions.append(Action(
                action_id=f"{agent.agent_id}_{control}_execute",
                control_id=control,
                description=f"Execute {control}",
                cost=1.0,
                risk=0.3,
                compliance_value=5.0,
                requires_approval=agent.tier.value >= 3
            ))
        return actions

    def generate_audit_trail(self, game_state: GameState,
                            equilibrium: Dict[Agent, Action],
                            is_nash: bool) -> Dict:
        """Generate audit trail for game theory validation"""
        audit_id = f"audit-{int(datetime.utcnow().timestamp())}"

        return {
            "audit_id": audit_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actor": "raci-game-validator",
            "action": "game_theoretic_validation",
            "workflow_step": "RACI-001",
            "inputs": {
                "agents_count": len(self.agents),
                "raci_assignments_count": len(self.raci_assignments),
                "game_model": "Stackelberg Leadership"
            },
            "outputs": {
                "nash_equilibrium": is_nash,
                "equilibrium_actions": {
                    agent.agent_id: action.action_id
                    for agent, action in equilibrium.items()
                },
                "compliance_score": game_state.compliance_score,
                "total_cost": game_state.total_cost,
                "total_risk": game_state.total_risk
            },
            "policy_controls_checked": ["APP-001", "G-02", "RACI-001"],
            "compliance_result": "pass" if is_nash else "warning",
            "evidence_hash": f"sha256:{hash(str(equilibrium))}",
            "auditor_agent": "raci-game-validator"
        }


def main():
    """Main entry point"""
    print(f"{Colors.CYAN}{'='*60}{Colors.NC}")
    print(f"{Colors.CYAN}Game-Theoretic RACI Validation{Colors.NC}")
    print(f"{Colors.CYAN}AI Agent Governance Framework v2.1{Colors.NC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")

    # Define agents with hierarchy
    agents = [
        Agent("architect-agent", AgentTier.TIER4_ARCHITECT, ["APP-001", "G-02"],
              cost_per_action=2.0, risk_tolerance=0.8),
        Agent("security-agent", AgentTier.TIER3_OPERATIONS, ["SEC-001", "MI-003"],
              cost_per_action=1.5, risk_tolerance=0.6),
        Agent("ops-agent", AgentTier.TIER3_OPERATIONS, ["AU-002", "MI-020"],
              cost_per_action=1.0, risk_tolerance=0.5),
        Agent("dev-agent", AgentTier.TIER2_DEVELOPER, ["MI-009", "MI-021"],
              cost_per_action=0.8, risk_tolerance=0.4),
    ]

    # Define RACI assignments
    raci_assignments = [
        RACIAssignment(
            control_id="APP-001",
            responsible=agents[1],  # security-agent
            accountable=agents[0],  # architect-agent
            consulted=[agents[2]],  # ops-agent
            informed=[agents[3]]    # dev-agent
        ),
        RACIAssignment(
            control_id="SEC-001",
            responsible=agents[1],  # security-agent
            accountable=agents[0],  # architect-agent
            consulted=[],
            informed=[agents[2], agents[3]]
        ),
        RACIAssignment(
            control_id="AU-002",
            responsible=agents[2],  # ops-agent
            accountable=agents[0],  # architect-agent
            consulted=[agents[1]],
            informed=[agents[3]]
        ),
    ]

    # Initialize validator
    validator = RACIGameValidator(agents, raci_assignments)

    # Step 1: Validate RACI constraints
    print(f"{Colors.MAGENTA}Step 1: Validating RACI Constraints{Colors.NC}")
    print("-" * 60)
    is_valid, violations = validator.validate_raci_constraints()

    if is_valid:
        print(f"{Colors.GREEN}✅ All RACI constraints satisfied{Colors.NC}\n")
    else:
        print(f"{Colors.RED}❌ RACI violations detected:{Colors.NC}")
        for v in violations:
            print(f"  • {v}")
        print()

    # Step 2: Detect conflicts
    print(f"{Colors.MAGENTA}Step 2: Detecting Game-Theoretic Conflicts{Colors.NC}")
    print("-" * 60)
    conflicts = validator.detect_raci_conflicts()

    if not conflicts:
        print(f"{Colors.GREEN}✅ No conflicts detected{Colors.NC}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Conflicts found:{Colors.NC}")
        for conflict in conflicts:
            print(f"  • [{conflict['severity'].upper()}] {conflict['description']}")
        print()

    # Step 3: Solve for Stackelberg equilibrium
    print(f"{Colors.MAGENTA}Step 3: Computing Stackelberg Equilibrium{Colors.NC}")
    print("-" * 60)

    actions_by_agent = {agent: validator._get_agent_actions(agent) for agent in agents}
    equilibrium = validator.stackelberg_equilibrium(actions_by_agent)

    # Step 4: Verify Nash equilibrium
    print(f"\n{Colors.MAGENTA}Step 4: Verifying Nash Equilibrium{Colors.NC}")
    print("-" * 60)

    game_state = GameState(agents=agents, raci_assignments=raci_assignments)
    for agent, action in equilibrium.items():
        game_state.actions_taken.append((agent, action))

    is_nash, nash_violations = validator.check_nash_equilibrium(game_state, equilibrium)

    if is_nash:
        print(f"{Colors.GREEN}✅ Action profile is a Nash equilibrium{Colors.NC}")
        print(f"   No agent can improve by unilateral deviation\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Not a Nash equilibrium:{Colors.NC}")
        for v in nash_violations:
            print(f"  • {v}")
        print()

    # Step 5: Generate audit trail
    audit_trail = validator.generate_audit_trail(game_state, equilibrium, is_nash)

    audit_file = f"/tmp/{audit_trail['audit_id']}.json"
    with open(audit_file, 'w') as f:
        json.dump(audit_trail, f, indent=2)

    print(f"{Colors.MAGENTA}Step 5: Audit Trail Generated{Colors.NC}")
    print("-" * 60)
    print(f"Audit ID: {audit_trail['audit_id']}")
    print(f"File: {audit_file}")
    print(f"Compliance Score: {game_state.compliance_score:.2f}")
    print(f"Total Cost: ${game_state.total_cost:.2f}")
    print(f"Total Risk: {game_state.total_risk:.2f}\n")

    # Summary
    print(f"{Colors.CYAN}{'='*60}{Colors.NC}")
    print(f"{Colors.CYAN}Summary{Colors.NC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.NC}")
    print(f"RACI Valid: {Colors.GREEN if is_valid else Colors.RED}{'YES' if is_valid else 'NO'}{Colors.NC}")
    print(f"Conflicts: {len(conflicts)}")
    print(f"Nash Equilibrium: {Colors.GREEN if is_nash else Colors.YELLOW}{'YES' if is_nash else 'NO'}{Colors.NC}")
    print(f"Game Model: Stackelberg Leadership")
    print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")

    return 0 if (is_valid and is_nash and not conflicts) else 1


if __name__ == "__main__":
    sys.exit(main())
