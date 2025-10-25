#!/usr/bin/env python3
"""
AI Agent Token Usage Logger

This script is used by AI agents to log token consumption and efficiency
metrics at the end of each session. Logs are validated against the JSON schema
and stored for analysis and leadership reporting.

Usage:
    python3 scripts/log-token-usage.py --session-id SESSION_ID --user USER_EMAIL \\
        --project PROJECT_NAME --task "DESCRIPTION" --tokens-used 25000 \\
        --tokens-optimal 10000 --files-changed 5 --clarification-rounds 3 \\
        --root-cause vague_requirements --human-score 30 --ai-score 70

Environment Variables:
    TOKEN_LOG_DIR: Directory to store logs (default: logs/token-usage/)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Try to import jsonschema for validation (optional)
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Validation disabled.", file=sys.stderr)
    print("Install with: pip install jsonschema", file=sys.stderr)


def calculate_efficiency_category(efficiency_pct: float) -> str:
    """Determine efficiency category based on percentage."""
    if efficiency_pct >= 80:
        return "optimal"
    elif efficiency_pct >= 60:
        return "acceptable"
    elif efficiency_pct >= 40:
        return "inefficient"
    else:
        return "severely_wasteful"


def calculate_waste_metrics(tokens_used: int, tokens_optimal: int, cost_per_1k: float = 0.003) -> Dict:
    """Calculate waste tokens, cost, and efficiency percentage."""
    waste_tokens = tokens_used - tokens_optimal
    efficiency_pct = (tokens_optimal / tokens_used * 100) if tokens_used > 0 else 0
    waste_cost_usd = (waste_tokens * cost_per_1k) / 1000
    total_cost_usd = (tokens_used * cost_per_1k) / 1000

    return {
        "waste_tokens": waste_tokens,
        "efficiency_pct": round(efficiency_pct, 2),
        "waste_cost_usd": round(waste_cost_usd, 4),
        "total_cost_usd": round(total_cost_usd, 4)
    }


def generate_recommendations(
    root_cause: str,
    patterns_violated: List[str],
    human_score: int,
    efficiency_pct: float
) -> List[str]:
    """Generate specific recommendations based on inefficiency causes."""
    recommendations = []

    if root_cause == "vague_requirements":
        recommendations.append(
            "Provide specific, detailed requirements at the start instead of iterative clarifications"
        )

    if root_cause == "missing_file_paths":
        recommendations.append(
            "Always include exact file paths: /full/path/to/file.txt"
        )

    if "complete_requirements_upfront" in patterns_violated:
        recommendations.append(
            "Review token_optimization.md section 'Demand Complete Requirements Upfront'"
        )

    if "exact_file_paths" in patterns_violated:
        recommendations.append(
            "Specify exact paths to avoid search/guessing overhead"
        )

    if "batch_questions" in patterns_violated:
        recommendations.append(
            "Ask all questions in one message instead of yes/no loops"
        )

    if human_score < 50:
        recommendations.append(
            "Schedule training on Human-AI Interaction Guide (docs/HUMAN-AI-INTERACTION-GUIDE.md)"
        )

    if efficiency_pct < 40:
        recommendations.append(
            "This session was severely wasteful. Consider requiring pre-approval for future AI agent usage."
        )
    elif efficiency_pct >= 80:
        recommendations.append(
            "Excellent session - continue this pattern of clear upfront requirements"
        )

    return recommendations if recommendations else ["No specific recommendations"]


def load_schema(schema_path: Path) -> Optional[Dict]:
    """Load JSON schema from file."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load schema from {schema_path}: {e}", file=sys.stderr)
        return None


