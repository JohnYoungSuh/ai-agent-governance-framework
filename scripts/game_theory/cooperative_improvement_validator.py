#!/usr/bin/env python3
"""
Cooperative Game Theory - AI Agent Improvement Proposals
AI Agent Governance Framework v2.1
Control: APP-001, G-02, RACI-001, IMPROVE-001

Purpose: Validate AI agent improvement proposals using cooperative game theory
         Ensure Pareto improvements, truthful reporting, and human due diligence

Model: Cooperative Bargaining Game + Mechanism Design
- AI Agents: Propose improvements (efficiency, cost reduction, workflow optimization)
- Human Actors: Review and approve/reject with accountability
- Game Theory: Ensure truthful proposals, validate review diligence
- Objective: Continuous improvement without agent conflict

Theory:
- Pareto Efficiency: No agent worse off, at least one better off
- Truthful Reporting: VCG mechanism incentivizes honesty
- Review Validation: Statistical bounds on review time vs. complexity
"""

import json
import sys
import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib

# ANSI colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


class ProposalType(Enum):
    """Type of improvement proposal"""
    COST_REDUCTION = "cost_reduction"
    EFFICIENCY_GAIN = "efficiency_gain"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    RISK_MITIGATION = "risk_mitigation"
    COMPLIANCE_ENHANCEMENT = "compliance_enhancement"


