#!/usr/bin/env python3
"""
Agent Message Validator - Runtime Control #4

Validates and authenticates agent-to-agent messages using HMAC-SHA256.
Prevents message tampering, replay attacks, and unauthorized communication.

Aligned to: Framework agent communication, NIST SC-8 (Transmission Confidentiality)
"""

import hmac
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, Dict, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Structured agent-to-agent message"""
    message_id: str
    sender_agent_id: str
    recipient_agent_id: str
    message_type: str  # task_request, task_response, status_update, error_notification
    payload: Dict
    timestamp: str  # ISO 8601
    correlation_id: Optional[str] = None
    signature: Optional[str] = None


class AgentMessageValidator:
    """
    Validate and authenticate agent-to-agent messages.
    
    Features:
    - HMAC-SHA256 signature verification
    - Message deduplication (replay attack prevention)
    - Schema validation
    - Timestamp validation
    """
    
    def __init__(self, agent_id: str, shared_secret: str):
        self.agent_id = agent_id
        self.shared_secret = shared_secret.encode('utf-8')
        self.seen_messages: Dict[str, datetime] = {}  # message_id -> timestamp
        self.deduplication_window = timedelta(minutes=5)
        
        # Valid message types
        self.valid_message_types = [
            "task_request",
            "task_response",
            "status_update",
            "error_notification",
            "approval_request"
        ]
        
        logger.info(f"Initialized message validator for agent: {agent_id}")
    
    def _compute_signature(self, message: AgentMessage) -> str:
        """Compute HMAC-SHA256 signature for message"""
        # Create canonical message (without signature field)
        canonical = {
            "message_id": message.message_id,
            "sender_agent_id": message.sender_agent_id,
            "recipient_agent_id": message.recipient_agent_id,
            "message_type": message.message_type,
            "payload": message.payload,
            "timestamp": message.timestamp,
            "correlation_id": message.correlation_id
        }
        
        # Sort keys for deterministic serialization
        canonical_json = json.dumps(canonical, sort_keys=True)
        
        # Compute HMAC
        signature = hmac.new(
            self.shared_secret,
            canonical_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def sign_message(self, message: AgentMessage) -> AgentMessage:
        """Sign a message before sending"""
        message.signature = self._compute_signature(message)
        return message
    
    def verify_signature(self, message: AgentMessage) -> Tuple[bool, str]:
        """Verify message signature"""
        if not message.signature:
            return False, "Message missing signature"
        
        expected_signature = self._compute_signature(message)
        
        # Use constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(message.signature, expected_signature):
            return False, "Invalid signature"
        
        return True, ""
    
    def validate_schema(self, message: AgentMessage) -> Tuple[bool, str]:
        """Validate message schema"""
        # Check required fields
        if not message.message_id:
            return False, "Missing message_id"
        
        if not message.sender_agent_id:
            return False, "Missing sender_agent_id"
        
        if not message.recipient_agent_id:
            return False, "Missing recipient_agent_id"
        
        if not message.message_type:
            return False, "Missing message_type"
        
        if message.message_type not in self.valid_message_types:
            return False, f"Invalid message_type: {message.message_type}"
        
        if not message.payload:
            return False, "Missing payload"
        
        if not message.timestamp:
            return False, "Missing timestamp"
        
        # Validate recipient
        if message.recipient_agent_id != self.agent_id:
            return False, f"Message not for this agent (recipient: {message.recipient_agent_id})"
        
        return True, ""
    
    def validate_timestamp(self, message: AgentMessage, max_age_minutes: int = 5) -> Tuple[bool, str]:
        """Validate message timestamp (prevent replay attacks)"""
        try:
            msg_time = datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
            now = datetime.now(msg_time.tzinfo)
            
            age = now - msg_time
            
            if age > timedelta(minutes=max_age_minutes):
                return False, f"Message too old: {age.total_seconds():.0f}s (max {max_age_minutes*60}s)"
            
            if age < timedelta(seconds=-30):  # Allow 30s clock skew
                return False, "Message timestamp in future"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid timestamp format: {e}"
    
    def check_duplicate(self, message: AgentMessage) -> Tuple[bool, str]:
        """Check for duplicate messages (replay attack)"""
        # Clean up old entries
        cutoff = datetime.now() - self.deduplication_window
        self.seen_messages = {
            msg_id: ts for msg_id, ts in self.seen_messages.items()
            if ts > cutoff
        }
        
        # Check if we've seen this message
        if message.message_id in self.seen_messages:
            return True, f"Duplicate message (seen at {self.seen_messages[message.message_id]})"
        
        # Record this message
        self.seen_messages[message.message_id] = datetime.now()
        
        return False, ""
    
    def validate(self, message: AgentMessage) -> Tuple[bool, List[str]]:
        """
        Validate message (schema, signature, timestamp, deduplication).
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Schema validation
        is_valid, error = self.validate_schema(message)
        if not is_valid:
            errors.append(f"Schema: {error}")
        
        # Signature verification
        is_valid, error = self.verify_signature(message)
        if not is_valid:
            errors.append(f"Signature: {error}")
        
        # Timestamp validation
        is_valid, error = self.validate_timestamp(message)
        if not is_valid:
            errors.append(f"Timestamp: {error}")
        
        # Duplicate check
        is_duplicate, error = self.check_duplicate(message)
        if is_duplicate:
            errors.append(f"Duplicate: {error}")
        
        return len(errors) == 0, errors
    
    def create_message(
        self,
        recipient_agent_id: str,
        message_type: str,
        payload: Dict,
        correlation_id: Optional[str] = None
    ) -> AgentMessage:
        """Create and sign a new message"""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_agent_id=self.agent_id,
            recipient_agent_id=recipient_agent_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            correlation_id=correlation_id
        )
        
        return self.sign_message(message)