def validate_log(log_entry: Dict, schema: Optional[Dict]) -> bool:
    """Validate log entry against schema."""
    if not HAS_JSONSCHEMA or schema is None:
        return True  # Skip validation if not available

    try:
        jsonschema.validate(instance=log_entry, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation error: {e.message}", file=sys.stderr)
        return False


def write_log(log_entry: Dict, log_dir: Path) -> Path:
    """Write log entry to file."""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Use session_id as filename
    session_id = log_entry["session_id"]
    log_file = log_dir / f"{session_id}.json"

    with open(log_file, 'w') as f:
        json.dump(log_entry, f, indent=2)

    return log_file


def main():
    parser = argparse.ArgumentParser(
        description="Log AI agent token usage and efficiency metrics"
    )

    # Required fields
    parser.add_argument("--session-id", required=True, help="Session ID (UUID or timestamp format)")
    parser.add_argument("--user", required=True, help="User email address")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--tokens-used", type=int, required=True, help="Total tokens consumed")
    parser.add_argument("--tokens-optimal", type=int, required=True, help="Estimated optimal token count")
    parser.add_argument("--files-changed", type=int, required=True, help="Number of files modified")

    # Optional fields
    parser.add_argument("--user-name", help="Full name of user")
    parser.add_argument("--clarification-rounds", type=int, default=0, help="Number of clarification exchanges")
    parser.add_argument("--root-cause",
                       choices=["vague_requirements", "missing_file_paths", "unclear_scope",
                               "multiple_approaches_not_specified", "incomplete_context",
                               "midstream_requirement_changes", "ai_agent_error",
                               "technical_issue", "optimal_execution", "other"],
                       default="other", help="Primary cause of inefficiency")
    parser.add_argument("--root-cause-detail", help="Detailed explanation of root cause")
    parser.add_argument("--patterns-violated", nargs="+",
                       choices=["complete_requirements_upfront", "exact_file_paths",
                               "clarify_scope_upfront", "batch_questions",
                               "document_for_future_sessions", "single_pass_execution",
                               "demand_clarity_before_starting", "avoid_yes_no_loops", "none"],
                       default=["none"], help="Interaction patterns violated")
    parser.add_argument("--human-score", type=int, help="Human quality score 0-100")
    parser.add_argument("--ai-score", type=int, help="AI quality score 0-100")
    parser.add_argument("--outcome", choices=["completed", "partial", "abandoned", "blocked"],
                       default="completed", help="Session outcome")
    parser.add_argument("--commits", nargs="+", help="Git commit hashes produced")
    parser.add_argument("--agent-type", default="Claude Sonnet 4.5", help="AI agent type/model")
    parser.add_argument("--cost-per-1k", type=float, default=0.003, help="Cost per 1000 tokens in USD")
    parser.add_argument("--session-notes-created", action="store_true", help="Whether session notes were created")
    parser.add_argument("--environment", choices=["dev", "staging", "prod"], help="Environment")
    parser.add_argument("--urgency", choices=["low", "medium", "high", "critical"], help="Task urgency")
    parser.add_argument("--complexity", choices=["trivial", "simple", "moderate", "complex", "very_complex"],
                       help="Task complexity")

    # Output options
    parser.add_argument("--log-dir", type=Path, help="Directory to store logs (default: logs/token-usage/)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip schema validation")
    parser.add_argument("--dry-run", action="store_true", help="Print log without writing to file")

    args = parser.parse_args()

    # Determine log directory
    log_dir = args.log_dir or Path("logs/token-usage")

    # Calculate metrics
    metrics = calculate_waste_metrics(args.tokens_used, args.tokens_optimal, args.cost_per_1k)

    # Determine efficiency category
    efficiency_category = calculate_efficiency_category(metrics["efficiency_pct"])

    # Generate recommendations
    recommendations = generate_recommendations(
        args.root_cause,
        args.patterns_violated,
        args.human_score or 50,
        metrics["efficiency_pct"]
    )

    # Build log entry
    log_entry = {
        "session_id": args.session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_email": args.user,
        "project_name": args.project,
        "task_description": args.task,
        "tokens_used": args.tokens_used,
        "tokens_optimal": args.tokens_optimal,
        "efficiency_pct": metrics["efficiency_pct"],
        "waste_tokens": metrics["waste_tokens"],
        "waste_cost_usd": metrics["waste_cost_usd"],
        "files_changed": args.files_changed,
        "clarification_rounds": args.clarification_rounds,
        "efficiency_category": efficiency_category,
        "root_cause": args.root_cause,
        "pattern_violated": args.patterns_violated,
        "session_outcome": args.outcome,
        "agent_type": args.agent_type,
        "cost_per_1k_tokens": args.cost_per_1k,
        "total_cost_usd": metrics["total_cost_usd"],
        "recommendations": recommendations,
        "session_notes_created": args.session_notes_created
    }

    # Add optional fields if provided
    if args.user_name:
        log_entry["user_name"] = args.user_name
    if args.root_cause_detail:
        log_entry["root_cause_detail"] = args.root_cause_detail
    if args.human_score is not None:
        log_entry["human_quality_score"] = args.human_score
    if args.ai_score is not None:
        log_entry["ai_quality_score"] = args.ai_score
    if args.commits:
        log_entry["commits"] = args.commits

    # Add metadata if provided
    metadata = {}
    if args.environment:
        metadata["environment"] = args.environment
    if args.urgency:
        metadata["urgency"] = args.urgency
    if args.complexity:
        metadata["complexity"] = args.complexity
    if metadata:
        log_entry["metadata"] = metadata

    # Validate against schema
    if not args.skip_validation:
        # Assuming script is in project_root/scripts/
        schema_path = Path(__file__).parent.parent / "policies/schemas/token-usage.json"
        schema = load_schema(schema_path)

        if not validate_log(log_entry, schema):
            print("Error: Log entry failed schema validation", file=sys.stderr)
            sys.exit(1)

    # Dry run - just print
    if args.dry_run:
        print(json.dumps(log_entry, indent=2))
        sys.exit(0)

    # Write log to file
    log_file = write_log(log_entry, log_dir)

    print(f"✅ Token usage logged successfully")
    print(f"   Session ID: {args.session_id}")
    print(f"   Tokens used: {args.tokens_used:,}")
    print(f"   Efficiency: {metrics['efficiency_pct']:.1f}% ({efficiency_category})")
    print(f"   Waste: {metrics['waste_tokens']:,} tokens (${metrics['waste_cost_usd']:.4f})")
    print(f"   Log file: {log_file}")

    # Print recommendations
    if recommendations and recommendations != ["No specific recommendations"]:
        print(f"\n📋 Recommendations for {args.user}:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

    # Warning for severely wasteful sessions
    if efficiency_category == "severely_wasteful":
        print(f"\n⚠️  WARNING: This session was severely wasteful (< 40% efficient)")
        print(f"   Leadership will be notified via waste report.")


if __name__ == "__main__":
    main()
