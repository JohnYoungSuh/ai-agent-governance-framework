#!/usr/bin/env python3
"""
Submit Project Creation Request to Jira for Leadership Approval
Integrates with Jira to create approval workflow for AI-driven projects
Includes AI Gatekeeper evaluation before human review
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

# Jira Configuration (customize for your instance)
JIRA_URL = os.getenv("JIRA_URL", "https://your-company.atlassian.net")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_USERNAME = os.getenv("JIRA_USERNAME", "")
JIRA_PROJECT_APPROVAL_KEY = os.getenv("JIRA_PROJECT_APPROVAL_KEY", "PROJAPPR")

# Approval tiers based on monthly budget
APPROVAL_TIERS = {
    "team_lead": {"max_budget": 500, "label": "Team Lead Only (<$500/mo)"},
    "manager": {"max_budget": 2000, "label": "Manager Approval ($500-$2K/mo)"},
    "director": {"max_budget": 10000, "label": "Director Approval ($2K-$10K/mo)"},
    "vp": {"max_budget": 50000, "label": "VP Approval ($10K-$50K/mo)"},
    "executive": {"max_budget": float('inf'), "label": "Executive Approval (>$50K/mo or Strategic)"}
}

# Strategic goals that always require executive approval
STRATEGIC_GOALS_REQUIRING_EXEC_APPROVAL = [
    "Enter New Market",
    "Product Innovation"
]


def determine_approval_tier(budget_monthly: float, strategic_goal: str) -> str:
    """Determine required approval tier based on budget and strategic goal"""

    # Strategic goals always require executive approval
    if strategic_goal in STRATEGIC_GOALS_REQUIRING_EXEC_APPROVAL:
        return APPROVAL_TIERS["executive"]["label"]

    # Budget-based approval tiers
    for tier, config in APPROVAL_TIERS.items():
        if budget_monthly < config["max_budget"]:
            return config["label"]

    return APPROVAL_TIERS["executive"]["label"]


def calculate_roi_estimate(revenue_impact: Dict, total_cost: float) -> Dict:
    """Calculate estimated ROI for leadership review"""
    annual_value = revenue_impact.get("estimated_annual_value", 0)
    annual_cost = total_cost * 12  # Assuming total_cost is monthly

    if annual_cost == 0:
        roi_ratio = "N/A"
    else:
        roi_ratio = f"{annual_value / annual_cost:.2f}:1"

    payback_months = "N/A"
    if annual_value > 0 and total_cost > 0:
        payback_months = f"{(annual_cost / annual_value) * 12:.1f} months"

    return {
        "annual_value": annual_value,
        "annual_cost": annual_cost,
        "roi_ratio": roi_ratio,
        "payback_period": payback_months,
        "net_annual_impact": annual_value - annual_cost
    }


def create_jira_issue(project_request: Dict) -> str:
    """Create Jira issue for project approval"""

    if not JIRA_API_TOKEN or not JIRA_USERNAME:
        print("⚠ Warning: Jira credentials not configured. Skipping Jira creation.")
        print("Set JIRA_API_TOKEN and JIRA_USERNAME environment variables.")
        return "MOCK-123"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    # Extract key information
    project_meta = project_request["project_metadata"]
    business = project_request["business_alignment"]
    resources = project_request["resource_requirements"]
    approval = project_request["approval_workflow"]

    # Calculate ROI
    roi = calculate_roi_estimate(business["revenue_impact"], resources["estimated_total_cost"])

    # Check if AI evaluation exists
    ai_eval_section = ""
    if "ai_gatekeeper_decision" in project_request.get("approval_workflow", {}):
        ai_decision = project_request["approval_workflow"]["ai_gatekeeper_decision"]
        ai_eval_section = f"""
h2. 🤖 AI Gatekeeper Evaluation

*Evaluation ID:* {ai_decision.get("evaluation_id", "N/A")}
*AI Agent:* project-gatekeeper-agent-v1 (Tier 3)
*Score:* {ai_decision.get("score", 0)}/100
*Decision:* {ai_decision.get("result", "ESCALATE_TO_HUMAN")}
*Timestamp:* {ai_decision.get("timestamp", "N/A")}

*AI Recommendation:* This project requires human review due to budget/complexity.

----
"""

    # Build Jira description with rich formatting
    description = f"""
h2. 🚀 Project Creation Request