# Example usage
if __name__ == "__main__":
    # Shared secret (in production, load from Kubernetes Secret)
    SHARED_SECRET = "your-secret-key-here-change-in-production"
    
    # Create validators for two agents
    security_agent = AgentMessageValidator("security-agent", SHARED_SECRET)
    itops_agent = AgentMessageValidator("it-ops-agent", SHARED_SECRET)
    
    print("\n" + "="*80)
    print("AGENT MESSAGE VALIDATOR - TEST SUITE")
    print("="*80 + "\n")
    
    # Test 1: Valid message
    print("Test 1: Valid message")
    message = security_agent.create_message(
        recipient_agent_id="it-ops-agent",
        message_type="task_request",
        payload={
            "task": "restart_service",
            "parameters": {"service": "nginx"}
        }
    )
    
    is_valid, errors = itops_agent.validate(message)
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    if errors:
        print(f"Errors: {errors}")
    print()
    
    # Test 2: Tampered message
    print("Test 2: Tampered message (payload modified)")
    tampered_message = security_agent.create_message(
        recipient_agent_id="it-ops-agent",
        message_type="task_request",
        payload={"task": "delete_database"}
    )
    # Tamper with payload
    tampered_message.payload["task"] = "delete_production"
    
    is_valid, errors = itops_agent.validate(tampered_message)
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID (expected)'}")
    if errors:
        print(f"Errors: {errors}")
    print()
    
    # Test 3: Replay attack
    print("Test 3: Replay attack (duplicate message)")
    original = security_agent.create_message(
        recipient_agent_id="it-ops-agent",
        message_type="status_update",
        payload={"status": "completed"}
    )
    
    # First delivery - should succeed
    is_valid, errors = itops_agent.validate(original)
    print(f"First delivery: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    # Replay - should fail
    is_valid, errors = itops_agent.validate(original)
    print(f"Replay attempt: {'✅ VALID' if is_valid else '❌ INVALID (expected)'}")
    if errors:
        print(f"Errors: {errors}")
    print()
    
    # Test 4: Wrong recipient
    print("Test 4: Wrong recipient")
    wrong_recipient = security_agent.create_message(
        recipient_agent_id="architect-agent",  # Not it-ops-agent
        message_type="task_request",
        payload={"task": "analyze"}
    )
    
    is_valid, errors = itops_agent.validate(wrong_recipient)
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID (expected)'}")
    if errors:
        print(f"Errors: {errors}")
    print()
    
    print("="*80)
    print("All tests completed")
    print("="*80)
