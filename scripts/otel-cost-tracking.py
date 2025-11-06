#!/usr/bin/env python3
"""
OpenTelemetry Cost Tracking Integration
AI Agent Governance Framework v2.1
Control: MI-009 (Cost Monitoring), MI-021 (Budget Enforcement)

Purpose: Track AI agent costs using OpenTelemetry for observability
         Correlates with audit trails via shared event IDs
         Emits metrics, traces, and logs for cost analysis

Usage:
  # Track a single API call cost
  python3 otel-cost-tracking.py track-call \
      --agent-id ops-agent-01 \
      --model gpt-4 \
      --tokens 1500 \
      --cost 0.045

  # Track batch operation costs
  python3 otel-cost-tracking.py track-batch \
      --agent-id ops-agent-01 \
      --operations-file batch_costs.json

  # Export cost metrics to Prometheus
  python3 otel-cost-tracking.py export-prometheus --port 9090

  # Send cost alert
  python3 otel-cost-tracking.py alert \
      --agent-id ops-agent-01 \
      --threshold 100.0 \
      --actual 125.50

Environment Variables:
  OTEL_EXPORTER_OTLP_ENDPOINT  - OpenTelemetry collector endpoint
  OTEL_SERVICE_NAME            - Service name (default: ai-agent-cost-tracker)
  AUDIT_TRAIL_DIR              - Directory for audit trail correlation
  BUDGET_ALERT_WEBHOOK         - Webhook URL for budget alerts

Exit Codes:
  0 - Success
  1 - Configuration error
  2 - Cost tracking failed
  3 - Budget threshold exceeded
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4
import hashlib

# OpenTelemetry imports
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.trace import Status, StatusCode
except ImportError:
    print("ERROR: OpenTelemetry libraries not installed", file=sys.stderr)
    print("Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CostTracker:
    """OpenTelemetry-based cost tracker for AI agents"""

    # Model pricing (per 1K tokens)
    MODEL_PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'claude-3-opus': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
        'gemini-pro': {'input': 0.00025, 'output': 0.0005}
    }

    def __init__(self, service_name: str = None):
        """Initialize cost tracker with OpenTelemetry"""
        self.service_name = service_name or os.getenv('OTEL_SERVICE_NAME', 'ai-agent-cost-tracker')

        # Setup OpenTelemetry resource
        self.resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: "2.1",
            "framework": "ai-agent-governance",
            "environment": os.getenv("ENVIRONMENT", "production")
        })

        # Setup tracing
        self._setup_tracing()

        # Setup metrics
        self._setup_metrics()

        logger.info(f"Cost tracker initialized: {self.service_name}")

    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        # Create tracer provider
        tracer_provider = TracerProvider(resource=self.resource)

        # Configure exporter
        otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')

        if otlp_endpoint:
            # OTLP exporter for production
            span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        else:
            # Console exporter for development
            span_exporter = ConsoleSpanExporter()

        # Add batch processor
        tracer_provider.add_span_processor(
            BatchSpanProcessor(span_exporter)
        )

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        # Get tracer
        self.tracer = trace.get_tracer(__name__, "2.1")

    def _setup_metrics(self):
        """Setup OpenTelemetry metrics"""
        # Configure exporter
        otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')

        if otlp_endpoint:
            # OTLP exporter for production
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=otlp_endpoint),
                export_interval_millis=60000  # 1 minute
            )
        else:
            # Console exporter for development
            from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
            metric_reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=60000
            )

        # Create meter provider
        meter_provider = MeterProvider(
            resource=self.resource,
            metric_readers=[metric_reader]
        )

        # Set global meter provider
        metrics.set_meter_provider(meter_provider)

        # Get meter
        self.meter = metrics.get_meter(__name__, "2.1")

        # Create metrics
        self.token_counter = self.meter.create_counter(
            name="ai.agent.tokens.total",
            description="Total tokens consumed by AI agents",
            unit="tokens"
        )

        self.cost_counter = self.meter.create_counter(
            name="ai.agent.cost.total",
            description="Total cost in USD for AI agent operations",
            unit="USD"
        )

        self.api_call_counter = self.meter.create_counter(
            name="ai.agent.api_calls.total",
            description="Total API calls made by AI agents",
            unit="calls"
        )

        self.cost_gauge = self.meter.create_observable_gauge(
            name="ai.agent.cost.current",
            description="Current cumulative cost for agent",
            unit="USD",
            callbacks=[self._get_current_cost]
        )

    def _get_current_cost(self, options):
        """Callback for observable gauge - returns current cost"""
        # This would query actual cost from storage
        # For now, return a placeholder
        return []

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict:
        """
        Calculate cost for a model API call

        Args:
            model: Model name (e.g., 'gpt-4')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost breakdown dictionary
        """
        if model not in self.MODEL_PRICING:
            logger.warning(f"Unknown model: {model}. Using default pricing.")
            pricing = {'input': 0.001, 'output': 0.002}
        else:
            pricing = self.MODEL_PRICING[model]

        input_cost = (input_tokens / 1000.0) * pricing['input']
        output_cost = (output_tokens / 1000.0) * pricing['output']
        total_cost = input_cost + output_cost

        return {
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'input_cost_usd': round(input_cost, 6),
            'output_cost_usd': round(output_cost, 6),
            'total_cost_usd': round(total_cost, 6),
            'pricing': pricing
        }

    def track_api_call(self, agent_id: str, model: str, input_tokens: int,
                       output_tokens: int, audit_id: str = None,
                       additional_attrs: Dict = None) -> str:
        """
        Track a single API call with OpenTelemetry

        Args:
            agent_id: Agent identifier
            model: Model name
            input_tokens: Input tokens
            output_tokens: Output tokens
            audit_id: Audit trail ID for correlation
            additional_attrs: Additional span attributes

        Returns:
            Event ID (trace ID)
        """
        # Calculate cost
        cost_data = self.calculate_cost(model, input_tokens, output_tokens)

        # Generate event ID
        event_id = str(uuid4())

        # Create trace span
        with self.tracer.start_as_current_span(
            "ai.agent.api_call",
            attributes={
                "agent.id": agent_id,
                "model.name": model,
                "tokens.input": input_tokens,
                "tokens.output": output_tokens,
                "tokens.total": cost_data['total_tokens'],
                "cost.usd": cost_data['total_cost_usd'],
                "event.id": event_id,
                "audit.id": audit_id or "none",
                **(additional_attrs or {})
            }
        ) as span:
            # Record metrics
            self.token_counter.add(
                cost_data['total_tokens'],
                {
                    "agent.id": agent_id,
                    "model.name": model,
                    "token.type": "total"
                }
            )

            self.cost_counter.add(
                cost_data['total_cost_usd'],
                {
                    "agent.id": agent_id,
                    "model.name": model
                }
            )

            self.api_call_counter.add(
                1,
                {
                    "agent.id": agent_id,
                    "model.name": model
                }
            )

            # Set span status
            span.set_status(Status(StatusCode.OK))

            logger.info(
                f"Tracked API call: agent={agent_id}, model={model}, "
                f"tokens={cost_data['total_tokens']}, cost=${cost_data['total_cost_usd']:.6f}"
            )

        # Correlate with audit trail
        if audit_id:
            self._correlate_with_audit_trail(event_id, audit_id, cost_data)

        return event_id

    def _correlate_with_audit_trail(self, event_id: str, audit_id: str, cost_data: Dict):
        """
        Correlate cost event with audit trail

        Args:
            event_id: Cost tracking event ID
            audit_id: Audit trail ID
            cost_data: Cost calculation data
        """
        audit_dir = os.getenv('AUDIT_TRAIL_DIR', '/tmp/audit-trails')

        correlation = {
            'event_id': event_id,
            'audit_id': audit_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'cost_data': cost_data,
            'correlation_type': 'cost_to_audit'
        }

        # Save correlation
        os.makedirs(audit_dir, exist_ok=True)
        correlation_file = f"{audit_dir}/cost_correlation_{event_id}.json"

        with open(correlation_file, 'w') as f:
            json.dump(correlation, f, indent=2)

        logger.debug(f"Cost correlation saved: {correlation_file}")

    def track_batch(self, agent_id: str, operations: List[Dict]) -> Dict:
        """
        Track a batch of operations

        Args:
            agent_id: Agent identifier
            operations: List of operation dicts with model, input_tokens, output_tokens

        Returns:
            Batch summary with total cost
        """
        with self.tracer.start_as_current_span(
            "ai.agent.batch_operation",
            attributes={"agent.id": agent_id, "batch.size": len(operations)}
        ) as batch_span:

            total_cost = 0.0
            total_tokens = 0
            event_ids = []

            for op in operations:
                event_id = self.track_api_call(
                    agent_id,
                    op['model'],
                    op['input_tokens'],
                    op['output_tokens'],
                    op.get('audit_id')
                )
                event_ids.append(event_id)

                cost_data = self.calculate_cost(
                    op['model'],
                    op['input_tokens'],
                    op['output_tokens']
                )
                total_cost += cost_data['total_cost_usd']
                total_tokens += cost_data['total_tokens']

            batch_span.set_attribute("batch.total_cost", total_cost)
            batch_span.set_attribute("batch.total_tokens", total_tokens)
            batch_span.set_status(Status(StatusCode.OK))

            logger.info(
                f"Tracked batch: agent={agent_id}, operations={len(operations)}, "
                f"tokens={total_tokens}, cost=${total_cost:.6f}"
            )

            return {
                'agent_id': agent_id,
                'operations_count': len(operations),
                'total_tokens': total_tokens,
                'total_cost_usd': round(total_cost, 6),
                'event_ids': event_ids
            }

    def check_budget_threshold(self, agent_id: str, current_cost: float,
                              threshold: float) -> Dict:
        """
        Check if agent has exceeded budget threshold

        Args:
            agent_id: Agent identifier
            current_cost: Current cumulative cost
            threshold: Budget threshold

        Returns:
            Alert information if threshold exceeded
        """
        threshold_pct = (current_cost / threshold) * 100

        if current_cost >= threshold:
            alert = {
                'alert_type': 'budget_exceeded',
                'agent_id': agent_id,
                'current_cost': current_cost,
                'threshold': threshold,
                'threshold_percentage': round(threshold_pct, 2),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'severity': 'critical'
            }

            # Send alert
            self._send_budget_alert(alert)

            logger.error(
                f"Budget EXCEEDED: agent={agent_id}, cost=${current_cost:.2f}, "
                f"threshold=${threshold:.2f} ({threshold_pct:.1f}%)"
            )

            return alert

        elif threshold_pct >= 80:
            alert = {
                'alert_type': 'budget_warning',
                'agent_id': agent_id,
                'current_cost': current_cost,
                'threshold': threshold,
                'threshold_percentage': round(threshold_pct, 2),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'severity': 'warning'
            }

            logger.warning(
                f"Budget WARNING: agent={agent_id}, cost=${current_cost:.2f}, "
                f"threshold=${threshold:.2f} ({threshold_pct:.1f}%)"
            )

            return alert

        return {'status': 'ok'}

    def _send_budget_alert(self, alert: Dict):
        """Send budget alert to webhook"""
        webhook_url = os.getenv('BUDGET_ALERT_WEBHOOK')

        if not webhook_url:
            logger.debug("No webhook configured for budget alerts")
            return

        try:
            import requests

            response = requests.post(
                webhook_url,
                json=alert,
                timeout=5
            )
            response.raise_for_status()

            logger.info(f"Budget alert sent successfully")

        except ImportError:
            logger.warning("Requests library not available (pip install requests)")
        except Exception as e:
            logger.error(f"Failed to send budget alert: {str(e)}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='OpenTelemetry cost tracking for AI agents'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Track single call
    track_parser = subparsers.add_parser('track-call', help='Track single API call')
    track_parser.add_argument('--agent-id', required=True, help='Agent ID')
    track_parser.add_argument('--model', required=True, help='Model name')
    track_parser.add_argument('--input-tokens', type=int, required=True, help='Input tokens')
    track_parser.add_argument('--output-tokens', type=int, required=True, help='Output tokens')
    track_parser.add_argument('--audit-id', help='Audit trail ID for correlation')

    # Track batch
    batch_parser = subparsers.add_parser('track-batch', help='Track batch operations')
    batch_parser.add_argument('--agent-id', required=True, help='Agent ID')
    batch_parser.add_argument('--operations-file', required=True, help='JSON file with operations')

    # Check budget
    alert_parser = subparsers.add_parser('alert', help='Check budget threshold')
    alert_parser.add_argument('--agent-id', required=True, help='Agent ID')
    alert_parser.add_argument('--threshold', type=float, required=True, help='Budget threshold (USD)')
    alert_parser.add_argument('--actual', type=float, required=True, help='Actual cost (USD)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        tracker = CostTracker()

        if args.command == 'track-call':
            event_id = tracker.track_api_call(
                args.agent_id,
                args.model,
                args.input_tokens,
                args.output_tokens,
                args.audit_id
            )
            print(f"✅ Cost tracked successfully")
            print(f"Event ID: {event_id}")

        elif args.command == 'track-batch':
            with open(args.operations_file, 'r') as f:
                operations = json.load(f)

            result = tracker.track_batch(args.agent_id, operations)
            print(f"✅ Batch tracked successfully")
            print(f"Operations: {result['operations_count']}")
            print(f"Total tokens: {result['total_tokens']}")
            print(f"Total cost: ${result['total_cost_usd']:.6f}")

        elif args.command == 'alert':
            alert = tracker.check_budget_threshold(
                args.agent_id,
                args.actual,
                args.threshold
            )

            if alert.get('alert_type') == 'budget_exceeded':
                print(f"❌ BUDGET EXCEEDED")
                print(f"Current: ${alert['current_cost']:.2f}")
                print(f"Threshold: ${alert['threshold']:.2f}")
                print(f"Percentage: {alert['threshold_percentage']:.1f}%")
                sys.exit(3)
            elif alert.get('alert_type') == 'budget_warning':
                print(f"⚠️  BUDGET WARNING")
                print(f"Current: ${alert['current_cost']:.2f}")
                print(f"Threshold: ${alert['threshold']:.2f}")
                print(f"Percentage: {alert['threshold_percentage']:.1f}%")
            else:
                print(f"✅ Budget OK")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(2)


if __name__ == '__main__':
    main()