class ReviewStatus(Enum):
    """Status of human review"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    INSUFFICIENT_REVIEW = "insufficient_review"


@dataclass
class ImprovementMetrics:
    """Quantifiable improvement metrics"""
    cost_savings_usd: float = 0.0
    time_savings_hours: float = 0.0
    quality_improvement_pct: float = 0.0
    risk_reduction_pct: float = 0.0
    compliance_score_delta: float = 0.0

    def is_pareto_improvement(self) -> bool:
        """Check if this is a Pareto improvement (all non-negative, at least one positive)"""
        metrics = [
            self.cost_savings_usd,
            self.time_savings_hours,
            self.quality_improvement_pct,
            self.risk_reduction_pct,
            self.compliance_score_delta
        ]
        return all(m >= 0 for m in metrics) and any(m > 0 for m in metrics)

    def total_value(self) -> float:
        """Calculate total value of improvement"""
        # Normalize to USD equivalent
        return (
            self.cost_savings_usd +
            self.time_savings_hours * 75.0 +  # $75/hour labor rate
            self.quality_improvement_pct * 100.0 +  # Quality value
            self.risk_reduction_pct * 500.0 +  # Risk avoidance value
            self.compliance_score_delta * 1000.0  # Compliance value
        )


@dataclass
class Proposal:
    """AI agent improvement proposal"""
    proposal_id: str
    agent_id: str
    agent_tier: int
    proposal_type: ProposalType
    title: str
    description: str
    current_state: str
    proposed_state: str
    metrics: ImprovementMetrics
    affected_controls: List[str]
    implementation_cost_usd: float
    implementation_time_hours: float
    risk_assessment: str
    submitted_at: datetime
    jira_cr_id: Optional[str] = None

    def net_benefit(self) -> float:
        """Calculate net benefit (benefit - cost)"""
        return self.metrics.total_value() - self.implementation_cost_usd

    def roi(self) -> float:
        """Calculate ROI"""
        if self.implementation_cost_usd == 0:
            return float('inf') if self.metrics.total_value() > 0 else 0.0
        return self.metrics.total_value() / self.implementation_cost_usd

    def complexity_score(self) -> float:
        """
        Estimate proposal complexity (0-100)
        Used to validate review time
        """
        score = 0.0

        # Affected controls complexity
        score += len(self.affected_controls) * 5.0

        # Implementation complexity
        score += min(self.implementation_time_hours, 40.0)

        # Cost complexity
        score += min(self.implementation_cost_usd / 100.0, 20.0)

        # Description length (proxy for complexity)
        score += min(len(self.description) / 100.0, 15.0)

        return min(score, 100.0)


@dataclass
class HumanReview:
    """Human review of proposal"""
    review_id: str
    reviewer_id: str
    reviewer_role: str  # "Change Manager", "Security Lead", etc.
    proposal_id: str
    status: ReviewStatus
    review_start_time: datetime
    review_end_time: Optional[datetime] = None
    review_duration_minutes: float = 0.0
    comments: str = ""
    approval_signature: Optional[str] = None
    concerns_raised: List[str] = field(default_factory=list)
    questions_asked: int = 0
    documents_reviewed: List[str] = field(default_factory=list)

    def calculate_duration(self):
        """Calculate review duration"""
        if self.review_end_time:
            delta = self.review_end_time - self.review_start_time
            self.review_duration_minutes = delta.total_seconds() / 60.0


@dataclass
class CooperativeGameState:
    """State of the cooperative game"""
    proposals: List[Proposal]
    reviews: List[HumanReview]
    approved_proposals: List[Proposal] = field(default_factory=list)
    rejected_proposals: List[Proposal] = field(default_factory=list)
    total_value_approved: float = 0.0
    total_cost_approved: float = 0.0
    agents_truthfulness_score: Dict[str, float] = field(default_factory=dict)


class CooperativeImprovementValidator:
    """Validator for cooperative improvement proposals"""

    # Statistical bounds for review validation
    MIN_REVIEW_MINUTES_PER_COMPLEXITY = 0.5  # 30 seconds per complexity point
    MAX_REVIEW_MINUTES_PER_COMPLEXITY = 3.0  # 3 minutes per complexity point

    def __init__(self):
        self.game_state = CooperativeGameState(proposals=[], reviews=[])

    def validate_pareto_improvement(self, proposal: Proposal) -> Tuple[bool, List[str]]:
        """
        Validate proposal is a Pareto improvement

        Pareto Criterion:
        1. No stakeholder is worse off
        2. At least one stakeholder is better off
        3. Net benefit > 0
        """
        issues = []

        # Check Pareto improvement
        if not proposal.metrics.is_pareto_improvement():
            issues.append(
                "Not a Pareto improvement: Some metrics are negative. "
                "All improvements must be non-negative."
            )

        # Check net benefit
        net_benefit = proposal.net_benefit()
        if net_benefit <= 0:
            issues.append(
                f"Negative net benefit: ${net_benefit:.2f}. "
                f"Benefits (${proposal.metrics.total_value():.2f}) must exceed "
                f"costs (${proposal.implementation_cost_usd:.2f})."
            )

        # Check ROI threshold
        roi = proposal.roi()
        if roi < 1.2:  # Require 20% ROI minimum
            issues.append(
                f"ROI too low: {roi:.2f}x. Minimum required: 1.2x (20% return). "
                "Proposal must demonstrate clear value."
            )

        return len(issues) == 0, issues

    def validate_truthful_reporting(self, proposal: Proposal,
                                    agent_history: List[Proposal]) -> Tuple[float, List[str]]:
        """
        Validate agent is reporting truthfully using VCG-like mechanism

        Truthfulness Score (0-1):
        - Historical accuracy of estimates
        - Consistency in reporting
        - Correlation with actual outcomes

        Returns: (truthfulness_score, warnings)
        """
        warnings = []
        score = 1.0

        if not agent_history:
            # New agent, give benefit of doubt with slight penalty
            score = 0.9
            warnings.append("New agent - limited history for truthfulness assessment")
            return score, warnings

        # Analyze historical accuracy
        cost_errors = []
        time_errors = []
        benefit_errors = []

        for past_proposal in agent_history:
            # Check if metrics were realistic (would need actual outcome data)
            # For now, check for consistency patterns

            # Flag suspiciously optimistic estimates
            if past_proposal.metrics.total_value() > 10000 and past_proposal.implementation_cost_usd < 100:
                cost_errors.append(past_proposal.proposal_id)

            if past_proposal.implementation_time_hours < 1 and past_proposal.metrics.time_savings_hours > 100:
                time_errors.append(past_proposal.proposal_id)

        # Penalize patterns of over-promising
        if len(cost_errors) > len(agent_history) * 0.3:
            score -= 0.2
            warnings.append(
                f"Pattern detected: Agent consistently underestimates costs "
                f"({len(cost_errors)}/{len(agent_history)} proposals)"
            )

        if len(time_errors) > len(agent_history) * 0.3:
            score -= 0.2
            warnings.append(
                f"Pattern detected: Agent consistently overestimates benefits "
                f"({len(time_errors)}/{len(agent_history)} proposals)"
            )

        # Check current proposal for red flags
        if proposal.metrics.total_value() > 50000 and proposal.implementation_cost_usd < 500:
            score -= 0.1
            warnings.append(
                "Red flag: Claimed benefits (${:.2f}) seem disproportionate to costs (${:.2f})".format(
                    proposal.metrics.total_value(), proposal.implementation_cost_usd
                )
            )

        return max(score, 0.0), warnings

    def validate_review_diligence(self, proposal: Proposal, review: HumanReview) -> Tuple[bool, List[str]]:
        """
        Validate human reviewer performed due diligence

        Statistical Validation:
        1. Review time proportional to complexity
        2. Sufficient questions asked
        3. Documents reviewed
        4. Comments substantive (not rubber-stamp)
        """
        issues = []

        complexity = proposal.complexity_score()

        # Minimum review time based on complexity
        min_expected_minutes = complexity * self.MIN_REVIEW_MINUTES_PER_COMPLEXITY
        max_expected_minutes = complexity * self.MAX_REVIEW_MINUTES_PER_COMPLEXITY

        review_time = review.review_duration_minutes

        # Check if review time is suspiciously short
        if review_time < min_expected_minutes:
            issues.append(
                f"Review time too short: {review_time:.1f} minutes for complexity {complexity:.0f}. "
                f"Expected minimum: {min_expected_minutes:.1f} minutes. "
                f"Possible rubber-stamp approval without due diligence."
            )

        # Check if review time is suspiciously long (possible review avoidance)
        if review_time > max_expected_minutes * 2:
            issues.append(
                f"Review time excessively long: {review_time:.1f} minutes for complexity {complexity:.0f}. "
                f"Expected maximum: {max_expected_minutes:.1f} minutes. "
                f"Possible review abandonment or lack of focus."
            )

        # Require comments for approvals
        if review.status == ReviewStatus.APPROVED and len(review.comments) < 50:
            issues.append(
                f"Insufficient review comments: {len(review.comments)} characters. "
                "Approvals require substantive explanation (minimum 50 characters)."
            )

        # Require concerns for rejections
        if review.status == ReviewStatus.REJECTED and not review.concerns_raised:
            issues.append(
                "No concerns documented for rejection. "
                "Rejections must specify reasons."
            )

        # Check for engagement markers
        engagement_score = 0
        if review.questions_asked > 0:
            engagement_score += 1
        if len(review.documents_reviewed) > 0:
            engagement_score += 1
        if len(review.comments) > 100:
            engagement_score += 1
        if review.concerns_raised:
            engagement_score += 1

        if engagement_score < 2:
            issues.append(
                f"Low engagement score: {engagement_score}/4. "
                "Review shows insufficient due diligence markers "
                "(questions, documents, comments, concerns)."
            )

        return len(issues) == 0, issues

    def calculate_social_welfare(self, proposals: List[Proposal]) -> float:
        """
        Calculate social welfare (total value to all stakeholders)

        Cooperative game objective: Maximize social welfare
        """
        total_welfare = 0.0
        for proposal in proposals:
            total_welfare += proposal.net_benefit()
        return total_welfare

    def find_pareto_optimal_set(self, proposals: List[Proposal],
                               budget_constraint: float) -> List[Proposal]:
        """
        Find Pareto optimal set of proposals within budget

        This is a cooperative optimization:
        - Maximize total social welfare
        - Subject to budget constraint
        - Ensure all proposals are Pareto improvements
        """
        # Filter to only valid Pareto improvements
        valid_proposals = []
        for p in proposals:
            is_valid, _ = self.validate_pareto_improvement(p)
            if is_valid:
                valid_proposals.append(p)

        # Sort by ROI (greedy approximation to knapsack)
        sorted_proposals = sorted(valid_proposals, key=lambda p: p.roi(), reverse=True)

        # Select proposals within budget
        selected = []
        remaining_budget = budget_constraint

        for proposal in sorted_proposals:
            if proposal.implementation_cost_usd <= remaining_budget:
                selected.append(proposal)
                remaining_budget -= proposal.implementation_cost_usd

        return selected

    def generate_improvement_audit_trail(self, proposal: Proposal, review: HumanReview,
                                        is_approved: bool, validation_results: Dict) -> Dict:
        """Generate audit trail for improvement proposal"""
        audit_id = f"audit-improve-{int(datetime.utcnow().timestamp())}"

        return {
            "audit_id": audit_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actor": review.reviewer_id,
            "action": "improvement_proposal_review",
            "workflow_step": "IMPROVE-001",
            "jira_reference": {
                "cr_id": proposal.jira_cr_id or "N/A",
                "approver_role": review.reviewer_role,
                "controls": proposal.affected_controls
            },
            "inputs": {
                "proposal_id": proposal.proposal_id,
                "agent_id": proposal.agent_id,
                "agent_tier": proposal.agent_tier,
                "proposal_type": proposal.proposal_type.value,
                "complexity_score": proposal.complexity_score(),
                "net_benefit_usd": proposal.net_benefit(),
                "roi": proposal.roi()
            },
            "outputs": {
                "review_status": review.status.value,
                "review_duration_minutes": review.review_duration_minutes,
                "due_diligence_validated": validation_results["due_diligence"],
                "pareto_improvement": validation_results["pareto"],
                "truthfulness_score": validation_results["truthfulness"],
                "approved": is_approved
            },
            "policy_controls_checked": ["APP-001", "G-02", "RACI-001", "IMPROVE-001"],
            "compliance_result": "pass" if validation_results["all_valid"] else "fail",
            "evidence_hash": f"sha256:{hashlib.sha256(str(proposal.__dict__).encode()).hexdigest()}",
            "auditor_agent": "cooperative-improvement-validator"
        }


def main():
    """Main entry point - demonstration"""
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}")
    print(f"{Colors.CYAN}Cooperative Game Theory - AI Agent Improvement Proposals{Colors.NC}")
    print(f"{Colors.CYAN}AI Agent Governance Framework v2.1{Colors.NC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}\n")

    validator = CooperativeImprovementValidator()

    # Example: AI agent proposes cost reduction
    proposal = Proposal(
        proposal_id="PROP-2025-001",
        agent_id="ops-agent",
        agent_tier=3,
        proposal_type=ProposalType.COST_REDUCTION,
        title="Optimize Lambda memory configuration",
        description=(
            "Analysis shows Lambda functions are over-provisioned with 3GB memory "
            "but only using 512MB average. Propose reducing to 1GB, resulting in "
            "50% cost savings with no performance impact. Tested in dev environment "
            "with 1000+ invocations showing identical performance profile."
        ),
        current_state="Lambda functions: 3GB memory, $250/month",
        proposed_state="Lambda functions: 1GB memory, $125/month",
        metrics=ImprovementMetrics(
            cost_savings_usd=125.0,  # Monthly savings
            time_savings_hours=0.0,
            quality_improvement_pct=0.0,
            risk_reduction_pct=5.0,  # Lower resource usage = lower risk
            compliance_score_delta=0.0
        ),
        affected_controls=["MI-009", "MI-021"],
        implementation_cost_usd=50.0,  # Terraform change + testing
        implementation_time_hours=2.0,
        risk_assessment="Low - tested in dev, gradual rollout planned",
        submitted_at=datetime.utcnow()
    )

    # Human review (simulated)
    review = HumanReview(
        review_id="REV-2025-001",
        reviewer_id="change-manager@company.com",
        reviewer_role="Change Manager",
        proposal_id=proposal.proposal_id,
        status=ReviewStatus.APPROVED,
        review_start_time=datetime.utcnow() - timedelta(minutes=25),
        review_end_time=datetime.utcnow(),
        comments=(
            "Reviewed proposal thoroughly. Verified test results in dev environment. "
            "Cost savings projection validated against CloudWatch metrics. "
            "Rollout plan includes canary deployment with rollback capability. "
            "Approved for implementation."
        ),
        questions_asked=3,
        documents_reviewed=["cloudwatch-metrics.pdf", "test-results.json"],
        approval_signature="sha256:abc123..."
    )
    review.calculate_duration()

    print(f"{Colors.MAGENTA}Proposal Details:{Colors.NC}")
    print(f"  ID: {proposal.proposal_id}")
    print(f"  Agent: {proposal.agent_id} (Tier {proposal.agent_tier})")
    print(f"  Type: {proposal.proposal_type.value}")
    print(f"  Title: {proposal.title}")
    print(f"  Complexity: {proposal.complexity_score():.0f}/100")
    print()

    print(f"{Colors.MAGENTA}Step 1: Validating Pareto Improvement{Colors.NC}")
    print("-" * 70)
    is_pareto, pareto_issues = validator.validate_pareto_improvement(proposal)

    if is_pareto:
        print(f"{Colors.GREEN}✅ Valid Pareto improvement{Colors.NC}")
        print(f"   Net Benefit: ${proposal.net_benefit():.2f}")
        print(f"   ROI: {proposal.roi():.2f}x")
        print(f"   Total Value: ${proposal.metrics.total_value():.2f}")
    else:
        print(f"{Colors.RED}❌ Not a Pareto improvement:{Colors.NC}")
        for issue in pareto_issues:
            print(f"   • {issue}")
    print()

    print(f"{Colors.MAGENTA}Step 2: Validating Truthful Reporting{Colors.NC}")
    print("-" * 70)
    agent_history = []  # Empty for demo
    truthfulness, truth_warnings = validator.validate_truthful_reporting(proposal, agent_history)

    print(f"Truthfulness Score: {Colors.GREEN if truthfulness > 0.8 else Colors.YELLOW}{truthfulness:.2f}/1.00{Colors.NC}")
    if truth_warnings:
        for warning in truth_warnings:
            print(f"   ⚠️  {warning}")
    else:
        print(f"   {Colors.GREEN}No concerns detected{Colors.NC}")
    print()

    print(f"{Colors.MAGENTA}Step 3: Validating Human Review Diligence{Colors.NC}")
    print("-" * 70)
    print(f"Reviewer: {review.reviewer_id} ({review.reviewer_role})")
    print(f"Review Duration: {review.review_duration_minutes:.1f} minutes")
    print(f"Expected Range: {proposal.complexity_score() * 0.5:.1f}-{proposal.complexity_score() * 3.0:.1f} minutes")
    print()

    is_diligent, diligence_issues = validator.validate_review_diligence(proposal, review)

    if is_diligent:
        print(f"{Colors.GREEN}✅ Due diligence validated{Colors.NC}")
        print(f"   Questions Asked: {review.questions_asked}")
        print(f"   Documents Reviewed: {len(review.documents_reviewed)}")
        print(f"   Comment Length: {len(review.comments)} characters")
    else:
        print(f"{Colors.RED}❌ Insufficient due diligence:{Colors.NC}")
        for issue in diligence_issues:
            print(f"   • {issue}")
    print()

    # Generate audit trail
    validation_results = {
        "pareto": is_pareto,
        "truthfulness": truthfulness,
        "due_diligence": is_diligent,
        "all_valid": is_pareto and truthfulness > 0.7 and is_diligent
    }

    audit_trail = validator.generate_improvement_audit_trail(
        proposal, review, review.status == ReviewStatus.APPROVED, validation_results
    )

    audit_file = f"/tmp/{audit_trail['audit_id']}.json"
    with open(audit_file, 'w') as f:
        json.dump(audit_trail, f, indent=2)

    print(f"{Colors.MAGENTA}Step 4: Audit Trail Generated{Colors.NC}")
    print("-" * 70)
    print(f"Audit ID: {audit_trail['audit_id']}")
    print(f"File: {audit_file}")
    print(f"Status: {review.status.value}")
    print()

    # Summary
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}")
    print(f"{Colors.CYAN}Summary{Colors.NC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}")
    print(f"Pareto Improvement: {Colors.GREEN if is_pareto else Colors.RED}{'YES' if is_pareto else 'NO'}{Colors.NC}")
    print(f"Truthfulness Score: {Colors.GREEN if truthfulness > 0.8 else Colors.YELLOW}{truthfulness:.2f}{Colors.NC}")
    print(f"Due Diligence: {Colors.GREEN if is_diligent else Colors.RED}{'PASS' if is_diligent else 'FAIL'}{Colors.NC}")
    print(f"Overall: {Colors.GREEN if validation_results['all_valid'] else Colors.RED}{'APPROVED' if validation_results['all_valid'] else 'REJECTED'}{Colors.NC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}\n")

    return 0 if validation_results['all_valid'] else 1


if __name__ == "__main__":
    sys.exit(main())
