#!/usr/bin/env python3
"""
Shared Utilities for AI Agent Governance Framework

This module provides common functionality used across multiple scripts,
eliminating code duplication and ensuring consistency.

SINGLE SOURCE OF TRUTH: frameworks/governance-framework.yaml
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class GovernanceFramework:
    """Loads and provides access to governance framework configuration."""

    def __init__(self, framework_path: Optional[Path] = None):
        """
        Initialize governance framework loader.

        Args:
            framework_path: Path to governance-framework.yaml
                          If None, auto-detects from script location
        """
        if framework_path is None:
            # Auto-detect: assuming script is in scripts/, framework is in frameworks/
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            framework_path = project_root / "frameworks" / "governance-framework.yaml"

        self.framework_path = framework_path
        self._config = None
        self._load_framework()

    def _load_framework(self):
        """Load governance framework from YAML file."""
        try:
            with open(self.framework_path, 'r') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Governance framework not found at {self.framework_path}. "
                f"Ensure frameworks/governance-framework.yaml exists."
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in governance framework: {e}")

    @property
    def config(self) -> Dict:
        """Get full configuration dictionary."""
        return self._config

    def get_strategic_goals(self) -> List[Dict]:
        """
        Get list of strategic goals.

        Returns:
            List of dictionaries with keys: id, name, description, weight
        """
        return self._config.get('strategic_goals', [])

    def get_strategic_goal_names(self) -> List[str]:
        """Get list of strategic goal names only."""
        return [goal['name'] for goal in self.get_strategic_goals()]

    def get_revenue_impact_types(self) -> List[Dict]:
        """
        Get list of revenue impact types.

        Returns:
            List of dictionaries with keys: id, name, description, scoring_multiplier
        """
        return self._config.get('revenue_impact_types', [])

    def get_revenue_impact_names(self) -> List[str]:
        """Get list of revenue impact type names only."""
        return [rt['name'] for rt in self.get_revenue_impact_types()]

    def get_approval_tiers(self) -> List[Dict]:
        """
        Get approval tier definitions.

        Returns:
            List of tier dictionaries with budget ranges and requirements
        """
        return self._config.get('approval_tiers', [])

    def get_approval_tier_for_budget(self, budget: float) -> Dict:
        """
        Determine which approval tier applies for a given budget.

        Args:
            budget: Budget amount in USD

        Returns:
            Dictionary with tier information
        """
        tiers = self.get_approval_tiers()
        for tier in tiers:
            tier_min = tier['budget_range']['min']
            tier_max = tier['budget_range']['max']

            if tier_max is None:  # Unlimited upper bound
                if budget >= tier_min:
                    return tier
            elif tier_min <= budget <= tier_max:
                return tier

        # Default to highest tier if not found
        return tiers[-1] if tiers else {}

    def get_evaluation_criteria(self) -> Dict:
        """
        Get evaluation criteria with weights and thresholds.

        Returns:
            Dictionary of evaluation criteria
        """
        return self._config.get('evaluation_criteria', {})

    def get_overall_threshold(self) -> int:
        """Get overall approval threshold score."""
        return self._config.get('overall_approval_threshold', 70)

    def get_roi_benchmarks(self) -> Dict:
        """Get ROI calculation benchmarks."""
        return self._config.get('roi_benchmarks', {})

    def get_token_budgets(self) -> Dict:
        """Get token accountability budgets by environment."""
        return self._config.get('token_accountability', {}).get('budgets', {})

    def get_devcontainer_standards(self) -> Dict:
        """Get devcontainer configuration standards."""
        return self._config.get('devcontainer_standards', {})

    def get_agent_tiers(self) -> Dict:
        """Get agent classification tiers."""
        return self._config.get('agent_tiers', {})


class ROICalculator:
    """Consolidated ROI calculation logic."""

    def __init__(self, framework: Optional[GovernanceFramework] = None):
        """
        Initialize ROI calculator.

        Args:
            framework: GovernanceFramework instance
                      If None, creates new instance
        """
        self.framework = framework or GovernanceFramework()

    def calculate_roi_percentage(
        self,
        estimated_benefit: float,
        estimated_cost: float
    ) -> float:
        """
        Calculate ROI as a percentage.

        Formula: ((Benefit - Cost) / Cost) * 100

        Args:
            estimated_benefit: Expected benefit in USD
            estimated_cost: Total cost in USD

        Returns:
            ROI percentage (can be negative)
        """
        if estimated_cost == 0:
            return 0.0 if estimated_benefit == 0 else float('inf')

        roi = ((estimated_benefit - estimated_cost) / estimated_cost) * 100
        return round(roi, 2)

    def calculate_payback_period(
        self,
        estimated_cost: float,
        monthly_benefit: float
    ) -> float:
        """
        Calculate payback period in months.

        Args:
            estimated_cost: Total initial cost
            monthly_benefit: Expected monthly benefit

        Returns:
            Number of months to break even
        """
        if monthly_benefit <= 0:
            return float('inf')

        return round(estimated_cost / monthly_benefit, 1)

    def score_roi(self, roi_percentage: float) -> Tuple[int, str]:
        """
        Score ROI based on benchmarks from governance framework.

        Args:
            roi_percentage: ROI as percentage

        Returns:
            Tuple of (score, category)
        """
        benchmarks = self.framework.get_roi_benchmarks()

        # Sort benchmarks by min_roi_percentage descending
        sorted_benchmarks = sorted(
            benchmarks.items(),
            key=lambda x: x[1].get('min_roi_percentage', 0),
            reverse=True
        )

        for category, benchmark in sorted_benchmarks:
            if roi_percentage >= benchmark.get('min_roi_percentage', 0):
                return benchmark.get('score', 50), category

        # Default to lowest score
        return 20, 'negative'

    def score_payback_period(self, payback_months: float) -> Tuple[int, str]:
        """
        Score payback period based on benchmarks.

        Args:
            payback_months: Payback period in months

        Returns:
            Tuple of (bonus_score, category)
        """
        payback_config = self.framework.config.get('roi_benchmarks', {}).get('payback_period', {})

        if payback_months <= 6:
            return 15, 'fast'
        elif payback_months <= 12:
            return 10, 'moderate'
        elif payback_months <= 24:
            return 5, 'slow'
        else:
            return 0, 'very_slow'

    def calculate_financial_viability_score(
        self,
        estimated_cost: float,
        estimated_benefit: float,
        monthly_benefit: float,
        revenue_impact_type: Optional[str] = None
    ) -> Dict:
        """
        Calculate comprehensive financial viability score.

        Args:
            estimated_cost: Total cost in USD
            estimated_benefit: Total expected benefit in USD
            monthly_benefit: Monthly recurring benefit in USD
            revenue_impact_type: Type of revenue impact (optional)

        Returns:
            Dictionary with scores and details
        """
        # Calculate ROI
        roi_percentage = self.calculate_roi_percentage(estimated_benefit, estimated_cost)
        roi_score, roi_category = self.score_roi(roi_percentage)

        # Calculate payback period
        payback_months = self.calculate_payback_period(estimated_cost, monthly_benefit)
        payback_bonus, payback_category = self.score_payback_period(payback_months)

        # Apply revenue impact multiplier if provided
        multiplier = 1.0
        if revenue_impact_type:
            revenue_types = self.framework.get_revenue_impact_types()
            for rt in revenue_types:
                if rt['name'] == revenue_impact_type or rt['id'] == revenue_impact_type:
                    multiplier = rt.get('scoring_multiplier', 1.0)
                    break

        # Calculate final score
        base_score = roi_score + payback_bonus
        final_score = min(100, round(base_score * multiplier))

        return {
            'score': final_score,
            'roi_percentage': roi_percentage,
            'roi_category': roi_category,
            'payback_months': payback_months,
            'payback_category': payback_category,
            'multiplier': multiplier,
            'base_score': base_score
        }


class ProjectEvaluator:
    """Evaluates projects against governance criteria."""

    def __init__(self, framework: Optional[GovernanceFramework] = None):
        """Initialize project evaluator."""
        self.framework = framework or GovernanceFramework()
        self.roi_calculator = ROICalculator(self.framework)

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate weighted overall score from individual criteria scores.

        Args:
            scores: Dictionary mapping criterion name to score (0-100)

        Returns:
            Weighted overall score (0-100)
        """
        criteria = self.framework.get_evaluation_criteria()
        total_weight = 0
        weighted_sum = 0

        for criterion, config in criteria.items():
            if criterion in scores:
                weight = config.get('weight', 0)
                score = scores[criterion]
                weighted_sum += score * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(weighted_sum / total_weight, 2)

    def evaluate_project(self, project_data: Dict) -> Dict:
        """
        Comprehensive project evaluation.

        Args:
            project_data: Dictionary with project information

        Returns:
            Evaluation result with scores and recommendation
        """
        scores = {}

        # Extract scores from project data or calculate them
        criteria = self.framework.get_evaluation_criteria()

        for criterion in criteria.keys():
            # Try to get score from project_data
            score_key = f"{criterion}_score"
            if score_key in project_data:
                scores[criterion] = project_data[score_key]
            elif criterion in project_data:
                scores[criterion] = project_data[criterion]
            else:
                # Default to 50 if not provided
                scores[criterion] = 50

        # Calculate weighted overall score
        overall_score = self.calculate_weighted_score(scores)

        # Determine approval
        threshold = self.framework.get_overall_threshold()
        approved = overall_score >= threshold

        # Get approval tier
        budget = project_data.get('estimated_cost', 0)
        approval_tier = self.framework.get_approval_tier_for_budget(budget)

        return {
            'overall_score': overall_score,
            'individual_scores': scores,
            'approved': approved,
            'threshold': threshold,
            'approval_tier': approval_tier,
            'recommendation': 'Approved' if approved else 'Rejected',
            'evaluated_at': datetime.now().isoformat()
        }


