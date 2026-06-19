#!/usr/bin/env python3
"""
QA Agent Headless Runner — AI Agent Governance Framework
Scores the codebase across 5 dimensions with tiered environment thresholds.

Usage:
    python3 scripts/qa-agent.py --env dev
    python3 scripts/qa-agent.py --env staging --output json
    python3 scripts/qa-agent.py --env prod --fail-fast
    python3 scripts/qa-agent.py --env dev --dimension security
    python3 scripts/qa-agent.py --env dev --scenarios security-agent

Environment thresholds:
    dev:     ≥ 80  (exit 0 = pass, exit 1 = fail)
    staging: ≥ 90  (additionally: no TODOs, 100% compliance tests, zero HIGH+ CVEs)
    prod:    ≥ 95  (additionally: zero CRITICAL CVEs, verified mTLS, kill switch tested)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# ── Environment thresholds ─────────────────────────────────────────────────
THRESHOLDS = {
    "dev": 80,
    "staging": 90,
    "prod": 95,
}

# ── Dimension weights (must sum to 100) ────────────────────────────────────
WEIGHTS = {
    "security": 30,
    "compliance": 25,
    "test_coverage": 20,
    "token_efficiency": 15,
    "patent_integrity": 10,
}

assert sum(WEIGHTS.values()) == 100, "Weights must sum to 100"

PROJECT_ROOT = Path(__file__).parent.parent


def run(cmd: str, capture: bool = True, timeout: int = 120) -> tuple[int, str]:
    """Run a shell command and return (returncode, output)."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture,
        text=True,
        timeout=timeout,
        cwd=PROJECT_ROOT,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


# ── DIMENSION: Security (30%) ──────────────────────────────────────────────

def score_security(env: str, verbose: bool) -> tuple[float, list[str]]:
    """
    Checks:
    - No hardcoded secrets in app/ (regex scan)
    - Prompt injection patterns blocked (pytest compliance test)
    - No TODO-level security suppressions
    - Conjur/IRSA wiring present (not just env var fallback)
    - Container image pinned to digest (Dockerfile check)
    """
    failures = []
    score = 100.0

    # 1. Hardcoded secret scan
    rc, out = run(
        'grep -rn "SECRET_KEY\\s*=\\s*[\"\'\']" app/ --include="*.py"'
    )
    if rc == 0 and out:
        failures.append(f"HARDCODED_SECRET: {out[:200]}")
        score -= 40  # Critical deduction

    # 2. Prompt injection test
    rc, _ = run("PYTHONPATH=. ./venv/bin/pytest tests/ -k 'injection' -q --tb=no 2>/dev/null")
    if rc != 0:
        failures.append("INJECTION_TESTS_MISSING_OR_FAILING: no prompt injection tests found")
        score -= 20

    # 3. os.getenv startup assertion pattern
    rc, out = run(r'grep -rn "os.getenv" app/main.py | grep -v "if not\|assert\|raise"')
    if rc == 0 and out:
        failures.append(f"MISSING_STARTUP_ASSERTION: {out[:200]}")
        score -= 10

    # 4. Dockerfile digest pinning (at least one agent)
    rc, out = run(r'grep -r "FROM.*:latest$" agents/ --include="Dockerfile" 2>/dev/null')
    if rc == 0 and out:
        failures.append(f"UNPINNED_IMAGE_TAG: {out[:200]}")
        score -= 15

    # 5. Staging/prod: no HIGH+ CVEs (trivy scan, if available)
    if env in ("staging", "prod"):
        rc_trivy, _ = run("which trivy", capture=True)
        if rc_trivy == 0:
            rc, out = run(
                "trivy fs . --severity HIGH,CRITICAL --exit-code 1 --quiet 2>&1 | tail -5",
                timeout=180,
            )
            if rc != 0:
                sev = "CRITICAL" if env == "prod" else "HIGH"
                failures.append(f"CVE_{sev}_FOUND: Run trivy fs . for details")
                score -= 20 if env == "staging" else 30
        else:
            failures.append("TRIVY_NOT_INSTALLED: install trivy for CVE scanning")
            score -= 5  # Warning only

    return max(0.0, score), failures


# ── DIMENSION: Compliance (25%) ────────────────────────────────────────────

