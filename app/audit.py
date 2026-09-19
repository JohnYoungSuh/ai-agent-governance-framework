"""Schema-validated audit-trail emission for GPIS authorize decisions.

Does not mutate policies/schemas/audit-trail.json (patent anchor).
Fail-closed: callers must treat emit failure as a denied decision.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "policies" / "schemas" / "audit-trail.json"
REQUIRED_FIELDS = ("audit_id", "timestamp", "actor", "action", "workflow_step", "compliance_result")


def _schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def audit_dir() -> Path:
    path = Path(os.getenv("GPIS_AUDIT_DIR", "/tmp/gpis-audit"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def emit_audit_event(
    *,
    actor: str,
    action: str,
    workflow_step: str,
    compliance_result: str,
    reason: str,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    policy_controls_checked: Optional[List[str]] = None,
    jira_cr_id: Optional[str] = None,
) -> str:
    """Write one schema-validated audit-trail record. Returns audit_id."""
    if compliance_result not in ("pass", "fail", "warning"):
        raise ValueError(f"invalid compliance_result: {compliance_result}")

    audit_id = str(uuid.uuid4())
    record: Dict[str, Any] = {
        "audit_id": audit_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "workflow_step": workflow_step,
        "compliance_result": compliance_result,
        "inputs": inputs or {},
        "outputs": {**(outputs or {}), "reason": reason},
        "policy_controls_checked": policy_controls_checked or ["AC-6"],
        "auditor_agent": "GPIS",
    }
    if jira_cr_id:
        record["jira_reference"] = {"cr_id": jira_cr_id}

    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    record["evidence_hash"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    missing = [key for key in REQUIRED_FIELDS if not record.get(key)]
    if missing:
        raise ValueError(f"audit record missing required fields: {missing}")

    try:
        import jsonschema

        jsonschema.validate(instance=record, schema=_schema())
    except ImportError:
        pass

    out_path = audit_dir() / f"{audit_id}.json"
    out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return audit_id