class TokenTracker:
    """Tracks and validates token usage."""

    def __init__(self, framework: Optional[GovernanceFramework] = None):
        """Initialize token tracker."""
        self.framework = framework or GovernanceFramework()

    def get_budget_for_environment(self, environment: str) -> Dict:
        """
        Get token budget configuration for an environment.

        Args:
            environment: Environment name (development, testing, production)

        Returns:
            Budget configuration dictionary
        """
        budgets = self.framework.get_token_budgets()
        return budgets.get(environment.lower(), {})

    def check_budget_threshold(
        self,
        current_usage: int,
        limit: int,
        threshold_percentage: float
    ) -> Tuple[bool, str]:
        """
        Check if usage has exceeded threshold.

        Args:
            current_usage: Current token usage
            limit: Budget limit
            threshold_percentage: Alert threshold (e.g., 80 for 80%)

        Returns:
            Tuple of (exceeded, severity)
        """
        usage_percentage = (current_usage / limit) * 100 if limit > 0 else 0

        if usage_percentage >= 100:
            return True, 'critical'
        elif usage_percentage >= threshold_percentage:
            return True, 'warning'
        else:
            return False, 'ok'

    def calculate_waste(
        self,
        actual_usage: int,
        expected_usage: int
    ) -> Dict:
        """
        Calculate token waste metrics.

        Args:
            actual_usage: Actual tokens used
            expected_usage: Expected tokens to be used

        Returns:
            Dictionary with waste metrics
        """
        waste_amount = actual_usage - expected_usage
        waste_percentage = (waste_amount / expected_usage * 100) if expected_usage > 0 else 0

        waste_config = self.framework.config.get('token_accountability', {}).get('waste_thresholds', {})
        warning_threshold = waste_config.get('warning_percentage', 20)
        critical_threshold = waste_config.get('critical_percentage', 50)

        if waste_percentage >= critical_threshold:
            severity = 'critical'
        elif waste_percentage >= warning_threshold:
            severity = 'warning'
        else:
            severity = 'ok'

        return {
            'waste_amount': waste_amount,
            'waste_percentage': round(waste_percentage, 2),
            'severity': severity,
            'actual_usage': actual_usage,
            'expected_usage': expected_usage
        }


