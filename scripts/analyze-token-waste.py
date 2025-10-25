#!/usr/bin/env python3
"""
Token Waste Analysis and Reporting

Analyzes token usage logs and generates reports for leadership showing:
- Which humans are providing vague requirements
- Token waste by user, project, and root cause
- Trends over time
- Cost impact

Usage:
    # Generate report for all users
    python3 scripts/analyze-token-waste.py --log-dir logs/token-usage

    # Generate report for specific user
    python3 scripts/analyze-token-waste.py --user youngs@suhlabs.com

    # Generate report for date range
    python3 scripts/analyze-token-waste.py --start-date 2025-10-01 --end-date 2025-10-31

    # Output formats
    python3 scripts/analyze-token-waste.py --format json --output report.json
    python3 scripts/analyze-token-waste.py --format markdown --output report.md
    python3 scripts/analyze-token-waste.py --format html --output report.html
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import statistics


def load_logs(log_dir: Path, start_date: str = None, end_date: str = None, user: str = None) -> List[Dict]:
    """Load all token usage logs from directory with optional filters."""
    logs = []

    if not log_dir.exists():
        print(f"Error: Log directory {log_dir} does not exist", file=sys.stderr)
        return logs

    for log_file in log_dir.glob("*.json"):
        try:
            with open(log_file, 'r') as f:
                log = json.load(f)

                # Apply filters
                if user and log.get("user_email") != user:
                    continue

                log_date = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))

                if start_date:
                    start = datetime.fromisoformat(start_date)
                    if log_date < start:
                        continue

                if end_date:
                    end = datetime.fromisoformat(end_date)
                    if log_date > end:
                        continue

                logs.append(log)
        except Exception as e:
            print(f"Warning: Could not load {log_file}: {e}", file=sys.stderr)

    return logs


def analyze_by_user(logs: List[Dict]) -> Dict:
    """Analyze token waste grouped by user."""
    user_stats = defaultdict(lambda: {
        "total_sessions": 0,
        "total_tokens": 0,
        "total_waste_tokens": 0,
        "total_cost_usd": 0,
        "total_waste_cost_usd": 0,
        "avg_efficiency_pct": [],
        "avg_human_quality_score": [],
        "severely_wasteful_count": 0,
        "optimal_count": 0,
        "root_causes": defaultdict(int),
        "patterns_violated": defaultdict(int),
        "projects": set()
    })

    for log in logs:
        user = log.get("user_email", "unknown")
        stats = user_stats[user]

        stats["total_sessions"] += 1
        stats["total_tokens"] += log.get("tokens_used", 0)
        stats["total_waste_tokens"] += log.get("waste_tokens", 0)
        stats["total_cost_usd"] += log.get("total_cost_usd", 0)
        stats["total_waste_cost_usd"] += log.get("waste_cost_usd", 0)
        stats["avg_efficiency_pct"].append(log.get("efficiency_pct", 0))

        if log.get("human_quality_score") is not None:
            stats["avg_human_quality_score"].append(log["human_quality_score"])

        if log.get("efficiency_category") == "severely_wasteful":
            stats["severely_wasteful_count"] += 1
        elif log.get("efficiency_category") == "optimal":
            stats["optimal_count"] += 1

        stats["root_causes"][log.get("root_cause", "unknown")] += 1

        for pattern in log.get("pattern_violated", []):
            if pattern != "none":
                stats["patterns_violated"][pattern] += 1

        stats["projects"].add(log.get("project_name", "unknown"))

    # Calculate averages
    for user, stats in user_stats.items():
        if stats["avg_efficiency_pct"]:
            stats["avg_efficiency_pct"] = round(statistics.mean(stats["avg_efficiency_pct"]), 2)
        else:
            stats["avg_efficiency_pct"] = 0

        if stats["avg_human_quality_score"]:
            stats["avg_human_quality_score"] = round(statistics.mean(stats["avg_human_quality_score"]), 2)
        else:
            stats["avg_human_quality_score"] = None

        stats["projects"] = list(stats["projects"])
        stats["root_causes"] = dict(stats["root_causes"])
        stats["patterns_violated"] = dict(stats["patterns_violated"])

    return dict(user_stats)


def rank_users_by_waste(user_stats: Dict) -> List[Tuple[str, Dict]]:
    """Rank users by total waste (descending)."""
    return sorted(user_stats.items(), key=lambda x: x[1]["total_waste_cost_usd"], reverse=True)


def generate_markdown_report(logs: List[Dict], user_stats: Dict, start_date: str = None, end_date: str = None) -> str:
    """Generate markdown format report."""
    ranked_users = rank_users_by_waste(user_stats)

    # Calculate totals
    total_sessions = len(logs)
    total_tokens = sum(log.get("tokens_used", 0) for log in logs)
    total_waste_tokens = sum(log.get("waste_tokens", 0) for log in logs)
    total_cost = sum(log.get("total_cost_usd", 0) for log in logs)
    total_waste_cost = sum(log.get("waste_cost_usd", 0) for log in logs)
    avg_efficiency = statistics.mean([log.get("efficiency_pct", 0) for log in logs]) if logs else 0

    report = f"""# Token Waste Analysis Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

    if start_date or end_date:
        report += f"**Period:** {start_date or 'inception'} to {end_date or 'present'}\n"

    report += f"""
## Executive Summary

- **Total Sessions:** {total_sessions:,}
- **Total Tokens Consumed:** {total_tokens:,}
- **Total Tokens Wasted:** {total_waste_tokens:,}
- **Overall Efficiency:** {avg_efficiency:.1f}%
- **Total Cost:** ${total_cost:.2f}
- **Total Wasted Cost:** ${total_waste_cost:.2f}

**Waste Impact:** {(total_waste_cost / total_cost * 100) if total_cost > 0 else 0:.1f}% of AI agent costs are due to inefficient human-AI interactions.

---

## User Rankings by Token Waste

Users ranked by total wasted cost (highest to lowest):

| Rank | User | Sessions | Waste $ | Efficiency | Human Score | Severely Wasteful Sessions |
|------|------|----------|---------|------------|-------------|----------------------------|
"""

    for rank, (user, stats) in enumerate(ranked_users, 1):
        human_score = stats["avg_human_quality_score"]
        human_score_str = f"{human_score:.0f}/100" if human_score is not None else "N/A"

        report += f"| {rank} | {user} | {stats['total_sessions']} | ${stats['total_waste_cost_usd']:.2f} | {stats['avg_efficiency_pct']:.1f}% | {human_score_str} | {stats['severely_wasteful_count']} |\n"

    report += "\n---\n\n## Detailed User Analysis\n\n"

    for rank, (user, stats) in enumerate(ranked_users, 1):
        user_name = user.split('@')[0]  # Extract name before @
        waste_pct = (stats['total_waste_cost_usd'] / stats['total_cost_usd'] * 100) if stats['total_cost_usd'] > 0 else 0

        report += f"""### {rank}. {user}

**Performance Metrics:**
- **Total Sessions:** {stats['total_sessions']}
- **Average Efficiency:** {stats['avg_efficiency_pct']:.1f}%
- **Human Quality Score:** {stats['avg_human_quality_score']:.0f}/100 if stats['avg_human_quality_score'] is not None else "Not scored"
- **Optimal Sessions:** {stats['optimal_count']} ({stats['optimal_count'] / stats['total_sessions'] * 100:.1f}%)
- **Severely Wasteful Sessions:** {stats['severely_wasteful_count']} ({stats['severely_wasteful_count'] / stats['total_sessions'] * 100:.1f}%)

**Cost Impact:**
- **Total Tokens Used:** {stats['total_tokens']:,}
- **Tokens Wasted:** {stats['total_waste_tokens']:,}
- **Total Cost:** ${stats['total_cost_usd']:.2f}
- **Wasted Cost:** ${stats['total_waste_cost_usd']:.2f} ({waste_pct:.1f}% of user's total)

**Primary Causes of Waste:**
"""

        for cause, count in sorted(stats['root_causes'].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{cause.replace('_', ' ').title()}**: {count} sessions\n"

        if stats['patterns_violated']:
            report += "\n**Most Violated Patterns:**\n"
            for pattern, count in sorted(stats['patterns_violated'].items(), key=lambda x: x[1], reverse=True)[:3]:
                report += f"- **{pattern.replace('_', ' ').title()}**: {count} times\n"

        report += f"\n**Projects Worked On:** {', '.join(stats['projects'])}\n\n"

        # Recommendations
        if stats['avg_efficiency_pct'] < 60:
            report += "**🚨 RECOMMENDATION:** This user requires immediate training on Human-AI Interaction Guide.\n\n"
        elif stats['avg_efficiency_pct'] < 80:
            report += "**⚠️  RECOMMENDATION:** Review token optimization protocols with this user.\n\n"
        else:
            report += "**✅ RECOMMENDATION:** User demonstrates good efficiency practices.\n\n"

        report += "---\n\n"

    # Top root causes across all users
    all_causes = defaultdict(int)
    for log in logs:
        all_causes[log.get("root_cause", "unknown")] += 1

    report += "## Top Root Causes of Waste (All Users)\n\n"
    for cause, count in sorted(all_causes.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(logs) * 100 if logs else 0
        report += f"- **{cause.replace('_', ' ').title()}**: {count} sessions ({pct:.1f}%)\n"

    report += "\n---\n\n## Recommendations for Leadership\n\n"

    # Generate leadership recommendations
    if total_waste_cost > 100:
        report += "1. **URGENT:** Token waste exceeds $100. Implement mandatory training program.\n"
    elif total_waste_cost > 50:
        report += "1. **HIGH PRIORITY:** Token waste exceeds $50. Schedule training for top offenders.\n"

    high_waste_users = [user for user, stats in ranked_users if stats['avg_efficiency_pct'] < 60]
    if high_waste_users:
        report += f"2. **Require pre-approval for AI agent usage** for these users until efficiency improves: {', '.join(high_waste_users)}\n"

    report += f"3. **Mandate use of token logging** for all AI agent sessions above {50000} tokens.\n"
    report += f"4. **Distribute Human-AI Interaction Guide** to all users with efficiency <80%.\n"
    report += f"5. **Consider API wrapper implementation** (Option B) to automate token tracking.\n"

    report += "\n---\n\n*Report generated by AI Agent Governance Framework v2.1*\n"

    return report


def generate_json_report(logs: List[Dict], user_stats: Dict) -> str:
    """Generate JSON format report."""
    total_sessions = len(logs)
    total_tokens = sum(log.get("tokens_used", 0) for log in logs)
    total_waste_tokens = sum(log.get("waste_tokens", 0) for log in logs)
    total_cost = sum(log.get("total_cost_usd", 0) for log in logs)
    total_waste_cost = sum(log.get("waste_cost_usd", 0) for log in logs)
    avg_efficiency = statistics.mean([log.get("efficiency_pct", 0) for log in logs]) if logs else 0

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_sessions": total_sessions,
            "total_tokens": total_tokens,
            "total_waste_tokens": total_waste_tokens,
            "total_cost_usd": round(total_cost, 2),
            "total_waste_cost_usd": round(total_waste_cost, 2),
            "avg_efficiency_pct": round(avg_efficiency, 2),
            "waste_impact_pct": round((total_waste_cost / total_cost * 100) if total_cost > 0 else 0, 2)
        },
        "user_rankings": rank_users_by_waste(user_stats),
        "user_details": user_stats
    }

    return json.dumps(report, indent=2)


