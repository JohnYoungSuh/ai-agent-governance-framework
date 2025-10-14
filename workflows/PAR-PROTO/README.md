# PAR-PROTO: Multi-Agent Development Workflow

**Version:** 1.0
**Last Updated:** 2025-10-14
**Framework:** AI Agent Governance Framework v2.0

---

## Overview

The **PAR-PROTO workflow** extends the standard PAR (Problem → Action → Results) model to support **multi-agent development patterns**, where different AI agents are strategically used at different project stages to maximize efficiency, quality, and cost-effectiveness.

### Key Concept

Rather than using a single AI agent for an entire project lifecycle, leverage **specialized agents** for specific phases:

- **Prototyping agents** (e.g., GitHub Copilot): Fast iteration, exploration, proof-of-concept
- **Production agents** (e.g., Claude): Deep analysis, comprehensive documentation, production-quality output
- **Testing agents** (e.g., Google Gemini): Test generation, security analysis, quality validation

### Workflow Patterns

This guide covers the **two-agent pattern** (Copilot → Claude). For production-critical systems requiring comprehensive testing:

👉 **See [Three-Agent Workflow](three-agent-workflow.md)** - Adds Gemini for testing & QA
👉 **See [Jira Integration](integrations/jira-integration.md)** - Issue tracking and approvals
👉 **See [Slack Integration](integrations/slack-integration.md)** - Discussion tracking

---

## PROTO Extension for Multi-Agent Workflows

**PROTO** = **PR**ototype → **O**utput (with validation gates)

```
┌────────────────────────────────────────────────────────────────┐
│ PROBLEM DEFINITION                                             │
│ ├─ Define requirements                                         │
│ ├─ Identify complexity level                                   │
│ └─ Choose agent strategy (single vs. multi-agent)             │
├────────────────────────────────────────────────────────────────┤
│ PROTOTYPE PHASE (Agent 1: Fast Iteration)                     │
│ ├─ Rapid exploration with prototyping agent                   │
│ ├─ Proof of concept development                               │
│ ├─ Architecture validation                                    │
│ └─ Quality Gate: Prototype review                             │
├────────────────────────────────────────────────────────────────┤
│ REFINEMENT PHASE (Agent 2: Production Quality)                │
│ ├─ Comprehensive documentation                                │
│ ├─ Production-ready code                                      │
│ ├─ Testing and validation                                     │
│ └─ Quality Gate: Production readiness review                  │
├────────────────────────────────────────────────────────────────┤
│ OUTPUT & RESULTS                                               │
│ ├─ Final deliverables                                         │
│ ├─ Handoff documentation                                      │
│ ├─ ROI analysis                                               │
│ └─ Lessons learned                                            │
└────────────────────────────────────────────────────────────────┘
```

---

## When to Use Multi-Agent Workflow

### Use Multi-Agent Pattern When:

✅ **Project complexity is high**
- Multiple interconnected components
- Comprehensive documentation needed
- Production-critical systems

✅ **Different skills needed at different stages**
- Fast prototyping → Detailed refinement
- Code generation → Documentation writing
- Architecture design → Implementation

✅ **Quality gates are critical**
- Clear separation between prototype and production
- Human review between phases
- Audit trail requirements

✅ **Cost optimization matters**
- Use cheaper agents for exploration
- Use expensive agents only for critical refinement
- ROI targets: Tier 2+ (5:1 or better)

### Use Single-Agent Pattern When:

❌ Simple, straightforward tasks
❌ Tight timeline with no review phase
❌ Exploratory work with no production deliverable
❌ Budget-constrained projects (Tier 1)

---

## Agent Selection Matrix

| Phase | Copilot | Claude | Gemini | Cursor |
|-------|---------|--------|--------|--------|
| **Quick code snippets** | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ |
| **Rapid prototyping** | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ |
| **Architecture design** | ❌ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Comprehensive docs** | ❌ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Production refactoring** | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Test generation** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Security analysis** | ❌ | ⭐⭐ | ⭐⭐⭐ | ❌ |
| **Large codebase review** | ❌ | ⭐⭐ | ⭐⭐⭐ | ⭐ |

