# Three-Agent Workflow: Copilot → Claude → Gemini

**Version:** 1.0
**Last Updated:** 2025-10-14
**Pattern:** Prototype → Production → Testing

---

## Overview

The **three-agent workflow** extends the two-stage pattern by adding a dedicated testing and quality assurance phase using Google Gemini. This creates a comprehensive development pipeline with specialized agents at each critical stage.

```
┌──────────────────────────────────────────────────────────────┐
│ STAGE 1: PROTOTYPE (Copilot)                                │
│ Fast iteration, proof of concept, rapid exploration         │
├──────────────────────────────────────────────────────────────┤
│ Quality Gate 1: Prototype Review                            │
├──────────────────────────────────────────────────────────────┤
│ STAGE 2: PRODUCTION (Claude)                                │
│ Comprehensive docs, production code, architecture            │
├──────────────────────────────────────────────────────────────┤
│ Quality Gate 2: Pre-Testing Review                          │
├──────────────────────────────────────────────────────────────┤
│ STAGE 3: TESTING & VALIDATION (Gemini)                      │
│ Test generation, security analysis, quality validation      │
├──────────────────────────────────────────────────────────────┤
│ Quality Gate 3: Production Readiness                        │
├──────────────────────────────────────────────────────────────┤
│ DEPLOYMENT                                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Why Add Gemini as Testing Agent?

### Gemini's Strengths for Testing

1. **Multi-Modal Analysis**: Analyze code, docs, and visual outputs together
2. **Large Context Window**: Review entire codebases (up to 2M tokens)
3. **Code Understanding**: Strong at understanding code logic and edge cases
4. **Cost-Effective**: Lower cost for test generation workloads
5. **Integration Capabilities**: Works well with Google Cloud tools

### Testing Use Cases

| Use Case | Why Gemini | Alternative |
|----------|------------|-------------|
| **Test Generation** | Excellent at generating comprehensive test suites | Claude (more expensive) |
| **Security Analysis** | Strong pattern recognition for vulnerabilities | GPT-4 + security tools |
| **Code Review** | Large context for whole-project analysis | Claude (similar) |
| **Documentation Validation** | Multi-modal: verify docs match code | Manual review |
| **Performance Testing** | Generate load test scenarios | Manual creation |
| **Edge Case Discovery** | Good at "what if" scenario generation | Human QA team |

---

## Three-Agent Workflow Pattern

### Stage 1: Prototype with Copilot

**Duration:** 1-2 days | **Cost:** $5-10

```yaml
stage_1_prototype:
  agent: "GitHub Copilot"

  activities:
    - "Rapid code exploration"
    - "Multiple approach testing"
    - "Basic functionality proof"
    - "Architecture validation"

  deliverables:
    - "Working prototype"
    - "Architecture notes"
    - "Lessons learned"

  handoff_to_stage_2:
    - "prototype_code/"
    - "architecture.md"
    - "open_questions.md"
```

---

### Stage 2: Production with Claude

**Duration:** 2-5 days | **Cost:** $40-100

```yaml
stage_2_production:
  agent: "Claude Sonnet 4.5"

  activities:
    - "Refactor to production quality"
    - "Comprehensive documentation"
    - "Error handling & edge cases"
    - "Configuration management"

  deliverables:
    - "Production-ready code"
    - "Technical whitepaper"
    - "API documentation"
    - "Deployment guides"

  handoff_to_stage_3:
    - "production_code/"
    - "docs/"
    - "configs/"
    - "test_requirements.md"
```

---

### Stage 3: Testing & Validation with Gemini

**Duration:** 1-3 days | **Cost:** $10-30

```yaml
stage_3_testing:
  agent: "Google Gemini 1.5 Pro"

  activities:
    - "Generate comprehensive test suites"
    - "Security vulnerability analysis"
    - "Performance test scenarios"
    - "Documentation-code consistency check"
    - "Edge case identification"
    - "Load test planning"

  deliverables:
    - "Unit test suite (target: 90% coverage)"
    - "Integration tests"
    - "Security audit report"
    - "Performance test plan"
    - "Edge case test scenarios"
    - "QA validation report"

  quality_validations:
    - "All tests pass"
    - "Security vulnerabilities addressed"
    - "Performance meets SLAs"
    - "Documentation accurate"
