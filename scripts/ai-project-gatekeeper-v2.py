#!/usr/bin/env python3
"""
AI Project Gatekeeper Agent - Refactored Version
Evaluates project creation requests before human leadership review
Acts as first-line filter to prevent misaligned projects from reaching leadership

REFACTORED: Uses shared_utils.py to eliminate duplication
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path

# Import shared utilities
try:
    from shared_utils import (
        GovernanceFramework,
        ROICalculator,
        ProjectEvaluator
    )
except ImportError:
    # Add parent directory to path if running directly
    sys.path.insert(0, str(Path(__file__).parent))
    from shared_utils import (
        GovernanceFramework,
        ROICalculator,
        ProjectEvaluator
    )

# AI Agent Configuration
AGENT_ID = "project-gatekeeper-agent-v2"
AGENT_TIER = 3  # Operations tier with production evaluation authority
EVALUATION_VERSION = "2.0.0"  # Updated to v2 with shared utilities

# Initialize shared utilities
framework = GovernanceFramework()
roi_calculator = ROICalculator(framework)
project_evaluator = ProjectEvaluator(framework)


def generate_evaluation_id() -> str:
    """Generate unique evaluation ID"""
    year = datetime.now().year
    random_num = f"{hash(datetime.now()) % 10000:04d}"
    return f"EVAL-{year}-{random_num}"


def evaluate_strategic_alignment(request: Dict) -> Tuple[float, Dict]:
    """
    Evaluate strategic alignment using governance framework goals.

    This function now uses strategic goals from the framework YAML instead
    of hardcoded values.
    """
    business = request.get("business_alignment", {})
    strategic_goal = business.get("strategic_goal", "")
    goal_details = business.get("strategic_goal_details", "")
    project_desc = request.get("project_metadata", {}).get("description", "")

    score = 0
    findings = []

    # Get strategic goals from framework
    strategic_goals = framework.get_strategic_goals()
    goal_names = [g['name'] for g in strategic_goals]
    goal_weights = {g['name']: g['weight'] for g in strategic_goals}

    # Check if goal is a company priority
    if strategic_goal in goal_names:
        weight = goal_weights.get(strategic_goal, 1.0)
        score += 5 * weight
        findings.append(f"Strategic goal '{strategic_goal}' is recognized company priority (weight: {weight})")
    else:
        findings.append(f"⚠ Strategic goal not in company priority list")

    # Check quality of goal explanation
    if len(goal_details) > 100:
        score += 5
        findings.append("Detailed explanation of strategic alignment provided")
    elif len(goal_details) > 50:
        score += 3
        findings.append("⚠ Strategic alignment explanation is brief")
    else:
        findings.append("❌ Strategic alignment explanation is too vague")

    # Check if description aligns with goal (using keyword matching)
    goal_keywords = {
        "Revenue Growth": ["revenue", "sales", "customer", "growth", "ARR", "MRR"],
        "Cost Reduction": ["cost", "efficiency", "automat", "reduce", "save"],
        "Customer Satisfaction": ["customer", "experience", "satisfaction", "NPS", "support"],
        "Innovation": ["innovation", "new", "feature", "capability", "differentiat"],
        "Scalability": ["scale", "growth", "expand", "capacity"],
        "Compliance & Security": ["compliance", "risk", "security", "audit", "regulatory"],
        "Risk Mitigation": ["risk", "mitigation", "reduce", "prevent"],
        "Efficiency Improvement": ["efficiency", "productivity", "optimize", "streamline"]
    }

    keywords = goal_keywords.get(strategic_goal, [])
    matches = sum(1 for kw in keywords if kw.lower() in project_desc.lower() or kw.lower() in goal_details.lower())

    if matches >= 2:
        score += 7
        findings.append("Project description strongly aligns with stated goal")
    elif matches >= 1:
        score += 4
        findings.append("⚠ Project description moderately aligns with stated goal")
    else:
        findings.append("❌ Project description does not clearly align with stated goal")

    # Bonus for high-weight goals with strong justification
    if goal_weights.get(strategic_goal, 0) >= 1.1 and len(goal_details) > 100:
        score += 3
        findings.append("✅ High-priority goal with strong justification")

    alignment_strength = "Strong" if score >= 16 else "Moderate" if score >= 12 else "Weak" if score >= 8 else "None"

    return min(score, 20), {
        "score": min(score, 20),
        "max_score": 20,
        "weight": 0.30,  # Increased from 0.25 to match framework
        "rationale": f"Strategic alignment is {alignment_strength}",
        "findings": findings
    }


def evaluate_financial_viability(request: Dict) -> Tuple[float, Dict]:
    """
    Evaluate financial viability using ROI calculator from shared utilities.
    """
    business = request.get("business_alignment", {})
    resources = request.get("resource_requirements", {})
    revenue_impact = business.get("revenue_impact", {})

    score = 0
    findings = []

    # Extract financial data
    revenue_type = revenue_impact.get("type", "None")
    annual_value = revenue_impact.get("estimated_annual_value", 0)
    confidence = revenue_impact.get("confidence_level", "Low (<50%)")
    explanation = revenue_impact.get("explanation", "")

    budget_monthly = resources.get("budget_monthly", 0)
    total_cost = resources.get("estimated_total_cost", budget_monthly * 12)

    # Use ROI calculator from shared utilities
    monthly_benefit = annual_value / 12 if annual_value > 0 else 0

    financial_analysis = roi_calculator.calculate_financial_viability_score(
        estimated_cost=total_cost,
        estimated_benefit=annual_value,
        monthly_benefit=monthly_benefit,
        revenue_impact_type=revenue_type
    )

    # Map framework scores to our 0-25 scale
    # Framework returns 0-100, we need 0-25
    base_score = (financial_analysis['score'] / 100) * 25

    findings.append(f"ROI: {financial_analysis['roi_percentage']}% ({financial_analysis['roi_category']})")
    findings.append(f"Payback period: {financial_analysis['payback_months']} months ({financial_analysis['payback_category']})")

    # Confidence level adjustments
    if "High" in confidence:
        findings.append("High confidence in financial estimates")
    elif "Medium" in confidence:
        base_score *= 0.9
        findings.append("⚠ Medium confidence in financial estimates")
    else:
        base_score *= 0.7
        findings.append("⚠ Low confidence in financial estimates - consider more research")

    # Explanation quality adjustments
    if len(explanation) > 150:
        findings.append("Detailed financial justification provided")
    elif len(explanation) > 75:
        base_score *= 0.95
        findings.append("⚠ Financial justification could be more detailed")
    else:
        base_score *= 0.8
        findings.append("❌ Financial justification is too brief")

    score = min(base_score, 25)

    return score, {
        "score": score,
        "max_score": 25,
        "weight": 0.25,
        "rationale": f"ROI of {financial_analysis['roi_percentage']}% - {financial_analysis['roi_category']}",
        "roi_check": financial_analysis['score'] >= 60,
        "roi_value": financial_analysis['roi_percentage'] / 100,  # As ratio for compatibility
        "roi_details": financial_analysis,
        "findings": findings
    }


def evaluate_resource_feasibility(request: Dict) -> Tuple[float, Dict]:
    """Evaluate resource feasibility"""
    resources = request.get("resource_requirements", {})
    project_meta = request.get("project_metadata", {})

    score = 0
    findings = []

    budget_monthly = resources.get("budget_monthly", 0)
    human_resources = resources.get("human_resources", [])
    agent_tier = project_meta.get("agent_tier", 1)

    # Get approval tier from framework
    annual_budget = budget_monthly * 12
    approval_tier = framework.get_approval_tier_for_budget(annual_budget)

    # Check if budget is appropriate for tier
    tier_name = approval_tier.get('name', 'Unknown')
    tier_range = approval_tier.get('budget_range', {})
    min_budget = tier_range.get('min', 0)
    max_budget = tier_range.get('max', float('inf'))

    if min_budget <= annual_budget <= (max_budget or float('inf')):
        score += 8
        findings.append(f"✅ Budget ${annual_budget}/year is appropriate for {tier_name} tier")
    elif annual_budget < min_budget:
        score += 4
        findings.append(f"⚠ Budget ${annual_budget}/year is low for {tier_name} tier")
    else:
        score += 2
        findings.append(f"⚠ Budget ${annual_budget}/year exceeds {tier_name} tier maximum")

    # Human resources identified (max 6 points)
    if len(human_resources) >= 2:
        score += 6
        findings.append(f"Human resources clearly identified ({len(human_resources)} roles)")
    elif len(human_resources) == 1:
        score += 4
        findings.append("⚠ Limited human resources identified (consider backup)")
    else:
        score += 0
        findings.append("❌ No human resources identified")

    # Tech stack appropriateness (max 6 points)
    tech_stack = project_meta.get("tech_stack", "")
    infrastructure = project_meta.get("infrastructure", "")

    if len(tech_stack) > 20 and len(infrastructure) > 10:
        score += 6
        findings.append("Technical stack and infrastructure clearly defined")
    elif len(tech_stack) > 10:
        score += 3
        findings.append("⚠ Technical details could be more comprehensive")
    else:
        findings.append("❌ Technical details are vague")

    return min(score, 20), {
        "score": min(score, 20),
        "max_score": 20,
        "weight": 0.15,
        "rationale": "Resource allocation is feasible" if score >= 14 else "Resource planning needs improvement",
        "approval_tier": tier_name,
        "findings": findings
    }


def evaluate_risk_assessment(request: Dict) -> Tuple[float, Dict]:
    """Evaluate risk factors"""
    score = 20  # Start with full score, deduct for red flags
    red_flags = []

    business = request.get("business_alignment", {})
    resources = request.get("resource_requirements", {})
    project_meta = request.get("project_metadata", {})

    # Check for unrealistic ROI claims
    revenue_impact = business.get("revenue_impact", {})
    annual_value = revenue_impact.get("estimated_annual_value", 0)
    budget_monthly = resources.get("budget_monthly", 0)
    annual_cost = budget_monthly * 12

    if annual_cost > 0:
        roi_percentage = roi_calculator.calculate_roi_percentage(annual_value, annual_cost)

        if roi_percentage > 2000:  # 20:1 ratio = 2000%
            score -= 5
            red_flags.append("❌ ROI > 20:1 is unrealistic - verify calculations")
        elif roi_percentage > 1000:  # 10:1 ratio = 1000%
            score -= 2
            red_flags.append("⚠ ROI > 10:1 is ambitious - ensure justification is solid")

    # Check for vague descriptions
    description = project_meta.get("description", "")
    if len(description) < 50:
        score -= 3
        red_flags.append("❌ Project description too vague")

    goal_details = business.get("strategic_goal_details", "")
    if len(goal_details) < 30:
        score -= 3
        red_flags.append("❌ Strategic alignment explanation too brief")

    # Check for compliance mismatches
    compliance = project_meta.get("compliance", "None")
    agent_tier = project_meta.get("agent_tier", 1)

    if agent_tier >= 3 and compliance == "None":
        score -= 4
        red_flags.append("⚠ Tier 3+ project should declare compliance requirements")

    # Check for budget/value mismatch
    if budget_monthly < 100 and annual_value > 100000:
        score -= 3
        red_flags.append("⚠ Large value claim with small budget - verify feasibility")

    if not red_flags:
        red_flags.append("✅ No significant risk flags identified")

    return max(score, 0), {
        "score": max(score, 0),
        "max_score": 20,
        "weight": 0.10,
        "rationale": "Low risk" if score >= 16 else "Moderate risk" if score >= 12 else "High risk",
        "red_flags": red_flags
    }


def evaluate_business_case_quality(request: Dict) -> Tuple[float, Dict]:
    """Evaluate overall business case quality"""
    score = 0

    # Check completeness of all required fields
    required_fields = [
        ("project_metadata.name", request.get("project_metadata", {}).get("name")),
        ("project_metadata.description", request.get("project_metadata", {}).get("description")),
        ("business_alignment.strategic_goal", request.get("business_alignment", {}).get("strategic_goal")),
        ("business_alignment.revenue_impact", request.get("business_alignment", {}).get("revenue_impact")),
        ("resource_requirements.budget_monthly", request.get("resource_requirements", {}).get("budget_monthly"))
    ]

    completeness = sum(1 for _, value in required_fields if value) / len(required_fields) * 100

    if completeness == 100:
        score += 7
    elif completeness >= 80:
        score += 5
    else:
        score += 2

    # Check clarity (length and detail of descriptions)
    description = request.get("project_metadata", {}).get("description", "")
    goal_details = request.get("business_alignment", {}).get("strategic_goal_details", "")
    revenue_explanation = request.get("business_alignment", {}).get("revenue_impact", {}).get("explanation", "")

    total_text_length = len(description) + len(goal_details) + len(revenue_explanation)

    if total_text_length > 400:
        score += 8
        clarity = 90
    elif total_text_length > 200:
        score += 5
        clarity = 70
    else:
        score += 2
        clarity = 40

    return min(score, 15), {
        "score": min(score, 15),
        "max_score": 15,
        "weight": 0.20,
        "rationale": "Business case is well-documented" if score >= 12 else "Business case needs improvement",
        "completeness": completeness,
        "clarity": clarity
    }


def calculate_total_score(category_scores: Dict) -> float:
    """Calculate weighted total score"""
    total = 0
    for category, data in category_scores.items():
        total += data["score"] * data["weight"]
    return total


def determine_recommendation(total_score: float, category_scores: Dict, request: Dict) -> Dict:
    """Determine final recommendation using framework thresholds"""
    budget_monthly = request.get("resource_requirements", {}).get("budget_monthly", 0)
    annual_budget = budget_monthly * 12

    # Get approval threshold from framework
    threshold = framework.get_overall_threshold()

    # Auto-approval criteria
    auto_approve_threshold = 80
    auto_approve_budget = 5000  # Auto-approve limit

    auto_approve = (
        total_score >= auto_approve_threshold and
        annual_budget < auto_approve_budget and
        category_scores["strategic_alignment"]["score"] >= 16 and
        category_scores["financial_viability"]["roi_check"] and
        len([f for f in category_scores["risk_assessment"]["red_flags"] if f.startswith("❌")]) == 0
    )

    if auto_approve:
        action = "AUTO_APPROVE"
        confidence = "High (>85%)"
        summary = f"Project scores {total_score:.1f}/100 and meets all auto-approval criteria. Recommend immediate approval."
    elif total_score >= threshold:
        action = "PROCEED_TO_LEADERSHIP"
        confidence = "High (>85%)" if total_score >= 75 else "Medium (60-85%)"
        summary = f"Project scores {total_score:.1f}/100 (threshold: {threshold}). Recommend forwarding to leadership for review."
    elif total_score >= 50:
        action = "REQUEST_REVISION"
        confidence = "Medium (60-85%)"
        summary = f"Project scores {total_score:.1f}/100. Promising but needs improvements before leadership review."
    else:
        action = "REJECT_SEND_FEEDBACK"
        confidence = "High (>85%)"
        summary = f"Project scores {total_score:.1f}/100. Does not meet minimum standards. Recommend rejection with feedback."

    return {
        "action": action,
        "confidence": confidence,
        "summary": summary,
        "threshold_used": threshold
    }


def evaluate_project_request(request: Dict) -> Dict:
    """Main evaluation function"""
    evaluation_id = generate_evaluation_id()
    start_time = datetime.now()

    # Run all evaluation categories
    strategic_score, strategic_detail = evaluate_strategic_alignment(request)
    financial_score, financial_detail = evaluate_financial_viability(request)
    resource_score, resource_detail = evaluate_resource_feasibility(request)
    risk_score, risk_detail = evaluate_risk_assessment(request)
    quality_score, quality_detail = evaluate_business_case_quality(request)

    category_scores = {
        "strategic_alignment": strategic_detail,
        "financial_viability": financial_detail,
        "resource_feasibility": resource_detail,
        "risk_assessment": risk_detail,
        "business_case_quality": quality_detail
    }

    # Calculate total score
    total_score = calculate_total_score(category_scores)
    threshold = framework.get_overall_threshold()
    passes_threshold = total_score >= threshold

    # Determine recommendation
    recommendation = determine_recommendation(total_score, category_scores, request)

    # Determine evaluation result
    if recommendation["action"] == "AUTO_APPROVE":
        result = "APPROVED"
    elif recommendation["action"] == "PROCEED_TO_LEADERSHIP":
        result = "ESCALATE_TO_HUMAN"
    elif recommendation["action"] == "REQUEST_REVISION":
        result = "NEEDS_REVISION"
    else:
        result = "REJECTED"

    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Build evaluation output
    evaluation = {
        "evaluation_id": evaluation_id,
        "timestamp": datetime.now().isoformat(),
        "request_id": request.get("request_id", "UNKNOWN"),
        "ai_agent_id": AGENT_ID,
        "ai_agent_tier": AGENT_TIER,
        "evaluation_result": result,
        "scoring": {
            "total_score": round(total_score, 1),
            "threshold": threshold,
            "pass": passes_threshold,
            "category_scores": category_scores
        },
        "recommendation": recommendation,
        "framework_version": framework.config.get('version', 'unknown'),
        "audit_trail": {
            "evaluation_duration_ms": round(duration_ms, 2),
            "ai_model_used": "shared-framework-evaluation-v2",
            "evaluation_version": EVALUATION_VERSION,
            "framework_path": str(framework.framework_path)
        }
    }

    return evaluation


def main():
    parser = argparse.ArgumentParser(
        description="AI Project Gatekeeper v2 - Evaluate project requests using shared governance framework"
    )
    parser.add_argument("--request-file", required=True, help="Path to project request JSON file")
    parser.add_argument("--output-file", help="Path to save evaluation output")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output")

    args = parser.parse_args()

    # Load project request
    try:
        with open(args.request_file, 'r') as f:
            request = json.load(f)
    except Exception as e:
        print(f"❌ Error loading request file: {str(e)}")
        sys.exit(1)

    print("=" * 70)
    print("AI PROJECT GATEKEEPER EVALUATION (v2 - Framework-Based)")
    print("=" * 70)
    print(f"Agent: {AGENT_ID} (Tier {AGENT_TIER})")
    print(f"Framework: {framework.framework_path}")
    print(f"Request ID: {request.get('request_id', 'UNKNOWN')}")
    print(f"Project: {request.get('project_metadata', {}).get('name', 'Unknown')}")
    print("=" * 70)
    print()

    # Run evaluation
    evaluation = evaluate_project_request(request)

    # Display results
    result = evaluation["evaluation_result"]
    score = evaluation["scoring"]["total_score"]
    threshold = evaluation["scoring"]["threshold"]
    recommendation = evaluation["recommendation"]["action"]

    result_emoji = {
        "APPROVED": "✅",
        "ESCALATE_TO_HUMAN": "👔",
        "NEEDS_REVISION": "⚠️",
        "REJECTED": "❌"
    }

    print(f"{result_emoji.get(result, '❓')} EVALUATION RESULT: {result}")
    print(f"📊 Total Score: {score}/100 (Threshold: {threshold})")
    print(f"💡 Recommendation: {recommendation}")
    print()
    print("Category Scores:")
    for category, data in evaluation["scoring"]["category_scores"].items():
        category_name = category.replace("_", " ").title()
        pct = data["score"] / data["max_score"] * 100
        print(f"  {category_name}: {data['score']:.1f}/{data['max_score']} ({pct:.0f}%)")
    print()

    if args.verbose:
        print("Recommendation Summary:")
        print(f"  {evaluation['recommendation']['summary']}")
        print()

    # Save output
    output_file = args.output_file or args.request_file.replace(".json", "-evaluation-v2.json")

    with open(output_file, 'w') as f:
        json.dump(evaluation, f, indent=2)

    print(f"📄 Evaluation saved to: {output_file}")
    print()

    # Exit code based on result
    if result in ["APPROVED", "ESCALATE_TO_HUMAN"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