**Legend:**
- ⭐⭐⭐ Best: Recommended for this use case
- ⭐⭐ Good: Suitable, acceptable alternative
- ⭐ OK/Limited: Can work but not ideal
- ❌ Not recommended: Wrong tool for the job

---

## Two-Stage Pattern: Copilot → Claude

This is the most common multi-agent pattern, used successfully in projects like **splunk-asset-identity-framework**.

### Stage 1: Prototype with Copilot

**Objective:** Rapid exploration and proof-of-concept

**Characteristics:**
- Fast inline suggestions
- Quick iteration cycles
- Low context switching
- Lower cost per iteration

**Activities:**
```yaml
stage_1_prototype:
  agent: "GitHub Copilot"
  environment: "VS Code / IDE"

  activities:
    - "Explore problem space with quick code experiments"
    - "Generate initial code structures"
    - "Test multiple approaches rapidly"
    - "Create basic working prototype"
    - "Validate core assumptions"

  deliverables:
    - "Working prototype (may be rough)"
    - "Architecture notes"
    - "Key learnings and gotchas"
    - "List of open questions"

  success_criteria:
    - "Proof of concept demonstrates feasibility"
    - "Core technical challenges identified"
    - "Architecture approach validated"

  typical_duration: "Hours to 1-2 days"
  cost_range: "$0.50 - $5.00"
```

**Quality Gate: Prototype Review**

Before moving to Stage 2, verify:
- [ ] Core functionality works
- [ ] Architecture is sound
- [ ] No major blockers identified
- [ ] Prototype demonstrates value
- [ ] Stakeholder alignment on approach

---

### Stage 2: Production with Claude

**Objective:** Transform prototype into production-quality deliverable

**Characteristics:**
- Deep contextual understanding
- Comprehensive documentation
- Production-ready code quality
- Higher cost but better quality

**Activities:**
```yaml
stage_2_production:
  agent: "Claude (Sonnet/Opus)"
  environment: "Claude Code CLI / API"

  activities:
    - "Review prototype and identify improvements"
    - "Refactor code for production standards"
    - "Write comprehensive documentation"
    - "Implement error handling and edge cases"
    - "Create testing framework"
    - "Optimize for performance and maintainability"

  deliverables:
    - "Production-ready code"
    - "Comprehensive documentation (README, guides, runbooks)"
    - "Test suites"
    - "Deployment procedures"
    - "Troubleshooting guides"

  success_criteria:
    - "Code passes all quality checks"
    - "Documentation is complete and clear"
    - "Tests achieve >80% coverage"
    - "Production deployment is documented"
    - "Handoff to operations team is smooth"

  typical_duration: "2-5 days"
  cost_range: "$10 - $100"
```

**Quality Gate: Production Readiness Review**

Before deployment, verify:
- [ ] All code follows style guides
- [ ] Documentation is comprehensive
- [ ] Testing is thorough
- [ ] Security review completed
- [ ] Performance validated
- [ ] Rollback plan documented

---

## Implementation Guide

### Step 1: Problem Definition

```yaml
problem:
  title: "Build Splunk Asset & Identity Framework"

  complexity_assessment:
    code_complexity: medium
    documentation_needs: high
    stakeholder_count: 5+
    production_critical: yes

  decision: "Use multi-agent pattern (Copilot → Claude)"

  rationale:
    - "Complex domain requiring comprehensive documentation"
    - "Production use by security analysts"
    - "High documentation quality requirement"
    - "Need both rapid exploration and polished output"
```

---

### Step 2: Prototype Phase (Agent 1)

```yaml
prototype_phase:
  agent: "GitHub Copilot"

  problem: "Build Splunk Asset & Identity Framework"

  actions:
    - action: "Explore Splunk data models"
      method: "Quick SPL queries with Copilot suggestions"
      duration: "2 hours"

    - action: "Draft basic correlation logic"
      method: "Prototype asset/identity matching"
      duration: "4 hours"

    - action: "Test with sample data"
      method: "Iterate on queries with Copilot assistance"
      duration: "3 hours"

  results:
    deliverables:
      - "Working SPL prototypes"
      - "Basic correlation logic"
      - "Notes on edge cases"

    lessons_learned:
      - "MAC address normalization is critical"
      - "DHCP logs provide best IP→hostname mapping"
      - "Multiple data sources needed for complete picture"

    handoff_to_stage_2:
      - file: "prototype_queries.spl"
      - file: "architecture_notes.md"
      - file: "open_questions.md"
```

