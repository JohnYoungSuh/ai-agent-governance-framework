#!/usr/bin/env python3
"""
Kill Switch Validation Runner — AI Agent Governance Framework
Validates: suspend (automated) -> block new requests -> approve (human PA) -> restore authorization
"""

import sys
import os

# Set python path to find app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app, SUSPENSIONS

def run_kill_switch_validation():
    print("=== Starting Kill Switch Lifecycle Validation ===")
    
    # Ensure environment variables are set
    os.environ["GPIS_JWT_SECRET"] = "suhlabs-super-secret-governance-key"
    client = TestClient(app)
    
    agent_id = "security-agent"
    
    # Reset any existing suspensions
    SUSPENSIONS.clear()
    
    # 1. Verify normal authorization is allowed
    print("Step 1: Testing normal authorize request...")
    normal_req = {
        "agent_id": agent_id,
        "category": "SECURITY",
        "payload": {
            "cve_score": 9.5,
            "action": "emergency_patch",
            "agent_tier": "tier2"
        }
    }
    res = client.post("/api/v1/authorize", json=normal_req)
    if res.status_code != 200:
        print(f"[-] Initial authorize failed: {res.status_code} - {res.text}")
        sys.exit(1)
        
    print("[+] Initial authorize succeeded: JWT issued.")
    
    # 2. Trigger automated suspension
    print("Step 2: Triggering automated agent suspension...")
    res_sus = client.post(f"/admin/v1/suspend/{agent_id}")
    if res_sus.status_code != 200:
        print(f"[-] Suspend call failed: {res_sus.status_code} - {res_sus.text}")
        sys.exit(1)
        
    sus_data = res_sus.json()
    susp_token = sus_data["token"]
    print(f"[+] Agent suspended successfully. Suspension Token: {susp_token}")
    
    # 3. Verify new authorization requests are blocked
    print("Step 3: Verifying new authorization requests are blocked...")
    res_block = client.post("/api/v1/authorize", json=normal_req)
    if res_block.status_code != 403:
        print(f"[-] Request was not blocked! Got status code {res_block.status_code}")
        sys.exit(1)
        
    block_reason = res_block.json()["detail"]["reason"]
    print(f"[+] Request blocked as expected. Reason: {block_reason}")
    if "suspended" not in block_reason.lower():
        print("[-] Block reason did not specify suspension.")
        sys.exit(1)
        
    # 4. Approve suspension (Simulating Human PA sign-off)
    print("Step 4: Approving suspension (simulating Human PA)...")
    res_app = client.post(f"/admin/v1/approve/{susp_token}")
    if res_app.status_code != 200:
        print(f"[-] Approve call failed: {res_app.status_code}")
        sys.exit(1)
        
    print("[+] Suspension approved by human PA.")
    
    # 5. Verify authorization requests are allowed again
    print("Step 5: Verifying authorization is restored...")
    res_restore = client.post("/api/v1/authorize", json=normal_req)
    if res_restore.status_code != 200:
        print(f"[-] Authorization was not restored! Got status code {res_restore.status_code} - {res_restore.text}")
        sys.exit(1)
        
    print("[+] Authorization successfully restored: JWT issued.")
    print("=== Kill Switch Lifecycle Validation PASSED ===")

if __name__ == "__main__":
    run_kill_switch_validation()