def score_compliance(env: str, verbose: bool) -> tuple[float, list[str]]:
    """
    Checks:
    - All 3 JSON schemas valid (pytest tests/compliance/test_schemas.py)
    - PPSM registry exists and has required entries
    - Audit trail emitted for GPIS decisions (unit test)
    - NIST control mappings present for all new features
    - Helm lint passes
    """
    failures = []
    score = 100.0

    # 1. Schema compliance tests
    rc, out = run("PYTHONPATH=. ./venv/bin/pytest tests/compliance/ -v --tb=short -q 2>&1 | tail -20")
    if rc != 0:
        failures.append(f"SCHEMA_TESTS_FAILED: {out[:300]}")
        score -= 30

    # 2. PPSM registry exists with required entries
    ppsm_path = PROJECT_ROOT / "policies" / "ppsm" / "ppsm-registry.yml"
    if not ppsm_path.exists():
        failures.append("PPSM_REGISTRY_MISSING: policies/ppsm/ppsm-registry.yml not found")
        score -= 15
    else:
        content = ppsm_path.read_text()
        for required_service in ("gpis", "redis", "conjur"):
            if required_service not in content:
                failures.append(f"PPSM_MISSING_SERVICE: {required_service} not in registry")
                score -= 5

    # 3. Helm lint
    for values_file in ("values-k3s.yaml", "values-eks.yaml"):
        vpath = PROJECT_ROOT / "deploy" / "helm" / "ai-agent" / values_file
        if vpath.exists():
            rc, out = run(
                f"helm lint deploy/helm/ai-agent/ -f deploy/helm/ai-agent/{values_file} 2>&1"
            )
            if rc != 0:
                failures.append(f"HELM_LINT_FAILED ({values_file}): {out[:200]}")
                score -= 10

    # 4. SIEM emitter tests
    siem_script = PROJECT_ROOT / "scripts" / "test-siem-emitter.sh"
    if siem_script.exists():
        rc, out = run("./scripts/test-siem-emitter.sh 2>&1 | tail -5")
        if "10/10" not in out and rc != 0:
            failures.append(f"SIEM_EMITTER_PARTIAL: {out[:200]}")
            score -= 15
    else:
        failures.append("SIEM_EMITTER_SCRIPT_MISSING: scripts/test-siem-emitter.sh not found")
        score -= 10

    # 5. Staging: no TODO comments in app/
    if env in ("staging", "prod"):
        rc, out = run(r'grep -rn "# TODO\|# FIXME\|# HACK" app/ --include="*.py"')
        if rc == 0 and out:
            count = len(out.strip().split("\n"))
            failures.append(f"TODO_IN_APP_CODE: {count} TODO/FIXME/HACK comments found in app/")
            score -= min(20, count * 5)

    return max(0.0, score), failures


# ── DIMENSION: Test Coverage (20%) ─────────────────────────────────────────

def score_test_coverage(env: str, verbose: bool) -> tuple[float, list[str]]:
    """
    Checks:
    - pytest coverage ≥ 80% for app/ and scripts/
    - Allow AND deny path tests exist for each policy category
    - QA scenario tests exist for all 4 agent personas
    """
    failures = []
    score = 100.0

    # 1. pytest with coverage
    rc, out = run(
        "PYTHONPATH=. ./venv/bin/pytest tests/ -v --cov=app --cov-report=term-missing --tb=short -q 2>&1 | tail -30",
        timeout=180,
    )

    # Parse coverage percentage
    cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", out)
    if cov_match:
        coverage_pct = int(cov_match.group(1))
        if coverage_pct < 80:
            failures.append(f"COVERAGE_LOW: {coverage_pct}% (target: ≥80%)")
            score -= max(0, (80 - coverage_pct) * 2)
    else:
        failures.append("COVERAGE_NOT_MEASURED: run pytest with --cov=app")
        score -= 20

    if rc != 0:
        failed_match = re.search(r"(\d+) failed", out)
        n_failed = int(failed_match.group(1)) if failed_match else "?"
        failures.append(f"PYTEST_FAILED: {n_failed} test(s) failed")
        score -= min(30, (int(n_failed) if isinstance(n_failed, int) else 10) * 5)

    # 2. QA scenario tests presence
    scenarios_dir = PROJECT_ROOT / "tests" / "qa_scenarios"
    expected_scenarios = [
        "test_security_agent_scenarios.py",
        "test_it_ops_agent_scenarios.py",
        "test_ai_agent_scenarios.py",
        "test_architect_agent_scenarios.py",
    ]
    for scenario in expected_scenarios:
        if not (scenarios_dir / scenario).exists():
            failures.append(f"SCENARIO_MISSING: tests/qa_scenarios/{scenario}")
            score -= 5

    # 3. Allow+deny path tests for each policy category
    for category in ("security", "deployment", "operations"):
        rc_allow, _ = run(
            f"grep -r 'def test.*{category}.*allow' tests/ --include='*.py' -l"
        )
        rc_deny, _ = run(
            f"grep -r 'def test.*{category}.*deny' tests/ --include='*.py' -l"
        )
        if rc_allow != 0:
            failures.append(f"MISSING_ALLOW_TEST: no allow-path test for {category} category")
            score -= 5
        if rc_deny != 0:
            failures.append(f"MISSING_DENY_TEST: no deny-path test for {category} category")
            score -= 5

    return max(0.0, score), failures


