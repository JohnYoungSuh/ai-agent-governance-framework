# PAR-PROTO Workflow - Integration Guide

**Version:** 1.0
**Last Updated:** 2025-10-12
**Framework:** AI Agent Governance Framework

---

## Table of Contents

1. [Overview](#overview)
2. [Core PAR Model](#core-par-model)
3. [PROTO Extension](#proto-extension)
4. [Workflow Integration](#workflow-integration)
5. [Tier-Specific Implementations](#tier-specific-implementations)
6. [Templates & Examples](#templates--examples)
7. [Quality Assurance](#quality-assurance)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The **PAR-PROTO Workflow** is a structured approach for AI agent task execution that ensures:
- **Accountability**: Every action is traceable to a problem and validated by results
- **Governance**: Tier-appropriate oversight and approval processes
- **Quality**: Consistent execution with measurable outcomes
- **Scalability**: Works across all agent tiers (Observer → Architect)

### Key Principles

1. **Problem-First Thinking**: Every agent action must address a clearly defined problem
2. **Action Planning**: All actions are planned, reviewed, and approved before execution
3. **Results Validation**: Outcomes are measured against success criteria
4. **PROTO Context**: Plan → Review → Observe → Test → Output for complex workflows
5. **Human Oversight**: Tier-appropriate human involvement throughout the cycle

---

## Core PAR Model

The PAR (Problem → Action → Results) model is the foundation of all agent workflows.

### 1. Problem Phase

**Objective**: Clearly define what needs to be solved

```yaml
problem:
  title: "Brief description of the issue"
  description: |
    Detailed explanation of:
    - What is wrong or needs improvement
    - Why it matters (business/technical impact)
    - Current state vs. desired state

  context:
    environment: [development, staging, production]
    affected_systems: ["list", "of", "systems"]
    priority: [low, medium, high, critical]

  success_criteria:
    - "Measurable outcome 1"
    - "Measurable outcome 2"

  constraints:
    - "Budget: $X"
    - "Timeline: Y hours/days"
    - "Dependencies: Z must be completed first"
```

**Best Practices:**
- Use specific, measurable language
- Include relevant context and history
- Define clear success criteria upfront
- Identify constraints early

**Example Problem Definitions:**

```yaml
# Good Problem Definition
problem:
  title: "API response time degradation in user-service"
  description: |
    P95 latency for /users endpoint increased from 150ms to 850ms
    over the past 48 hours. Affecting 45% of user requests.
    No recent deployments. Database CPU at 85%.
  success_criteria:
    - "P95 latency < 200ms"
    - "Database CPU < 60%"
    - "No service disruption during fix"

# Poor Problem Definition (avoid this)
problem:
  title: "API is slow"
  description: "Users are complaining about performance"
  # Missing: metrics, impact, success criteria, constraints
```

---

### 2. Action Phase

**Objective**: Plan, approve, and execute solutions

#### 2.1 Action Planning

```yaml
action:
  proposed_solution: "High-level approach"

  steps:
    - step: 1
      description: "Analyze database query performance"
      commands:
        - "EXPLAIN ANALYZE SELECT * FROM users WHERE active = true"
      estimated_time: "15 minutes"
      risk: low
      reversible: true

    - step: 2
      description: "Add index on active column"
      commands:
        - "CREATE INDEX CONCURRENTLY idx_users_active ON users(active)"
      estimated_time: "30 minutes"
      risk: medium
      reversible: true
      rollback_plan: "DROP INDEX idx_users_active"

  required_approvals:
    - type: "pre_approval"
      approver: "Database Admin"
      reason: "Production database modification"

  risk_assessment:
    likelihood: medium
    impact: low
    mitigation: "Using CONCURRENTLY to avoid table locks"

  resources_required:
    cost_estimate: "$2.50"
    time_estimate: "45 minutes"
    human_oversight: "Monitoring during execution"
```

#### 2.2 Approval Process

The approval process varies by agent tier:

| Tier | Approval Type | Approver | Timeline |
|------|---------------|----------|----------|
| Tier 1 (Observer) | Post-review | Any team member | Within 24 hours |
| Tier 2 (Developer) | Pre-approval (architecture) + Post-review (implementation) | Tech lead | < 1 hour |
| Tier 3 (Operations) | Pre-approval + Real-time monitoring | Ops manager | < 4 hours |
| Tier 4 (Architect) | Collaborative decision | Stakeholders | 1-5 days |

**Approval Workflow Example:**

```yaml
approval_request:
  agent_tier: tier_3
  workflow: enhanced_approval

  request:
    problem_id: "PERF-2025-001"
    proposed_actions: "Add database index on users.active column"
    risk_level: medium
    estimated_cost: "$2.50"
    estimated_time: "45 minutes"

  approval_chain:
    - role: "Tech Lead"
      decision: [approve, reject, modify]
      timestamp: "2025-10-12T14:30:00Z"

    - role: "Database Admin"
      decision: [approve, reject]
      timestamp: "2025-10-12T14:45:00Z"

  status: approved
  execution_window: "2025-10-12T15:00:00Z to 2025-10-12T16:00:00Z"
```

#### 2.3 Execution

```yaml
execution:
  start_time: "2025-10-12T15:00:00Z"

  real_time_log:
    - timestamp: "2025-10-12T15:00:05Z"
      step: 1
      status: "started"
      message: "Running EXPLAIN ANALYZE"

    - timestamp: "2025-10-12T15:02:30Z"
      step: 1
      status: "completed"
      message: "Query plan shows sequential scan on 2M rows"

    - timestamp: "2025-10-12T15:03:00Z"
      step: 2
      status: "started"
      message: "Creating index with CONCURRENTLY option"

    - timestamp: "2025-10-12T15:28:00Z"
      step: 2
      status: "completed"
      message: "Index created successfully. No locks detected."

  monitoring:
    metrics_tracked:
      - "Database CPU utilization"
      - "Active connections"
      - "Query latency"

  end_time: "2025-10-12T15:28:30Z"
  total_duration: "28 minutes 30 seconds"
```

---

### 3. Results Phase

**Objective**: Validate outcomes and capture learnings

```yaml
results:
  success: true

  outcomes:
    - metric: "P95 latency"
      before: "850ms"
      after: "165ms"
      improvement: "80.6%"
      meets_criteria: true

    - metric: "Database CPU"
      before: "85%"
      after: "52%"
      improvement: "38.8%"
      meets_criteria: true

    - metric: "Service availability"
      value: "100% (no downtime)"
      meets_criteria: true

  actual_costs:
    compute: "$2.35"
    human_time: "10 minutes oversight"
    total: "$2.35 + $8.33 = $10.68"

  roi_analysis:
    time_saved_per_week: "5 hours (reduced incident response)"
    cost_saved_per_week: "$250"
    roi_ratio: "23.4:1"

  lessons_learned:
    - "CONCURRENTLY option prevented table locks as expected"
    - "Query planner immediately utilized new index"
    - "Consider proactive index analysis for other high-traffic tables"

  follow_up_actions:
    - action: "Schedule quarterly index review"
      assignee: "Database Admin"
      due_date: "2026-01-15"

    - action: "Document index strategy in runbook"
      assignee: "Tier 1 Observer Agent"
      due_date: "2025-10-15"

  artifacts:
    - type: "execution_log"
      location: "s3://logs/PERF-2025-001/execution.log"

    - type: "metrics_dashboard"
      location: "https://grafana.company.com/d/perf-2025-001"

    - type: "post_mortem"
      location: "docs/incidents/PERF-2025-001-postmortem.md"
```

**Results Quality Checklist:**

- [ ] All success criteria addressed
- [ ] Metrics include before/after comparison
- [ ] ROI calculated (for Tier 2+)
- [ ] Lessons learned documented
- [ ] Follow-up actions assigned
- [ ] Artifacts archived
- [ ] Stakeholders notified

---

## PROTO Extension

For complex, multi-step workflows, extend PAR with the **PROTO** framework:

**P**lan → **R**eview → **O**bserve → **T**est → **O**utput

### When to Use PROTO

Use PROTO when:
- Task involves multiple systems or dependencies
- Changes affect production systems (Tier 3+)
- Solution requires iterative refinement
- Risk level is medium or high
- Multiple stakeholders involved

### PROTO Workflow

```yaml
proto_workflow:
  problem: "Migrate user authentication from OAuth 1.0 to OAuth 2.0"

  # P - Plan
  plan:
    approach: "Phased migration with backward compatibility"
    phases:
      - phase: 1
        name: "Add OAuth 2.0 support (parallel to OAuth 1.0)"
        duration: "2 weeks"

      - phase: 2
        name: "Migrate 10% of users (canary deployment)"
        duration: "1 week"

      - phase: 3
        name: "Migrate remaining users"
        duration: "1 week"

      - phase: 4
        name: "Deprecate OAuth 1.0"
        duration: "1 week"

    dependencies:
      - "Update OAuth library to v2.3+"
      - "Configure new OAuth provider"
      - "Update client applications"

    rollback_strategy: "Keep OAuth 1.0 active until 100% migration verified"

  # R - Review
  review:
    peer_review:
      - reviewer: "Senior Developer"
        focus: "Code quality and security"
        status: "approved"

      - reviewer: "Security Engineer"
        focus: "Authentication flow and token handling"
        status: "approved_with_comments"
        comments: "Add rate limiting on token endpoint"

    architecture_review:
      reviewer: "Tier 4 Architect Agent"
      status: "approved"
      recommendations:
        - "Use refresh tokens with 7-day expiry"
        - "Implement token rotation"

    risk_review:
      identified_risks:
        - risk: "User session disruption during migration"
          mitigation: "Gradual rollout with instant rollback capability"
          severity: medium

        - risk: "OAuth provider downtime"
          mitigation: "Multi-region provider with failover"
          severity: low

  # O - Observe
  observe:
    monitoring_setup:
      metrics:
        - "Authentication success rate (OAuth 1.0 vs 2.0)"
        - "Token issuance latency"
        - "User session errors"
        - "Provider API errors"

      alerts:
        - condition: "OAuth 2.0 success rate < 95%"
          action: "Pause migration, notify team"

        - condition: "Token latency > 500ms"
          action: "Investigate provider performance"

      dashboards:
        - "Real-time migration progress"
        - "Authentication metrics comparison"

    baseline_metrics:
      oauth1_success_rate: "99.2%"
      oauth1_avg_latency: "180ms"
      daily_active_users: "45,000"

  # T - Test
  test:
    test_phases:
      - phase: "Unit Tests"
        coverage: "95%"
        status: "passed"

      - phase: "Integration Tests"
        scenarios:
          - "New user registration with OAuth 2.0"
          - "Existing user login (OAuth 1.0 to 2.0 migration)"
          - "Token refresh flow"
          - "Token revocation"
        status: "passed"

      - phase: "Load Tests"
        scenarios:
          - "10,000 concurrent authentications"
          - "Token refresh under load"
        results:
          p95_latency: "165ms"
          success_rate: "99.8%"
        status: "passed"

      - phase: "Security Tests"
        tests:
          - "OWASP OAuth 2.0 security checklist"
          - "Penetration testing"
          - "Token leakage analysis"
        status: "passed"

      - phase: "Canary Deployment (10% users)"
        duration: "7 days"
        metrics:
          success_rate: "99.6%"
          user_issues: 2
          rollbacks: 0
        status: "passed"

  # O - Output
  output:
    deliverables:
      - artifact: "Updated authentication service"
        location: "https://github.com/company/auth-service/releases/v2.0.0"

      - artifact: "Migration runbook"
        location: "docs/runbooks/oauth2-migration.md"

      - artifact: "Security audit report"
        location: "docs/security/oauth2-audit-2025-10.pdf"

      - artifact: "Monitoring dashboard"
        location: "https://grafana.company.com/d/oauth2-migration"

    results_summary:
      total_users_migrated: "45,000"
      success_rate: "99.8%"
      issues_encountered: 2
      downtime: "0 minutes"
      total_duration: "5 weeks"

    roi_analysis:
      development_cost: "$12,000"
      reduced_maintenance: "$4,000/year"
      improved_security: "Eliminated 3 known OAuth 1.0 vulnerabilities"
      user_experience: "15% faster authentication"
      payback_period: "3 years"

    lessons_learned:
      - "Gradual rollout prevented user disruption"
      - "Real-time monitoring enabled quick issue detection"
      - "Backward compatibility was critical for smooth migration"
      - "Security review identified rate limiting gap early"

    handoff:
      to: "Operations Team"
      documentation: "Complete"
      training: "Conducted on 2025-10-10"
      support_plan: "24/7 on-call for 2 weeks post-migration"
```

---

## Workflow Integration

### Integration with Agent Tiers

The PAR-PROTO workflow adapts to each agent tier's capabilities and oversight requirements.

#### Tier 1 (Observer) - Read-Only Operations

```yaml
tier_1_par_workflow:
  permitted_activities:
    - "Problem identification through monitoring"
    - "Report generation"
    - "Documentation creation"
    - "Static code analysis"

  approval_process:
    type: "post_review"
    timeline: "Within 24 hours"

  example_use_case:
    problem: "Generate monthly security audit report"

    action:
      - "Query audit logs from security SIEM"
      - "Analyze compliance violations"
      - "Generate markdown report"
      - "Upload to documentation repository"

    results:
      - "Report generated: docs/audits/2025-10-security-audit.md"
      - "5 minor violations identified"
      - "0 critical issues"
      - "100% compliance with SOC 2 requirements"

    cost: "$0.35"
    roi: "Saved 4 hours of manual work"
```

#### Tier 2 (Developer) - Development Environment

```yaml
tier_2_par_workflow:
  permitted_activities:
    - "Code development in feature branches"
    - "Test execution in isolated environments"
    - "Pull request creation"
    - "Refactoring with approval"

  approval_process:
    type: "pre_approval_architecture_post_review_implementation"
    timeline: "< 1 hour"

  example_use_case:
    problem: "Refactor user authentication module for testability"

    action:
      plan:
        - "Extract authentication logic into service class"
        - "Add dependency injection"
        - "Write unit tests (target: 90% coverage)"
        - "Create pull request"

      approval_required:
        - stage: "Architecture"
          approver: "Tech Lead"
          status: "approved"

      execution:
        - "Create feature branch: refactor/auth-module"
        - "Implement service pattern"
        - "Run test suite (125 tests, 92% coverage)"
        - "Create PR #4521"

    results:
      - "Code complexity reduced by 40%"
      - "Test coverage increased from 65% to 92%"
      - "0 regressions detected"
      - "PR approved and merged"

    cost: "$4.25"
    roi: "12:1 (easier maintenance, faster future changes)"
```

#### Tier 3 (Operations) - Production Deployments

```yaml
tier_3_par_workflow:
  permitted_activities:
    - "Approved production deployments"
    - "Runbook execution"
    - "Service restarts (within SOP)"
    - "Resource scaling (within limits)"

  approval_process:
    type: "enhanced_approval_with_real_time_monitoring"
    timeline: "< 4 hours"

  example_use_case:
    problem: "Deploy hotfix for critical payment processing bug"

    action:
      plan:
        - "Deploy hotfix v3.2.1 to production"
        - "Monitor payment success rate"
        - "Rollback if success rate < 99%"

      approval_required:
        - stage: "Pre-deployment"
          approvers:
            - "Engineering Manager"
            - "On-call Engineer"
          status: "approved"

      execution:
        - timestamp: "2025-10-12T09:00:00Z"
          action: "Deploy to production-east-1"
          status: "success"

        - timestamp: "2025-10-12T09:05:00Z"
          action: "Monitor payment metrics"
          metrics:
            success_rate: "99.4%"
            latency_p95: "320ms"

        - timestamp: "2025-10-12T09:10:00Z"
          action: "Deploy to production-west-1"
          status: "success"

      real_time_oversight:
        human_observer: "On-call Engineer"
        monitoring: "Continuous"
        communication: "Slack #incidents channel"

    results:
      - "Deployment successful across all regions"
      - "Payment success rate: 99.6% (up from 94.2%)"
      - "0 rollbacks required"
      - "Total downtime: 0 minutes"

    post_deployment:
      - "Post-mortem scheduled"
      - "Root cause analysis assigned"
      - "Prevention measures documented"

    cost: "$8.50"
    roi: "Prevented $50K/hour revenue loss"
```

#### Tier 4 (Architect) - Strategic Planning

```yaml
tier_4_par_workflow:
  permitted_activities:
    - "System architecture design"
    - "Technology evaluation"
    - "Cost-benefit analysis"
    - "POC development"

  approval_process:
    type: "collaborative_decision_making"
    timeline: "1-5 days"

  example_use_case:
    problem: "Evaluate migration from monolith to microservices"

    action:
      research_phase:
        - "Analyze current system bottlenecks"
        - "Evaluate microservices patterns (Event-driven, API Gateway, etc.)"
        - "Research container orchestration (Kubernetes, ECS)"
        - "Calculate migration costs and timeline"

      proto_workflow: true

      plan:
        approach: "Strangler Fig pattern (gradual extraction)"
        phases:
          - "Extract user service (pilot)"
          - "Extract payment service"
          - "Extract inventory service"
          - "Migrate remaining components"
        duration: "18 months"

      review:
        stakeholders:
          - "CTO"
          - "Engineering Managers"
          - "DevOps Lead"
          - "Security Team"
        review_sessions: 3

      observe:
        pilot_metrics:
          - "User service performance"
          - "Development velocity"
          - "Operational overhead"

      test:
        poc_deliverables:
          - "User service microservice (containerized)"
          - "API Gateway configuration"
          - "Service mesh implementation"
          - "Monitoring and logging"

      output:
        recommendation: "Proceed with phased migration"
        rationale:
          - "Pilot reduced user service latency by 60%"
          - "Improved team autonomy and velocity"
          - "Managed operational complexity with service mesh"

    results:
      decision: "approved"
      budget_allocated: "$450,000"
      timeline: "18 months"
      success_metrics:
        - "50% reduction in deployment lead time"
        - "80% reduction in service-specific outages"
        - "30% improvement in team velocity"

    cost: "$28.00 (agent research and analysis)"
    roi: "Strategic value (enables future scalability)"
```

---

## Tier-Specific Implementations

### Quick Reference Matrix

| Aspect | Tier 1 (Observer) | Tier 2 (Developer) | Tier 3 (Operations) | Tier 4 (Architect) |
|--------|-------------------|-------------------|--------------------|--------------------|
| **Problem Scope** | Reporting, analysis | Feature development | Deployments, incidents | System design |
| **Action Authority** | Read-only | Dev environment | Production (approved) | Advisory |
| **Approval Type** | Post-review | Pre-approval (arch) | Enhanced approval | Collaborative |
| **PROTO Usage** | Rarely | Sometimes | Often | Always |
| **Cost Range** | $0.10 - $0.50 | $0.50 - $5.00 | $1.00 - $10.00 | $5.00 - $50.00 |
| **ROI Target** | 10:1 | 5:1 | 3:1 | Strategic value |

---

## Templates & Examples

### PAR Workflow Template (Basic)

```yaml
# Copy this template for simple, single-step workflows

metadata:
  workflow_id: "TASK-YYYY-NNN"
  agent_tier: [1, 2, 3, 4]
  created_at: "YYYY-MM-DDTHH:MM:SSZ"
  created_by: "agent-name"

# PROBLEM
problem:
  title: "Brief problem description"
  description: |
    Detailed problem explanation:
    - What is wrong?
    - Why does it matter?
    - Current vs. desired state

  context:
    environment: [dev, staging, production]
    priority: [low, medium, high, critical]

  success_criteria:
    - "Measurable outcome 1"
    - "Measurable outcome 2"

# ACTION
action:
  proposed_solution: "High-level approach"

  steps:
    - step: 1
      description: "What will be done"
      commands: ["command1", "command2"]
      estimated_time: "X minutes"
      risk: [low, medium, high]
      reversible: [true, false]
      rollback_plan: "How to undo if needed"

  required_approvals:
    - type: [pre_approval, post_review, dual_signoff]
      approver: "Role or name"

  risk_assessment:
    likelihood: [low, medium, high]
    impact: [low, medium, high]
    mitigation: "How risks are managed"

# RESULTS
results:
  success: [true, false]

  outcomes:
    - metric: "Metric name"
      before: "Value before"
      after: "Value after"
      meets_criteria: [true, false]

  actual_costs:
    compute: "$X.XX"
    human_time: "Y minutes"

  roi_analysis:
    time_saved: "Z hours/week"
    roi_ratio: "N:1"

  lessons_learned:
    - "Lesson 1"
    - "Lesson 2"
```

### PAR-PROTO Workflow Template (Complex)

```yaml
# Copy this template for complex, multi-step workflows

metadata:
  workflow_id: "PROJECT-YYYY-NNN"
  agent_tier: [2, 3, 4]
  workflow_type: "PAR-PROTO"
  created_at: "YYYY-MM-DDTHH:MM:SSZ"

# PROBLEM
problem:
  title: "Complex problem requiring multi-phase solution"
  description: |
    Detailed problem with systemic implications
  success_criteria:
    - "High-level success metric 1"
    - "High-level success metric 2"

# PLAN
plan:
  approach: "Overall strategy"
  phases:
    - phase: 1
      name: "Phase name"
      duration: "Time estimate"
      deliverables: ["item1", "item2"]

  dependencies:
    - "Dependency 1"

  rollback_strategy: "How to revert entire project"

# REVIEW
review:
  peer_review:
    - reviewer: "Name/Role"
      focus: "Review focus area"
      status: [approved, rejected, approved_with_comments]
      comments: "Feedback"

  architecture_review:
    reviewer: "Architect name"
    status: [approved, rejected]
    recommendations: ["rec1", "rec2"]

  risk_review:
    identified_risks:
      - risk: "Risk description"
        mitigation: "How to handle"
        severity: [low, medium, high, critical]

# OBSERVE
observe:
  monitoring_setup:
    metrics: ["metric1", "metric2"]
    alerts:
      - condition: "Alert condition"
        action: "What to do"
    dashboards: ["dashboard1"]

  baseline_metrics:
    metric1: "Current value"

# TEST
test:
  test_phases:
    - phase: "Test phase name"
      scenarios: ["scenario1", "scenario2"]
      status: [passed, failed]
      results:
        metric1: "Result value"

# OUTPUT
output:
  deliverables:
    - artifact: "Artifact name"
      location: "URL or path"

  results_summary:
    key_metric1: "Final value"

  roi_analysis:
    development_cost: "$X"
    annual_savings: "$Y"
    payback_period: "Z months"

  lessons_learned:
    - "Lesson 1"

  handoff:
    to: "Team/Role"
    documentation: [complete, incomplete]
    training: [conducted, scheduled, not_required]
```

---

## Quality Assurance

### Pre-Execution Checklist

Before executing any PAR workflow:

- [ ] **Problem is clearly defined**
  - [ ] Measurable success criteria
  - [ ] Context and constraints documented
  - [ ] Priority level assigned

- [ ] **Action plan is complete**
  - [ ] Steps are detailed and specific
  - [ ] Risk assessment completed
  - [ ] Rollback plan documented
  - [ ] Cost estimate provided

- [ ] **Approvals obtained**
  - [ ] Correct approval type for agent tier
  - [ ] Required approvers identified
  - [ ] Approval timeline realistic

- [ ] **Monitoring ready** (Tier 3+)
  - [ ] Metrics identified
  - [ ] Alerts configured
  - [ ] Dashboard available
  - [ ] Human oversight assigned

### Post-Execution Checklist

After completing any PAR workflow:

- [ ] **Results validated**
  - [ ] Success criteria met
  - [ ] Metrics show improvement
  - [ ] No unintended side effects

- [ ] **Documentation complete**
  - [ ] Execution log saved
  - [ ] Artifacts archived
  - [ ] Lessons learned captured

- [ ] **Follow-up actions assigned**
  - [ ] Owner identified
  - [ ] Due dates set
  - [ ] Tracking mechanism in place

- [ ] **Stakeholders notified**
  - [ ] Results communicated
  - [ ] Feedback collected
  - [ ] Next steps clarified

### Quality Metrics

Track these metrics to ensure PAR-PROTO workflow effectiveness:

```yaml
quality_metrics:
  success_rate:
    definition: "% of workflows meeting success criteria"
    target: ">95%"
    current: "97.2%"

  approval_time:
    definition: "Average time from request to approval"
    target:
      tier_1: "<24 hours"
      tier_2: "<1 hour"
      tier_3: "<4 hours"
      tier_4: "<5 days"

  defect_rate:
    definition: "% of workflows requiring rollback or rework"
    target: "<5%"
    current: "2.8%"

  roi_achievement:
    definition: "% of workflows meeting ROI targets"
    target:
      tier_1: ">90% achieve 10:1"
      tier_2: ">85% achieve 5:1"
      tier_3: ">80% achieve 3:1"
    current:
      tier_1: "92%"
      tier_2: "88%"
      tier_3: "85%"

  documentation_completeness:
    definition: "% of workflows with complete PAR documentation"
    target: "100%"
    current: "98.5%"
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Unclear Problem Definition

**Symptoms:**
- Success criteria are vague or subjective
- Multiple interpretations of the problem
- Scope creep during execution

**Solutions:**
1. Use the "5 Whys" technique to drill down to root cause
2. Include quantitative metrics in success criteria
3. Get stakeholder alignment before proceeding
4. Document what is explicitly out of scope

**Example:**
```yaml
# Before (unclear)
problem:
  title: "Improve system performance"
  success_criteria:
    - "System runs faster"

# After (clear)
problem:
  title: "Reduce API p95 latency for /users endpoint"
  success_criteria:
    - "P95 latency < 200ms (currently 850ms)"
    - "P99 latency < 500ms (currently 2100ms)"
    - "No increase in error rate"
  out_of_scope:
    - "Other endpoints (handled separately)"
    - "Database infrastructure upgrades"
```

---

#### Issue: Approval Delays

**Symptoms:**
- Workflow stalled waiting for approval
- Approver unavailable or unaware
- Unclear what needs approval

**Solutions:**
1. Identify approvers early in planning phase
2. Use tier-appropriate approval workflows
3. Provide clear approval request with context
4. Escalate per framework guidelines
5. Configure backup approvers

**Example:**
```yaml
approval_request:
  urgency: high
  required_by: "2025-10-12T16:00:00Z"

  primary_approver:
    role: "Database Admin"
    name: "Jane Smith"
    contact: "jane@company.com"

  backup_approver:
    role: "Senior Database Engineer"
    name: "Bob Johnson"
    contact: "bob@company.com"
    escalation_after: "2 hours"

  context:
    problem_summary: "P1 incident: Payment processing down"
    proposed_action: "Restart database cluster"
    risk: "2-3 minute downtime during restart"
    impact_of_delay: "$10K revenue loss per hour"
```

---

#### Issue: Results Don't Meet Success Criteria

**Symptoms:**
- Metrics worse than expected
- Success criteria not achieved
- Unintended side effects

**Solutions:**
1. Document actual results honestly
2. Perform root cause analysis
3. Don't mark workflow as "success: true"
4. Create follow-up PAR workflow
5. Update approach based on learnings

**Example:**
```yaml
results:
  success: false

  outcomes:
    - metric: "API latency"
      target: "<200ms"
      actual: "650ms"
      meets_criteria: false

  root_cause_analysis:
    finding: "Index creation improved query time, but network latency is the bottleneck"
    evidence:
      - "Database query time: 45ms (good)"
      - "Network round-trip: 590ms (problem)"

  lessons_learned:
    - "Should have profiled entire request path, not just database"
    - "Network issues were masked by slow database"

  follow_up_actions:
    - problem: "Investigate network latency between API and database"
      workflow_id: "PERF-2025-002"
      assigned_to: "Tier 3 Operations Agent"
      priority: high
```

---

#### Issue: Cost Overruns

**Symptoms:**
- Actual cost exceeds estimate by >25%
- Unexpected resource usage
- Timeline extended

**Solutions:**
1. Include buffer in estimates (20-30%)
2. Monitor costs during execution
3. Pause and reassess if overrun detected
4. Document reasons for overrun
5. Improve estimation for future workflows

**Example:**
```yaml
cost_analysis:
  estimated: "$5.00"
  actual: "$8.50"
  variance: "+70%"

  breakdown:
    compute: "$2.50 (estimated: $2.00)"
    human_oversight: "$6.00 (estimated: $3.00)"

  reasons_for_overrun:
    - "Rollback required after first attempt"
    - "Additional human review needed for compliance"
    - "Database operation took 2x longer than estimated"

  prevention_measures:
    - "Add 30% buffer for database operations"
    - "Include compliance review time in estimates"
    - "Test in staging first to validate timing"
```

---

#### Issue: PROTO Workflow Complexity

**Symptoms:**
- Too many phases causing confusion
- Handoffs between phases unclear
- Review cycles taking too long

**Solutions:**
1. Break large PROTO workflows into smaller PAR workflows
2. Limit phases to 3-5 maximum
3. Define clear phase transition criteria
4. Assign phase owners explicitly
5. Use parallel workstreams where possible

**Example:**
```yaml
# Instead of one large PROTO workflow:
proto_workflow:
  problem: "Modernize entire tech stack"
  phases: [1, 2, 3, 4, 5, 6, 7, 8]  # Too many!

# Break into multiple smaller workflows:
par_workflow_1:
  problem: "Upgrade database to PostgreSQL 15"
  phases: [plan, execute, validate]

par_workflow_2:
  problem: "Migrate from REST to GraphQL API"
  phases: [design, prototype, rollout]
  depends_on: "par_workflow_1"

par_workflow_3:
  problem: "Containerize monolith application"
  phases: [design, test, deploy]
  can_run_parallel_with: "par_workflow_2"
```

---

### Escalation Paths

When workflows encounter blockers:

```yaml
escalation_matrix:
  technical_blocker:
    examples:
      - "Required infrastructure not available"
      - "Third-party dependency failing"
      - "Technical approach not viable"
    escalate_to: "Senior Engineer or Architect"
    escalation_time: "< 2 hours"

  approval_blocker:
    examples:
      - "Approver unavailable for >2 hours"
      - "Approval denied without clear feedback"
      - "Conflicting approvals from stakeholders"
    escalate_to: "Engineering Manager"
    escalation_time: "< 4 hours"

  resource_blocker:
    examples:
      - "Cost exceeds budget by >50%"
      - "Timeline exceeds estimate by >100%"
      - "Required human expertise not available"
    escalate_to: "Engineering Manager or Director"
    escalation_time: "< 8 hours"

  policy_blocker:
    examples:
      - "Action violates governance policy"
      - "Compliance concern raised"
      - "Security risk identified"
    escalate_to: "Governance Committee"
    escalation_time: "< 24 hours"
```

---

## Appendix

### Glossary

- **PAR**: Problem → Action → Results workflow model
- **PROTO**: Plan → Review → Observe → Test → Output extension for complex workflows
- **Agent Tier**: Classification of agent autonomy and authority (1-4)
- **Pre-Approval**: Human must approve before agent executes action
- **Post-Review**: Human reviews after agent completes action
- **Dual Signoff**: Two humans must approve before execution
- **Rollback Plan**: Documented steps to undo an action if it fails
- **Success Criteria**: Measurable outcomes that define successful problem resolution
- **ROI**: Return on Investment (time/cost saved vs. spent)

### Related Documents

- [Agent Tier Definitions](../frameworks/agent-tiers.yml)
- [Approval Workflows](../frameworks/approval-workflows.yml)
- [Governance Policy](GOVERNANCE-POLICY.md)
- [Cost Management](COST-MANAGEMENT.md)
- [Quick Start Guide](QUICK-START.md)

### Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-12 | Initial PAR-PROTO Integration Guide | AI Governance Framework |

### Feedback and Contributions

This framework is continuously improved based on real-world usage. Please submit:

- **Issues**: Problems or gaps in the framework
- **Enhancements**: Suggestions for improvement
- **Examples**: Real-world PAR-PROTO workflows that worked well

Submit via GitHub Issues: [https://github.com/JohnYoungSuh/ai-agent-governance-framework/issues](https://github.com/JohnYoungSuh/ai-agent-governance-framework/issues)

---

**End of PAR-PROTO Workflow Integration Guide**
