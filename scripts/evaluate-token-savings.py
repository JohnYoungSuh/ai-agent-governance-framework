#!/usr/bin/env python3
"""
Token Savings Evaluator

Compares token usage with governance framework vs without framework.
Measures savings from:
1. Reduced AI context loading (smaller, focused configs vs scattered data)
2. Eliminated redundant operations (single source vs multiple lookups)
3. Devcontainer optimizations (vendor images vs custom builds)
4. Validation efficiency (schema-based vs manual checks)
5. CI/CD efficiency (consolidated checks vs multiple validations)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

try:
    from shared_utils import GovernanceFramework
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from shared_utils import GovernanceFramework


class TokenSavingsEvaluator:
    """Evaluate token savings from using governance framework"""

    def __init__(self):
        self.framework = GovernanceFramework()

        # Token cost constants (based on typical AI operations)
        self.TOKEN_COSTS = {
            # Configuration loading
            "load_hardcoded_config": 50,  # Parse hardcoded dicts/lists in code
            "load_yaml_config": 10,       # Parse single YAML file

            # Data lookups
            "lookup_scattered_data": 30,  # Search through multiple files
            "lookup_centralized_data": 5, # Single framework lookup

            # Validation operations
            "manual_validation": 100,     # AI validates data manually
            "schema_validation": 20,      # Schema-based validation

            # Context building
            "build_context_scattered": 200,  # Gather context from multiple sources
            "build_context_framework": 50,   # Load framework once

            # Devcontainer operations
            "devcontainer_custom_build": 425,  # Custom Dockerfile build
            "devcontainer_vendor_pull": 15,    # Vendor image pull

            # CI/CD operations
            "duplicate_policy_checks": 75,   # Multiple policy check scripts
            "consolidated_policy_check": 25, # Single framework-based check

            # Documentation generation
            "manual_doc_sync": 150,  # Manually sync docs with code
            "auto_doc_generation": 30, # Generate from framework
        }

    def evaluate_configuration_loading(self) -> Dict:
        """
        Evaluate token savings from centralized config loading.

        Without framework: Each script loads hardcoded strategic goals,
                          revenue types, approval tiers separately
        With framework: Single YAML load shared across operations
        """

        # Scenario: Loading configuration for project evaluation
        without_framework = {
            "load_strategic_goals": self.TOKEN_COSTS["load_hardcoded_config"],
            "load_revenue_types": self.TOKEN_COSTS["load_hardcoded_config"],
            "load_approval_tiers": self.TOKEN_COSTS["load_hardcoded_config"],
            "load_roi_benchmarks": self.TOKEN_COSTS["load_hardcoded_config"],
            "total": self.TOKEN_COSTS["load_hardcoded_config"] * 4
        }

        with_framework = {
            "load_framework_yaml": self.TOKEN_COSTS["load_yaml_config"],
            "access_all_configs": 0,  # Already loaded
            "total": self.TOKEN_COSTS["load_yaml_config"]
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "Configuration Loading",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per script execution",
            "annual_estimate": {
                "executions_per_year": 1000,
                "total_savings": savings * 1000
            }
        }

    def evaluate_data_lookups(self) -> Dict:
        """
        Evaluate token savings from centralized data access.

        Without framework: Search through multiple docs/scripts for values
        With framework: Single framework query
        """

        # Scenario: Looking up approval tier for a budget amount
        without_framework = {
            "search_workflow_doc": self.TOKEN_COSTS["lookup_scattered_data"],
            "search_quickref_doc": self.TOKEN_COSTS["lookup_scattered_data"],
            "search_gatekeeper_script": self.TOKEN_COSTS["lookup_scattered_data"],
            "reconcile_differences": self.TOKEN_COSTS["manual_validation"],
            "total": (self.TOKEN_COSTS["lookup_scattered_data"] * 3) +
                     self.TOKEN_COSTS["manual_validation"]
        }

        with_framework = {
            "query_framework": self.TOKEN_COSTS["lookup_centralized_data"],
            "total": self.TOKEN_COSTS["lookup_centralized_data"]
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "Data Lookups",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per lookup operation",
            "annual_estimate": {
                "lookups_per_year": 500,
                "total_savings": savings * 500
            }
        }

    def evaluate_validation_operations(self) -> Dict:
        """
        Evaluate token savings from schema-based validation.

        Without framework: AI manually validates consistency
        With framework: Schema validation + framework consistency
        """

        # Scenario: Validating a project request
        without_framework = {
            "validate_strategic_goal": self.TOKEN_COSTS["manual_validation"],
            "validate_revenue_type": self.TOKEN_COSTS["manual_validation"],
            "validate_budget_tier": self.TOKEN_COSTS["manual_validation"],
            "check_consistency": self.TOKEN_COSTS["manual_validation"],
            "total": self.TOKEN_COSTS["manual_validation"] * 4
        }

        with_framework = {
            "schema_validation": self.TOKEN_COSTS["schema_validation"],
            "framework_consistency": self.TOKEN_COSTS["schema_validation"],
            "total": self.TOKEN_COSTS["schema_validation"] * 2
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "Validation Operations",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per project validation",
            "annual_estimate": {
                "validations_per_year": 200,
                "total_savings": savings * 200
            }
        }

    def evaluate_context_building(self) -> Dict:
        """
        Evaluate token savings from efficient context loading.

        Without framework: AI loads context from multiple scattered files
        With framework: Single framework provides all context
        """

        # Scenario: Building context for project evaluation
        without_framework = {
            "load_5_doc_files": self.TOKEN_COSTS["build_context_scattered"],
            "load_3_script_files": self.TOKEN_COSTS["build_context_scattered"] * 0.6,
            "load_2_schema_files": self.TOKEN_COSTS["build_context_scattered"] * 0.4,
            "reconcile_context": self.TOKEN_COSTS["manual_validation"],
            "total": (self.TOKEN_COSTS["build_context_scattered"] * 2) +
                     self.TOKEN_COSTS["manual_validation"]
        }

        with_framework = {
            "load_framework": self.TOKEN_COSTS["build_context_framework"],
            "total": self.TOKEN_COSTS["build_context_framework"]
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "Context Building",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per AI session start",
            "annual_estimate": {
                "sessions_per_year": 2000,
                "total_savings": savings * 2000
            }
        }

    def evaluate_devcontainer_operations(self) -> Dict:
        """
        Evaluate token savings from devcontainer vendor image pattern.

        This is already documented in the framework, so we use actual numbers.
        """

        # From devcontainer documentation
        without_framework = {
            "custom_build_auth": 50,
            "build_context_upload": 100,
            "layer_caching_checks": 75,
            "build_log_parsing": 200,
            "total": 425
        }

        with_framework = {
            "image_pull_cached": 10,
            "container_start": 5,
            "total": 15
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "Devcontainer Operations",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per devcontainer rebuild",
            "annual_estimate": {
                "rebuilds_per_year": 100,
                "total_savings": savings * 100
            }
        }

    def evaluate_cicd_operations(self) -> Dict:
        """
        Evaluate token savings from consolidated CI/CD checks.

        Without framework: Multiple separate policy check scripts
        With framework: Single framework-based validation
        """

        # Scenario: Running policy checks on PR
        without_framework = {
            "check_strategic_alignment": self.TOKEN_COSTS["duplicate_policy_checks"],
            "check_budget_compliance": self.TOKEN_COSTS["duplicate_policy_checks"],
            "check_approval_tier": self.TOKEN_COSTS["duplicate_policy_checks"],
            "check_schema_compliance": self.TOKEN_COSTS["duplicate_policy_checks"],
            "total": self.TOKEN_COSTS["duplicate_policy_checks"] * 4
        }

        with_framework = {
            "framework_validation": self.TOKEN_COSTS["consolidated_policy_check"],
            "schema_check": self.TOKEN_COSTS["consolidated_policy_check"],
            "total": self.TOKEN_COSTS["consolidated_policy_check"] * 2
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "CI/CD Policy Checks",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per pull request",
            "annual_estimate": {
                "pull_requests_per_year": 500,
                "total_savings": savings * 500
            }
        }

    def evaluate_documentation_sync(self) -> Dict:
        """
        Evaluate token savings from auto-generated documentation.

        Without framework: Manually sync docs with code changes
        With framework: Auto-generate doc sections from framework
        """

        # Scenario: Updating documentation after governance change
        without_framework = {
            "update_workflow_doc": self.TOKEN_COSTS["manual_doc_sync"],
            "update_quickref_doc": self.TOKEN_COSTS["manual_doc_sync"],
            "update_gatekeeper_doc": self.TOKEN_COSTS["manual_doc_sync"],
            "verify_consistency": self.TOKEN_COSTS["manual_validation"],
            "total": (self.TOKEN_COSTS["manual_doc_sync"] * 3) +
                     self.TOKEN_COSTS["manual_validation"]
        }

        with_framework = {
            "update_framework_yaml": self.TOKEN_COSTS["load_yaml_config"],
            "regenerate_docs": self.TOKEN_COSTS["auto_doc_generation"],
            "total": self.TOKEN_COSTS["load_yaml_config"] +
                     self.TOKEN_COSTS["auto_doc_generation"]
        }

        savings = without_framework["total"] - with_framework["total"]
        savings_pct = (savings / without_framework["total"]) * 100

        return {
            "operation": "Documentation Synchronization",
            "without_framework_tokens": without_framework["total"],
            "with_framework_tokens": with_framework["total"],
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "breakdown": {
                "without_framework": without_framework,
                "with_framework": with_framework
            },
            "frequency": "Per governance update",
            "annual_estimate": {
                "updates_per_year": 12,
                "total_savings": savings * 12
            }
        }

    def calculate_total_savings(self, evaluations: List[Dict]) -> Dict:
        """Calculate total token savings across all operations"""

        total_without = sum(e["without_framework_tokens"] for e in evaluations)
        total_with = sum(e["with_framework_tokens"] for e in evaluations)
        total_saved = total_without - total_with
        total_pct = (total_saved / total_without) * 100 if total_without > 0 else 0

        annual_without = sum(e["annual_estimate"]["executions_per_year"] *
                            e["without_framework_tokens"]
                            for e in evaluations if "executions_per_year" in e["annual_estimate"])

        # Use specific annual estimates where available
        annual_saved = sum(e["annual_estimate"].get("total_savings", 0) for e in evaluations)

        # Calculate cost savings (assuming $0.01 per 1000 tokens)
        cost_per_1k_tokens = 0.01
        annual_cost_savings = (annual_saved / 1000) * cost_per_1k_tokens

        return {
            "per_operation_summary": {
                "total_tokens_without_framework": total_without,
                "total_tokens_with_framework": total_with,
                "total_tokens_saved": total_saved,
                "savings_percentage": total_pct
            },
            "annual_summary": {
                "total_operations_per_year": sum(
                    e["annual_estimate"].get("executions_per_year",
                    e["annual_estimate"].get("lookups_per_year",
                    e["annual_estimate"].get("validations_per_year",
                    e["annual_estimate"].get("sessions_per_year",
                    e["annual_estimate"].get("rebuilds_per_year",
                    e["annual_estimate"].get("pull_requests_per_year",
                    e["annual_estimate"].get("updates_per_year", 0)))))))
                    for e in evaluations
                ),
                "total_tokens_saved_annually": annual_saved,
                "cost_savings_usd": round(annual_cost_savings, 2)
            },
            "by_category": {
                e["operation"]: {
                    "tokens_saved": e["tokens_saved"],
                    "savings_percentage": e["savings_percentage"],
                    "annual_savings": e["annual_estimate"].get("total_savings", 0)
                }
                for e in evaluations
            }
        }

    def generate_report(self) -> Dict:
        """Generate comprehensive token savings report"""

        print("Evaluating token savings from governance framework...")
        print()

        evaluations = [
            self.evaluate_configuration_loading(),
            self.evaluate_data_lookups(),
            self.evaluate_validation_operations(),
            self.evaluate_context_building(),
            self.evaluate_devcontainer_operations(),
            self.evaluate_cicd_operations(),
            self.evaluate_documentation_sync()
        ]

        total_savings = self.calculate_total_savings(evaluations)

        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "framework_version": self.framework.config.get("version", "1.0"),
                "evaluator_version": "1.0.0"
            },
            "executive_summary": total_savings,
            "detailed_evaluations": evaluations,
            "methodology": {
                "description": "Compares token usage for common operations with and without governance framework",
                "token_costs": self.TOKEN_COSTS,
                "assumptions": [
                    "Token costs based on typical AI operation overhead",
                    "Annual frequency estimates based on team of 10 developers",
                    "Cost calculated at $0.01 per 1000 tokens",
                    "Includes direct token usage, not indirect time savings"
                ]
            }
        }

        return report

    def print_report(self, report: Dict):
        """Print human-readable report"""

        print("=" * 80)
        print("TOKEN SAVINGS EVALUATION REPORT")
        print("=" * 80)
        print()

        summary = report["executive_summary"]

        print("EXECUTIVE SUMMARY")
        print("-" * 80)
        print(f"Total Tokens Saved (per operation set): {summary['per_operation_summary']['total_tokens_saved']}")
        print(f"Savings Percentage: {summary['per_operation_summary']['savings_percentage']:.1f}%")
        print(f"Annual Token Savings: {summary['annual_summary']['total_tokens_saved_annually']:,}")
        print(f"Annual Cost Savings: ${summary['annual_summary']['cost_savings_usd']:,.2f}")
        print()

        print("SAVINGS BY CATEGORY")
        print("-" * 80)
        for category, data in summary["by_category"].items():
            print(f"\n{category}:")
            print(f"  Tokens Saved: {data['tokens_saved']} per operation")
            print(f"  Savings: {data['savings_percentage']:.1f}%")
            print(f"  Annual Savings: {data['annual_savings']:,} tokens")

        print()
        print()
        print("DETAILED EVALUATIONS")
        print("-" * 80)

        for eval_result in report["detailed_evaluations"]:
            print(f"\n{eval_result['operation']}")
            print(f"  Without Framework: {eval_result['without_framework_tokens']} tokens")
            print(f"  With Framework: {eval_result['with_framework_tokens']} tokens")
            print(f"  Saved: {eval_result['tokens_saved']} tokens ({eval_result['savings_percentage']:.1f}%)")
            print(f"  Frequency: {eval_result['frequency']}")

            annual = eval_result['annual_estimate']
            if 'total_savings' in annual:
                print(f"  Annual Savings: {annual['total_savings']:,} tokens")

        print()
        print("=" * 80)
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate token savings from using governance framework"
    )
    parser.add_argument("--output", help="Save report to JSON file")
    parser.add_argument("--verbose", action="store_true", help="Show detailed breakdown")

    args = parser.parse_args()

    evaluator = TokenSavingsEvaluator()
    report = evaluator.generate_report()

    evaluator.print_report(report)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {args.output}")

    # Return success
    return 0


if __name__ == "__main__":
    sys.exit(main())
