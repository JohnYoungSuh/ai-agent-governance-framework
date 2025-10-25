#!/usr/bin/env python3
"""
AI Project Gatekeeper Agent
Evaluates project creation requests before human leadership review
Acts as first-line filter to prevent misaligned projects from reaching leadership
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple

# AI Agent Configuration
AGENT_ID = "project-gatekeeper-agent-v1"
AGENT_TIER = 3  # Operations tier with production evaluation authority
EVALUATION_VERSION = "1.0.0"

# Scoring thresholds
SCORING_THRESHOLD = 60  # Minimum score to pass (0-100)
AUTO_APPROVE_THRESHOLD = 80  # Score for auto-approval
AUTO_APPROVE_BUDGET_LIMIT = 500  # Max budget for auto-approval

# Company strategic priorities (customize for your company)
COMPANY_STRATEGIC_PRIORITIES = {
    "Increase Revenue": {"priority": "High", "weight": 1.0},
    "Reduce Costs": {"priority": "High", "weight": 1.0},
    "Improve Customer Experience": {"priority": "High", "weight": 0.9},
    "Enter New Market": {"priority": "Medium", "weight": 0.7},
    "Product Innovation": {"priority": "High", "weight": 0.9},
    "Operational Excellence": {"priority": "Medium", "weight": 0.8},
    "Compliance & Risk Management": {"priority": "High", "weight": 1.0},
    "Technical Debt Reduction": {"priority": "Low", "weight": 0.5},
    "Team Productivity": {"priority": "Medium", "weight": 0.7}
}

# Expected ROI benchmarks by revenue type
ROI_BENCHMARKS = {
    "Direct Revenue Generation": {"min_roi": 3.0, "typical_roi": 5.0},
    "Revenue Enablement": {"min_roi": 2.5, "typical_roi": 4.0},
    "Cost Reduction (OpEx)": {"min_roi": 3.0, "typical_roi": 5.0},
    "Cost Reduction (CapEx)": {"min_roi": 2.0, "typical_roi": 3.5},
    "Cost Avoidance": {"min_roi": 2.0, "typical_roi": 3.0},
    "Customer Retention": {"min_roi": 4.0, "typical_roi": 6.0},
    "Efficiency Gain": {"min_roi": 2.5, "typical_roi": 4.0},
    "Risk Mitigation": {"min_roi": 1.5, "typical_roi": 2.5},
    "None": {"min_roi": 0.0, "typical_roi": 0.0}
}


def generate_evaluation_id() -> str:
    """Generate unique evaluation ID"""
    year = datetime.now().year
    random_num = f"{hash(datetime.now()) % 10000:04d}"
    return f"EVAL-{year}-{random_num}"


def evaluate_strategic_alignment(request: Dict) -> Tuple[float, Dict]:
    """Evaluate strategic alignment (max 20 points)"""
    business = request.get("business_alignment", {})
    strategic_goal = business.get("strategic_goal", "")
    goal_details = business.get("strategic_goal_details", "")
    project_desc = request.get("project_metadata", {}).get("description", "")

    score = 0
    findings = []

    # Check if goal is a company priority
    priority_info = COMPANY_STRATEGIC_PRIORITIES.get(strategic_goal, {"priority": "Low", "weight": 0.3})
    priority_weight = priority_info["weight"]

    if strategic_goal in COMPANY_STRATEGIC_PRIORITIES:
        score += 5 * priority_weight
        findings.append(f"Strategic goal '{strategic_goal}' is recognized company priority ({priority_info['priority']})")
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

    # Check if description aligns with goal
    goal_keywords = {
        "Increase Revenue": ["revenue", "sales", "customer", "growth", "ARR", "MRR"],
        "Reduce Costs": ["cost", "efficiency", "automat", "reduce", "save"],
        "Improve Customer Experience": ["customer", "experience", "satisfaction", "NPS", "support"],
        "Product Innovation": ["innovation", "new", "feature", "capability", "differentiat"],
        "Operational Excellence": ["process", "operational", "quality", "efficiency"],
        "Compliance & Risk Management": ["compliance", "risk", "security", "audit", "regulatory"],
        "Technical Debt": ["debt", "refactor", "maintenance", "legacy"],
        "Team Productivity": ["productivity", "efficiency", "tool", "developer", "automation"]
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

    # Bonus for high-priority goals
    if priority_info["priority"] == "High" and len(goal_details) > 100:
        score += 3
        findings.append("✅ High-priority goal with strong justification")

    alignment_strength = "Strong" if score >= 16 else "Moderate" if score >= 12 else "Weak" if score >= 8 else "None"

    return min(score, 20), {
        "score": min(score, 20),
        "max_score": 20,
        "weight": 0.25,
        "rationale": f"Strategic alignment is {alignment_strength}. Priority weight: {priority_weight}",
        "findings": findings
    }


def evaluate_financial_viability(request: Dict) -> Tuple[float, Dict]:
    """Evaluate financial viability (max 25 points)"""
    business = request.get("business_alignment", {})
    resources = request.get("resource_requirements", {})
    revenue_impact = business.get("revenue_impact", {})

    score = 0
    findings = []

    revenue_type = revenue_impact.get("type", "None")
    annual_value = revenue_impact.get("estimated_annual_value", 0)
    confidence = revenue_impact.get("confidence_level", "Low (<50%)")
    explanation = revenue_impact.get("explanation", "")

    budget_monthly = resources.get("budget_monthly", 0)
    total_cost = resources.get("estimated_total_cost", budget_monthly)
    annual_cost = total_cost * 12

    # Calculate ROI
    if annual_cost > 0:
        roi_ratio = annual_value / annual_cost
    else:
        roi_ratio = 0

    # Check against benchmarks
    benchmark = ROI_BENCHMARKS.get(revenue_type, {"min_roi": 2.0, "typical_roi": 3.0})
    min_roi = benchmark["min_roi"]
    typical_roi = benchmark["typical_roi"]

    # ROI scoring (max 12 points)
    if roi_ratio >= typical_roi:
        score += 12
        findings.append(f"✅ Excellent ROI: {roi_ratio:.1f}:1 (exceeds typical {typical_roi:.1f}:1)")
    elif roi_ratio >= min_roi:
        score += 8
        findings.append(f"Good ROI: {roi_ratio:.1f}:1 (meets minimum {min_roi:.1f}:1)")
    elif roi_ratio >= 1.0:
        score += 4
        findings.append(f"⚠ Low ROI: {roi_ratio:.1f}:1 (below typical for {revenue_type})")
    else:
        findings.append(f"❌ Negative ROI: {roi_ratio:.1f}:1 (does not justify investment)")

    # Confidence level scoring (max 5 points)
    if "High" in confidence:
        score += 5
        findings.append("High confidence in financial estimates")
    elif "Medium" in confidence:
        score += 3
        findings.append("⚠ Medium confidence in financial estimates")
    else:
        score += 1
        findings.append("⚠ Low confidence in financial estimates - consider more research")

    # Explanation quality (max 5 points)
    if len(explanation) > 150:
        score += 5
        findings.append("Detailed financial justification provided")
    elif len(explanation) > 75:
        score += 3
        findings.append("⚠ Financial justification could be more detailed")
    else:
        findings.append("❌ Financial justification is too brief")

    # Revenue type appropriateness (max 3 points)
    if revenue_type != "None":
        score += 3
        findings.append(f"Clear revenue impact type: {revenue_type}")
    else:
        findings.append("❌ No revenue impact identified")

    roi_acceptable = roi_ratio >= min_roi

    return min(score, 25), {
        "score": min(score, 25),
        "max_score": 25,
        "weight": 0.30,
        "rationale": f"ROI of {roi_ratio:.1f}:1 {'meets' if roi_acceptable else 'does not meet'} minimum benchmark",
        "roi_check": roi_acceptable,
        "roi_value": roi_ratio,
        "findings": findings
    }


def evaluate_resource_feasibility(request: Dict) -> Tuple[float, Dict]:
    """Evaluate resource feasibility (max 20 points)"""
    resources = request.get("resource_requirements", {})
    project_meta = request.get("project_metadata", {})

    score = 0
    findings = []

    budget_monthly = resources.get("budget_monthly", 0)
    human_resources = resources.get("human_resources", [])
    agent_tier = project_meta.get("agent_tier", 1)

    # Budget appropriateness for tier (max 8 points)
    tier_budget_ranges = {
        1: (10, 500),    # Observer
        2: (50, 5000),   # Developer
        3: (100, 10000), # Operations
        4: (500, 50000)  # Architect
    }

    min_budget, max_budget = tier_budget_ranges.get(agent_tier, (0, float('inf')))

    if min_budget <= budget_monthly <= max_budget:
        score += 8
        findings.append(f"✅ Budget ${budget_monthly}/mo is appropriate for Tier {agent_tier}")
    elif budget_monthly < min_budget:
        score += 4
        findings.append(f"⚠ Budget ${budget_monthly}/mo is low for Tier {agent_tier} (typical min: ${min_budget})")
    else:
        score += 2
        findings.append(f"⚠ Budget ${budget_monthly}/mo is high for Tier {agent_tier} (typical max: ${max_budget})")

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
        "weight": 0.20,
        "rationale": "Resource allocation is feasible" if score >= 14 else "Resource planning needs improvement",
        "findings": findings
    }


def evaluate_risk_assessment(request: Dict) -> Tuple[float, Dict]:
    """Evaluate risk factors (max 20 points)"""
    score = 20  # Start with full score, deduct for red flags
    red_flags = []

    business = request.get("business_alignment", {})
    resources = request.get("resource_requirements", {})
    project_meta = request.get("project_metadata", {})

    # Check for unrealistic claims
    revenue_impact = business.get("revenue_impact", {})
    annual_value = revenue_impact.get("estimated_annual_value", 0)
    budget_monthly = resources.get("budget_monthly", 0)
    annual_cost = budget_monthly * 12

    if annual_cost > 0:
        roi_ratio = annual_value / annual_cost
        if roi_ratio > 20:
            score -= 5
            red_flags.append("❌ ROI > 20:1 is unrealistic - verify calculations")
        elif roi_ratio > 10:
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

    # Check priority alignment
    priority = business.get("priority", "Low")
    strategic_goal = business.get("strategic_goal", "")
    goal_priority = COMPANY_STRATEGIC_PRIORITIES.get(strategic_goal, {}).get("priority", "Low")

    if priority == "Critical" and goal_priority == "Low":
        score -= 2
        red_flags.append("⚠ Critical priority on low-priority strategic goal")

    if not red_flags:
        red_flags.append("✅ No significant risk flags identified")

    return max(score, 0), {
        "score": max(score, 0),
        "max_score": 20,
        "weight": 0.15,
        "rationale": "Low risk" if score >= 16 else "Moderate risk" if score >= 12 else "High risk",
        "red_flags": red_flags
    }


def evaluate_business_case_quality(request: Dict) -> Tuple[float, Dict]:
    """Evaluate overall business case quality (max 15 points)"""
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
        "weight": 0.10,
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
    """Determine final recommendation"""
    budget_monthly = request.get("resource_requirements", {}).get("budget_monthly", 0)

    # Check auto-approval eligibility
    auto_approve = (
        total_score >= AUTO_APPROVE_THRESHOLD and
        budget_monthly < AUTO_APPROVE_BUDGET_LIMIT and
        category_scores["strategic_alignment"]["score"] >= 16 and
        category_scores["financial_viability"]["roi_check"] and
        len(category_scores["risk_assessment"]["red_flags"]) <= 1
    )

    if auto_approve:
        action = "AUTO_APPROVE"
        confidence = "High (>85%)"
        summary = f"Project scores {total_score:.1f}/100 and meets all auto-approval criteria. Recommend immediate approval."
    elif total_score >= SCORING_THRESHOLD:
        action = "PROCEED_TO_LEADERSHIP"
        confidence = "High (>85%)" if total_score >= 75 else "Medium (60-85%)"
        summary = f"Project scores {total_score:.1f}/100 (threshold: {SCORING_THRESHOLD}). Recommend forwarding to leadership for review."
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
        "reasoning": generate_reasoning(total_score, category_scores, request)
    }


def generate_reasoning(total_score: float, category_scores: Dict, request: Dict) -> str:
    """Generate detailed reasoning for recommendation"""
    reasoning = f"Total Score: {total_score:.1f}/100\n\n"

    reasoning += "Category Breakdown:\n"
    for category, data in category_scores.items():
        category_name = category.replace("_", " ").title()
        reasoning += f"- {category_name}: {data['score']:.1f}/{data['max_score']} ({data['score']/data['max_score']*100:.0f}%)\n"

    reasoning += "\nKey Strengths:\n"
    strengths = []
    if category_scores["strategic_alignment"]["score"] >= 16:
        strengths.append("Strong strategic alignment with company goals")
    if category_scores["financial_viability"]["roi_check"]:
        strengths.append(f"ROI of {category_scores['financial_viability']['roi_value']:.1f}:1 meets benchmarks")
    if category_scores["risk_assessment"]["score"] >= 16:
        strengths.append("Low risk profile")

    if strengths:
        for strength in strengths:
            reasoning += f"- {strength}\n"
    else:
        reasoning += "- None identified\n"

    reasoning += "\nKey Concerns:\n"
    concerns = []
    if category_scores["strategic_alignment"]["score"] < 12:
        concerns.append("Weak strategic alignment")
    if not category_scores["financial_viability"]["roi_check"]:
        concerns.append("ROI below acceptable benchmarks")
    if category_scores["risk_assessment"]["score"] < 12:
        concerns.append("High risk factors present")
    if category_scores["business_case_quality"]["completeness"] < 80:
        concerns.append("Incomplete business case")

    if concerns:
        for concern in concerns:
            reasoning += f"- {concern}\n"
    else:
        reasoning += "- None identified\n"

    return reasoning


def identify_required_revisions(category_scores: Dict) -> List[Dict]:
    """Identify specific revisions needed"""
    revisions = []

    # Strategic alignment revisions
    if category_scores["strategic_alignment"]["score"] < 12:
        revisions.append({
            "category": "Strategic Alignment",
            "issue": "Strategic alignment is not clearly demonstrated",
            "suggested_fix": "Provide more detailed explanation of how project supports the strategic goal with specific examples and metrics",
            "severity": "Critical"
        })

    # Financial viability revisions
    if not category_scores["financial_viability"]["roi_check"]:
        revisions.append({
            "category": "Financial Justification",
            "issue": f"ROI of {category_scores['financial_viability']['roi_value']:.1f}:1 is below acceptable benchmark",
            "suggested_fix": "Revise financial estimates or provide additional justification for the ROI. Consider if project scope can be adjusted.",
            "severity": "Critical"
        })

    # Resource planning revisions
    if category_scores["resource_feasibility"]["score"] < 12:
        revisions.append({
            "category": "Resource Planning",
            "issue": "Resource requirements are not well-defined",
            "suggested_fix": "Identify specific human resources, provide more detail on technical stack, and ensure budget aligns with agent tier",
            "severity": "Important"
        })

    # Risk management revisions
    red_flags = [flag for flag in category_scores["risk_assessment"]["red_flags"] if flag.startswith("❌")]
    if red_flags:
        revisions.append({
            "category": "Risk Management",
            "issue": f"Risk flags identified: {', '.join(red_flags)}",
            "suggested_fix": "Address identified risk factors before resubmitting",
            "severity": "Important"
        })

    # Business case quality revisions
    if category_scores["business_case_quality"]["completeness"] < 80:
        revisions.append({
            "category": "Business Case Quality",
            "issue": "Business case is incomplete or lacks detail",
            "suggested_fix": "Provide more comprehensive descriptions and explanations for all required fields",
            "severity": "Important"
        })

    return revisions


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
    passes_threshold = total_score >= SCORING_THRESHOLD

    # Determine recommendation
    recommendation = determine_recommendation(total_score, category_scores, request)

    # Identify required revisions if needed
    required_revisions = []
    if recommendation["action"] in ["REQUEST_REVISION", "REJECT_SEND_FEEDBACK"]:
        required_revisions = identify_required_revisions(category_scores)

    # Check auto-approval eligibility
    budget_monthly = request.get("resource_requirements", {}).get("budget_monthly", 0)
    auto_eligible = recommendation["action"] == "AUTO_APPROVE"

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
            "threshold": SCORING_THRESHOLD,
            "pass": passes_threshold,
            "category_scores": category_scores
        },
        "recommendation": recommendation,
        "analysis": {
            "strategic_alignment_check": {
                "goal_is_company_priority": request.get("business_alignment", {}).get("strategic_goal") in COMPANY_STRATEGIC_PRIORITIES,
                "alignment_strength": "Strong" if strategic_score >= 16 else "Moderate" if strategic_score >= 12 else "Weak"
            },
            "financial_analysis": {
                "roi_ratio": financial_detail.get("roi_value", 0),
                "roi_acceptable": financial_detail.get("roi_check", False)
            },
            "risk_flags": {
                "unrealistic_roi": financial_detail.get("roi_value", 0) > 20,
                "vague_business_case": quality_detail.get("completeness", 100) < 60,
                "details": risk_detail.get("red_flags", [])
            }
        },
        "required_revisions": required_revisions,
        "auto_approval_eligible": {
            "eligible": auto_eligible,
            "criteria_met": {
                "low_budget": budget_monthly < AUTO_APPROVE_BUDGET_LIMIT,
                "high_score": total_score > AUTO_APPROVE_THRESHOLD,
                "strong_alignment": strategic_score > 16,
                "good_roi": financial_detail.get("roi_check", False),
                "low_risk": len([f for f in risk_detail.get("red_flags", []) if f.startswith("❌")]) == 0
            },
            "rationale": "All auto-approval criteria met" if auto_eligible else "Does not meet all auto-approval criteria"
        },
        "human_review_notes": {
            "key_points": [
                f"Total score: {total_score:.1f}/100",
                f"Strategic alignment: {strategic_detail['score']:.1f}/20",
                f"Financial viability: {financial_detail['score']:.1f}/25",
                f"ROI: {financial_detail.get('roi_value', 0):.1f}:1"
            ],
            "areas_needing_attention": [rev["issue"] for rev in required_revisions if rev["severity"] == "Critical"],
            "questions_for_requester": []
        },
        "audit_trail": {
            "evaluation_duration_ms": round(duration_ms, 2),
            "ai_model_used": "rule-based-evaluation-engine-v1",
            "evaluation_version": EVALUATION_VERSION
        }
    }

    return evaluation


def main():
    parser = argparse.ArgumentParser(
        description="AI Project Gatekeeper - Evaluate project requests before human review"
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
    print("AI PROJECT GATEKEEPER EVALUATION")
    print("=" * 70)
    print(f"Agent: {AGENT_ID} (Tier {AGENT_TIER})")
    print(f"Request ID: {request.get('request_id', 'UNKNOWN')}")
    print(f"Project: {request.get('project_metadata', {}).get('name', 'Unknown')}")
    print("=" * 70)
    print()

    # Run evaluation
    evaluation = evaluate_project_request(request)

    # Display results
    result = evaluation["evaluation_result"]
    score = evaluation["scoring"]["total_score"]
    recommendation = evaluation["recommendation"]["action"]

    result_emoji = {
        "APPROVED": "✅",
        "ESCALATE_TO_HUMAN": "👔",
        "NEEDS_REVISION": "⚠️",
        "REJECTED": "❌"
    }

    print(f"{result_emoji.get(result, '❓')} EVALUATION RESULT: {result}")
    print(f"📊 Total Score: {score}/100 (Threshold: {SCORING_THRESHOLD})")
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
        print("Reasoning:")
        print(evaluation['recommendation']['reasoning'])
        print()

    if evaluation["required_revisions"]:
        print("Required Revisions:")
        for i, rev in enumerate(evaluation["required_revisions"], 1):
            print(f"  {i}. [{rev['severity']}] {rev['category']}: {rev['issue']}")
            print(f"     → {rev['suggested_fix']}")
        print()

    # Save output
    output_file = args.output_file or args.request_file.replace(".json", "-evaluation.json")

    with open(output_file, 'w') as f:
        json.dump(evaluation, f, indent=2)

    print(f"📄 Evaluation saved to: {output_file}")
    print()

    # Exit code based on result
    if result == "APPROVED":
        print("✅ Project approved - can proceed without human review")
        sys.exit(0)
    elif result == "ESCALATE_TO_HUMAN":
        print("👔 Project requires human leadership review")
        sys.exit(0)
    elif result == "NEEDS_REVISION":
        print("⚠️ Project needs revisions before proceeding")
        sys.exit(1)
    else:
        print("❌ Project rejected - does not meet minimum standards")
        sys.exit(1)


if __name__ == "__main__":
    main()
