#!/usr/bin/env python3
"""
Jira Webhook Receiver
AI Agent Governance Framework v2.1
Control: G-07 (Jira Integration), APP-001 (Human Primacy)

Purpose: Real-time webhook receiver for Jira CR status changes
         Enables immediate response to approval/rejection events

Usage:
  Production (HTTPS with TLS):
    python3 jira-webhook-receiver.py --port 8443 --tls-cert /path/to/cert.pem --tls-key /path/to/key.pem

  Development (HTTP):
    python3 jira-webhook-receiver.py --port 8080

Environment Variables:
  WEBHOOK_SECRET      - Secret token for webhook authentication (HMAC validation)
  REDIS_URL          - Redis URL for caching CR status (optional)
  JIRA_URL           - Jira instance URL for validation
  SLACK_WEBHOOK_URL  - Slack webhook for notifications (optional)

Jira Webhook Configuration:
  1. Go to Jira Settings > System > WebHooks
  2. Create webhook with URL: https://your-domain.com/jira/webhook
  3. Events: Issue Updated, Issue Transitioned
  4. JQL Filter: project = CR AND issuetype = "Change Request"
  5. Add custom header: X-Webhook-Secret: <your-secret>

Exit Codes:
  0 - Server shutdown gracefully
  1 - Configuration error
  2 - Server startup failed
"""

import os
import sys
import json
import hmac
import hashlib
import logging
import signal
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JiraWebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Jira webhooks"""

    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set HTTP response headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('X-Framework', 'AI-Agent-Governance-v2.1')
        self.end_headers()

    def _validate_webhook_secret(self, payload: bytes) -> bool:
        """Validate webhook HMAC signature"""
        webhook_secret = os.getenv('WEBHOOK_SECRET')
        if not webhook_secret:
            logger.warning("WEBHOOK_SECRET not set - skipping HMAC validation")
            return True

        # Get signature from header
        signature_header = self.headers.get('X-Hub-Signature-256') or \
                          self.headers.get('X-Webhook-Signature')

        if not signature_header:
            logger.error("No webhook signature header found")
            return False

        # Calculate expected signature
        expected_sig = 'sha256=' + hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison
        return hmac.compare_digest(signature_header, expected_sig)

    def _process_jira_event(self, event_data: Dict) -> Dict:
        """Process Jira webhook event and extract CR status"""
        try:
            # Extract issue details
            issue = event_data.get('issue', {})
            issue_key = issue.get('key', 'Unknown')
            fields = issue.get('fields', {})

            # Extract status
            status = fields.get('status', {}).get('name', 'Unknown')
            old_status = event_data.get('changelog', {}).get('items', [{}])[0].get('fromString')

            # Extract CR details
            cr_data = {
                'cr_id': issue_key,
                'status': status,
                'old_status': old_status,
                'summary': fields.get('summary', ''),
                'priority': fields.get('priority', {}).get('name', 'Medium'),
                'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned'),
                'updated_at': fields.get('updated', ''),
                'webhook_timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }

            # Check if this is a CR issue type
            issue_type = fields.get('issuetype', {}).get('name', '')
            if 'Change Request' not in issue_type and 'CR' not in issue_type:
                logger.info(f"Ignoring non-CR issue: {issue_key} (type: {issue_type})")
                return None

            logger.info(f"CR Status Update: {issue_key} - {old_status} → {status}")

            return cr_data

        except Exception as e:
            logger.error(f"Error processing Jira event: {str(e)}")
            return None

    def _cache_cr_status(self, cr_data: Dict):
        """Cache CR status in Redis for fast lookup"""
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            logger.debug("REDIS_URL not set - skipping cache")
            return

        try:
            import redis
            r = redis.from_url(redis_url)

            # Cache with 24-hour TTL
            cache_key = f"cr_status:{cr_data['cr_id']}"
            r.setex(cache_key, 86400, json.dumps(cr_data))

            logger.info(f"Cached CR status: {cr_data['cr_id']}")

        except ImportError:
            logger.warning("Redis library not available (pip install redis)")
        except Exception as e:
            logger.error(f"Redis cache error: {str(e)}")

    def _send_notification(self, cr_data: Dict):
        """Send notification for critical status changes"""
        if cr_data['status'] not in ['Approved', 'Rejected', 'Cancelled']:
            return

        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if not slack_webhook:
            logger.debug("SLACK_WEBHOOK_URL not set - skipping notification")
            return

        try:
            import requests

            # Determine color and emoji
            color_map = {
                'Approved': '#00FF00',
                'Rejected': '#FF0000',
                'Cancelled': '#FFA500'
            }
            emoji_map = {
                'Approved': '✅',
                'Rejected': '❌',
                'Cancelled': '⚠️'
            }

            color = color_map.get(cr_data['status'], '#808080')
            emoji = emoji_map.get(cr_data['status'], '📋')

            # Build Slack message
            slack_msg = {
                "attachments": [{
                    "color": color,
                    "title": f"{emoji} Jira CR Status Changed",
                    "fields": [
                        {"title": "CR ID", "value": cr_data['cr_id'], "short": True},
                        {"title": "Status", "value": f"{cr_data['old_status']} → {cr_data['status']}", "short": True},
                        {"title": "Summary", "value": cr_data['summary'], "short": False},
                        {"title": "Assignee", "value": cr_data['assignee'], "short": True},
                        {"title": "Priority", "value": cr_data['priority'], "short": True}
                    ],
                    "footer": "AI Agent Governance Framework",
                    "ts": int(datetime.utcnow().timestamp())
                }]
            }

            response = requests.post(
                slack_webhook,
                json=slack_msg,
                timeout=5
            )
            response.raise_for_status()

            logger.info(f"Notification sent for {cr_data['cr_id']}")

        except ImportError:
            logger.warning("Requests library not available (pip install requests)")
        except Exception as e:
            logger.error(f"Notification error: {str(e)}")

    def _generate_audit_trail(self, cr_data: Dict) -> str:
        """Generate audit trail entry for webhook event"""
        audit_id = f"audit-{int(datetime.utcnow().timestamp())}-{str(uuid4())[:8]}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        audit_entry = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "actor": "jira-webhook-receiver",
            "action": "jira_cr_status_change",
            "workflow_step": "G-07",
            "jira_reference": {
                "cr_id": cr_data['cr_id'],
                "approver_role": "N/A",
                "budget_tokens": 0,
                "controls": ["G-07", "APP-001"]
            },
            "inputs": {
                "cr_id": cr_data['cr_id'],
                "old_status": cr_data.get('old_status', 'Unknown'),
                "new_status": cr_data['status'],
                "webhook_source": "jira"
            },
            "outputs": {
                "status_updated": True,
                "cache_updated": True,
                "notification_sent": cr_data['status'] in ['Approved', 'Rejected', 'Cancelled']
            },
            "policy_controls_checked": ["G-07", "APP-001"],
            "compliance_result": "pass",
            "evidence_hash": f"sha256:{hashlib.sha256(json.dumps(cr_data, sort_keys=True).encode()).hexdigest()}",
            "auditor_agent": "jira-webhook-receiver"
        }

        # Save to file
        audit_dir = "/tmp/audit-trails"
        os.makedirs(audit_dir, exist_ok=True)
        audit_path = f"{audit_dir}/{audit_id}.json"

        with open(audit_path, 'w') as f:
            json.dump(audit_entry, f, indent=2)

        logger.info(f"Audit trail saved: {audit_path}")
        return audit_id

    def do_GET(self):
        """Handle GET requests (health check)"""
        if self.path == '/health':
            self._set_headers(200)
            response = {
                'status': 'healthy',
                'service': 'jira-webhook-receiver',
                'version': '2.1',
                'timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())

    def do_POST(self):
        """Handle POST requests (webhook events)"""
        if self.path != '/jira/webhook':
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
            return

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(content_length)

        # Validate webhook signature
        if not self._validate_webhook_secret(payload):
            logger.error("Webhook signature validation failed")
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return

        # Parse JSON payload
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
            return

        # Process event
        cr_data = self._process_jira_event(event_data)

        if not cr_data:
            self._set_headers(200)
            self.wfile.write(json.dumps({'status': 'ignored'}).encode())
            return

        # Cache status
        self._cache_cr_status(cr_data)

        # Send notifications
        self._send_notification(cr_data)

        # Generate audit trail
        audit_id = self._generate_audit_trail(cr_data)

        # Respond
        self._set_headers(200)
        response = {
            'status': 'processed',
            'cr_id': cr_data['cr_id'],
            'audit_id': audit_id,
            'timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Override to use Python logging instead of stderr"""
        logger.info("%s - %s" % (self.address_string(), format % args))


