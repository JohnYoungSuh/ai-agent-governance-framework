"""Shared GPIS client — agents must obtain a JWT before side effects."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class GpisAuthorizationError(Exception):
    """Raised when GPIS denies or is unreachable (fail-closed)."""

    def __init__(self, message: str, status_code: int = 403):
        super().__init__(message)
        self.status_code = status_code


def gpis_base_url() -> str:
    return os.getenv("GPIS_URL", "http://127.0.0.1:8000").rstrip("/")


def require_gpis_token(
    agent_id: str,
    category: str,
    payload: Dict[str, Any],
    *,
    timeout_seconds: float = 5.0,
    session: Optional[Any] = None,
) -> str:
    """POST /api/v1/authorize. Returns JWT. Never fail-open."""
    url = f"{gpis_base_url()}/api/v1/authorize"
    http = session or requests
    try:
        response = http.post(
            url,
            json={"agent_id": agent_id, "category": category, "payload": payload},
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        raise GpisAuthorizationError(
            f"GPIS unreachable; refusing to act: {exc}",
            status_code=503,
        ) from exc

    if response.status_code != 200:
        try:
            body = response.json()
            reason = body.get("detail", body)
            if isinstance(reason, dict):
                reason = reason.get("reason", str(reason))
        except ValueError:
            reason = response.text
        raise GpisAuthorizationError(
            f"GPIS denied {agent_id}: {reason}",
            status_code=response.status_code,
        )

    data = response.json()
    token = data.get("token")
    if not data.get("allowed") or not token:
        raise GpisAuthorizationError("GPIS returned allow without a token")
    return token
