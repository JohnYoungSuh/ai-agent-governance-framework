# Enforced Project Creation Workflow

## Overview
This document describes the **enforced, AI-driven project creation system** that embeds governance, accountability, and compliance from Day 1. No project can be created without proper governance metadata and controls.

## Philosophy
**AI-driven labor with human accountability and responsibility**

Every project created through this system:
- Has a designated human owner
- Operates within a defined agent tier with specific controls
- Has budget limits and cost tracking
- Requires compliance declarations
- Includes automatic audit trails
- Enforces appropriate approvals for production systems

## Enforced Project Creation

### Command
```bash
~/projects/ai-agent-governance-framework/scripts/create-governed-project.sh
```

### What Gets Enforced

#### 1. Required Metadata (Cannot Skip)
- **Project Name** - Must be valid directory name
- **Project Description** - Purpose and scope
- **Tech Stack** - Languages and frameworks
- **Infrastructure** - Deployment environment
- **Owner Name** - Human accountable for all agent actions
- **Owner Email** - Must be valid email format
- **Agent Tier (1-4)** - Determines controls and approvals
- **Compliance Requirements** - Regulatory framework(s)
- **Budget Limit** - Monthly cost cap in dollars

#### 2. Tier-Based Governance (Automatic)

**Tier 1 (Observer)**
- Read-only access enforced
- Required mitigations: MI-001, MI-009
- Cost target: $0.10-$0.50/task
- No special approvals needed

**Tier 2 (Developer)**
- Development environment only
- Required mitigations: MI-001, MI-009, MI-021
- Cost target: $0.50-$5.00/task
- No production access

**Tier 3 (Operations)**
- Production access (with approval)
- Required mitigations: MI-001, MI-003, MI-009, MI-021
- Cost target: $1.00-$10.00/task
- **REQUIRED**: Jira CR approval
- **REQUIRED**: Threat modeling (STRIDE-based)

**Tier 4 (Architect)**
- Design and research authority
- Required mitigations: MI-001, MI-003, MI-009, MI-021
- Cost target: $5.00-$50.00/task
- **REQUIRED**: Jira CR approval
- **REQUIRED**: Threat modeling (STRIDE-based)

#### 3. Automatic File Structure

Every project includes:

```
project-name/
├── .claude/
│   ├── prompts/
│   │   └── project-context.md    # Auto-loaded governance context
│   ├── commands/                  # Custom slash commands
│   └── settings.local.json        # Governance metadata + permissions
├── src/                           # Application code
├── tests/                         # Test files
├── docs/                          # Documentation
├── scripts/                       # Automation scripts
├── config/                        # Configuration
├── GOVERNANCE.md                  # Governance summary
├── README.md                      # Project readme with governance
└── .gitignore                     # Standard ignore rules
```

#### 4. Mandatory Governance Files

**`.claude/prompts/project-context.md`**
- Project metadata
- Owner information
- Agent tier requirements and restrictions
- Required mitigations
- Budget and cost controls
- Compliance requirements
- Audit and accountability rules
- Auto-loaded when project opens in Claude Code

**`.claude/settings.local.json`**
- Tier-appropriate permissions
- Governance metadata (project name, owner, tier, budget, etc.)
- Framework version tracking
- Machine-readable for automation

**`GOVERNANCE.md`**
- Human accountability declaration
- Required controls for the tier
- Compliance framework
- Audit trail information
- Links to governance framework

**`README.md`**
- Project description
- Governance summary
- Owner information
- Quick start guide

#### 5. Git Initialization with Governance Commit

Every project starts with a governance-tagged initial commit:
```
Initial commit: Governed project creation

Project: project-name
Owner: John Doe <john@example.com>
Agent Tier: 3
Compliance: SOC2
Budget: $500/month
Created: 2025-10-23T12:34:56Z

🤖 Created with AI Agent Governance Framework v2.1
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Validation Rules

### Email Validation
- Must match standard email regex
- Cannot proceed with invalid email

### Agent Tier Validation
- Must be 1, 2, 3, or 4
- Cannot skip or use invalid values

### Required Fields
- All fields are mandatory
- Empty values cause script to exit with error

### Tier 3/4 Additional Requirements
- Jira CR ID is mandatory
- Script reminds user about threat modeling requirement
- Production deployment blocked until threat model complete

## Usage Example

```bash
$ ~/projects/ai-agent-governance-framework/scripts/create-governed-project.sh

╔════════════════════════════════════════════════════════════╗
║  AI-Driven Governed Project Creation System               ║
║  Enforcing accountability & responsible AI from Day 1      ║
╚════════════════════════════════════════════════════════════╝

Step 1: Project Metadata (Required)
─────────────────────────────────────
Project Name (lowercase-with-dashes): customer-support-bot
Project Description: AI agent for customer support ticket triage
Tech Stack (e.g., Python/FastAPI, Node/Express): Python/FastAPI
Infrastructure (e.g., AWS Lambda, Kubernetes, Docker): AWS Lambda