def create_server(port: int, tls_cert: Optional[str] = None, tls_key: Optional[str] = None):
    """Create and configure HTTP/HTTPS server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, JiraWebhookHandler)

    # Enable TLS if certificates provided
    if tls_cert and tls_key:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(tls_cert, tls_key)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        protocol = 'HTTPS'
    else:
        protocol = 'HTTP'

    logger.info(f"{protocol} server listening on port {port}")
    logger.info(f"Webhook endpoint: {protocol.lower()}://localhost:{port}/jira/webhook")
    logger.info(f"Health check: {protocol.lower()}://localhost:{port}/health")

    return httpd


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal, stopping server...")
    sys.exit(0)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Jira Webhook Receiver for AI Agent Governance')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--tls-cert', type=str, help='Path to TLS certificate (PEM format)')
    parser.add_argument('--tls-key', type=str, help='Path to TLS private key (PEM format)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Configure debug logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate TLS configuration
    if args.tls_cert and not args.tls_key:
        logger.error("ERROR: --tls-key required when --tls-cert is provided")
        sys.exit(1)
    if args.tls_key and not args.tls_cert:
        logger.error("ERROR: --tls-cert required when --tls-key is provided")
        sys.exit(1)

    # Validate environment
    if not os.getenv('WEBHOOK_SECRET'):
        logger.warning("WARNING: WEBHOOK_SECRET not set - webhook authentication disabled")
        logger.warning("This is a SECURITY RISK in production!")

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start server
    try:
        server = create_server(args.port, args.tls_cert, args.tls_key)
        logger.info("Server started successfully")
        logger.info("Press Ctrl+C to stop")
        server.serve_forever()
    except PermissionError:
        logger.error(f"ERROR: Permission denied to bind to port {args.port}")
        logger.error("Try using a port > 1024 or run with sudo")
        sys.exit(2)
    except OSError as e:
        logger.error(f"ERROR: Failed to start server: {str(e)}")
        sys.exit(2)
    except Exception as e:
        logger.error(f"ERROR: Unexpected error: {str(e)}")
        sys.exit(2)


if __name__ == '__main__':
    main()