def generate_html_report(markdown_report: str) -> str:
    """Generate HTML format report (simple wrapper around markdown)."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Token Waste Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }}
        h3 {{ color: #666; margin-top: 20px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{ background-color: #f9f9f9; }}
        .summary {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .warning {{ color: #ff6b6b; font-weight: bold; }}
        .success {{ color: #51cf66; font-weight: bold; }}
        .info {{ color: #339af0; font-weight: bold; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <pre>{markdown_report}</pre>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Analyze token waste and generate reports")

    parser.add_argument("--log-dir", type=Path, default=Path("logs/token-usage"),
                       help="Directory containing token usage logs")
    parser.add_argument("--user", help="Filter by specific user email")
    parser.add_argument("--start-date", help="Start date (ISO format: 2025-10-01)")
    parser.add_argument("--end-date", help="End date (ISO format: 2025-10-31)")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown",
                       help="Output format")
    parser.add_argument("--output", type=Path, help="Output file (default: stdout)")
    parser.add_argument("--min-waste", type=float, help="Only show users with waste above this amount (USD)")

    args = parser.parse_args()

    # Load logs
    logs = load_logs(args.log_dir, args.start_date, args.end_date, args.user)

    if not logs:
        print("No logs found matching criteria", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(logs)} log entries", file=sys.stderr)

    # Analyze by user
    user_stats = analyze_by_user(logs)

    # Filter by minimum waste if specified
    if args.min_waste:
        user_stats = {
            user: stats for user, stats in user_stats.items()
            if stats["total_waste_cost_usd"] >= args.min_waste
        }

    # Generate report
    if args.format == "markdown":
        report = generate_markdown_report(logs, user_stats, args.start_date, args.end_date)
    elif args.format == "json":
        report = generate_json_report(logs, user_stats)
    elif args.format == "html":
        markdown_report = generate_markdown_report(logs, user_stats, args.start_date, args.end_date)
        report = generate_html_report(markdown_report)

    # Output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
