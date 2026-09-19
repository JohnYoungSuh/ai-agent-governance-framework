"""GPIS client fail-closed behavior."""

from unittest.mock import Mock

import pytest
import requests

from agents.shared.gpis_client import GpisAuthorizationError, require_gpis_token


def test_require_token_returns_jwt():
    session = Mock()
    session.post.return_value.status_code = 200
    session.post.return_value.json.return_value = {"allowed": True, "token": "jwt-abc"}
    token = require_gpis_token(
        "security-agent",
        "ACCESS",
        {"subcategory": "logs", "risk_level": "low"},
        session=session,
    )
    assert token == "jwt-abc"


def test_require_token_denies():
    session = Mock()
    session.post.return_value.status_code = 403
    session.post.return_value.json.return_value = {
        "detail": {"reason": "Denied: pending", "allowed": False}
    }
    with pytest.raises(GpisAuthorizationError, match="Denied"):
        require_gpis_token("security-agent", "ACCESS", {}, session=session)


def test_require_token_unreachable():
    session = Mock()
    session.post.side_effect = requests.ConnectionError("down")
    with pytest.raises(GpisAuthorizationError, match="unreachable"):
        require_gpis_token("security-agent", "ACCESS", {}, session=session)