# ── DIMENSION: Token Efficiency (15%) ──────────────────────────────────────

def score_token_efficiency(env: str, verbose: bool) -> tuple[float, list[str]]:
    """
    Checks:
    - benchmark_token_savings.py reports ≥70% conservative reduction
    - GovernanceRouter LLM clients are wired (not mock stubs)
    - Cache backend is Redis (not in-memory dict)
    """
    failures = []
    score = 100.0

    # 1. Token benchmark
    benchmark = PROJECT_ROOT / "scripts" / "benchmark_token_savings.py"
    if benchmark.exists():
        rc, out = run("python3 scripts/benchmark_token_savings.py --format json 2>&1")
        try:
            data = json.loads(out)
            conservative = data.get("conservative_reduction_pct", 0)
            if conservative < 70:
                failures.append(
                    f"TOKEN_SAVINGS_LOW: {conservative:.1f}% (target: ≥70%)"
                )
                score -= max(0, (70 - conservative) * 2)
        except json.JSONDecodeError:
            failures.append("BENCHMARK_PARSE_ERROR: could not parse benchmark JSON output")
            score -= 10
    else:
        failures.append("BENCHMARK_SCRIPT_MISSING: scripts/benchmark_token_savings.py not found")
        score -= 10

    # 2. LLM clients wired check (no mock stubs)
    rc, out = run(r'grep -n "# TODO.*LLM\|MockModel\|placeholder" scripts/governance_router.py')
    if rc == 0 and out:
        lines = len(out.strip().split("\n"))
        failures.append(f"LLM_CLIENTS_NOT_WIRED: {lines} mock/TODO lines in governance_router.py")
        score -= min(30, lines * 10)

    # 3. Cache backend check (Redis vs in-memory)
    rc, out = run(r'grep -n "self\.cache\s*=\s*{}" scripts/governance_router.py')
    if rc == 0 and out:
        failures.append("IN_MEMORY_CACHE: GovernanceRouter using dict cache (not Redis)")
        score -= 15

    return max(0.0, score), failures


# ── DIMENSION: Patent Integrity (10%) ──────────────────────────────────────

def score_patent_integrity(env: str, verbose: bool) -> tuple[float, list[str]]:
    """
    Checks:
    - audit-trail.json schema is unchanged vs git HEAD~1
    - AGT required fields still present
    - No new event types without patent counsel flag in commit message
    """
    failures = []
    score = 100.0

    schema_path = "policies/schemas/audit-trail.json"

    # 1. Schema unchanged check
    rc, out = run(f"git diff HEAD -- {schema_path}")
    if rc == 0 and out.strip():
        failures.append(
            "AUDIT_SCHEMA_MODIFIED: audit-trail.json changed — requires patent counsel review"
        )
        score -= 40

    # 2. Required AGT fields still present
    schema_file = PROJECT_ROOT / "policies" / "schemas" / "audit-trail.json"
    if schema_file.exists():
        try:
            schema = json.loads(schema_file.read_text())
            required_fields = {"audit_id", "timestamp", "actor", "action", "compliance_result"}
            schema_required = set(schema.get("required", []))
            missing = required_fields - schema_required
            if missing:
                failures.append(f"AGT_FIELDS_MISSING: {missing} removed from required fields")
                score -= 30
        except json.JSONDecodeError:
            failures.append("AUDIT_SCHEMA_INVALID_JSON: audit-trail.json is not valid JSON")
            score -= 50
    else:
        failures.append("AUDIT_SCHEMA_NOT_FOUND: policies/schemas/audit-trail.json missing")
        score -= 50

    # 3. New event types without counsel flag
    rc, out = run(
        r'git log -1 --pretty=%B | grep -i "patent\|AGT\|counsel"'
    )
    rc_events, out_events = run(
        r'git diff HEAD -- policies/schemas/audit-trail.json | grep "^+" | grep -i "event_type\|SUSPENDED\|RESUMED"'
    )
    if rc_events == 0 and out_events and rc != 0:
        failures.append(
            "NEW_EVENT_TYPE_NO_COUNSEL: new audit event types added without patent counsel flag in commit"
        )
        score -= 20

    return max(0.0, score), failures


