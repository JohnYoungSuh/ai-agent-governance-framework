# Stage Handoff Template

**Version:** 1.0
**Purpose:** Transfer context from Prototype to Production phase

---

## Project Information

**Project Name:** [Project Name]
**Stage 1 Agent:** [e.g., GitHub Copilot]
**Stage 2 Agent:** [e.g., Claude Sonnet 4.5]
**Handoff Date:** YYYY-MM-DD
**Stage 1 Duration:** [X days/hours]
**Stage 1 Cost:** $X.XX

---

## Executive Summary

**Problem Statement:**
[Brief description of what we're trying to solve]

**Prototype Outcome:**
[Summary of what was achieved in Stage 1]

**Key Decision:**
[ ] Proceed to Production Phase
[ ] Revise Prototype
[ ] Cancel Project

---

## Stage 1 Deliverables

### Code/Artifacts

| Artifact | Location | Description | Status |
|----------|----------|-------------|--------|
| [Name] | [Path/URL] | [Brief description] | [Complete/Partial] |

### Documentation

- **Architecture Notes:** [path/to/architecture.md]
- **Design Decisions:** [path/to/decisions.md]
- **Lessons Learned:** [path/to/lessons.md]
- **Open Questions:** [path/to/questions.md]

---

## What Worked Well

### Successful Approaches

1. **[Approach Name]**
   - Description: [What was done]
   - Why it worked: [Explanation]
   - Recommendation: **Preserve in Stage 2**

2. **[Another Approach]**
   - Description: [What was done]
   - Why it worked: [Explanation]
   - Recommendation: **Preserve in Stage 2**

### Key Learnings

```yaml
learning_1:
  finding: "Description of what we learned"
  evidence: "How we discovered this"
  impact: "Why this matters for Stage 2"
  action: "What to do differently"
```

---

## What Needs Improvement

### Areas Requiring Refactoring

1. **[Component/Module Name]**
   - Current state: [Description]
   - Issues: [What's wrong]
   - Priority: [High/Medium/Low]
   - Suggested approach: [How to improve]

### Technical Debt

| Debt Item | Severity | Effort to Fix | Priority |
|-----------|----------|---------------|----------|
| [Description] | [High/Med/Low] | [Hours] | [1-5] |

### Edge Cases to Address

- [ ] **[Edge Case 1]**
  - Scenario: [Description]
  - Current behavior: [What happens now]
  - Expected behavior: [What should happen]

- [ ] **[Edge Case 2]**
  - Scenario: [Description]
  - Current behavior: [What happens now]
  - Expected behavior: [What should happen]

---

## Architecture Decisions

### Confirmed Decisions

| Decision | Rationale | Alternatives Considered | Status |
|----------|-----------|------------------------|--------|
| [Architecture choice] | [Why chosen] | [Other options] | ✅ Confirmed |

### Open Decisions

| Decision Needed | Options | Recommendation | Owner |
|-----------------|---------|----------------|-------|
| [What needs deciding] | [Possible choices] | [Suggested approach] | [Who should decide] |

---

## Technical Context

### Technology Stack

```yaml
languages: [Python, JavaScript, etc.]
frameworks: [React, Django, etc.]
databases: [PostgreSQL, MongoDB, etc.]
services: [AWS S3, Splunk, etc.]
tools: [Docker, Kubernetes, etc.]
```

### Dependencies

```yaml
critical_dependencies:
  - name: "Dependency name"
    version: "X.Y.Z"
    purpose: "What it's used for"
    issues: "Any known issues"

optional_dependencies:
  - name: "Dependency name"
    version: "X.Y.Z"
    purpose: "What it's used for"
```

### Environment Setup

```bash
# Commands to set up development environment
git clone [repo]
npm install
# etc.
```

---

## Stage 2 Requirements

### Must-Have (P0)

- [ ] **[Requirement 1]**
  - Description: [What needs to be done]
  - Acceptance criteria: [How to verify]
  - Estimated effort: [Hours/Days]

- [ ] **[Requirement 2]**
  - Description: [What needs to be done]
  - Acceptance criteria: [How to verify]
  - Estimated effort: [Hours/Days]

### Should-Have (P1)

- [ ] **[Requirement]**
  - Description: [What needs to be done]
  - Acceptance criteria: [How to verify]

### Nice-to-Have (P2)

- [ ] **[Requirement]**
  - Description: [What needs to be done]

---

## Documentation Requirements

### Required Documentation

- [ ] **README.md**
  - Installation instructions
  - Quick start guide
  - Basic usage examples

- [ ] **Technical Whitepaper/Guide**
  - Comprehensive documentation
  - Architecture explanation
  - Best practices

- [ ] **Operational Runbook**
  - Deployment procedures
  - Troubleshooting guide
  - Common operations

- [ ] **Configuration Guide**
  - All configuration options
  - Environment-specific configs
  - Secrets management

### Documentation Standards

```yaml
style:
  format: "Markdown"
  tone: "Professional but accessible"
  audience: "[Primary audience]"

structure:
  - "Executive summary"
  - "Quick start (5-15 minutes)"
  - "Comprehensive guide"
  - "Reference material"
  - "Troubleshooting"
```

---

## Testing Requirements

### Test Coverage Targets

- **Unit Tests:** >80% coverage
- **Integration Tests:** All critical paths
- **End-to-End Tests:** Happy path + key error scenarios

### Test Scenarios

```yaml
scenario_1:
  name: "Primary user workflow"
  steps:
    - "Step 1"
    - "Step 2"
  expected_outcome: "Description"
  priority: "High"

scenario_2:
  name: "Error handling"
  steps:
    - "Step 1"
  expected_outcome: "Description"
  priority: "Medium"
```

---

## Quality Standards

### Code Quality

- **Style Guide:** [Link to style guide]
- **Linting:** [Tool and rules]
- **Code Review:** Required before merge
- **Documentation:** Inline comments for complex logic

### Performance Standards

- **Response Time:** < [X]ms for [operation]
- **Throughput:** > [Y] requests/second
- **Resource Usage:** < [Z]MB memory

### Security Standards

- [ ] Input validation implemented
- [ ] Authentication/authorization correct
- [ ] Secrets never hardcoded
- [ ] Dependencies scanned for vulnerabilities

---

## Known Issues and Gotchas

### Bugs/Limitations

1. **[Issue Description]**
   - Impact: [Who/what is affected]
   - Workaround: [Temporary solution]
   - Fix required: [Yes/No/Maybe]

### Gotchas

```yaml
gotcha_1:
  situation: "When this happens..."
  problem: "This unexpected thing occurs"
  solution: "Do this instead"
  why: "Explanation of root cause"
```

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | [High/Med/Low] | [High/Med/Low] | [How to mitigate] |

### Timeline Risks

| Risk | Impact on Schedule | Mitigation |
|------|-------------------|------------|
| [Risk description] | [Days delayed] | [How to mitigate] |

---

## Resource Requirements

### Estimated Effort

```yaml
stage_2_estimate:
  development: "[X days]"
  documentation: "[Y days]"
  testing: "[Z days]"
  total: "[Total days]"
```

### Budget

```yaml
estimated_costs:
  agent_costs: "$XX.XX"
  human_oversight: "$YY.YY (Z hours)"
  infrastructure: "$ZZ.ZZ"
  total: "$TTT.TT"
```

### Human Resources Needed

- [ ] Technical review: [X hours]
- [ ] Security review: [Y hours]
- [ ] Stakeholder demos: [Z hours]

---

## Success Criteria

### Stage 2 Success Metrics

- [ ] **Functional Requirements Met**
  - All P0 requirements implemented
  - All P1 requirements implemented (or explicitly deferred)

- [ ] **Quality Standards Met**
  - Code quality: A grade
  - Test coverage: >80%
  - Documentation: 100% complete

- [ ] **Performance Standards Met**
  - Response time < [X]ms
  - No memory leaks
  - Scalable to [Y] users/requests

- [ ] **Stakeholder Approval**
  - Product owner satisfied
  - Technical team approves
  - End users can successfully use it

---

## Communication Plan

### Stakeholders

| Stakeholder | Role | Update Frequency | Contact |
|-------------|------|-----------------|---------|
| [Name] | [Role] | [Weekly/etc] | [Email] |

### Status Updates

- **When:** [Daily/Weekly]
- **Format:** [Email/Slack/Meeting]
- **Content:** Progress, blockers, next steps

---

## Approval

**Stage 1 Complete - Approved for Stage 2**

- Stage 1 Agent Summary: _________________________
- Stage 1 Human Review: _________________________ Date: __________
- Quality Gate Passed: [ ] Yes [ ] No (with exceptions)

**Stage 2 Kick-off**

- Stage 2 Agent: _________________________
- Stage 2 Owner: _________________________ Date: __________
- Expected Completion: __________

---

## Appendix

### File Locations

```
project-root/
├── prototype/
│   ├── code/
│   ├── notes/
│   └── artifacts/
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   └── lessons-learned.md
└── handoff/
    └── [this-file].md
```

### Additional Resources

- [Link to relevant documentation]
- [Link to reference implementations]
- [Link to similar projects]

---

**Template Version:** 1.0
**Last Updated:** 2025-10-14