```

---

## Detailed Stage 3: Gemini Testing Workflow

### 3.1 Test Generation

**Objective:** Comprehensive automated testing

```yaml
test_generation:
  inputs:
    - production_code/
    - test_requirements.md
    - api_documentation.md

  gemini_tasks:
    unit_tests:
      - "Analyze each function/class"
      - "Generate test cases for happy paths"
      - "Generate test cases for error conditions"
      - "Generate edge case tests"
      - "Mock external dependencies"
      target_coverage: ">90%"

    integration_tests:
      - "Test component interactions"
      - "Test API endpoints"
      - "Test database operations"
      - "Test authentication/authorization"
      scenarios: "All critical user workflows"

    end_to_end_tests:
      - "User registration flow"
      - "Main user workflows"
      - "Error recovery scenarios"
      - "Performance under load"

  output:
    location: "tests/"
    structure:
      - "tests/unit/"
      - "tests/integration/"
      - "tests/e2e/"
      - "tests/performance/"
```

### 3.2 Security Analysis

**Objective:** Identify and validate security vulnerabilities

```yaml
security_analysis:
  gemini_tasks:
    vulnerability_scan:
      - "OWASP Top 10 checks"
      - "SQL injection vectors"
      - "XSS vulnerabilities"
      - "Authentication bypass attempts"
      - "Authorization flaws"
      - "Sensitive data exposure"

    code_analysis:
      - "Hardcoded secrets detection"
      - "Unsafe deserialization"
      - "Path traversal vulnerabilities"
      - "CSRF token validation"
      - "Rate limiting checks"

    dependency_analysis:
      - "Known CVEs in dependencies"
      - "Outdated package versions"
      - "License compliance"

  output:
    - "security_audit_report.md"
    - "vulnerability_findings.csv"
    - "remediation_priorities.md"
```

### 3.3 Performance Testing

**Objective:** Validate performance and scalability

```yaml
performance_testing:
  gemini_tasks:
    load_test_scenarios:
      - "Define baseline load (normal usage)"
      - "Define peak load scenarios"
      - "Define stress test scenarios"
      - "Generate load test scripts"

    performance_analysis:
      - "Identify slow queries"
      - "Analyze algorithm complexity"
      - "Check for N+1 query problems"
      - "Review caching strategy"
      - "Memory leak detection patterns"

    scalability_assessment:
      - "Horizontal scaling readiness"
      - "Database connection pooling"
      - "Rate limiting effectiveness"
      - "Resource bottleneck identification"

  output:
    - "performance_test_plan.md"
    - "load_test_scripts/"
    - "performance_baseline.json"
    - "optimization_recommendations.md"
```

### 3.4 Documentation Validation

**Objective:** Ensure documentation matches implementation

```yaml
documentation_validation:
  gemini_tasks:
    accuracy_check:
      - "Compare API docs with actual implementation"
      - "Verify configuration options documented"
      - "Check example code runs correctly"
      - "Validate setup instructions"

    completeness_check:
      - "All public APIs documented"
      - "Error codes documented"
      - "Configuration options documented"
      - "Troubleshooting guide covers common issues"

    quality_check:
      - "Code examples are runnable"
      - "Screenshots are current"
      - "Links are valid"
      - "Tone is consistent"

  output:
    - "documentation_audit.md"
    - "documentation_fixes_needed.md"