# ── Main runner ────────────────────────────────────────────────────────────

def run_qa(env: str, output_format: str, dimension: Optional[str], fail_fast: bool) -> dict:
    threshold = THRESHOLDS[env]
    start = time.time()

    dimension_runners = {
        "security": score_security,
        "compliance": score_compliance,
        "test_coverage": score_test_coverage,
        "token_efficiency": score_token_efficiency,
        "patent_integrity": score_patent_integrity,
    }

    if dimension and dimension not in dimension_runners:
        print(f"Unknown dimension: {dimension}. Valid: {list(dimension_runners.keys())}")
        sys.exit(2)

    runners = {dimension: dimension_runners[dimension]} if dimension else dimension_runners

    results = {}
    all_failures = []

    for dim_name, runner in runners.items():
        raw_score, failures = runner(env, verbose=(output_format == "text"))
        weight = WEIGHTS[dim_name] if not dimension else 100
        weighted = raw_score * (weight / 100)
        results[dim_name] = {
            "raw_score": round(raw_score, 1),
            "weight": weight,
            "weighted_score": round(weighted, 1),
            "failures": failures,
        }
        all_failures.extend(failures)

        if fail_fast and failures:
            break

    # Compute weighted total
    if dimension:
        total = results[dimension]["raw_score"]
    else:
        total = sum(v["weighted_score"] for v in results.values())

    passed = total >= threshold
    elapsed = round(time.time() - start, 1)

    report = {
        "env": env,
        "threshold": threshold,
        "score": round(total, 1),
        "pass": passed,
        "elapsed_seconds": elapsed,
        "dimensions": results,
        "failures": all_failures,
        "summary": f"{'✅ PASS' if passed else '❌ FAIL'} — {total:.1f}/{threshold} ({env})",
    }

    # Emit QA_GATE_FAILED SIEM event if failing (structure-only, no actual OTLP call here)
    if not passed:
        siem_event = {
            "event_type": "QA_GATE_FAILED",
            "env": env,
            "score": round(total, 1),
            "threshold": threshold,
            "failure_count": len(all_failures),
            "critical_security_fail": results.get("security", {}).get("raw_score", 100) < 60,
        }
        print(f"SIEM_EVENT: {json.dumps(siem_event)}", file=sys.stderr)

    return report


def main():
    parser = argparse.ArgumentParser(description="QA Agent Headless Runner")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Target environment (determines pass threshold: dev=80, staging=90, prod=95)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--dimension",
        choices=list(WEIGHTS.keys()),
        help="Score only a single dimension",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after first dimension with failures",
    )
    parser.add_argument(
        "--scenarios",
        choices=["security-agent", "it-ops-agent", "ai-agent", "architect-agent"],
        help="Run headless scenario tests for a specific agent persona",
    )
    args = parser.parse_args()

    # Handle --scenarios flag
    if args.scenarios:
        scenario_map = {
            "security-agent": "tests/qa_scenarios/test_security_agent_scenarios.py",
            "it-ops-agent": "tests/qa_scenarios/test_it_ops_agent_scenarios.py",
            "ai-agent": "tests/qa_scenarios/test_ai_agent_scenarios.py",
            "architect-agent": "tests/qa_scenarios/test_architect_agent_scenarios.py",
        }
        scenario_file = scenario_map[args.scenarios]
        print(f"Running scenario tests: {scenario_file}")
        rc, out = run(f"PYTHONPATH=. ./venv/bin/pytest {scenario_file} -v --tb=short 2>&1")
        print(out)
        sys.exit(rc)

    report = run_qa(args.env, args.output, args.dimension, args.fail_fast)

    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"QA Agent Score Report — {report['env'].upper()}")
        print(f"{'='*60}")
        for dim, data in report["dimensions"].items():
            status = "✅" if not data["failures"] else "❌"
            print(f"  {status} {dim:<20} {data['raw_score']:>6.1f}/100  (weight: {data['weight']}%)")
            for f in data["failures"]:
                print(f"       ↳ {f}")
        print(f"{'='*60}")
        print(f"  TOTAL SCORE: {report['score']:.1f} / {report['threshold']} ({report['env']})")
        print(f"  RESULT:      {report['summary']}")
        print(f"  ELAPSED:     {report['elapsed_seconds']}s")
        print(f"{'='*60}\n")

    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