*Request ID:* {project_request["request_id"]}
*Submitted by:* {project_request["requester"]["name"]} ({project_request["requester"]["department"]})
*Date:* {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

----

{ai_eval_section}

h2. 📋 Project Overview

*Project Name:* {project_meta["name"]}
*Description:* {project_meta["description"]}
*Owner:* {project_meta["owner"]["name"]} ({project_meta["owner"]["email"]})
*Tech Stack:* {project_meta["tech_stack"]}
*Infrastructure:* {project_meta["infrastructure"]}
*AI Agent Tier:* {project_meta["agent_tier"]} ({["", "Observer", "Developer", "Operations", "Architect"][project_meta["agent_tier"]])
*Compliance:* {project_meta["compliance"]}

----

h2. 🎯 Business Alignment

*Strategic Goal:* {business["strategic_goal"]}
{business.get("strategic_goal_details", "")}

*Revenue Impact Type:* {business["revenue_impact"]["type"]}
*Estimated Annual Value:* ${business["revenue_impact"]["estimated_annual_value"]:,.0f}
*Confidence Level:* {business["revenue_impact"]["confidence_level"]}
*Time to Value:* {business["revenue_impact"].get("time_to_value", "TBD")}

*Explanation:*
{business["revenue_impact"]["explanation"]}

*Priority:* {business["priority"]}
*OKR Reference:* {business.get("okr_reference", "N/A")}

h3. Success Metrics
"""

    for metric in business["success_metrics"]:
        description += f"\n* *{metric['metric']}:* {metric['target']} (measured via {metric['measurement_method']})"

    description += f"""

----

h2. 💰 Financial Analysis

*Monthly AI Budget:* ${resources["budget_monthly"]:,.0f}
*Monthly Infrastructure:* ${resources.get("infrastructure_costs", 0):,.0f}
*Total Monthly Cost:* ${resources["estimated_total_cost"]:,.0f}
*Annual Cost:* ${roi["annual_cost"]:,.0f}

*ROI Analysis:*
* Estimated Annual Value: ${roi["annual_value"]:,.0f}
* ROI Ratio: {roi["roi_ratio"]}
* Payback Period: {roi["payback_period"]}
* Net Annual Impact: ${roi["net_annual_impact"]:,.0f}

h3. Human Resources Required
"""

    for resource in resources["human_resources"]:
        description += f"\n* {resource['role']}: {resource['time_allocation']}"
        if "duration" in resource:
            description += f" for {resource['duration']}"

    # Add risk assessment if present
    if "risk_assessment" in project_request:
        risk = project_request["risk_assessment"]
        description += f"""

----

h2. ⚠️ Risk Assessment

*Overall Risk Level:* {risk["overall_risk_level"]}

h3. Risk Factors:
"""
        for factor in risk["risk_factors"]:
            description += f"""
* *{factor['category']}* ({factor.get('severity', 'Medium')}): {factor['description']}
  _Mitigation:_ {factor['mitigation']}
"""

    description += f"""

----

h2. ✅ Approval Required

*Approval Tier:* {approval["approval_tier"]}
*Decision Deadline:* {approval.get("decision_deadline", "N/A")}

h3. Required Approvers:
"""

    for approver in approval["required_approvers"]:
        description += f"\n* {approver['name']} ({approver['role']}) - {approver['email']}"

    description += """

----

h2. 📝 Next Steps for Approvers

# Review business alignment and revenue impact
# Validate resource requirements and budget
# Assess risks and mitigations
# Approve or request more information via Jira comments
# Upon approval, project will be created with governance controls

_This is an AI-driven project creation request. All projects are created with mandatory governance, accountability, and audit trails._
"""

    # Create Jira issue payload
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_APPROVAL_KEY},
            "summary": f"Project Approval: {project_meta['name']} - ${resources['budget_monthly']}/mo - {business['strategic_goal']}",
            "description": description,
            "issuetype": {"name": "Task"},
            "priority": {"name": business["priority"]},
            "labels": [
                f"agent-tier-{project_meta['agent_tier']}",
                f"budget-${resources['budget_monthly']}",
                business["strategic_goal"].lower().replace(" ", "-"),
                business["revenue_impact"]["type"].lower().replace(" ", "-"),
                project_request["requester"]["department"].lower()
            ],
            "customfield_10000": project_request["request_id"]  # Custom field for request ID
        }
    }

    try:
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue",
            headers=headers,
            auth=auth,
            json=payload
        )

        if response.status_code == 201:
            issue_key = response.json()["key"]
            print(f"✅ Jira issue created: {JIRA_URL}/browse/{issue_key}")
            return issue_key
        else:
            print(f"❌ Failed to create Jira issue: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ Error creating Jira issue: {str(e)}")
        return None


def send_slack_notification(project_request: Dict, jira_key: str):
    """Send Slack notification to leadership (optional)"""
    slack_webhook = os.getenv("SLACK_LEADERSHIP_WEBHOOK", "")

    if not slack_webhook:
        return

    project_meta = project_request["project_metadata"]
    business = project_request["business_alignment"]
    resources = project_request["resource_requirements"]
    roi = calculate_roi_estimate(business["revenue_impact"], resources["estimated_total_cost"])

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 New Project Approval Request: {project_meta['name']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Requester:*\n{project_request['requester']['name']}"},
                    {"type": "mrkdwn", "text": f"*Department:*\n{project_request['requester']['department']}"},
                    {"type": "mrkdwn", "text": f"*Strategic Goal:*\n{business['strategic_goal']}"},
                    {"type": "mrkdwn", "text": f"*Priority:*\n{business['priority']}"},
                    {"type": "mrkdwn", "text": f"*Monthly Budget:*\n${resources['budget_monthly']:,.0f}"},
                    {"type": "mrkdwn", "text": f"*Est. Annual Value:*\n${roi['annual_value']:,.0f}"},
                    {"type": "mrkdwn", "text": f"*ROI:*\n{roi['roi_ratio']}"},
                    {"type": "mrkdwn", "text": f"*Agent Tier:*\n{project_meta['agent_tier']}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Revenue Impact:* {business['revenue_impact']['type']}\n{business['revenue_impact']['explanation'][:200]}..."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Review in Jira"},
                        "url": f"{JIRA_URL}/browse/{jira_key}",
                        "style": "primary"
                    }
                ]
            }
        ]
    }

    try:
        requests.post(slack_webhook, json=message)
    except Exception as e:
        print(f"⚠ Warning: Failed to send Slack notification: {str(e)}")


def save_request_locally(project_request: Dict, output_dir: str = "."):
    """Save project request to local file for audit trail"""
    filename = f"{output_dir}/{project_request['request_id']}.json"

    os.makedirs(output_dir, exist_ok=True)

    with open(filename, 'w') as f:
        json.dump(project_request, f, indent=2)

    print(f"📄 Request saved to: {filename}")
    return filename


def run_ai_gatekeeper_evaluation(request_file: str) -> Dict:
    """Run AI Gatekeeper evaluation on project request"""
    print("=" * 60)
    print("🤖 RUNNING AI GATEKEEPER EVALUATION")
    print("=" * 60)
    print()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    gatekeeper_script = os.path.join(script_dir, "ai-project-gatekeeper.py")

    evaluation_file = request_file.replace(".json", "-evaluation.json")

    try:
        result = subprocess.run(
            ["python3", gatekeeper_script, "--request-file", request_file, "--output-file", evaluation_file],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if os.path.exists(evaluation_file):
            with open(evaluation_file, 'r') as f:
                evaluation = json.load(f)
            return evaluation
        else:
            print("⚠ Warning: Evaluation file not created")
            return None

    except Exception as e:
        print(f"⚠ Warning: AI Gatekeeper evaluation failed: {str(e)}")
        print("Proceeding with manual review...")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Submit project creation request for leadership approval (with AI Gatekeeper)"
    )
    parser.add_argument("--request-file", required=True, help="Path to project request JSON file")
    parser.add_argument("--output-dir", default="./project-requests", help="Directory to save requests")
    parser.add_argument("--skip-jira", action="store_true", help="Skip Jira creation (testing only)")
    parser.add_argument("--skip-ai-eval", action="store_true", help="Skip AI Gatekeeper evaluation")

    args = parser.parse_args()

    # Load project request
    try:
        with open(args.request_file, 'r') as f:
            project_request = json.load(f)
    except Exception as e:
        print(f"❌ Error loading request file: {str(e)}")
        sys.exit(1)

    # Validate against schema (basic validation)
    required_fields = ["request_id", "requester", "project_metadata", "business_alignment",
                      "resource_requirements", "approval_workflow"]

    for field in required_fields:
        if field not in project_request:
            print(f"❌ Error: Missing required field '{field}' in request")
            sys.exit(1)

    print("=" * 60)
    print("PROJECT CREATION APPROVAL REQUEST")
    print("=" * 60)
    print()

    # Display summary
    print(f"Request ID: {project_request['request_id']}")
    print(f"Project: {project_request['project_metadata']['name']}")
    print(f"Requester: {project_request['requester']['name']} ({project_request['requester']['department']})")
    print(f"Strategic Goal: {project_request['business_alignment']['strategic_goal']}")
    print(f"Monthly Budget: ${project_request['resource_requirements']['budget_monthly']:,.0f}")
    print(f"Approval Tier: {project_request['approval_workflow']['approval_tier']}")
    print()

    # Calculate and display ROI
    roi = calculate_roi_estimate(
        project_request['business_alignment']['revenue_impact'],
        project_request['resource_requirements']['estimated_total_cost']
    )

    print("Financial Analysis:")
    print(f"  Annual Value: ${roi['annual_value']:,.0f}")
    print(f"  Annual Cost: ${roi['annual_cost']:,.0f}")
    print(f"  ROI Ratio: {roi['roi_ratio']}")
    print(f"  Net Annual Impact: ${roi['net_annual_impact']:,.0f}")
    print()

    # Save locally
    local_file = save_request_locally(project_request, args.output_dir)

    # Run AI Gatekeeper evaluation (unless skipped)
    ai_evaluation = None
    if not args.skip_ai_eval:
        ai_evaluation = run_ai_gatekeeper_evaluation(local_file)

        if ai_evaluation:
            result = ai_evaluation["evaluation_result"]
            score = ai_evaluation["scoring"]["total_score"]
            recommendation = ai_evaluation["recommendation"]["action"]

            # Handle AI Gatekeeper decision
            if result == "REJECTED":
                print()
                print("=" * 60)
                print("❌ AI GATEKEEPER: PROJECT REJECTED")
                print("=" * 60)
                print()
                print(f"The AI Gatekeeper has rejected this project (score: {score}/100)")
                print()
                print("Reasons:")
                for rev in ai_evaluation.get("required_revisions", []):
                    print(f"  - [{rev['severity']}] {rev['issue']}")
                print()
                print("This project does not meet minimum standards and will not be forwarded to leadership.")
                print(f"Feedback saved to: {local_file.replace('.json', '-evaluation.json')}")
                print()
                sys.exit(1)

            elif result == "NEEDS_REVISION":
                print()
                print("=" * 60)
                print("⚠️ AI GATEKEEPER: REVISIONS REQUIRED")
                print("=" * 60)
                print()
                print(f"The AI Gatekeeper requires revisions before proceeding (score: {score}/100)")
                print()
                print("Required Revisions:")
                for i, rev in enumerate(ai_evaluation.get("required_revisions", []), 1):
                    print(f"  {i}. [{rev['severity']}] {rev['category']}")
                    print(f"     Issue: {rev['issue']}")
                    print(f"     Fix: {rev['suggested_fix']}")
                    print()
                print("Please revise the project request and resubmit.")
                print(f"Evaluation saved to: {local_file.replace('.json', '-evaluation.json')}")
                print()
                sys.exit(1)

            elif result == "APPROVED":
                print()
                print("=" * 60)
                print("✅ AI GATEKEEPER: AUTO-APPROVED")
                print("=" * 60)
                print()
                print(f"The AI Gatekeeper has auto-approved this project (score: {score}/100)")
                print()
                print("This project meets all criteria and does NOT require leadership review.")
                print("Project can proceed immediately with creation.")
                print()
                # Update project request with approval
                project_request["approval_workflow"]["status"] = "Approved"
                project_request["approval_workflow"]["ai_gatekeeper_decision"] = {
                    "evaluation_id": ai_evaluation["evaluation_id"],
                    "result": "APPROVED",
                    "score": score,
                    "timestamp": ai_evaluation["timestamp"]
                }
                with open(local_file, 'w') as f:
                    json.dump(project_request, f, indent=2)
                print(f"Approval recorded in: {local_file}")
                print()
                return  # Skip Jira creation for auto-approved projects

            else:  # ESCALATE_TO_HUMAN
                print()
                print("=" * 60)
                print("👔 AI GATEKEEPER: ESCALATING TO LEADERSHIP")
                print("=" * 60)
                print()
                print(f"The AI Gatekeeper recommends leadership review (score: {score}/100)")
                print()
                print("The project will be submitted to Jira for human approval.")
                # Continue to Jira creation below
    else:
        print("⚠ AI Gatekeeper evaluation skipped (--skip-ai-eval flag)")
        print()

    # Create Jira issue
    if not args.skip_jira:
        print("Creating Jira approval request...")
        jira_key = create_jira_issue(project_request)

        if jira_key:
            # Update request with Jira key
            project_request["approval_workflow"]["jira_issue_key"] = jira_key
            project_request["approval_workflow"]["status"] = "Pending Approval"

            # Save updated request
            with open(local_file, 'w') as f:
                json.dump(project_request, f, indent=2)

            # Send Slack notification
            send_slack_notification(project_request, jira_key)

            print()
            print("✅ Approval request submitted successfully!")
            print(f"Jira Issue: {JIRA_URL}/browse/{jira_key}")
            print()
            print("Next Steps:")
            print("1. Leadership will review the request in Jira")
            print("2. Required approvers will approve or request more info")
            print("3. Once approved, project can be created with governance controls")
        else:
            print("❌ Failed to create Jira issue. Request saved locally.")
            sys.exit(1)
    else:
        print("⚠ Skipping Jira creation (--skip-jira flag set)")


if __name__ == "__main__":
    main()
