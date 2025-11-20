# Autonomy and Cost Attribution Implementation Guide

## Overview

This guide explains how to implement the two mandatory business goals introduced in Framework v3.0:

1. **≥80% Autonomous Operations** (≤20% human-in-the-loop)
2. **100% Cost Attribution** (zero manual reconciliation)

---

## PART 1: ACHIEVING ≥80% AUTONOMY

### **Problem Statement**

**Current State** (v2.x):
- Tier 3 agents require human approval for all production deployments
- Tier 4 agents require human approval for all actions
- Budget decisions require finance team approval
- Incident response requires on-call engineer approval
- **Result**: 60-80% of actions require human intervention

**Target State** (v3.0):
- ≥80% of actions auto-approved based on risk scoring
- Human approval only for high-risk scenarios (score ≥70)
- Autonomous incident remediation for known issues
- Autonomous budget management within pre-approved envelopes
- **Result**: ≤20% of actions require human intervention

---

### **Solution: Risk-Based Autonomy Framework**

#### **Component 1: Risk Scoring Engine**

Every agent action is scored 0-100 based on five dimensions:

```yaml
Risk Score Calculation:
  
  1. Blast Radius (30% weight)
     - How many resources/users affected?
     - < 5 resources = 10 points
     - 5-50 resources = 50 points
     - > 50 resources = 90 points
  
  2. Reversibility (25% weight)
     - Can the action be automatically undone?
     - Automatic rollback available = 10 points
     - Manual rollback possible = 50 points
     - Irreversible = 90 points
  
  3. Data Sensitivity (20% weight)
     - What data classification is affected?
     - Public/Internal = 10 points
     - Confidential = 50 points
     - Critical/Regulated/PII = 90 points
  
  4. Cost Impact (15% weight)
     - What is the cost delta?
     - < $100 = 10 points
     - $100-$1000 = 50 points
     - > $1000 = 90 points
  
  5. Historical Success (10% weight)
     - What is the success rate for similar actions?
     - > 95% success = 10 points
     - 80-95% success = 50 points
     - < 80% success = 90 points

Final Risk Score = Weighted Sum (0-100)
```

**Example Calculations**:

```
Example 1: Deploy tested service to production
  - Blast radius: 10 pods = 50 * 0.30 = 15
  - Reversibility: Auto rollback = 10 * 0.25 = 2.5
  - Data sensitivity: Internal = 10 * 0.20 = 2
  - Cost impact: $50 = 10 * 0.15 = 1.5
  - Historical success: 98% = 10 * 0.10 = 1
  Total Risk Score = 22 → AUTO-APPROVED ✅

Example 2: Delete production database
  - Blast radius: 100+ resources = 90 * 0.30 = 27
  - Reversibility: Irreversible = 90 * 0.25 = 22.5
  - Data sensitivity: Critical = 90 * 0.20 = 18
  - Cost impact: $5000 = 90 * 0.15 = 13.5
  - Historical success: Never done = 90 * 0.10 = 9
  Total Risk Score = 90 → REQUIRES APPROVAL ❌
```

#### **Component 2: Automated Approval Decision Engine**

Based on risk score, the system makes approval decisions:

```yaml
Decision Logic:

  Risk Score < 30 (Low Risk):
    Action: Auto-approve immediately
    Human Notification: Post-action summary (daily digest)
    Example: Restart pod, scale within limits, renew certificate
  
  Risk Score 30-70 (Medium Risk):
    Action: Notify human, wait 15 minutes
    Timeout Behavior: Auto-approve if no response
    Human Notification: Immediate alert
    Example: Deploy new version with canary, scale beyond normal limits
  
  Risk Score ≥ 70 (High Risk):
    Action: Require explicit human approval
    Timeout Behavior: Deny if no response within 60 minutes
    Human Notification: Page on-call engineer
    Example: Delete production data, change security policies
```

**Implementation**:

```python
# Pseudocode for approval decision
def should_auto_approve(action):
    risk_score = calculate_risk_score(action)
    
    if risk_score < 30:
        # Low risk - auto-approve
        log_action(action, "auto_approved", risk_score)
        notify_async(action, "post_action_summary")
        return True
    
    elif risk_score < 70:
        # Medium risk - wait for human with timeout
        notification_sent = notify_human(action, risk_score, urgency="high")
        response = wait_for_approval(timeout=15*60)  # 15 minutes
        
        if response == "approved":
            return True
        elif response == "denied":
            return False
        else:  # Timeout
            # Auto-approve on timeout for medium risk
            log_action(action, "auto_approved_on_timeout", risk_score)
            return True
    
    else:  # risk_score >= 70
        # High risk - require explicit approval
        page_on_call(action, risk_score)
        response = wait_for_approval(timeout=60*60)  # 60 minutes
        
        if response == "approved":
            return True
        else:  # Denied or timeout
            log_action(action, "denied", risk_score)
            return False
```

#### **Component 3: Autonomous Incident Remediation**

Pre-approved remediation playbooks for common incidents:

```yaml
Autonomous Remediation Rules:

  Incident: Pod Crash Loop
    Detection:
      - restart_count > 3 in 5 minutes
      - exit_code != 0
    Conditions for Auto-Remediation:
      - crash_count < 5
      - similar incidents resolved automatically before
      - blast_radius < 5 pods
    Actions:
      1. Restart pod
      2. Collect logs (retain 7 days)
      3. Check resource limits
      4. Alert if persists after 3 restarts
    Human Notification: Post-action summary
    Rollback: Automatic if remediation fails
  
  Incident: Resource Exhaustion
    Detection:
      - cpu_utilization > 90% for 5 minutes
      - memory_utilization > 85% for 5 minutes
    Conditions for Auto-Remediation:
      - within_scaling_limits
      - cost_delta < $50
      - auto_scaling_enabled
    Actions:
      1. Scale horizontally (+1 replica)
      2. Monitor metrics for 10 minutes
      3. Scale down if utilization drops
    Human Notification: Post-action summary
    Rollback: Automatic scale-down after 30 minutes if stable
  
  Incident: Certificate Expiring
    Detection:
      - days_until_expiry < 7
    Conditions for Auto-Remediation:
      - auto_renewal_configured
      - renewal_tested_successfully
    Actions:
      1. Request certificate renewal
      2. Validate new certificate
      3. Update in secret store
      4. Rolling restart affected pods
    Human Notification: Post-action summary
    Rollback: Revert to previous certificate if validation fails
```

**Autonomy Impact**: 80% of incidents auto-remediated

#### **Component 4: Autonomous Budget Management**

Pre-approved budget envelopes allow autonomous spending:

```yaml
Budget Envelope Configuration:

  Envelope: "tier-3-operations-monthly"
    Amount: $5000
    Period: monthly
    Auto-renew: true
    Rollover: 20% to next month
  
  Autonomous Spending Rules:
    Auto-Approve if:
      - cost <= remaining_budget_in_envelope
      - cost_per_unit < historical_average * 1.2
      - ROI_projection > 2.0 AND payback < 3 months
    
    Require Approval if:
      - cost > remaining_budget_in_envelope
      - cost_per_unit > historical_average * 2.0
  
  Automatic Reallocation:
    Trigger: envelope_utilization > 80% AND period_remaining > 25%
    Action: Request additional 20% from reserve
    Approval: Automatic if reserve available
```

**Example**:

```
Agent needs to scale up (cost: $50)
  - Remaining budget in envelope: $2000
  - $50 <= $2000 → Auto-approved ✅
  - No human approval needed
  - Budget updated: $1950 remaining

Agent needs new infrastructure (cost: $6000)
  - Remaining budget in envelope: $1950
  - $6000 > $1950 → Requires approval ❌
  - Escalated to cost center owner
```

**Autonomy Impact**: 90% of budget decisions auto-approved

---

### **Measuring Autonomy**

Track these metrics continuously:

```yaml
Autonomy Metrics:

  Overall Autonomy:
    Formula: (auto_approved_actions + auto_executed_actions) / total_actions
    Target: >= 0.80
    Measurement: Real-time
  
  By Category:
    - Deployment Autonomy: >= 0.85
    - Incident Autonomy: >= 0.80
    - Budget Autonomy: >= 0.90
    - Compliance Autonomy: >= 0.95
  
  Reporting:
    - Daily: Operations team dashboard
    - Weekly: Leadership executive summary
  
  Alerting:
    - overall_autonomy < 0.80 → Investigate bottlenecks
    - autonomy_trend_decreasing → Review risk thresholds
```

**Dashboard Example**:

```
┌─────────────────────────────────────────────────────┐
│ Autonomy Dashboard - Last 7 Days                    │
├─────────────────────────────────────────────────────┤
│ Overall Autonomy:        ████████░░ 82% ✅          │
│ Deployment Autonomy:     █████████░ 87% ✅          │
│ Incident Autonomy:       ████████░░ 81% ✅          │
│ Budget Autonomy:         █████████░ 92% ✅          │
│ Compliance Autonomy:     ██████████ 96% ✅          │
├─────────────────────────────────────────────────────┤
│ Actions Today:                                       │
│   Auto-Approved:   245 (83%)                        │
│   Human-Approved:   42 (14%)                        │
│   Denied:            8 (3%)                         │
├─────────────────────────────────────────────────────┤
│ Top Approval Reasons:                                │
│   1. High cost impact (>$1000)      15 actions      │
│   2. Regulated data affected         12 actions      │
│   3. Novel action type               10 actions      │
└─────────────────────────────────────────────────────┘
```

---

## PART 2: ACHIEVING 100% COST ATTRIBUTION

### **Problem Statement**

**Current State** (v2.x):
- Cost attribution tags are optional
- 60% of resources lack proper tagging
- Shared infrastructure costs not allocated
- Manual monthly reconciliation required
- **Result**: ~40% cost attribution completeness

**Target State** (v3.0):
- Mandatory cost attribution tags (admission control enforced)
- 100% of resources tagged
- Shared costs automatically allocated
- Real-time chargeback with automated invoicing
- **Result**: 100% cost attribution, <0.01% reconciliation variance

---

### **Solution: Universal Cost Attribution Framework**

#### **Component 1: Mandatory Resource Tagging**

Admission control blocks resources without required tags:

```yaml
Required Tags (Enforced at Admission):

  Business Attribution (from namespace):
    - cost-center: "CC-1234"
      Pattern: ^CC-[0-9]{4}$
      Validated against: finance_system_api
    
    - project-id: "PROJ-ABC123"
      Pattern: ^PROJ-[A-Z0-9]{6}$
      Validated against: project_management_system
    
    - business-unit: "engineering"
      Pattern: ^(engineering|operations|research|sales)$
      Validated against: org_hierarchy_api
  
  Agent Attribution (from pod labels):
    - agent-id: "security-agent"
      Pattern: ^[a-z0-9-]+$
    
    - agent-tier: "3"
      Pattern: ^[1-4]$
    
    - agent-owner: "team-lead@company.com"
      Pattern: ^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$
  
  Resource Attribution (auto-populated):
    - resource-owner: "agent:security-agent"
      Auto-populated from pod metadata
    
    - creation-timestamp: "2025-11-20T15:30:00Z"
      Auto-populated from metadata
```

**Enforcement**:

```yaml
Admission Control Policy:

  On Resource Creation:
    1. Extract required tags
    2. Validate tag values against patterns
    3. Validate tag values against authoritative sources (cached 5 min)
    4. If any tag missing or invalid → DENY creation
    5. If all tags valid → ALLOW creation
  
  Tag Propagation:
    - Inherit from namespace: cost-center, project-id, business-unit
    - Inherit from parent: agent-id, agent-tier
    - Propagate to children: persistent volumes, services, ingress
  
  No Exemptions:
    - Cost attribution tags are ALWAYS required
    - No bypass mechanism
```

**Result**: 100% of resources have complete cost attribution tags

