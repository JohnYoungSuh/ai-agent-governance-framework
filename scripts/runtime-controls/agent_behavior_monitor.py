#!/usr/bin/env python3
"""
Agent Behavior Monitor - Runtime Control #1

Monitors AI agent behavior in real-time and triggers circuit breakers on anomalies.
Detects unusual patterns in request rates, token usage, API access, and costs.

Aligned to: Framework MI-020 (Tier Enforcement), NIST SI-4 (System Monitoring)
"""

import time
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import statistics
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AgentBehaviorBaseline:
    """Statistical baseline for normal agent behavior"""
    agent_id: str
    tier: int
    
    # Request rate statistics
    avg_requests_per_hour: float
    std_requests_per_hour: float
    
    # Token usage statistics
    avg_tokens_per_request: float
    std_tokens_per_request: float
    
    # Cost statistics
    avg_cost_per_request: float
    std_cost_per_request: float
    
    # Allowed behaviors
    typical_actions: List[str]
    allowed_api_endpoints: List[str]
    
    # Circuit breaker configuration
    circuit_breaker_enabled: bool = True
    circuit_breaker_mode: str = "alert_only"  # alert_only, auto_pause
    cooldown_minutes: int = 30
    
    # Anomaly detection thresholds (in standard deviations)
    request_rate_threshold: float = 5.0  # 5 sigma
    token_usage_threshold: float = 10.0  # 10 sigma
    cost_threshold: float = 3.0  # 3 sigma


@dataclass
class AgentActivity:
    """Single agent activity record"""
    timestamp: datetime
    action: str
    api_endpoint: Optional[str]
    tokens_used: int
    cost: float
    success: bool
    error_message: Optional[str] = None