---

### Step 3: Quality Gate Review

```yaml
quality_gate_1:
  review_type: "Prototype → Production transition"

  checklist:
    technical:
      - status: "✅ passed"
        item: "Prototype demonstrates core functionality"
      - status: "✅ passed"
        item: "Architecture approach validated"
      - status: "✅ passed"
        item: "No major technical blockers"

    business:
      - status: "✅ passed"
        item: "Stakeholders approve approach"
      - status: "✅ passed"
        item: "ROI projection is positive"

  decision: "Proceed to Stage 2"
  approver: "Tech Lead"
  timestamp: "2025-10-13T10:00:00Z"
```

---

### Step 4: Production Phase (Agent 2)

```yaml
production_phase:
  agent: "Claude Sonnet 4.5"

  inputs_from_stage_1:
    - "prototype_queries.spl"
    - "architecture_notes.md"
    - "open_questions.md"

  actions:
    - action: "Transform prototype into production framework"
      activities:
        - "Refactor SPL with proper error handling"
        - "Add comprehensive inline comments"
        - "Optimize query performance"
      duration: "1 day"

    - action: "Create comprehensive documentation"
      activities:
        - "Write technical whitepaper (1000+ lines)"
        - "Create quick-start guide"
        - "Build SOC analyst runbook"
        - "Document troubleshooting procedures"
      duration: "2 days"

    - action: "Build supporting materials"
      activities:
        - "Configuration templates (props.conf, transforms.conf)"
        - "Dashboard XML examples"
        - "Test cases and validation queries"
      duration: "1 day"

  results:
    deliverables:
      - artifact: "Complete whitepaper"
        location: "docs/whitepaper.md"
        lines: 1088

      - artifact: "Quick-start guide"
        location: "docs/quick-start.md"

      - artifact: "SOC runbook"
        location: "docs/soc-runbook.md"

      - artifact: "Production SPL examples"
        location: "spl-examples/"

      - artifact: "Configuration templates"
        location: "configs/"

    quality_metrics:
      documentation_completeness: "100%"
      code_quality_score: "A"
      test_coverage: "85%"

    cost_analysis:
      stage_1_cost: "$4.50"
      stage_2_cost: "$45.00"
      total_cost: "$49.50"
      human_time_saved: "40 hours"
      roi: "48:1"
```

---

### Step 5: Final Quality Gate

```yaml
quality_gate_2:
  review_type: "Production readiness"

  checklist:
    code_quality:
      - status: "✅ passed"
        item: "SPL follows Splunk best practices"
      - status: "✅ passed"
        item: "Error handling implemented"
      - status: "✅ passed"
        item: "Performance optimized"

    documentation:
      - status: "✅ passed"
        item: "Whitepaper is comprehensive"
      - status: "✅ passed"
        item: "Quick-start tested by new user"
      - status: "✅ passed"
        item: "Troubleshooting guide covers common issues"

    deployment:
      - status: "✅ passed"
        item: "Configuration templates provided"
      - status: "✅ passed"
        item: "Installation tested in clean environment"
      - status: "✅ passed"
        item: "Rollback procedures documented"

  decision: "Approved for production"
  approvers:
    - "Tech Lead"
    - "Security Operations Manager"
  timestamp: "2025-10-14T15:00:00Z"
```

---

## Best Practices

### DO ✅

**Stage 1 (Prototype):**
- Use Copilot for rapid iteration
- Focus on proving feasibility
- Document gotchas and learnings
- Keep prototype scope narrow
- Test core assumptions quickly

**Stage 2 (Production):**
- Use Claude for comprehensive work
- Refactor prototype code for quality
- Write extensive documentation
- Add error handling and edge cases
- Test thoroughly before deployment

**Quality Gates:**
- Always review between stages
- Get stakeholder approval to proceed
- Document decision rationale
- Archive stage artifacts

### DON'T ❌

**Stage 1 (Prototype):**
- Don't over-engineer the prototype
- Don't skip documentation of learnings
- Don't commit to architecture prematurely
- Don't optimize performance too early

**Stage 2 (Production):**
- Don't skip prototype review
- Don't rewrite from scratch (build on prototype)
- Don't rush documentation
- Don't skip testing

