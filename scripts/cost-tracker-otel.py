#!/usr/bin/env python3
"""
OpenTelemetry Cost Tracker (G-04)
AI Agent Governance Framework v2.0
Control: MI-009 (Cost Monitoring), MI-021 (Budget Limits), G-04 (OpenTelemetry Integration)

Purpose: Emit cost tracking events to OpenTelemetry with enhanced observability
Usage: python3 cost-tracker-otel.py --agent <agent-id> --cost <amount> --tokens <count>

Requirements:
  pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("⚠️  WARNING: OpenTelemetry libraries not installed")
    print("Install via: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp")


class CostTracker:
    """OpenTelemetry-enabled cost tracker for AI agents"""

    def __init__(self, agent_id: str, otel_endpoint: Optional[str] = None):
        self.agent_id = agent_id
        self.otel_endpoint = otel_endpoint or os.getenv(
            'OTEL_EXPORTER_OTLP_ENDPOINT',
            'http://localhost:4317'
        )

        if OTEL_AVAILABLE:
            self._init_otel()
        else:
            self.tracer = None
            self.meter = None

    def _init_otel(self):
        """Initialize OpenTelemetry tracing and metrics"""
        # Create resource with agent metadata
        resource = Resource.create({
            "service.name": "ai-agent-cost-tracker",
            "service.version": "2.0",
            "agent.id": self.agent_id,
            "control.framework": "ai-governance-framework",
            "control.id": "MI-009"
        })

        # Initialize tracer provider
        trace_provider = TracerProvider(resource=resource)
        trace_exporter = OTLPSpanExporter(endpoint=self.otel_endpoint)
        trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
        trace.set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(__name__, "2.0")

        # Initialize metrics provider
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=self.otel_endpoint),
            export_interval_millis=10000  # 10 seconds
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(__name__, "2.0")

        # Create cost metrics
        self.cost_counter = self.meter.create_counter(
            "agent.cost.total_usd",
            description="Total cost incurred by AI agent in USD",
            unit="USD"
        )
        self.token_counter = self.meter.create_counter(
            "agent.tokens.total",
            description="Total tokens consumed by AI agent",
            unit="tokens"
        )
        self.task_counter = self.meter.create_counter(
            "agent.tasks.total",
            description="Total tasks executed by AI agent",
            unit="tasks"
        )
        self.cost_histogram = self.meter.create_histogram(
            "agent.cost.per_task",
            description="Distribution of cost per task",
            unit="USD"
        )

    def track_cost(
        self,
        cost_usd: float,
        tokens_used: int,
        task_id: str,
        task_outcome: str = "success",
        model: str = "unknown",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Track cost event with OpenTelemetry

        Args:
            cost_usd: Cost in USD
            tokens_used: Number of tokens consumed
            task_id: Unique task identifier
            task_outcome: 'success' or 'failure'
            model: LLM model name
            metadata: Additional metadata dict

        Returns:
            Dict with trace_id, span_id, and cost record
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        cost_id = f"cost-{int(datetime.utcnow().timestamp())}-{str(uuid4())[:8]}"

        metadata = metadata or {}

        cost_record = {
            "cost_id": cost_id,
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "task_id": task_id,
            "cost_usd": cost_usd,
            "tokens_used": tokens_used,
            "task_outcome": task_outcome,
            "model": model,
            "control_id": "MI-009",
            **metadata
        }

        if not OTEL_AVAILABLE or not self.tracer:
            print(f"📊 Cost tracked (no OTEL): ${cost_usd:.4f}, {tokens_used} tokens")
            return {"cost_record": cost_record}

        # Create span for cost tracking
        with self.tracer.start_as_current_span("cost.tracking") as span:
            # Set span attributes
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("task.id", task_id)
            span.set_attribute("cost.usd", cost_usd)
            span.set_attribute("tokens.used", tokens_used)
            span.set_attribute("task.outcome", task_outcome)
            span.set_attribute("model", model)
            span.set_attribute("control.id", "MI-009")

            # Add custom metadata
            for key, value in metadata.items():
                span.set_attribute(f"metadata.{key}", str(value))

            # Record metrics
            self.cost_counter.add(
                cost_usd,
                {"agent.id": self.agent_id, "outcome": task_outcome, "model": model}
            )
            self.token_counter.add(
                tokens_used,
                {"agent.id": self.agent_id, "model": model}
            )
            self.task_counter.add(
                1,
                {"agent.id": self.agent_id, "outcome": task_outcome}
            )
            self.cost_histogram.record(
                cost_usd,
                {"agent.id": self.agent_id, "model": model}
            )

            # Set span status
            if task_outcome == "success":
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.ERROR, "Task failed"))

            # Add cost record as event
            span.add_event(
                "cost.recorded",
                attributes={
                    "cost.id": cost_id,
                    "cost.usd": cost_usd,
                    "tokens": tokens_used
                }
            )

            trace_context = span.get_span_context()
            result = {
                "trace_id": format(trace_context.trace_id, '032x'),
                "span_id": format(trace_context.span_id, '016x'),
                "cost_record": cost_record
            }

            print(f"✅ Cost tracked via OpenTelemetry: ${cost_usd:.4f}, {tokens_used} tokens")
            print(f"   Trace ID: {result['trace_id']}")
            print(f"   Span ID:  {result['span_id']}")

            return result

    def check_budget_alert(self, total_cost: float, budget_limit: float) -> bool:
        """
        Check budget threshold and emit alert span

        Args:
            total_cost: Current total cost
            budget_limit: Budget limit in USD

        Returns:
            True if budget exceeded, False otherwise
        """
        budget_used_pct = (total_cost / budget_limit) * 100

        if not OTEL_AVAILABLE or not self.tracer:
            if budget_used_pct >= 90:
                print(f"🚨 CRITICAL: {budget_used_pct:.1f}% budget used (${total_cost}/${budget_limit})")
                return True
            elif budget_used_pct >= 50:
                print(f"⚠️  WARNING: {budget_used_pct:.1f}% budget used")
            return False

        # Create alert span
        with self.tracer.start_as_current_span("cost.budget.check") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("budget.total_usd", budget_limit)
            span.set_attribute("budget.used_usd", total_cost)
            span.set_attribute("budget.used_pct", budget_used_pct)

            if budget_used_pct >= 90:
                span.set_status(Status(StatusCode.ERROR, "Budget critically exceeded"))
                span.add_event(
                    "cost.budget.critical",
                    attributes={
                        "threshold": 90,
                        "current_pct": budget_used_pct,
                        "circuit_breaker_recommended": True
                    }
                )
                print(f"🚨 CRITICAL: {budget_used_pct:.1f}% budget used - circuit breaker recommended")
                return True

            elif budget_used_pct >= 50:
                span.set_status(Status(StatusCode.OK))
                span.add_event(
                    "cost.budget.warning",
                    attributes={
                        "threshold": 50,
                        "current_pct": budget_used_pct
                    }
                )
                print(f"⚠️  WARNING: {budget_used_pct:.1f}% budget used")

            else:
                span.set_status(Status(StatusCode.OK))

            return False


def main():
    parser = argparse.ArgumentParser(
        description="OpenTelemetry Cost Tracker for AI Agents (G-04)"
    )
    parser.add_argument("--agent", required=True, help="Agent ID")
    parser.add_argument("--cost", type=float, required=True, help="Cost in USD")
    parser.add_argument("--tokens", type=int, required=True, help="Tokens consumed")
    parser.add_argument("--task-id", default=None, help="Task ID")
    parser.add_argument("--outcome", default="success", choices=["success", "failure"])
    parser.add_argument("--model", default="unknown", help="LLM model name")
    parser.add_argument("--budget", type=float, help="Budget limit for alert check")
    parser.add_argument("--total-cost", type=float, help="Total cost so far (for budget check)")
    parser.add_argument("--otel-endpoint", help="OpenTelemetry collector endpoint")

    args = parser.parse_args()

    task_id = args.task_id or f"task-{str(uuid4())[:8]}"

    print("=" * 50)
    print("OpenTelemetry Cost Tracker (G-04)")
    print("=" * 50)
    print(f"Agent ID:    {args.agent}")
    print(f"Task ID:     {task_id}")
    print(f"Cost:        ${args.cost:.4f}")
    print(f"Tokens:      {args.tokens:,}")
    print(f"Model:       {args.model}")
    print(f"Outcome:     {args.outcome}")
    print("=" * 50)
    print()

    # Initialize tracker
    tracker = CostTracker(args.agent, args.otel_endpoint)

    # Track cost event
    result = tracker.track_cost(
        cost_usd=args.cost,
        tokens_used=args.tokens,
        task_id=task_id,
        task_outcome=args.outcome,
        model=args.model
    )

    # Check budget if specified
    if args.budget and args.total_cost is not None:
        print()
        budget_exceeded = tracker.check_budget_alert(args.total_cost, args.budget)
        if budget_exceeded:
            sys.exit(1)

    # Output result as JSON
    print()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