#### **Component 2: Shared Resource Cost Allocation**

Proportionally allocate shared infrastructure costs:

```yaml
Shared Resource Allocation:

  Network Egress:
    Allocation Method: Proportional by bytes transferred
    Metering Source: Network flow logs
    Attribution Key: source_pod_label.agent-id
    Calculation:
      agent_cost = total_egress_cost * (agent_bytes / total_bytes)
  
  Load Balancer:
    Allocation Method: Proportional by request count
    Metering Source: Ingress controller metrics
    Attribution Key: backend_service_label.agent-id
    Calculation:
      agent_cost = lb_cost * (agent_requests / total_requests)
  
  Object Storage:
    Allocation Method: Proportional by bytes stored
    Metering Source: Storage bucket tags
    Attribution Key: object_tag.agent-id
    Calculation:
      agent_cost = storage_cost * (agent_gb_hours / total_gb_hours)
  
  Metrics Storage:
    Allocation Method: Proportional by metric count
    Metering Source: Metrics database
    Attribution Key: metric_label.agent-id
    Calculation:
      agent_cost = metrics_cost * (agent_samples / total_samples)
  
  Log Storage:
    Allocation Method: Proportional by log volume
    Metering Source: Log aggregator
    Attribution Key: log_label.agent-id
    Calculation:
      agent_cost = log_cost * (agent_log_bytes / total_log_bytes)
  
  Control Plane Overhead:
    Allocation Method: Proportional by pod count
    Metering Source: Cluster inventory
    Attribution Key: pod_label.agent-id
    Calculation:
      agent_cost = platform_cost * (agent_pods / total_pods)
```

**Result**: 100% of shared infrastructure costs allocated

#### **Component 3: Real-Time Chargeback Engine**

Automated cost metering and invoicing:

```yaml
Chargeback Pipeline:

  Step 1: Metering (Real-Time)
    Sources:
      - Compute: CPU seconds, memory GB-seconds (1 min frequency)
      - Storage: GB-hours, IOPS (1 hour frequency)
      - Network: Ingress/egress bytes (5 min frequency)
      - External APIs: API calls, tokens (real-time)
    
    Granularity: Pod-level, volume-level, flow-level
  
  Step 2: Enrichment
    Join with:
      - Resource tags (agent-id, cost-center, project-id)
      - Namespace annotations (business-unit, environment)
      - Rate card (pricing per unit)
    
    Calculate: metric_value * rate = line_item_cost
  
  Step 3: Accumulation (Real-Time)
    Aggregate by:
      - agent-id
      - project-id
      - cost-center
      - business-unit
    
    Store in: cost_accumulation_database
  
  Step 4: Invoicing (Monthly)
    Generate:
      - Detailed line items (CSV + JSON)
      - Cost breakdown by resource type
      - Trend analysis vs previous month
    
    Deliver to: finance_system_api (automated push)
    
    Reconciliation: Automated three-way match
      - Platform metering data
      - Finance system general ledger
      - Cloud provider billing
    
    Variance Tolerance: < 0.01%
```

**Example Invoice**:

```
┌─────────────────────────────────────────────────────────────────┐
│ Monthly Invoice - November 2025                                 │
│ Cost Center: CC-1234 (Engineering)                              │
│ Project: PROJ-ABC123 (AI Agent Platform)                        │
├─────────────────────────────────────────────────────────────────┤
│ Agent: security-agent                                            │
│                                                                  │
│ Compute:                                                         │
│   CPU (1,234,567 seconds @ $0.00005/sec)        $61.73          │
│   Memory (45,678 GB-sec @ $0.00001/GB-sec)      $0.46           │
│   GPU (0 seconds)                               $0.00           │
│                                                  ------          │
│   Subtotal Compute:                             $62.19          │
│                                                                  │
│ Storage:                                                         │
│   Persistent Volumes (500 GB-hours @ $0.10/GB-hr) $50.00        │
│   Object Storage (1,200 GB-hours @ $0.02/GB-hr)   $24.00        │
│                                                  ------          │
│   Subtotal Storage:                             $74.00          │
│                                                                  │
│ Network:                                                         │
│   Egress (150 GB @ $0.12/GB)                    $18.00          │
│   Load Balancer (allocated)                     $5.23           │
│                                                  ------          │
│   Subtotal Network:                             $23.23          │
│                                                                  │
│ External Services:                                               │
│   LLM API (1.2M tokens @ $0.002/1k tokens)      $2.40           │
│   Third-party APIs (5,000 calls @ $0.01/call)   $50.00          │
│                                                  ------          │
│   Subtotal External:                            $52.40          │
│                                                                  │
│ Platform Overhead (allocated):                  $12.50          │
│                                                                  │
│ TOTAL:                                          $224.32          │
│                                                                  │
│ Budget: $5,000.00                                                │
│ Remaining: $4,775.68 (95.5%)                                     │
└─────────────────────────────────────────────────────────────────┘
```

#### **Component 4: License and API Cost Tracking**

Attribute software license and external API costs:

```yaml
License/API Cost Tracking:

  LLM API Costs:
    Metering: API call interception via proxy
    Attribution: Extract from request headers
      - X-Agent-ID
      - X-Cost-Center
      - X-Project-ID
    Calculation:
      - Input tokens * rate_per_1k_tokens
      - Output tokens * rate_per_1k_tokens
      - API calls * rate_per_call
    Enforcement: Deny requests without attribution headers
  
  External API Costs:
    Metering: Service mesh sidecar tracking
    Attribution: Extract from service mesh metadata
      - source_workload_label.agent-id
      - source_namespace_annotation.cost-center
    Calculation:
      - API calls * rate_per_call
      - Data transferred * rate_per_gb
  
  Software Licenses:
    Metering: Usage tracking via authentication logs
    Attribution: Extract from user attributes
      - user_attribute.agent-id
      - user_attribute.cost-center
    Calculation:
      - Concurrent users * rate_per_user_per_month
      - Feature usage * rate_per_feature
```

**Result**: 100% of license and API costs attributed

#### **Component 5: Idle Resource Detection**

Track and attribute costs of idle/wasted resources:

```yaml
Idle Resource Detection:

  Idle Pods:
    Criteria:
      - cpu_utilization < 5% for 24 hours
      - memory_utilization < 10% for 24 hours
      - network_bytes_transferred == 0 for 12 hours
    
    Cost Attribution:
      - Charge as: "waste_cost"
      - Attribute to: resource_owner_agent
      - Category: "idle_compute"
    
    Remediation:
      - idle > 7 days AND cost > $10/month → Notify + schedule deletion (48hr grace)
      - idle > 30 days → Auto-delete with notification
  
  Idle Volumes:
    Criteria:
      - read_ops == 0 AND write_ops == 0 for 7 days
      - attached_to_pod == false for 3 days
    
    Cost Attribution:
      - Charge as: "waste_cost"
      - Attribute to: volume_claim_owner_agent
      - Category: "idle_storage"
    
    Remediation:
      - idle > 14 days AND cost > $5/month → Snapshot + delete (72hr grace)
  
  Waste Reduction Target: < 5% of total cost
```

**Waste Report Example**:

```
┌─────────────────────────────────────────────────────┐
│ Idle Resource Report - Week of Nov 18-24, 2025     │
├─────────────────────────────────────────────────────┤
│ Agent: security-agent                                │
│                                                      │
│ Idle Compute:                                        │
│   - pod/scanner-backup (idle 10 days)    $15.20    │
│   - pod/temp-analyzer (idle 5 days)      $8.40     │
│                                           ------     │
│   Subtotal: $23.60                                   │
│                                                      │
│ Idle Storage:                                        │
│   - pvc/old-logs (idle 20 days)          $12.00    │
│                                           ------     │
│   Subtotal: $12.00                                   │
│                                                      │
│ Total Waste: $35.60 (15.9% of agent's total cost)  │
│                                                      │
│ Recommended Actions:                                 │
│   1. Delete pod/scanner-backup (saves $45/month)    │
│   2. Snapshot + delete pvc/old-logs (saves $18/mo)  │
└─────────────────────────────────────────────────────┘
```

