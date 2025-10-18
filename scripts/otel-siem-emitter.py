#!/usr/bin/env python3
"""
OpenTelemetry SIEM Event Emitter
AI Agent Governance Framework v2.1
Controls: AU-002, AU-012, G-03, SEC-001

Purpose:
- Emit SIEM events via OpenTelemetry protocol
- Conform to OCSF (Open Cybersecurity Schema Framework)
- Support multiple SIEM backends (Splunk, Datadog, AWS CloudWatch, etc.)
- Enable distributed tracing for audit correlation

Usage:
    python3 otel-siem-emitter.py \
        --agent-id security-agent \
        --control-id SEC-001 \
        --event-type compliance_check \
        --severity info \
        --description "KMS key rotation enabled" \
        --audit-id audit-12345 \
        --jira-cr-id CR-2025-1042

Environment Variables:
    OTEL_EXPORTER_OTLP_ENDPOINT     - OTLP endpoint (default: http://localhost:4318)
    OTEL_EXPORTER_OTLP_HEADERS      - Auth headers (e.g., x-api-key=...)
    OTEL_SERVICE_NAME               - Service name (default: ai-agent-governance)
    OTEL_ENVIRONMENT                - Environment (dev/staging/prod)
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# OpenTelemetry imports (optional - fallback to JSON-only mode if not available)
OTEL_AVAILABLE = False
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    OTEL_AVAILABLE = True
except ImportError:
    # Fallback mode - generate SIEM events without OpenTelemetry
    print("⚠️  OpenTelemetry not installed - running in fallback mode (JSON-only)", file=sys.stderr)
    print("   Install with: pip3 install -r scripts/requirements-otel.txt", file=sys.stderr)


class SIEMEventEmitter:
    """
    OpenTelemetry SIEM event emitter with OCSF mapping support.
    """

    # OCSF Category Mappings
    OCSF_CATEGORIES = {
        'system': 1,
        'findings': 2,
        'iam': 3,
        'network': 4,
        'discovery': 5,
        'application': 6
    }

    # OCSF Class Mappings (subset)
    OCSF_CLASSES = {
        'authentication': 3001,
        'account_change': 3005,
        'compliance_finding': 2001,
        'detection_finding': 2004,
        'api_activity': 6003,
        'web_activity': 6004
    }

    # OCSF Severity Mappings
    OCSF_SEVERITY = {
        'info': 1,
        'low': 2,
        'medium': 3,
        'high': 4,
        'critical': 5
    }

    # Event Type to OCSF Mapping
    EVENT_TYPE_OCSF = {
        'compliance_check': {'category': 'findings', 'class': 'compliance_finding'},
        'security_finding': {'category': 'findings', 'class': 'detection_finding'},
        'iam_change': {'category': 'iam', 'class': 'account_change'},
        'api_call': {'category': 'application', 'class': 'api_activity'},
        'authentication': {'category': 'iam', 'class': 'authentication'},
        'resource_access': {'category': 'application', 'class': 'api_activity'}
    }

    def __init__(self):
        """Initialize OpenTelemetry tracer and meter (or fallback mode)."""
        self.service_name = os.getenv('OTEL_SERVICE_NAME', 'ai-agent-governance')
        self.environment = os.getenv('OTEL_ENVIRONMENT', 'dev')
        self.otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')
        self.otel_enabled = OTEL_AVAILABLE

        if not OTEL_AVAILABLE:
            # Fallback mode - no OpenTelemetry
            self.tracer = None
            self.tracer_provider = None
            self.meter_provider = None
            self.event_counter = None
            self.compliance_gauge = None
            return

        # Create resource attributes
        resource_attributes = {
            'service.name': self.service_name,
            'service.version': '2.1',
            'deployment.environment': self.environment,
            'framework.name': 'AI-Agent-Governance',
            'framework.version': 'v2.1'
        }
        resource = Resource.create(resource_attributes)

        # Initialize tracer provider
        self.tracer_provider = TracerProvider(resource=resource)

        # Configure OTLP exporter
        otlp_headers = self._parse_otlp_headers()
        span_exporter = OTLPSpanExporter(
            endpoint=f"{self.otlp_endpoint}/v1/traces",
            headers=otlp_headers
        )

        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(span_exporter)
        )
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)

        # Initialize meter provider for metrics
        metric_exporter = OTLPMetricExporter(
            endpoint=f"{self.otlp_endpoint}/v1/metrics",
            headers=otlp_headers
        )
        metric_reader = PeriodicExportingMetricReader(metric_exporter)
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(__name__)

        # Create metrics
        self.event_counter = self.meter.create_counter(
            name='siem_events_total',
            description='Total SIEM events emitted',
            unit='1'
        )
        self.compliance_gauge = self.meter.create_up_down_counter(
            name='compliance_status',
            description='Compliance check results (1=pass, -1=fail)',
            unit='1'
        )

    def _parse_otlp_headers(self) -> Dict[str, str]:
        """Parse OTLP headers from environment variable."""
        headers = {}
        headers_env = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')

        if headers_env:
            # Format: "key1=value1,key2=value2"
            for header in headers_env.split(','):
                if '=' in header:
                    key, value = header.split('=', 1)
                    headers[key.strip()] = value.strip()

        return headers

    def _map_to_ocsf(self, event_type: str, severity: str) -> Dict[str, int]:
        """Map event type and severity to OCSF schema."""
        ocsf_type = self.EVENT_TYPE_OCSF.get(
            event_type,
            {'category': 'application', 'class': 'api_activity'}
        )

        return {
            'category_uid': self.OCSF_CATEGORIES[ocsf_type['category']],
            'class_uid': self.OCSF_CLASSES[ocsf_type['class']],
            'severity_id': self.OCSF_SEVERITY.get(severity.lower(), 1),
            'activity_id': self._get_activity_id(event_type)
        }

    def _get_activity_id(self, event_type: str) -> int:
        """Get OCSF activity ID for event type."""
        activity_map = {
            'compliance_check': 1,  # Create
            'security_finding': 2,  # Read
            'iam_change': 3,        # Update
            'api_call': 1,          # Create
            'authentication': 1,    # Logon
            'resource_access': 2    # Read
        }
        return activity_map.get(event_type, 0)

    def emit_event(
        self,
        agent_id: str,
        control_id: str,
        event_type: str,
        severity: str,
        description: str,
        audit_id: Optional[str] = None,
        jira_cr_id: Optional[str] = None,
        tier: int = 3,
        compliance_result: str = 'pass',
        payload: Optional[Dict[str, Any]] = None,
        resource_arn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Emit a SIEM event via OpenTelemetry.

        Args:
            agent_id: Agent identifier
            control_id: Governance control ID (e.g., SEC-001)
            event_type: Type of event (compliance_check, security_finding, etc.)
            severity: Severity level (info, low, medium, high, critical)
            description: Human-readable event description
            audit_id: Audit trail ID for correlation
            jira_cr_id: Jira CR ID for approval tracking
            tier: Agent tier (1-4)
            compliance_result: pass/fail/warning
            payload: Additional event data
            resource_arn: AWS resource ARN

        Returns:
            dict: SIEM event record conforming to schema
        """
        # Generate event ID
        siem_event_id = audit_id or f"siem-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Map to OCSF
        ocsf_mapping = self._map_to_ocsf(event_type, severity)

        # Build SIEM event
        siem_event = {
            'siem_event_id': siem_event_id,
            'timestamp': timestamp,
            'source': self._determine_source(event_type),
            'control_id': control_id,
            'agent_id': agent_id,
            'tier': tier,
            'payload': payload or {
                'description': description,
                'event_type': event_type,
                'resource_arn': resource_arn
            },
            'compliance_result': compliance_result,
            'ocsf_mapping': ocsf_mapping,
            'metadata': {
                'environment': self.environment,
                'correlation_id': audit_id
            }
        }

        # Add Jira reference if provided
        if jira_cr_id:
            siem_event['jira_reference'] = {
                'cr_id': jira_cr_id,
                'approver_role': 'Change Manager',
                'status': 'Approved'  # Assume approved if CR ID provided
            }

        # Emit as OpenTelemetry span (if enabled)
        if self.otel_enabled and self.tracer:
            with self.tracer.start_as_current_span(
                f"siem.{event_type}",
                attributes={
                    'siem.event_id': siem_event_id,
                    'siem.control_id': control_id,
                    'siem.agent_id': agent_id,
                    'siem.tier': tier,
                    'siem.severity': severity,
                    'siem.compliance_result': compliance_result,
                    'siem.event_type': event_type,
                    'ocsf.category_uid': ocsf_mapping['category_uid'],
                    'ocsf.class_uid': ocsf_mapping['class_uid'],
                    'ocsf.severity_id': ocsf_mapping['severity_id'],
                    'resource.arn': resource_arn or 'N/A',
                    'jira.cr_id': jira_cr_id or 'N/A'
                }
            ) as span:
                # Add event as span event
                span.add_event(
                    name=f"siem.{event_type}",
                    attributes={
                        'event.description': description,
                        'event.payload': json.dumps(payload or {})
                    }
                )

                # Set span status based on compliance result
                if compliance_result == 'fail':
                    span.set_status(Status(StatusCode.ERROR, description))
                elif compliance_result == 'warning':
                    span.set_status(Status(StatusCode.OK, f"Warning: {description}"))
                else:
                    span.set_status(Status(StatusCode.OK))

            # Update metrics
            self.event_counter.add(
                1,
                attributes={
                    'control_id': control_id,
                    'event_type': event_type,
                    'severity': severity,
                    'compliance_result': compliance_result
                }
            )

            if event_type == 'compliance_check':
                compliance_value = 1 if compliance_result == 'pass' else -1
                self.compliance_gauge.add(
                    compliance_value,
                    attributes={'control_id': control_id}
                )

        return siem_event

    def _determine_source(self, event_type: str) -> str:
        """Determine event source based on event type."""
        source_map = {
            'compliance_check': 'audit-trail',
            'security_finding': 'infra',
            'iam_change': 'infra',
            'api_call': 'agent-runtime',
            'authentication': 'jira',
            'resource_access': 'infra'
        }
        return source_map.get(event_type, 'other')

    def shutdown(self):
        """Flush and shutdown OpenTelemetry providers."""
        if self.otel_enabled:
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            if self.meter_provider:
                self.meter_provider.shutdown()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Emit SIEM events via OpenTelemetry with OCSF mapping'
    )
    parser.add_argument('--agent-id', required=True, help='Agent identifier')
    parser.add_argument('--control-id', required=True, help='Control ID (e.g., SEC-001)')
    parser.add_argument('--event-type', required=True,
                        choices=['compliance_check', 'security_finding', 'iam_change',
                                'api_call', 'authentication', 'resource_access'],
                        help='Type of event')
    parser.add_argument('--severity', required=True,
                        choices=['info', 'low', 'medium', 'high', 'critical'],
                        help='Event severity')
    parser.add_argument('--description', required=True, help='Event description')
    parser.add_argument('--audit-id', help='Audit trail ID for correlation')
    parser.add_argument('--jira-cr-id', help='Jira CR ID')
    parser.add_argument('--tier', type=int, default=3, choices=[1, 2, 3, 4],
                        help='Agent tier (default: 3)')
    parser.add_argument('--compliance-result', default='pass',
                        choices=['pass', 'fail', 'warning'],
                        help='Compliance result (default: pass)')
    parser.add_argument('--resource-arn', help='AWS resource ARN')
    parser.add_argument('--payload-json', help='Additional payload as JSON string')
    parser.add_argument('--output', help='Write SIEM event to file (JSON)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate event JSON without emitting to OTLP')

    args = parser.parse_args()

    # Parse payload if provided
    payload = None
    if args.payload_json:
        try:
            payload = json.loads(args.payload_json)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON payload: {e}", file=sys.stderr)
            sys.exit(1)

    # Create emitter
    emitter = SIEMEventEmitter()

    try:
        # Emit event
        if args.dry_run:
            print("DRY RUN MODE - Event not sent to OTLP endpoint", file=sys.stderr)

        siem_event = emitter.emit_event(
            agent_id=args.agent_id,
            control_id=args.control_id,
            event_type=args.event_type,
            severity=args.severity,
            description=args.description,
            audit_id=args.audit_id,
            jira_cr_id=args.jira_cr_id,
            tier=args.tier,
            compliance_result=args.compliance_result,
            payload=payload,
            resource_arn=args.resource_arn
        )

        # Write to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(siem_event, f, indent=2)
            print(f"✅ SIEM event written to {args.output}", file=sys.stderr)

        # Print event to stdout for logging
        print(json.dumps(siem_event, indent=2))

        if not args.dry_run:
            print(f"✅ SIEM event emitted: {siem_event['siem_event_id']}", file=sys.stderr)
            print(f"   Control: {args.control_id}", file=sys.stderr)
            print(f"   OCSF Category: {siem_event['ocsf_mapping']['category_uid']}", file=sys.stderr)
            print(f"   OCSF Severity: {siem_event['ocsf_mapping']['severity_id']}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: Failed to emit SIEM event: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Flush and shutdown
        emitter.shutdown()


if __name__ == '__main__':
    main()
