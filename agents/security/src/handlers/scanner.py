"""
Security Agent - Scanner Job
Scheduled vulnerability scanning (CronJob)
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
import yaml

_shared = Path("/app/shared")
if _shared.is_dir():
    sys.path.insert(0, str(_shared))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from gpis_client import GpisAuthorizationError, require_gpis_token

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scan():
    """Execute scheduled security scan"""
    logger.info("=" * 60)
    logger.info("Security Agent - Scheduled Scan")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    logger.info(f"Agent Tier: {os.getenv('AGENT_TIER', '3')}")
    logger.info("=" * 60)

    namespace = os.getenv("AGENT_NAMESPACE", "dev")
    tier_raw = os.getenv("AGENT_TIER", "3")
    agent_tier = f"tier{tier_raw}" if str(tier_raw).isdigit() else str(tier_raw)
    payload = {
        "subcategory": "config",
        "risk_level": "low",
        "namespace": namespace,
        "allowed_namespace": namespace,
        "agent_tier": agent_tier,
        "contains_pii": False,
        "contains_secrets": False,
    }
    if agent_tier in ("tier3", "tier4"):
        payload["jira_cr_id"] = os.getenv("JIRA_CR_ID", "")
    try:
        token = require_gpis_token("security-agent", "ACCESS", payload)
        logger.info("GPIS authorized scheduled scan (token prefix=%s)", token[:12])
    except GpisAuthorizationError as exc:
        logger.error("GPIS denied scheduled scan: %s", exc)
        return 1

    try:
        # Load configuration
        with open('/etc/security-agent/agent-config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            scan_config = config.get('scanning', {})
            tools = scan_config.get('tools', [])
            targets = scan_config.get('targets', [])

        logger.info(f"Scan tools: {', '.join(tools)}")
        logger.info(f"Scan targets: {', '.join(targets)}")

        # Placeholder: Run actual scans
        for target in targets:
            logger.info(f"Scanning {target}...")
            # Add actual scanning logic here
            # Example: run_trivy_scan(target)

        logger.info("✅ Scan completed successfully")
        return 0

    except Exception as e:
        logger.error(f"❌ Scan failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_scan())
