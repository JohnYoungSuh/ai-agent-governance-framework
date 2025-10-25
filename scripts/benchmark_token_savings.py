#!/usr/bin/env python3
"""
Token Savings Benchmark Calculator
Version: v1.0
Date: 2025-10-25

Validates token efficiency claims for the token-efficient governance system.
Provides detailed calculation assumptions and savings projections.

Usage:
    python3 benchmark_token_savings.py --cache-hit-rate 0.60 --requests 1000
"""

import argparse
import json
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Model token usage configuration"""
    name: str
    avg_input_tokens: int
    avg_output_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float

    @property
    def avg_total_tokens(self) -> int:
        return self.avg_input_tokens + self.avg_output_tokens

    @property
    def cost_per_request(self) -> float:
        """Calculate cost per request in USD"""
        input_cost = (self.avg_input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (self.avg_output_tokens / 1000) * self.cost_per_1k_output
        return input_cost + output_cost


# ============================================================================
# MODEL CONFIGURATIONS (Based on actual API pricing as of Oct 2025)
# ============================================================================

SMALL_MODEL = ModelConfig(
    name="Gemini 2.0 Flash Thinking",
    avg_input_tokens=80,   # Prompt template + request
    avg_output_tokens=120,  # JSON response
    cost_per_1k_input=0.0001,
    cost_per_1k_output=0.0002
)

LARGE_MODEL = ModelConfig(
    name="Claude Opus 4",
    avg_input_tokens=500,   # Full governance context + examples
    avg_output_tokens=300,  # Detailed decision with reasoning
    cost_per_1k_input=0.015,
    cost_per_1k_output=0.075
)

# ============================================================================
# ROUTING ASSUMPTIONS
# ============================================================================

class RoutingAssumptions:
    """Assumptions for token efficiency calculations"""

    # Cache hit rate (what percentage of requests hit cache)
    # Conservative: 50%, Realistic: 60%, Optimistic: 70%
    CACHE_HIT_RATE = 0.60

    # Intent router accuracy (what % can be handled by simple rules)
    # Conservative: 30%, Realistic: 35%, Optimistic: 40%
    SIMPLE_RULES_RATE = 0.35

    # Large model escalation rate (complex decisions)
    # Conservative: 15%, Realistic: 5%, Optimistic: 2%
    LARGE_MODEL_RATE = 0.05

    # Validation check
    @classmethod
    def validate(cls):
        total = cls.CACHE_HIT_RATE + cls.SIMPLE_RULES_RATE + cls.LARGE_MODEL_RATE
        assert abs(total - 1.0) < 0.01, f"Rates must sum to 1.0, got {total}"

    @classmethod
    def to_dict(cls):
        return {
            "cache_hit_rate": cls.CACHE_HIT_RATE,
            "simple_rules_rate": cls.SIMPLE_RULES_RATE,
            "large_model_rate": cls.LARGE_MODEL_RATE
        }


# ============================================================================
# TOKEN CALCULATION LOGIC
# ============================================================================

def calculate_baseline_tokens(num_requests: int) -> Dict[str, Any]:
    """
    Calculate baseline tokens if ALL requests go to large model
    (No optimization)
    """
    total_tokens = num_requests * LARGE_MODEL.avg_total_tokens
    total_cost = num_requests * LARGE_MODEL.cost_per_request

    return {
        "num_requests": num_requests,
        "model": LARGE_MODEL.name,
        "tokens_per_request": LARGE_MODEL.avg_total_tokens,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 2),
        "breakdown": {
            "input_tokens": num_requests * LARGE_MODEL.avg_input_tokens,
            "output_tokens": num_requests * LARGE_MODEL.avg_output_tokens
        }
    }


def calculate_optimized_tokens(num_requests: int, assumptions: RoutingAssumptions) -> Dict[str, Any]:
    """
    Calculate optimized tokens with cache + routing
    """
    # Validate assumptions
    assumptions.validate()

    # Calculate request distribution
    cache_hits = int(num_requests * assumptions.CACHE_HIT_RATE)
    simple_rules = int(num_requests * assumptions.SIMPLE_RULES_RATE)
    large_model = int(num_requests * assumptions.LARGE_MODEL_RATE)

    # Adjust for rounding
    diff = num_requests - (cache_hits + simple_rules + large_model)
    if diff > 0:
        cache_hits += diff  # Add remainder to cache hits

    # Token costs per route
    # Route 1: Cache Hit
    #   - Small model classifier: 80 input + 120 output = 200 tokens
    #   - Cached result retrieval: 0 tokens
    cache_tokens_per_request = SMALL_MODEL.avg_total_tokens
    cache_total_tokens = cache_hits * cache_tokens_per_request
    cache_total_cost = cache_hits * SMALL_MODEL.cost_per_request

    # Route 2: Simple Rules
    #   - Small model classifier: 200 tokens
    #   - Small model intent router: 200 tokens
    #   - Simple rule execution: 0 tokens
    simple_tokens_per_request = SMALL_MODEL.avg_total_tokens * 2  # Classifier + Router
    simple_total_tokens = simple_rules * simple_tokens_per_request
    simple_total_cost = simple_rules * (SMALL_MODEL.cost_per_request * 2)

    # Route 3: Large Model Escalation
    #   - Small model classifier: 200 tokens
    #   - Large model decision: 800 tokens
    large_tokens_per_request = SMALL_MODEL.avg_total_tokens + LARGE_MODEL.avg_total_tokens
    large_total_tokens = large_model * large_tokens_per_request
    large_total_cost = large_model * (SMALL_MODEL.cost_per_request + LARGE_MODEL.cost_per_request)

    # Totals
    total_tokens = cache_total_tokens + simple_total_tokens + large_total_tokens
    total_cost = cache_total_cost + simple_total_cost + large_total_cost

    return {
        "num_requests": num_requests,
        "routing_distribution": {
            "cache_hits": cache_hits,
            "simple_rules": simple_rules,
            "large_model_escalation": large_model
        },
        "tokens_per_route": {
            "cache_hit": cache_tokens_per_request,
            "simple_rules": simple_tokens_per_request,
            "large_model": large_tokens_per_request
        },
        "total_tokens_per_route": {
            "cache_hits": cache_total_tokens,
            "simple_rules": simple_total_tokens,
            "large_model": large_total_tokens
        },
        "total_tokens": total_tokens,
        "avg_tokens_per_request": round(total_tokens / num_requests, 1),
        "total_cost_usd": round(total_cost, 2),
        "cost_per_request_usd": round(total_cost / num_requests, 4)
    }


def calculate_savings(baseline: Dict, optimized: Dict) -> Dict[str, Any]:
    """Calculate savings metrics"""
    token_savings = baseline["total_tokens"] - optimized["total_tokens"]
    token_savings_pct = (token_savings / baseline["total_tokens"]) * 100

    cost_savings = baseline["total_cost_usd"] - optimized["total_cost_usd"]
    cost_savings_pct = (cost_savings / baseline["total_cost_usd"]) * 100

    return {
        "token_savings": token_savings,
        "token_savings_pct": round(token_savings_pct, 2),
        "cost_savings_usd": round(cost_savings, 2),
        "cost_savings_pct": round(cost_savings_pct, 2),
        "avg_tokens_reduction": {
            "baseline": baseline["tokens_per_request"],
            "optimized": optimized["avg_tokens_per_request"],
            "reduction": baseline["tokens_per_request"] - optimized["avg_tokens_per_request"]
        }
    }


def generate_report(num_requests: int, assumptions: RoutingAssumptions) -> Dict[str, Any]:
    """Generate full token savings report"""
    baseline = calculate_baseline_tokens(num_requests)
    optimized = calculate_optimized_tokens(num_requests, assumptions)
    savings = calculate_savings(baseline, optimized)

    return {
        "metadata": {
            "version": "v1.0",
            "date": "2025-10-25",
            "framework": "AI Agent Governance Framework"
        },
        "assumptions": {
            "routing": assumptions.to_dict(),
            "models": {
                "small": {
                    "name": SMALL_MODEL.name,
                    "avg_tokens": SMALL_MODEL.avg_total_tokens,
                    "cost_per_request": SMALL_MODEL.cost_per_request
                },
                "large": {
                    "name": LARGE_MODEL.name,
                    "avg_tokens": LARGE_MODEL.avg_total_tokens,
                    "cost_per_request": LARGE_MODEL.cost_per_request
                }
            }
        },
        "baseline_scenario": baseline,
        "optimized_scenario": optimized,
        "savings": savings,
        "validation": {
            "meets_70pct_target": savings["token_savings_pct"] >= 70.0,
            "meets_90pct_target": savings["token_savings_pct"] >= 90.0
        }
    }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Calculate and validate token savings for governance system"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=1000,
        help="Number of requests to simulate (default: 1000)"
    )
    parser.add_argument(
        "--cache-hit-rate",
        type=float,
        default=0.60,
        help="Cache hit rate (0.0-1.0, default: 0.60)"
    )
    parser.add_argument(
        "--simple-rules-rate",
        type=float,
        default=0.35,
        help="Simple rules handling rate (0.0-1.0, default: 0.35)"
    )
    parser.add_argument(
        "--large-model-rate",
        type=float,
        default=0.05,
        help="Large model escalation rate (0.0-1.0, default: 0.05)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    # Update assumptions
    RoutingAssumptions.CACHE_HIT_RATE = args.cache_hit_rate
    RoutingAssumptions.SIMPLE_RULES_RATE = args.simple_rules_rate
    RoutingAssumptions.LARGE_MODEL_RATE = args.large_model_rate

    # Generate report
    report = generate_report(args.requests, RoutingAssumptions)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        # Text format
        print("=" * 80)
        print("TOKEN EFFICIENCY BENCHMARK REPORT")
        print("=" * 80)
        print(f"\nSimulation: {args.requests:,} requests")
        print(f"\nRouting Distribution:")
        print(f"  Cache Hits:      {report['optimized_scenario']['routing_distribution']['cache_hits']:>6} ({args.cache_hit_rate:.0%})")
        print(f"  Simple Rules:    {report['optimized_scenario']['routing_distribution']['simple_rules']:>6} ({args.simple_rules_rate:.0%})")
        print(f"  Large Model:     {report['optimized_scenario']['routing_distribution']['large_model_escalation']:>6} ({args.large_model_rate:.0%})")

        print(f"\nBaseline (No Optimization):")
        print(f"  Total Tokens:    {report['baseline_scenario']['total_tokens']:>12,}")
        print(f"  Total Cost:      ${report['baseline_scenario']['total_cost_usd']:>11,.2f}")
        print(f"  Avg Tokens/Req:  {report['baseline_scenario']['tokens_per_request']:>12,}")

        print(f"\nOptimized (With Cache + Router):")
        print(f"  Total Tokens:    {report['optimized_scenario']['total_tokens']:>12,}")
        print(f"  Total Cost:      ${report['optimized_scenario']['total_cost_usd']:>11,.2f}")
        print(f"  Avg Tokens/Req:  {report['optimized_scenario']['avg_tokens_per_request']:>12,.1f}")

        print(f"\n{'SAVINGS':^80}")
        print(f"  Token Reduction: {report['savings']['token_savings']:>12,} ({report['savings']['token_savings_pct']:.1f}%)")
        print(f"  Cost Reduction:  ${report['savings']['cost_savings_usd']:>11,.2f} ({report['savings']['cost_savings_pct']:.1f}%)")

        print(f"\n{'VALIDATION':^80}")
        print(f"  Meets 70% Target: {'✅ YES' if report['validation']['meets_70pct_target'] else '❌ NO'}")
        print(f"  Meets 90% Target: {'✅ YES' if report['validation']['meets_90pct_target'] else '❌ NO'}")

        print("=" * 80)


if __name__ == "__main__":
    main()