**Quality Gates:**
- Don't skip gate reviews
- Don't proceed with blockers unresolved
- Don't skip stakeholder alignment

---

## Cost Optimization

### Cost Comparison

**Single-Agent Approach (Claude Only):**
```
Total Cost: ~$80
- Exploration: $25 (slower iteration)
- Development: $30
- Documentation: $25
Total Time: 6 days
```

**Multi-Agent Approach (Copilot → Claude):**
```
Total Cost: ~$50
- Stage 1 (Copilot): $5 (fast iteration)
- Stage 2 (Claude): $45 (focused on quality)
Total Time: 4 days
Savings: $30 (37.5%) + 2 days faster
```

### ROI Calculation

```yaml
roi_analysis:
  investment:
    agent_costs: "$49.50"
    human_oversight: "$100 (2 hours × $50/hr)"
    total: "$149.50"

  returns:
    human_time_saved: "40 hours × $50/hr = $2,000"
    faster_delivery: "2 days earlier = $400 value"
    higher_quality: "Fewer future bugs = $500 value"
    total: "$2,900"

  roi_ratio: "19.4:1"
  payback_period: "Immediate (first use)"
```

---

## Troubleshooting

### Issue: Prototype is too rough for Stage 2

**Symptoms:**
- Claude struggles to understand prototype
- Too many gaps in logic
- Architecture unclear

**Solutions:**
1. Improve Stage 1 documentation
2. Add architecture diagrams
3. Document design decisions
4. Run additional prototype review

---

### Issue: Stage 2 diverges from prototype

**Symptoms:**
- Claude suggests completely different approach
- Prototype learnings ignored
- Rework required

**Solutions:**
1. Better handoff documentation from Stage 1
2. Explicit instructions to build on prototype
3. Include prototype rationale in Stage 2 prompt
4. Human review at quality gate caught this

---

### Issue: Cost overruns in Stage 2

**Symptoms:**
- Claude iterations exceed budget
- Scope creep during refinement
- Documentation becomes too detailed

**Solutions:**
1. Set clear scope for Stage 2
2. Define documentation requirements upfront
3. Use token budgets and monitoring
4. Break into smaller chunks if needed

---

## Success Metrics

Track these metrics to validate multi-agent effectiveness:

```yaml
success_metrics:
  velocity:
    target: "2x faster than single-agent"
    measurement: "Time from start to production"

  quality:
    target: "≥90% stakeholder satisfaction"
    measurement: "Post-project survey"

  cost_efficiency:
    target: "ROI ≥ 10:1"
    measurement: "Cost vs. human time saved"

  documentation:
    target: "100% completeness"
    measurement: "Documentation checklist"

  defect_rate:
    target: "<5% issues post-deployment"
    measurement: "Bug tracking system"
```

---

## Templates

See the following templates for implementing PAR-PROTO workflows:

- [Multi-Agent Project Plan Template](templates/multi-agent-project-plan.yml)
- [Quality Gate Checklist](templates/quality-gate-checklist.md)
- [Stage Handoff Template](templates/stage-handoff-template.md)
- [ROI Analysis Template](templates/roi-analysis.yml)

---

## Real-World Example

**Case Study: Splunk Asset & Identity Framework**

- **Project**: Build production framework for Splunk asset/identity resolution
- **Pattern**: Copilot (prototype) → Claude (production)
- **Results**:
  - ✅ 1088-line comprehensive whitepaper
  - ✅ Production-ready SPL examples
  - ✅ Complete configuration templates
  - ✅ 48:1 ROI
  - ✅ Deployed in 4 days

See: `/home/suhlabs/projects/splunk-asset-identity-framework`

---

## Related Documentation

- [PAR Workflow Framework](../../docs/PAR-WORKFLOW-FRAMEWORK.md)
- [Agent Tier Definitions](../../frameworks/agent-tiers.yml)
- [Cost Management Guide](../../docs/COST-MANAGEMENT.md)
- [Quality Gates](../../templates/governance-review/)

---

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-14 | Initial PAR-PROTO multi-agent workflow guide | AI Governance Framework |

---

**This workflow pattern is validated by real-world usage in the splunk-asset-identity-framework project.**