---

### **Measuring Cost Attribution**

Track these metrics continuously:

```yaml
Cost Attribution Metrics:

  Overall Attribution:
    Formula: attributed_costs / total_costs
    Target: == 1.00
    Tolerance: < 0.001 (less than 0.1% unattributed)
    Measurement: Hourly
  
  By Resource Type:
    - Compute Attribution: == 1.00
    - Storage Attribution: == 1.00
    - Network Attribution: == 1.00
    - License/API Attribution: == 1.00
    - Shared Resource Attribution: == 1.00
  
  Reconciliation:
    - Frequency: Monthly
    - Method: Automated three-way match
    - Variance Tolerance: < 0.01%
  
  Reporting:
    - Daily: Finance team dashboard
    - Monthly: Cost center owners (detailed invoice)
  
  Alerting:
    - attribution_completeness < 0.99 → Investigate unattributed costs
    - reconciliation_variance > 0.01% → Audit attribution pipeline
```

---

## IMPLEMENTATION CHECKLIST

### **Phase 1: Foundation**

- [ ] Deploy mandatory tagging admission control
- [ ] Configure cost attribution tags on all namespaces
- [ ] Deploy risk scoring engine
- [ ] Validate 100% of new resources have required tags
- [ ] Validate risk scores calculated for all actions

### **Phase 2: Autonomy Enablement**

- [ ] Deploy automated approval decision engine
- [ ] Configure pre-approved budget envelopes
- [ ] Deploy autonomous remediation framework
- [ ] Tune risk thresholds based on historical data
- [ ] Achieve ≥60% autonomy

### **Phase 3: Cost Attribution**

- [ ] Deploy shared resource cost allocator
- [ ] Deploy real-time chargeback engine
- [ ] Integrate license/API cost tracking
- [ ] Configure automated monthly invoicing
- [ ] Achieve ≥95% cost attribution

### **Phase 4: Optimization**

- [ ] Deploy idle resource detector
- [ ] Tune autonomy thresholds to reach ≥80%
- [ ] Optimize cost allocation algorithms
- [ ] Validate reconciliation variance <0.01%
- [ ] Achieve ≥80% autonomy AND 100% cost attribution

### **Phase 5: Validation**

- [ ] Autonomy metrics dashboard operational
- [ ] Cost attribution dashboard operational
- [ ] Automated monthly invoicing working
- [ ] Finance reconciliation automated
- [ ] All business goals achieved ✅

---

## TROUBLESHOOTING

### **Autonomy < 80%**

**Symptom**: Overall autonomy percentage below target

**Diagnosis**:
1. Check which category is underperforming
2. Review approval logs for common denial reasons
3. Analyze risk score distribution

**Solutions**:
- If too many medium-risk actions denied: Increase timeout from 15min to 30min
- If risk scores too high: Recalibrate dimension weights
- If novel actions blocked: Add to pre-approved playbooks

### **Cost Attribution < 100%**

**Symptom**: Unattributed costs detected

**Diagnosis**:
1. Query for resources without required tags
2. Check shared resource allocation logs
3. Review reconciliation variance report

**Solutions**:
- If resources missing tags: Verify admission control is enforcing
- If shared costs unallocated: Check metering source connectivity
- If reconciliation variance high: Audit cost calculation formulas

---

## CONCLUSION

By implementing the Risk-Based Autonomy Framework and Universal Cost Attribution Framework, you will achieve:

✅ **≥80% Autonomous Operations**
- Agents operate independently for routine tasks
- Human approval only for high-risk scenarios
- Faster incident response and deployment velocity

✅ **100% Cost Attribution**
- Every dollar automatically attributed
- Real-time cost visibility
- Automated chargeback with zero manual reconciliation

**Next Steps**: Begin with Phase 1 (Foundation) and progress through the implementation roadmap.