Step 2: Governance & Accountability (Required)
─────────────────────────────────────
Project Owner (name): Jane Smith
Project Owner Email: jane.smith@example.com
AI Agent Tier (1-4): 3
Compliance Requirements (e.g., SOC2, HIPAA, FedRAMP, None): SOC2
Budget Limit ($/month, e.g., 100): 500

Step 3: Risk Assessment (Required for Tier 3+)
─────────────────────────────────────
⚠ Tier 3 requires threat modeling and Jira CR approval
Jira CR ID (for production deployment): CR-2025-1234

Creating governed project structure...

╔════════════════════════════════════════════════════════════╗
║  ✅ Governed Project Created Successfully!                 ║
╚════════════════════════════════════════════════════════════╝

Project Path: /home/user/projects/customer-support-bot
Owner: Jane Smith <jane.smith@example.com>
Agent Tier: 3
Budget: $500/month
Compliance: SOC2

⚠ REQUIRED NEXT STEPS (Tier 3):
1. Run threat model: ~/projects/ai-agent-governance-framework/workflows/threat-modeling/scripts/run-threat-model.sh
2. Implement required mitigations
3. Validate Jira CR approval: CR-2025-1234

Next Steps:
1. cd /home/user/projects/customer-support-bot
2. Customize project-context.md with your specific details
3. Add your source code to src/
4. Open in Claude Code - governance context loads automatically!
```

## Integration with AI Agents

### When AI Agent Creates a Project

The AI agent would:
1. Prompt user for required metadata
2. Validate all inputs (email format, tier range, etc.)
3. Create project structure with governance files
4. Initialize git with governance commit
5. Notify user of tier-specific requirements
6. Refuse to proceed without all required information

### Prompt Example for AI Agent

```
User: "Create a new customer support bot project"

AI Agent: "I'll help you create a governed project with proper accountability.

Required information:
1. What's the project name (lowercase-with-dashes)?
2. Brief description of the project?
3. What's your tech stack (language/framework)?
4. Infrastructure (AWS Lambda, Kubernetes, etc.)?
5. Who is the project owner (name and email)?
6. What agent tier (1=Observer, 2=Developer, 3=Operations, 4=Architect)?
7. Compliance requirements (SOC2, HIPAA, etc.)?
8. Monthly budget limit?
9. (If Tier 3+) Jira CR ID for production approval?

This ensures human accountability and proper governance from Day 1."
```

## Why This Matters

### For Your AI-Driven Company
- **Every project has a human owner** - No "orphaned" AI projects
- **Governance is automatic** - Can't skip or forget controls
- **Compliance from inception** - Audit trail starts at git init
- **Budget controls enforced** - No runaway costs
- **Tier-appropriate access** - Right level of autonomy for the use case
- **Production safety** - Tier 3/4 requires threat modeling + approvals

### Token Efficiency
- Claude Code auto-loads project context
- No need to explain governance every conversation
- Framework rules are embedded in the project
- AI agents know the constraints immediately

### Accountability Trail
- Git commit shows who, when, what tier, budget
- GOVERNANCE.md declares human responsibility
- settings.local.json machine-readable for automation
- All agent actions traceable to owner

## Enforcement Philosophy

This system embodies **"AI-driven labor with human accountability and responsibility"**:

1. **AI automates the process** - Project creation is fast and consistent
2. **Humans remain accountable** - Every project has a named owner
3. **Rules are enforced** - Cannot skip governance steps
4. **Appropriate controls** - Tier-based risk management
5. **Audit from Day 1** - Complete trail from project inception
6. **Cost consciousness** - Budget limits prevent waste
7. **Compliance built-in** - Not an afterthought

## Future Enhancements

Potential additions:
- Web UI for project creation (vs CLI)
- Integration with HR system for owner validation
- Automatic Slack/Teams notification to owner
- Dashboard showing all projects by tier/owner/budget
- Cost tracking integration from project creation
- Automatic SIEM event for new project creation
- CI/CD pipeline auto-configuration based on tier
- Auto-generated test scaffolding for the tech stack

## Comparison: Manual vs Enforced

| Aspect | Manual Creation | Enforced Creation |
|--------|----------------|-------------------|
| Governance setup | Optional, often forgotten | Mandatory, cannot skip |
| Owner declaration | May be missing | Required with validation |
| Budget controls | Added later (if at all) | Defined upfront |
| Compliance | Afterthought | Declared at inception |
| Audit trail | Incomplete | Complete from git init |
| Context loading | Manual `/init` | Automatic |
| Tier controls | Must be implemented | Pre-configured |
| Token efficiency | Wasteful repetition | One-time setup |

## Summary

The enforced project creation system ensures:
- ✅ Governance from Day 1
- ✅ Human accountability for every project
- ✅ Tier-appropriate controls
- ✅ Budget enforcement
- ✅ Compliance awareness
- ✅ Complete audit trails
- ✅ Token-efficient AI interactions
- ✅ Production safety (threat models + approvals)

**No project can escape governance. Accountability is built-in, not bolted-on.**
