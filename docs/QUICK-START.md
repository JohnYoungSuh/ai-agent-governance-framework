# Quick Start Guide

Get started with the AI Agent Governance Framework in 15 minutes.

## Prerequisites
- Git installed
- Access to AI/LLM API (Claude, GPT, etc.)
- Basic understanding of your use case

## Step 1: Choose Your Agent Tier

| Tier | Best For |
|------|----------|
| 1 - Observer | Documentation, analysis, reporting |
| 2 - Developer | Coding, testing, refactoring |
| 3 - Operations | Deployments, monitoring, runbooks |
| 4 - Architect | System design, research, strategy |

## Step 2: Deploy Your First Agent

```bash
# Using the setup script
./scripts/setup-agent.sh --tier 1 --name "my-agent"

# Manual setup
mkdir -p agents/my-agent
cp templates/agent-deployment/config-template.yml agents/my-agent/config.yml
# Edit config.yml with your settings
```

## Step 3: Run a PAR Cycle

### Problem Phase
```yaml
# problem.yml
context: "We need to analyze Q3 sales reports"
issue: "Reports are in different formats across regions"
impact: "Leadership needs consolidated view by Friday"
constraints:
  - Must preserve data privacy
  - Only use approved data sources
success_criteria:
  - Single consolidated report
  - All regions included
  - Delivered by EOW
```

### Action Phase
Submit problem to agent, review proposed approach, approve execution.

### Results Phase
Agent delivers results, you validate against success criteria.

## Step 4: Track Costs

```bash
# After task completion
./scripts/cost-report.sh --agent my-agent --task TASK-001
```

## Next Steps
- Review [PAR Workflow Framework](PAR-WORKFLOW-FRAMEWORK.md)
- Explore [example agents](../examples/)
- Set up [cost tracking](COST-MANAGEMENT.md)
- Configure [governance policies](GOVERNANCE-POLICY.md)

## Common Patterns

### Pattern: Code Review Agent (Tier 2)
```bash
./scripts/setup-agent.sh --tier 2 --name "code-reviewer"
# Configure to review PRs, suggest improvements
```

### Pattern: Deployment Agent (Tier 3)
```bash
./scripts/setup-agent.sh --tier 3 --name "deployer"
# Configure with production access, runbooks
```

### Pattern: Architecture Advisor (Tier 4)
```bash
./scripts/setup-agent.sh --tier 4 --name "architect"
# Configure for research, design proposals
```

## Troubleshooting

**Issue**: Agent costs too high  
**Solution**: Check token usage, optimize prompts, consider lower tier

**Issue**: Too many approval requests  
**Solution**: Review decision matrix, adjust tier permissions

**Issue**: Low ROI  
**Solution**: Ensure agent is assigned appropriate tasks for tier

## Support
- Issues: GitHub Issues
- Questions: GitHub Discussions
- Examples: See `/examples` directory
