#!/usr/bin/env python3
"""
Agent Rollback Monitor - Runtime Control #3

Monitors agent performance and triggers automatic rollback on degradation.
Integrates with Prometheus metrics and Kubernetes deployments.

Aligned to: Framework reliability, NIST SI-2 (Flaw Remediation)
"""

import subprocess
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Current agent performance metrics"""
    error_rate: float  # 0.0 - 1.0
    latency_p50: float  # milliseconds
    latency_p95: float  # milliseconds
    latency_p99: float  # milliseconds
    request_count: int
    cost_per_request: float
    timestamp: datetime


@dataclass
class RollbackConfig:
    """Rollback configuration thresholds"""
    threshold_error_rate: float = 0.10  # 10%
    threshold_latency_p99: float = 5000  # 5 seconds
    threshold_cost_spike: float = 3.0  # 3x baseline
    min_request_count: int = 50  # Minimum requests before rollback
    auto_rollback_enabled: bool = True
    canary_enabled: bool = False
    canary_percentage: int = 10
    canary_duration_minutes: int = 30


class AgentRollbackMonitor:
    """
    Monitor agent performance and trigger automatic rollback.
    
    Features:
    - Prometheus metrics integration
    - Automatic rollback on degradation
    - Canary deployment support
    - SIEM event emission
    """
    
    def __init__(
        self,
        agent_name: str,
        namespace: str,
        prometheus_url: str = "http://prometheus:9090",
        config: Optional[RollbackConfig] = None
    ):
        self.agent_name = agent_name
        self.namespace = namespace
        self.prometheus_url = prometheus_url
        self.config = config or RollbackConfig()
        
        self.baseline_metrics: Optional[AgentMetrics] = None
        self.rollback_in_progress = False
        
        logger.info(
            f"Initialized rollback monitor for {agent_name} "
            f"in namespace {namespace}"
        )
    
    def query_prometheus(self, query: str) -> float:
        """Query Prometheus and return scalar result"""
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            if data["status"] == "success" and data["data"]["result"]:
                return float(data["data"]["result"][0]["value"][1])
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
            return 0.0
    
    def get_current_metrics(self) -> AgentMetrics:
        """Query Prometheus for current agent metrics"""
        
        # Error rate: rate(errors) / rate(requests)
        error_rate_query = f'''
            rate(agent_errors_total{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m]) /
            rate(agent_requests_total{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m])
        '''
        error_rate = self.query_prometheus(error_rate_query)
        
        # Latency percentiles
        latency_p50_query = f'''
            histogram_quantile(0.50,
                rate(agent_request_duration_seconds_bucket{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m])
            ) * 1000
        '''
        latency_p50 = self.query_prometheus(latency_p50_query)
        
        latency_p95_query = f'''
            histogram_quantile(0.95,
                rate(agent_request_duration_seconds_bucket{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m])
            ) * 1000
        '''
        latency_p95 = self.query_prometheus(latency_p95_query)
        
        latency_p99_query = f'''
            histogram_quantile(0.99,
                rate(agent_request_duration_seconds_bucket{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m])
            ) * 1000
        '''
        latency_p99 = self.query_prometheus(latency_p99_query)
        
        # Request count
        request_count_query = f'''
            sum(increase(agent_requests_total{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m]))
        '''
        request_count = int(self.query_prometheus(request_count_query))
        
        # Cost per request
        cost_query = f'''
            rate(agent_cost_total{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m]) /
            rate(agent_requests_total{{agent="{self.agent_name}",namespace="{self.namespace}"}}[5m])
        '''
        cost_per_request = self.query_prometheus(cost_query)
        
        return AgentMetrics(
            error_rate=error_rate,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            request_count=request_count,
            cost_per_request=cost_per_request,
            timestamp=datetime.now()
        )
    
    def set_baseline(self, metrics: AgentMetrics):
        """Set baseline metrics for comparison"""
        self.baseline_metrics = metrics
        logger.info(f"Baseline metrics set for {self.agent_name}")
        logger.info(f"  Error rate: {metrics.error_rate:.2%}")
        logger.info(f"  P99 latency: {metrics.latency_p99:.0f}ms")
        logger.info(f"  Cost/req: ${metrics.cost_per_request:.4f}")
    
    def should_rollback(self, current: AgentMetrics) -> Tuple[bool, str]:
        """
        Determine if rollback is needed based on current metrics.
        
        Returns:
            (should_rollback, reason)
        """
        reasons = []
        
        # Check minimum request count
        if current.request_count < self.config.min_request_count:
            logger.debug(
                f"Insufficient requests ({current.request_count} < "
                f"{self.config.min_request_count}), skipping rollback check"
            )
            return False, ""
        
        # Check error rate
        if current.error_rate > self.config.threshold_error_rate:
            reasons.append(
                f"Error rate {current.error_rate:.2%} exceeds threshold "
                f"{self.config.threshold_error_rate:.2%}"
            )
        
        # Check P99 latency
        if current.latency_p99 > self.config.threshold_latency_p99:
            reasons.append(
                f"P99 latency {current.latency_p99:.0f}ms exceeds threshold "
                f"{self.config.threshold_latency_p99:.0f}ms"
            )
        
        # Check cost spike (if baseline exists)
        if self.baseline_metrics:
            if current.cost_per_request > (
                self.baseline_metrics.cost_per_request * self.config.threshold_cost_spike
            ):
                reasons.append(
                    f"Cost ${current.cost_per_request:.4f}/req is "
                    f"{current.cost_per_request / self.baseline_metrics.cost_per_request:.1f}x "
                    f"baseline ${self.baseline_metrics.cost_per_request:.4f}/req"
                )
        
        if reasons:
            return True, "; ".join(reasons)
        
        return False, ""
    
    def get_deployment_info(self) -> Dict:
        """Get current deployment information from Kubernetes"""
        try:
            cmd = [
                "kubectl", "get", "deployment", self.agent_name,
                "-n", self.namespace,
                "-o", "json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get deployment info: {e}")
            return {}
    
    def execute_rollback(self, reason: str):
        """Execute Kubernetes rollback"""
        if not self.config.auto_rollback_enabled:
            logger.warning(
                f"Auto-rollback disabled for {self.agent_name}, "
                f"manual intervention required"
            )
            self._emit_rollback_alert(reason, auto_executed=False)
            return
        
        if self.rollback_in_progress:
            logger.warning(f"Rollback already in progress for {self.agent_name}")
            return
        
        self.rollback_in_progress = True
        
        logger.critical(f"🔄 EXECUTING ROLLBACK: {self.agent_name}")
        logger.critical(f"Namespace: {self.namespace}")
        logger.critical(f"Reason: {reason}")
        
        try:
            # Get deployment info before rollback
            deployment_info = self.get_deployment_info()
            current_version = deployment_info.get("metadata", {}).get(
                "annotations", {}
            ).get("deployment.ai/version", "unknown")
            
            # Execute rollback
            cmd = [
                "kubectl", "rollout", "undo",
                f"deployment/{self.agent_name}",
                "-n", self.namespace
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Rollback command output: {result.stdout}")
            
            # Wait for rollback to complete
            wait_cmd = [
                "kubectl", "rollout", "status",
                f"deployment/{self.agent_name}",
                "-n", self.namespace,
                "--timeout=5m"
            ]
            
            subprocess.run(wait_cmd, check=True)
            
            # Get new version
            new_deployment_info = self.get_deployment_info()
            new_version = new_deployment_info.get("metadata", {}).get(
                "annotations", {}
            ).get("deployment.ai/version", "unknown")
            
            logger.info(
                f"✅ Rollback completed: {current_version} → {new_version}"
            )
            
            # Emit SIEM event
            self._emit_rollback_event(
                reason=reason,
                from_version=current_version,
                to_version=new_version,
                success=True
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Rollback failed: {e}")
            logger.error(f"stderr: {e.stderr}")
            
            self._emit_rollback_event(
                reason=reason,
                from_version="unknown",
                to_version="unknown",
                success=False,
                error=str(e)
            )
        
        finally:
            self.rollback_in_progress = False
    
    def _emit_rollback_event(
        self,
        reason: str,
        from_version: str,
        to_version: str,
        success: bool,
        error: Optional[str] = None
    ):
        """Emit SIEM event for rollback"""
        event = {
            "event_type": "agent_rollback_executed",
            "agent_name": self.agent_name,
            "namespace": self.namespace,
            "reason": reason,
            "from_version": from_version,
            "to_version": to_version,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        print(json.dumps(event))
    
    def _emit_rollback_alert(self, reason: str, auto_executed: bool):
        """Emit alert for rollback (manual intervention needed)"""
        alert = {
            "event_type": "agent_rollback_required",
            "agent_name": self.agent_name,
            "namespace": self.namespace,
            "reason": reason,
            "auto_executed": auto_executed,
            "timestamp": datetime.now().isoformat()
        }
        
        print(json.dumps(alert))
    
    def monitor_loop(self, interval_seconds: int = 60):
        """
        Main monitoring loop.
        
        Args:
            interval_seconds: How often to check metrics
        """
        logger.info(
            f"Starting rollback monitor for {self.agent_name} "
            f"(check interval: {interval_seconds}s)"
        )
        
        # Set baseline on first run
        initial_metrics = self.get_current_metrics()
        self.set_baseline(initial_metrics)
        
        while True:
            try:
                # Get current metrics
                current_metrics = self.get_current_metrics()
                
                logger.info(f"Current metrics for {self.agent_name}:")
                logger.info(f"  Error rate: {current_metrics.error_rate:.2%}")
                logger.info(f"  P99 latency: {current_metrics.latency_p99:.0f}ms")
                logger.info(f"  Requests: {current_metrics.request_count}")
                logger.info(f"  Cost/req: ${current_metrics.cost_per_request:.4f}")
                
                # Check if rollback needed
                should_rollback, reason = self.should_rollback(current_metrics)
                
                if should_rollback:
                    logger.warning(f"Rollback triggered: {reason}")
                    self.execute_rollback(reason)
                    
                    # Reset baseline after rollback
                    time.sleep(60)  # Wait for new version to stabilize
                    new_metrics = self.get_current_metrics()
                    self.set_baseline(new_metrics)
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(interval_seconds)


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Rollback Monitor")
    parser.add_argument("--agent", required=True, help="Agent name")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument(
        "--prometheus-url",
        default="http://prometheus:9090",
        help="Prometheus URL"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds"
    )
    parser.add_argument(
        "--error-threshold",
        type=float,
        default=0.10,
        help="Error rate threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--latency-threshold",
        type=float,
        default=5000,
        help="P99 latency threshold (ms)"
    )
    parser.add_argument(
        "--auto-rollback",
        action="store_true",
        help="Enable automatic rollback"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = RollbackConfig(
        threshold_error_rate=args.error_threshold,
        threshold_latency_p99=args.latency_threshold,
        auto_rollback_enabled=args.auto_rollback
    )
    
    # Create monitor
    monitor = AgentRollbackMonitor(
        agent_name=args.agent,
        namespace=args.namespace,
        prometheus_url=args.prometheus_url,
        config=config
    )
    
    # Start monitoring
    monitor.monitor_loop(interval_seconds=args.interval)