# Convenience functions for backward compatibility
def load_governance_framework() -> Dict:
    """Load governance framework configuration."""
    framework = GovernanceFramework()
    return framework.config


def get_strategic_goals() -> List[str]:
    """Get list of strategic goal names."""
    framework = GovernanceFramework()
    return framework.get_strategic_goal_names()


def get_revenue_impact_types() -> List[str]:
    """Get list of revenue impact type names."""
    framework = GovernanceFramework()
    return framework.get_revenue_impact_names()


def get_approval_tier(budget: float) -> Dict:
    """Get approval tier for budget amount."""
    framework = GovernanceFramework()
    return framework.get_approval_tier_for_budget(budget)


def calculate_roi(benefit: float, cost: float) -> float:
    """Calculate ROI percentage."""
    calculator = ROICalculator()
    return calculator.calculate_roi_percentage(benefit, cost)


if __name__ == '__main__':
    # Self-test
    print("Testing shared_utils.py...")

    framework = GovernanceFramework()
    print(f"✓ Loaded framework from {framework.framework_path}")

    goals = framework.get_strategic_goals()
    print(f"✓ Found {len(goals)} strategic goals")

    revenue_types = framework.get_revenue_impact_types()
    print(f"✓ Found {len(revenue_types)} revenue impact types")

    tiers = framework.get_approval_tiers()
    print(f"✓ Found {len(tiers)} approval tiers")

    # Test ROI calculator
    calculator = ROICalculator(framework)
    roi = calculator.calculate_roi_percentage(100000, 50000)
    print(f"✓ ROI calculation works: {roi}%")

    score, category = calculator.score_roi(roi)
    print(f"✓ ROI scoring works: {score} points ({category})")

    # Test project evaluator
    evaluator = ProjectEvaluator(framework)
    test_project = {
        'estimated_cost': 25000,
        'strategic_alignment': 85,
        'financial_viability': 75,
        'technical_feasibility': 80,
        'resource_availability': 70,
        'risk_assessment': 65
    }
    result = evaluator.evaluate_project(test_project)
    print(f"✓ Project evaluation works: {result['overall_score']} - {result['recommendation']}")

    # Test token tracker
    tracker = TokenTracker(framework)
    budget = tracker.get_budget_for_environment('development')
    print(f"✓ Token tracking works: Dev budget = {budget.get('monthly_limit', 0)} tokens")

    print("\nAll tests passed! ✓")