```

---

## Quality Gates

### Quality Gate 1: Prototype → Production

See [two-agent workflow](README.md#quality-gate-1-prototype--production-transition) for details.

---

### Quality Gate 2: Production → Testing (NEW)

**Review Date:** YYYY-MM-DD
**Reviewer:** [Tech Lead]

#### Pre-Testing Checklist

- [ ] **Code Complete**
  - All features implemented
  - Error handling in place
  - Configuration externalized

- [ ] **Documentation Complete**
  - README finished
  - API docs written
  - Deployment guide ready

- [ ] **Test Requirements Defined**
  - Test scenarios documented
  - Coverage targets set
  - Performance SLAs defined

- [ ] **Staging Environment Ready**
  - Deployment successful
  - Configuration correct
  - Monitoring enabled

#### Approval to Proceed

- Approved by: _________________________ Date: __________
- Stage 3 Agent: Gemini 1.5 Pro
- Expected Duration: 1-3 days
- Budget Allocated: $10-30

---

### Quality Gate 3: Testing → Production (NEW)

**Review Date:** YYYY-MM-DD
**Reviewer:** [QA Lead + Tech Lead]

#### Testing Completeness

- [ ] **Test Coverage Met**
  - Unit tests: ≥90% coverage
  - Integration tests: All critical paths covered
  - E2E tests: Main workflows validated

- [ ] **All Tests Passing**
  - CI/CD pipeline green
  - No flaky tests
  - Performance tests pass

- [ ] **Security Validated**
  - No critical vulnerabilities
  - High severity issues resolved
  - Medium issues documented/accepted

- [ ] **Performance Validated**
  - Response times meet SLAs
  - Load tests passed
  - No memory leaks detected

- [ ] **Documentation Validated**
  - Docs match implementation
  - Examples tested and working
  - Troubleshooting guide complete

#### Approval for Production

- QA Lead: _________________________ Date: __________
- Tech Lead: _________________________ Date: __________
- Security (if required): _________________________ Date: __________

---

## Cost Analysis: Two-Agent vs. Three-Agent

### Two-Agent Pattern (Copilot → Claude)

```
Stage 1 (Copilot): $5
Stage 2 (Claude): $45
Total: $50
Duration: 4 days
```

### Three-Agent Pattern (Copilot → Claude → Gemini)

```
Stage 1 (Copilot): $5
Stage 2 (Claude): $45
Stage 3 (Gemini): $20
Total: $70 (+40% cost)
Duration: 6 days (+2 days)

Benefits:
- Automated test generation (saves 3-5 days manual QA)
- Security analysis (prevents costly incidents)
- Performance validation (prevents post-launch issues)

ROI: Still >15:1 (higher quality, lower risk)
```

### When to Use Three-Agent Pattern

**Use three-agent when:**
- ✅ Production-critical systems (Tier 3+)
- ✅ Security is paramount
- ✅ Complex testing requirements
- ✅ Large codebase needs comprehensive coverage
- ✅ Performance SLAs are strict
- ✅ Regulatory compliance requires audit trail

**Use two-agent when:**
- ⚠️ Simple applications (Tier 1-2)
- ⚠️ Internal tools with limited users
- ⚠️ Prototypes or MVPs
- ⚠️ Time-constrained projects
- ⚠️ Manual QA team already in place

---

## Integration with Jira & Slack

See dedicated integration guides:
- [Jira Integration](integrations/jira-integration.md)
- [Slack Integration](integrations/slack-integration.md)

**Quick Summary:**

### Jira Integration
- Issue tracking for each stage
- Quality gate approvals via Jira workflows
- Change control documentation
- Audit trail maintenance

### Slack Integration
- Stage transition notifications
- Quality gate discussions
- Decision rationale tracking
- Stakeholder communication

---

## Example: Three-Agent Project Flow

### Real-World Scenario: E-Commerce Checkout System

**Project:** Secure payment processing module

```yaml
stage_1_copilot:
  duration: "1.5 days"
  cost: "$8"
  deliverables:
    - "Payment API prototype"
    - "Stripe integration POC"
    - "Basic error handling"
  jira_ticket: "PROJ-123"
  slack_channel: "#project-checkout"

quality_gate_1:
  date: "2025-10-15"
  approver: "Tech Lead"
  decision: "Approved with recommendations"
  jira_status: "In Production Development"

