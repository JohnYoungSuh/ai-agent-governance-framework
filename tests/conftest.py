"""Pytest env for fail-closed GPIS secrets. Loaded before test modules import app."""

from __future__ import annotations

import os

os.environ["GPIS_JWT_SECRET"] = os.environ.get(
    "GPIS_JWT_SECRET", "test-gpis-jwt-secret-ci-only"
)
os.environ["GPIS_ADMIN_API_KEY"] = os.environ.get(
    "GPIS_ADMIN_API_KEY", "test-gpis-admin-key-ci-only"
)
os.environ.setdefault("GPIS_AUDIT_DIR", "/tmp/gpis-audit-tests")
os.environ.setdefault("ENVIRONMENT", "test")

ADMIN_HEADERS = {"X-GPIS-Admin-Key": os.environ["GPIS_ADMIN_API_KEY"]}