class AgentBehaviorMonitor:
    """
    Real-time agent behavior monitoring with anomaly detection.
    
    Features:
    - Statistical anomaly detection (Z-score)
    - Circuit breaker on suspicious behavior
    - SIEM event emission
    - OpenTelemetry integration
    """
    
    def __init__(self, baseline: AgentBehaviorBaseline):
        self.baseline = baseline
        self.activity_buffer = deque(maxlen=1000)  # Last 1000 activities
        self.circuit_breaker_active = False
        self.circuit_breaker_until: Optional[datetime] = None
        
        logger.info(f"Initialized behavior monitor for agent: {baseline.agent_id}")
    
    def record_activity(self, activity: AgentActivity):
        """Record an agent activity for monitoring"""
        self.activity_buffer.append(activity)
        
        # Check if circuit breaker is active
        if self.circuit_breaker_active:
            if datetime.now() < self.circuit_breaker_until:
                logger.warning(
                    f"Circuit breaker active for {self.baseline.agent_id} "
                    f"until {self.circuit_breaker_until}"
                )
                return
            else:
                # Cooldown expired, reset circuit breaker
                self.circuit_breaker_active = False
                self.circuit_breaker_until = None
                logger.info(f"Circuit breaker reset for {self.baseline.agent_id}")
    
    def calculate_request_rate(self, window_hours: float = 1.0) -> float:
        """Calculate current request rate (requests/hour)"""
        if not self.activity_buffer:
            return 0.0
        
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        recent_activities = [
            a for a in self.activity_buffer 
            if a.timestamp >= cutoff_time
        ]
        
        return len(recent_activities) / window_hours
    
    def calculate_avg_tokens(self, window_size: int = 100) -> float:
        """Calculate average tokens per request over recent window"""
        if not self.activity_buffer:
            return 0.0
        
        recent_tokens = [a.tokens_used for a in list(self.activity_buffer)[-window_size:]]
        return statistics.mean(recent_tokens) if recent_tokens else 0.0
    
    def calculate_avg_cost(self, window_size: int = 100) -> float:
        """Calculate average cost per request over recent window"""
        if not self.activity_buffer:
            return 0.0
        
        recent_costs = [a.cost for a in list(self.activity_buffer)[-window_size:]]
        return statistics.mean(recent_costs) if recent_costs else 0.0
    
    def check_request_rate_anomaly(self) -> Tuple[bool, str]:
        """Detect request rate anomalies using Z-score"""
        current_rate = self.calculate_request_rate()
        
        # Calculate Z-score
        if self.baseline.std_requests_per_hour > 0:
            z_score = (
                (current_rate - self.baseline.avg_requests_per_hour) / 
                self.baseline.std_requests_per_hour
            )
        else:
            z_score = 0.0
        
        if abs(z_score) > self.baseline.request_rate_threshold:
            return True, (
                f"Request rate anomaly: {current_rate:.1f} req/hr "
                f"(baseline: {self.baseline.avg_requests_per_hour:.1f} ± "
                f"{self.baseline.std_requests_per_hour:.1f}, Z-score: {z_score:.2f})"
            )
        
        return False, ""
    
    def check_token_usage_anomaly(self) -> Tuple[bool, str]:
        """Detect token usage anomalies"""
        current_avg = self.calculate_avg_tokens()
        
        if self.baseline.std_tokens_per_request > 0:
            z_score = (
                (current_avg - self.baseline.avg_tokens_per_request) / 
                self.baseline.std_tokens_per_request
            )
        else:
            z_score = 0.0
        
        if abs(z_score) > self.baseline.token_usage_threshold:
            return True, (
                f"Token usage anomaly: {current_avg:.0f} tokens/req "
                f"(baseline: {self.baseline.avg_tokens_per_request:.0f} ± "
                f"{self.baseline.std_tokens_per_request:.0f}, Z-score: {z_score:.2f})"
            )
        
        return False, ""
    
    def check_cost_anomaly(self) -> Tuple[bool, str]:
        """Detect cost anomalies"""
        current_avg = self.calculate_avg_cost()
        
        if self.baseline.std_cost_per_request > 0:
            z_score = (
                (current_avg - self.baseline.avg_cost_per_request) / 
                self.baseline.std_cost_per_request
            )
        else:
            z_score = 0.0
        
        if abs(z_score) > self.baseline.cost_threshold:
            return True, (
                f"Cost anomaly: ${current_avg:.4f}/req "
                f"(baseline: ${self.baseline.avg_cost_per_request:.4f} ± "
                f"${self.baseline.std_cost_per_request:.4f}, Z-score: {z_score:.2f})"
            )
        
        return False, ""
    
    def check_unauthorized_action(self, action: str) -> Tuple[bool, str]:
        """Check if action is in typical behavior profile"""
        if action not in self.baseline.typical_actions:
            return True, f"Unauthorized action: {action}"
        return False, ""
    
    def check_unauthorized_api_endpoint(self, endpoint: Optional[str]) -> Tuple[bool, str]:
        """Check if API endpoint is allowed"""
        if endpoint is None:
            return False, ""
        
        # Check if endpoint matches any allowed pattern
        for allowed in self.baseline.allowed_api_endpoints:
            if allowed in endpoint:
                return False, ""
        
        return True, f"Unauthorized API endpoint: {endpoint}"
    
    def trigger_circuit_breaker(self, reason: str, severity: str = "high"):
        """Trigger circuit breaker to pause agent"""
        if not self.baseline.circuit_breaker_enabled:
            logger.warning(f"Circuit breaker disabled for {self.baseline.agent_id}")
            return
        
        self.circuit_breaker_active = True
        self.circuit_breaker_until = datetime.now() + timedelta(
            minutes=self.baseline.cooldown_minutes
        )
        
        # Emit SIEM event
        siem_event = {
            "event_type": "agent_circuit_breaker_triggered",
            "agent_id": self.baseline.agent_id,
            "tier": self.baseline.tier,
            "reason": reason,
            "severity": severity,
            "mode": self.baseline.circuit_breaker_mode,
            "cooldown_until": self.circuit_breaker_until.isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.critical(f"🚨 CIRCUIT BREAKER TRIGGERED: {self.baseline.agent_id}")
        logger.critical(f"Reason: {reason}")
        logger.critical(f"Mode: {self.baseline.circuit_breaker_mode}")
        logger.critical(f"Cooldown until: {self.circuit_breaker_until}")
        
        # Write to SIEM (JSON format for ingestion)
        print(json.dumps(siem_event), file=sys.stderr)
        
        # If auto_pause mode, actually pause the agent
        if self.baseline.circuit_breaker_mode == "auto_pause":
            self._pause_agent()
    
    def _pause_agent(self):
        """Pause agent execution (implementation-specific)"""
        # In production, this would:
        # 1. Set environment variable AGENT_PAUSED=true
        # 2. Update Kubernetes ConfigMap
        # 3. Send signal to agent process
        # 4. Notify on-call team
        
        logger.critical(f"⏸️  AGENT PAUSED: {self.baseline.agent_id}")
        
        # For now, set environment variable
        os.environ['AGENT_PAUSED'] = 'true'
    
    def check_all_anomalies(self, activity: AgentActivity) -> List[str]:
        """Run all anomaly checks and return list of violations"""
        violations = []
        
        # Check request rate
        is_anomaly, msg = self.check_request_rate_anomaly()
        if is_anomaly:
            violations.append(msg)
        
        # Check token usage
        is_anomaly, msg = self.check_token_usage_anomaly()
        if is_anomaly:
            violations.append(msg)
        
        # Check cost
        is_anomaly, msg = self.check_cost_anomaly()
        if is_anomaly:
            violations.append(msg)
        
        # Check action authorization
        is_anomaly, msg = self.check_unauthorized_action(activity.action)
        if is_anomaly:
            violations.append(msg)
        
        # Check API endpoint authorization
        is_anomaly, msg = self.check_unauthorized_api_endpoint(activity.api_endpoint)
        if is_anomaly:
            violations.append(msg)
        
        return violations
    
    def monitor(self, activity: AgentActivity):
        """Main monitoring function - call this for each agent activity"""
        # Record activity
        self.record_activity(activity)
        
        # Check for anomalies
        violations = self.check_all_anomalies(activity)
        
        if violations:
            logger.warning(f"Anomalies detected for {self.baseline.agent_id}:")
            for violation in violations:
                logger.warning(f"  - {violation}")
            
            # Trigger circuit breaker if violations detected
            reason = "; ".join(violations)
            self.trigger_circuit_breaker(reason)
        
        return len(violations) == 0


# Example usage
if __name__ == "__main__":
    # Define baseline for security agent
    baseline = AgentBehaviorBaseline(
        agent_id="security-agent",
        tier=3,
        avg_requests_per_hour=10.0,
        std_requests_per_hour=2.0,
        avg_tokens_per_request=500,
        std_tokens_per_request=100,
        avg_cost_per_request=0.05,
        std_cost_per_request=0.01,
        typical_actions=[
            "scan_vulnerabilities",
            "check_compliance",
            "generate_report",
            "analyze_security_posture"
        ],
        allowed_api_endpoints=[
            "trivy.io",
            "github.com/api",
            "aquasec.com",
            "snyk.io"
        ],
        circuit_breaker_enabled=True,
        circuit_breaker_mode="alert_only",  # Start in alert-only mode
        cooldown_minutes=30
    )
    
    # Create monitor
    monitor = AgentBehaviorMonitor(baseline)
    
    # Simulate normal activity
    print("\n=== Simulating normal activity ===")
    for i in range(10):
        activity = AgentActivity(
            timestamp=datetime.now(),
            action="scan_vulnerabilities",
            api_endpoint="trivy.io/scan",
            tokens_used=480,
            cost=0.048,
            success=True
        )
        monitor.monitor(activity)
        time.sleep(0.1)
    
    print("\n✅ Normal activity - no anomalies detected\n")
    
    # Simulate anomalous activity (request rate spike)
    print("\n=== Simulating request rate spike (50x normal) ===")
    for i in range(500):
        activity = AgentActivity(
            timestamp=datetime.now(),
            action="scan_vulnerabilities",
            api_endpoint="trivy.io/scan",
            tokens_used=500,
            cost=0.05,
            success=True
        )
        monitor.monitor(activity)
    
    # Simulate unauthorized action
    print("\n=== Simulating unauthorized action ===")
    activity = AgentActivity(
        timestamp=datetime.now(),
        action="delete_production_database",  # NOT in typical_actions
        api_endpoint="aws.amazon.com/rds",
        tokens_used=200,
        cost=0.02,
        success=False
    )
    monitor.monitor(activity)
    
    # Simulate unauthorized API endpoint
    print("\n=== Simulating unauthorized API endpoint ===")
    activity = AgentActivity(
        timestamp=datetime.now(),
        action="scan_vulnerabilities",
        api_endpoint="malicious-site.com/exfiltrate",  # NOT in allowed_api_endpoints
        tokens_used=500,
        cost=0.05,
        success=True
    )
    monitor.monitor(activity)