stage_2_claude:
  duration: "3 days"
  cost: "$55"
  deliverables:
    - "Production payment module"
    - "API documentation"
    - "Security guidelines"
    - "PCI compliance docs"
  jira_ticket: "PROJ-123"
  slack_thread: "Discussing encryption approach"

quality_gate_2:
  date: "2025-10-18"
  approver: "Tech Lead"
  decision: "Approved for testing"
  jira_status: "In QA"

stage_3_gemini:
  duration: "2 days"
  cost: "$25"
  deliverables:
    - "Security test suite (OWASP)"
    - "Payment flow integration tests"
    - "PCI compliance validation"
    - "Performance load tests"
    - "Security audit report"
  jira_ticket: "PROJ-123"
  slack_thread: "Security findings discussion"

  findings:
    critical: 0
    high: 2 (resolved)
    medium: 5 (3 resolved, 2 accepted)

quality_gate_3:
  date: "2025-10-20"
  approvers:
    - "QA Lead: Approved"
    - "Security Team: Approved"
    - "Tech Lead: Approved"
  decision: "Approved for production"
  jira_status: "Ready for Deployment"

deployment:
  date: "2025-10-21"
  result: "Successful"

results:
  total_cost: "$88"
  total_duration: "6.5 days"
  tests_generated: "127 tests"
  test_coverage: "94%"
  security_issues_found: "7 (all resolved or accepted)"
  performance: "Meets all SLAs"
  roi: "22:1 (saved 40 hours QA + prevented security incident)"
```

---

## Agent Selection Reference

### Quick Decision Matrix

| Task | Copilot | Claude | Gemini |
|------|---------|--------|--------|
| Rapid prototyping | ⭐⭐⭐ | ⭐ | ⭐ |
| Production code | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| Comprehensive docs | ❌ | ⭐⭐⭐ | ⭐⭐ |
| Test generation | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| Security analysis | ❌ | ⭐⭐ | ⭐⭐⭐ |
| Code review | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Performance analysis | ❌ | ⭐⭐ | ⭐⭐⭐ |
| Large codebase analysis | ❌ | ⭐⭐ | ⭐⭐⭐ |

**Legend:** ⭐⭐⭐ Best | ⭐⭐ Good | ⭐ Acceptable | ❌ Not suitable

---

## Best Practices

### DO ✅

**Stage 1 (Copilot):**
- Focus on speed over perfection
- Test multiple approaches
- Document learnings immediately

**Stage 2 (Claude):**
- Build on prototype (don't rewrite)
- Write comprehensive documentation
- Add production-grade error handling

**Stage 3 (Gemini):**
- Provide complete codebase context
- Be specific about test requirements
- Review generated tests before running
- Prioritize security findings

**Quality Gates:**
- Don't skip gates to save time
- Document all decisions in Jira
- Discuss concerns in Slack before approving

### DON'T ❌

**Stage 1:**
- Don't optimize prematurely
- Don't skip architecture documentation

**Stage 2:**
- Don't rush documentation
- Don't skip edge case handling

**Stage 3:**
- Don't blindly trust generated tests
- Don't skip manual security review
- Don't ignore performance findings

---

## Templates

See `/workflows/PAR-PROTO/templates/` for:
- `three-agent-project-plan.yml` - Complete planning template
- `gemini-testing-checklist.md` - Stage 3 testing checklist
- `quality-gate-3-template.md` - Final production readiness review

---

## Related Documentation

- [Two-Agent Workflow](README.md) - Copilot → Claude pattern
- [Jira Integration Guide](integrations/jira-integration.md)
- [Slack Integration Guide](integrations/slack-integration.md)
- [Agent Selection Guide](agent-selection-guide.md)

---

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-14 | Initial three-agent workflow with Gemini testing | AI Governance Framework |

---

**Validated Pattern:** This three-agent pattern provides comprehensive quality assurance while maintaining cost-effectiveness for production systems.
