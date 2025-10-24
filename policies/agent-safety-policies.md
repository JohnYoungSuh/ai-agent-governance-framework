# AI Agent Safety Policies

**Version:** 1.0
**Effective Date:** 2025-10-24
**Applies To:** All AI Agents (Tier 1-4)
**Policy Owner:** Governance Framework

---

## Overview

This policy defines **mandatory safety protocols** that AI agents MUST follow when performing operations that could:
- Delete or modify infrastructure
- Change running configurations
- Impact other projects or services
- Result in data loss or service disruption

**Principle:** When in doubt, ASK. Always err on the side of caution.

---

## Policy Statement

AI agents SHALL NOT perform destructive operations without:
1. ✅ Explicit human approval
2. ✅ Pre-flight context gathering
3. ✅ Rollback plan documentation
4. ✅ Incremental validation checkpoints

**Violation of this policy constitutes a governance failure and must be reported as an incident.**

---

## Scope & Definitions

### Destructive Operations

Operations that **REQUIRE** pre-flight approval:

#### Infrastructure (Docker/Kubernetes)
- `docker rm` - Delete containers
- `docker volume rm` - Delete volumes
- `docker network rm` - Delete networks
- `kubectl delete` - Delete K8s resources
- Modifying running container configurations
- Changing port mappings on active services

#### Files & Configurations
- Deleting files or directories
- Modifying configuration files in active use
- Changing environment variables for running services
- Altering `.env`, `devcontainer.json`, `docker-compose.yml`

#### Version Control
- Force push (`git push --force`)
- Rewriting history (`git rebase -i`, `git reset --hard`)
- Deleting branches (especially main/master)
- Removing `.git` directory

#### Database & Data
- Dropping tables or databases
- Truncating data
- Running UPDATE/DELETE without WHERE clause
- Disabling backups

### High-Risk Operations

Operations that **REQUIRE** explanation + approval:

- Switching implementation approaches (direct image → Dockerfile)
- Changing authentication mechanisms
- Modifying network configurations
- Altering security policies
- Changing user/permission models
- Upgrading major versions

---

## Mandatory Pre-Flight Protocol

### Phase 1: Context Gathering (Read-Only)

Before proposing ANY changes, AI agent MUST gather context:

#### For Docker/Container Operations
```bash
# 1. What's currently running?
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 2. What volumes exist?
docker volume ls

# 3. What networks exist?
docker network ls

# 4. What ports are in use?
netstat -tulpn | grep -E "<target-ports>"
```

#### For File Operations
```bash
# 1. What files will be affected?
find <path> -name "<pattern>"

# 2. Are files in use?
lsof | grep <file-path>

# 3. Are they tracked by git?
git status <path>
```

#### For Configuration Changes
```bash
# 1. Is this config in active use?
ps aux | grep <config-file>

# 2. What services depend on it?
grep -r "<config-file>" /etc/systemd/system/

# 3. Is there a backup?
ls -la <config-file>.backup* 2>/dev/null
```

**AI agent MUST present findings to user BEFORE proposing changes.**

---

### Phase 2: Scope Boundary Questions

AI agent MUST ask these questions:

#### Environmental Scope
```markdown
REQUIRED QUESTIONS:
- "Are there other projects using [Docker/K8s/filesystem] on this system?"
- "Should I list all [containers/pods/files] before proceeding?"
- "Are any of these resources critical to other work?"
- "Is this a shared development environment or single-user?"
```

#### Backup & Recovery
```markdown
REQUIRED QUESTIONS:
- "Do you have a backup of the current working state?"
- "Should I create a checkpoint before making changes?"
- "Do you have time to rebuild if something breaks?"
- "What's the acceptable downtime for this change?"
```

#### Change Impact
```markdown
REQUIRED QUESTIONS:
- "This will affect: [LIST]. Is this acceptable?"
- "Have you tested this change in a dev environment first?"
- "Do you want me to proceed incrementally or all at once?"
- "What's your rollback strategy if this fails?"
```

---

### Phase 3: Explicit Approval

AI agent MUST receive explicit approval before proceeding:

#### Approval Template
```markdown
## Proposed Operation: [OPERATION NAME]

### What Will Be Changed
- [Specific change 1]
- [Specific change 2]

### Impact Assessment
- **Resources Affected:** [List]
- **Other Projects Impacted:** [Yes/No - List if yes]
- **Data Loss Risk:** [High/Medium/Low]
- **Rollback Difficulty:** [Easy/Medium/Hard]

### Rollback Plan
1. [Step 1]
2. [Step 2]

### Estimated Time
- Implementation: X minutes
- Testing: Y minutes
- Rollback (if needed): Z minutes

**Proceed with this operation? (Type "YES" to confirm)**
```

**AI agent SHALL NOT proceed without explicit "YES" or "PROCEED".**

---

## Checkpoint & Rollback Protocol

### Before Making Changes

AI agent MUST create recovery checkpoints:

#### Git Checkpoint
```bash
# Stash all changes with timestamp
git stash push -u -m "AI Agent Checkpoint: [OPERATION] - $(date +%Y%m%d-%H%M%S)"
```

#### Configuration Backup
```bash
# Backup config files with timestamp
cp <config-file> <config-file>.backup-$(date +%s)
```

#### Container Checkpoint (Optional)
```bash
# For critical containers, create image snapshot
docker commit <container> <container>-backup-$(date +%s)
```

#### State Documentation
```bash
# Document current state for comparison
docker inspect <container> > container-state-pre-change.json
kubectl get all -o yaml > k8s-state-pre-change.yaml
```

---

### Rollback Instructions

AI agent MUST provide rollback steps WITH the proposal:

#### Rollback Template
```markdown
## Rollback Instructions (If Change Fails)

### Quick Rollback (< 5 minutes)
1. Stop service: `[command]`
2. Restore config: `cp <file>.backup <file>`
3. Restart service: `[command]`
4. Verify: `[test command]`

### Full Rollback (5-15 minutes)
1. Restore git state: `git stash pop stash@{0}`
2. Remove new resources: `[cleanup commands]`
3. Restore from checkpoint: `[restore commands]`
4. Rebuild: `[rebuild commands]`

### Nuclear Option (Last Resort)
1. Restore from system backup
2. Contact: [escalation contact]
```

---

## Incremental Change Pattern

### ❌ ANTI-PATTERN: Big Bang Deployment

```
Change everything at once
    ↓
Rebuild/restart
    ↓
Discover multiple failures
    ↓
Unable to identify root cause
    ↓
Full rollback required
```

**Risk:** High - Multiple variables changed, unclear which caused failure.

---

### ✅ CORRECT PATTERN: Incremental Validation

```
Change 1: [Single specific change]
    ↓
Test & Validate
    ↓
Success? → Commit → Document
    ↓
Change 2: [Next single change]
    ↓
Test & Validate
    ↓
Success? → Commit → Document
    ↓
Continue...
```

**Benefit:** Each change is isolated, failures are immediately identifiable, rollback is targeted.

---

### Implementation Example

**Scenario:** Migrate DevContainer from direct image to Dockerfile with new configs

#### ❌ Wrong Approach
```
1. Change devcontainer.json (image → build)
2. Add port forwards
3. Externalize secrets
4. Add configuration mounts
5. Change user
6. Rebuild
7. Hope it works
```

#### ✅ Correct Approach
```
Step 1: Externalize secrets ONLY
- Change: SPLUNK_PASSWORD → ${localEnv:SPLUNK_PASSWORD}
- Test: Rebuild, verify secret loaded
- Validate: `echo $SPLUNK_PASSWORD` inside container
- Commit: git commit -m "Externalize SPLUNK_PASSWORD"
- ✅ Success → Continue

Step 2: Add port forwards ONLY
- Change: Add -p 8000:8000 to runArgs
- Test: Rebuild, verify port accessible
- Validate: `curl -I http://localhost:8000`
- Commit: git commit -m "Add port forwards"
- ✅ Success → Continue

Step 3: Switch to Dockerfile build
- Change: image → build.dockerfile
- Test: Rebuild, verify image builds
- Validate: `docker exec <container> whoami` (check user)
- Commit: git commit -m "Switch to Dockerfile build"
- ✅ Success → Complete

If ANY step fails:
- Stop immediately
- Rollback that specific change
- Document failure reason
- Ask user for guidance
```

---

## Validation Gates

After EVERY change, AI agent MUST validate:

### Container/Service Validation

```bash
# ✅ Resource exists?
docker ps | grep <container-name>
kubectl get pod <pod-name>

# ✅ Running as correct user?
docker exec <container> whoami
kubectl exec <pod> -- whoami

# ✅ Ports accessible?
curl -I http://localhost:<port>
nc -zv localhost <port>

# ✅ Volumes mounted correctly?
docker inspect <container> | jq '.[0].Mounts'
kubectl exec <pod> -- ls -la /mnt/volume

# ✅ Permissions correct?
docker exec <container> stat -c '%U:%G %a' /critical/path

# ✅ Service responding?
curl http://localhost:<port>/health
```

### Application Validation

```bash
# ✅ Application started successfully?
docker logs <container> | tail -50
kubectl logs <pod> | tail -50

# ✅ No error messages in logs?
docker logs <container> 2>&1 | grep -i "error\|fatal\|permission denied"

# ✅ Dependencies available?
docker exec <container> <command> --version

# ✅ Configuration loaded?
docker exec <container> cat /path/to/config
```

**If ANY validation fails:**
1. ❌ STOP immediately
2. ❌ DO NOT mark task as complete
3. ❌ DO NOT proceed to next change
4. ✅ Rollback the change
5. ✅ Report failure to user with diagnostics

### Vendor Container Initialization (CRITICAL)

**Problem:** Vendor containers (Splunk, Postgres, Jenkins, etc.) initialize asynchronously. Passive checks miss critical errors.

**Mandatory Active Monitoring:**

```bash
# ❌ WRONG: Single check misses async initialization errors
docker logs <container> | grep ERROR

# ✅ CORRECT: Monitor full initialization cycle
docker logs -f <container> 2>&1 | tee /tmp/init-log.txt &
MONITOR_PID=$!
sleep <init_duration>  # e.g., 30s for Splunk, 10s for Postgres
kill $MONITOR_PID

# Check for failures
grep -iE "fatal|failed|error|permission denied|sudo.*required" /tmp/init-log.txt
```

**Initialization Durations:**

| Vendor | Duration | Critical Events to Watch |
|--------|----------|-------------------------|
| Splunk | ~30s | Ansible tasks, first-boot setup |
| Postgres | ~10s | Database initialization |
| Jenkins | ~60s | Plugin installation |
| Elasticsearch | ~20s | Cluster formation |

**Specific Checks for Vendor Containers:**

```bash
# ✅ Monitor logs for full initialization cycle (30+ seconds)
docker logs -f <container> 2>&1 | tee /tmp/init-log.txt &

# ✅ Check for sudo/permission errors in init tasks
grep -i "sudo.*password required" /tmp/init-log.txt

# ✅ Verify service status, not just container running
docker exec <container> <vendor-command> status
# Examples:
#   splunk status
#   systemctl status postgresql
#   jenkins-cli version

# ✅ Test workspace file access from correct user
docker exec <container> whoami
docker exec <container> ls -la /workspace

# ✅ Confirm ports are accessible (not just open)
curl -I http://localhost:<port>  # Check for HTTP response
nc -zv localhost:<port>           # Check for connection
```

**Common Vendor Init Errors:**

| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `sudo: a password is required` | Non-root user needs elevated privileges | Add passwordless sudo in Dockerfile |
| `Permission denied: /var/lib/<vendor>` | Volume ownership mismatch | Add `chown` to postStartCommand |
| `initialization timeout` | Init takes longer than expected | Increase monitoring duration |
| `connection refused` | Service not fully started | Wait longer before checks |

**Before Declaring DevContainer "Working":**

- [ ] Monitor logs for full initialization cycle (30+ seconds)
- [ ] Check for sudo/permission errors in init tasks
- [ ] Verify service status (not just container running)
- [ ] Test workspace file access from correct user
- [ ] Confirm ports are accessible (curl/nc check)
- [ ] Validate vendor-specific health endpoints
- [ ] Check that vendor CLI commands work

---

## Decision Tree for AI Agents

```
┌─────────────────────────────────────────┐
│ User requests operation                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Is this a destructive operation?        │
│ (See "Destructive Operations" section)  │
└─────┬─────────────────────────┬─────────┘
      │ YES                     │ NO
      ▼                         ▼
┌──────────────────────┐  ┌──────────────────┐
│ MANDATORY:           │  │ Is it high-risk? │
│ 1. Gather context    │  └────┬─────────┬───┘
│ 2. Ask scope qs      │       │ YES     │ NO
│ 3. Get explicit YES  │       ▼         ▼
└─────┬────────────────┘  ┌─────────┐ ┌────┐
      │                   │ Ask user│ │ Do │
      ▼                   └─────────┘ └────┘
┌──────────────────────┐
│ User approved?       │
└───┬──────────────┬───┘
    │ NO           │ YES
    ▼              ▼
┌────────┐   ┌─────────────────┐
│ ABORT  │   │ Create          │
│        │   │ checkpoints     │
└────────┘   └────┬────────────┘
                  ▼
            ┌─────────────────┐
            │ Make ONE change │
            │ (incremental)   │
            └────┬────────────┘
                 ▼
            ┌─────────────────┐
            │ Run validation  │
            │ gates           │
            └────┬────────────┘
                 ▼
            ┌─────────────────┐
            │ All validations │
            │ passed?         │
            └───┬─────────┬───┘
                │ NO      │ YES
                ▼         ▼
          ┌──────────┐ ┌──────────────┐
          │ ROLLBACK │ │ Commit       │
          │ & REPORT │ │ & document   │
          └──────────┘ └───┬──────────┘
                           ▼
                      ┌──────────────┐
                      │ More changes?│
                      └───┬──────┬───┘
                          │ YES  │ NO
                          ▼      ▼
                    ┌─────────┐ ┌────┐
                    │ Repeat  │ │DONE│
                    └─────────┘ └────┘
```

---

## Incident Reporting

When AI agent violates safety policy or causes unintended impact:

### Mandatory Incident Report

AI agent MUST create an incident report using this template:

```markdown
# AI Agent Safety Incident Report

**Incident ID:** INC-[YYYYMMDD]-[###]
**Date/Time:** [ISO 8601 timestamp]
**AI Agent:** [Name/Version/Session ID]
**Tier:** [1/2/3/4]
**Severity:** [Critical/High/Medium/Low]

---

## Incident Summary

[One-paragraph description of what went wrong]

---

## User Impact

- **Downtime:** [X minutes/hours]
- **Data Loss:** [Yes/No - Description]
- **Projects Affected:** [List]
- **Recovery Time:** [X minutes/hours]

---

## Root Cause Analysis

### What Went Wrong
1. [Primary cause]
2. [Contributing factor 1]
3. [Contributing factor 2]

### Safety Policies Violated
- [ ] Pre-flight context gathering skipped
- [ ] Scope boundary questions not asked
- [ ] Explicit approval not obtained
- [ ] Checkpoint not created
- [ ] Incremental validation not followed
- [ ] Validation gates failed but proceeded anyway
- [ ] Rollback plan not documented

---

## Timeline

| Time | Event | Agent Action | User Action |
|------|-------|-------------|-------------|
| T+0  | [Initial request] | [What agent did] | [What user requested] |
| T+X  | [Change made] | [Specific change] | - |
| T+Y  | [Failure detected] | [What broke] | - |
| T+Z  | [Recovery started] | [Rollback actions] | [User interventions] |

---

## What Should Have Been Done

### Correct Approach
1. [Step 1 - Context gathering]
2. [Step 2 - Scope questions]
3. [Step 3 - Approval]
4. [Step 4 - Checkpoint]
5. [Step 5 - Incremental change]
6. [Step 6 - Validation]

### Missing Safeguards
1. [Safeguard 1 that was skipped]
2. [Safeguard 2 that was skipped]

---

## Prevention Measures

### Policy Updates Needed
1. [New policy requirement 1]
2. [Checklist item to add]

### Training/Documentation Gaps
1. [Documentation to create/update]
2. [Example scenario to add]

### Technical Controls
1. [Automated check to implement]
2. [Validation gate to add]

---

## User Recovery

### Steps Taken to Recover
1. [User action 1]
2. [User action 2]

### Time Lost
- **User time:** [X minutes/hours]
- **Project delay:** [Y hours/days]

### Lessons Learned
1. [Lesson 1]
2. [Lesson 2]

---

## Follow-Up Actions

- [ ] Update safety policy documentation
- [ ] Add scenario to training examples
- [ ] Implement automated safeguard
- [ ] Review with governance team
- [ ] Communicate to AI agent developers

---

**Report Filed By:** [AI Agent Session ID]
**Reviewed By:** [Human reviewer]
**Status:** [Open/In Progress/Closed]
```

---

## Real-World Incident Example

### Incident: DevContainer Rebuild Failure (2025-10-24)

**Severity:** High
**Impact:** User's devcontainer broken, ports not forwarded, wrong user

#### What Went Wrong
1. AI agent deleted Docker containers without checking other projects
2. Changed from direct image to Dockerfile without incremental testing
3. Forgot to add port forwards in initial configuration
4. Container ran as wrong user (ansible instead of splunk)
5. No validation checkpoints between changes

#### Safety Policies Violated
- ✅ Pre-flight context gathering: **SKIPPED**
  - Did not list all running containers first
  - Did not ask about other projects
- ✅ Scope boundary questions: **SKIPPED**
  - Assumed single-project environment
  - Did not ask if emass-client-dev was critical
- ✅ Explicit approval: **SKIPPED**
  - Did not list what would be affected
  - Proceeded without "YES" confirmation
- ✅ Incremental validation: **VIOLATED**
  - Changed multiple things at once
  - Did not test each change independently
- ✅ Validation gates: **FAILED**
  - Did not verify user after rebuild
  - Did not test ports before marking complete

#### What Should Have Been Done

**Step 0: Pre-Flight (REQUIRED)**
```markdown
AI: "I see these containers running:
- emass-client-dev (active, 2 days old)
- splunk-dev (exited 18 hours ago)

Questions:
1. Is emass-client-dev a separate project? Should I avoid touching it?
2. Is splunk-dev safe to delete or still needed?
3. Do you have a backup of the working splunk configuration?

Proceed? [Y/N]"

User: "Yes, emass-client-dev is separate. Splunk-dev is old, ok to delete."
```

**Step 1: Externalize Secrets**
```bash
# Change ONLY secrets
Change: SPLUNK_PASSWORD hardcoded → ${localEnv:SPLUNK_PASSWORD}
Test: Rebuild
Validate: echo $SPLUNK_PASSWORD inside container
Result: ✅ Works
Commit: git commit -m "Externalize SPLUNK_PASSWORD"
```

**Step 2: Add Port Forwards**
```bash
# Change ONLY ports
Change: Add -p 8000:8000, -p 8088:8088, -p 8089:8089
Test: Rebuild
Validate: curl -I http://localhost:8000
Result: ✅ Port accessible
Commit: git commit -m "Add port forwards"
```

**Step 3: Test Direct Image First**
```bash
# Test with direct vendor image
Test: Rebuild with image: splunk/splunk:latest
Validate: docker exec container whoami → Should show "splunk"
Result: If works, keep it. If not, then try Dockerfile.
```

**Step 4: Only If Needed - Switch to Dockerfile**
```bash
# Only if direct image failed
Change: Switch to build.dockerfile
Test: Rebuild
Validate: whoami, ports, volumes
Result: ✅ All checks pass
Commit: git commit -m "Switch to Dockerfile for dev tools"
```

#### Prevention Measures Implemented

1. ✅ Created `AI-AGENT-SAFETY-CHECKLIST.md` in project
2. ✅ Adding this policy to ai-agent-governance-framework
3. ✅ Decision tree for destructive operations
4. ✅ Mandatory validation gates defined
5. ✅ Incident report template created

#### Lessons Learned

1. **Context is king** - Always gather full environmental context before changes
2. **Ask, don't assume** - Shared systems may have resources you don't know about
3. **One change at a time** - Incremental validation catches failures early
4. **Validate immediately** - Don't mark tasks complete without testing
5. **Document rollback** - User needs recovery steps when things break

---

## Compliance & Enforcement

### Automated Checks (Future Enhancement)

AI agents should implement these automated safeguards:

```python
# Pseudo-code for safety checks
class AIAgentSafetyEnforcement:

    def before_destructive_operation(self, operation):
        """Enforce pre-flight protocol"""

        # 1. Check if operation is destructive
        if operation in DESTRUCTIVE_OPERATIONS:

            # 2. Gather context automatically
            context = self.gather_context(operation)

            # 3. Present to user
            self.present_context(context)

            # 4. Ask scope questions
            responses = self.ask_scope_questions(operation)

            # 5. Get explicit approval
            approved = self.get_explicit_approval(operation, context, responses)

            if not approved:
                raise SafetyPolicyViolation("User did not approve destructive operation")

            # 6. Create checkpoint
            checkpoint = self.create_checkpoint(operation)

            # 7. Return checkpoint for rollback
            return checkpoint

        # Non-destructive, proceed
        return None

    def after_change_validation(self, operation, expected_state):
        """Enforce validation gates"""

        # Run validation checks
        results = self.run_validation_gates(operation)

        if not results.all_passed():
            # Auto-rollback on failure
            self.rollback(operation, checkpoint)
            raise ValidationFailure(f"Validation failed: {results.failures}")

        return results
```

### Audit Trail

All destructive operations MUST be logged:

```json
{
  "timestamp": "2025-10-24T15:30:00Z",
  "agent_id": "claude-code-session-12345",
  "operation": "docker rm splunk-dev",
  "pre_flight_completed": false,
  "user_approval": false,
  "checkpoint_created": false,
  "result": "failure",
  "policy_violations": [
    "pre-flight context gathering skipped",
    "explicit approval not obtained"
  ],
  "incident_id": "INC-20251024-001"
}
```

---

## Training & Examples

### Example Scenarios for AI Agent Training

#### Scenario 1: Safe Container Deletion

```markdown
User: "Delete the test-db container"

✅ CORRECT AI Response:
"Before deleting test-db container, let me gather context:

Current containers:
- test-db (exited 2 days ago, 500MB volume)
- prod-db (running, critical)
- app-server (running, depends on test-db network)

Questions:
1. Is test-db safe to delete? It shares a network with app-server.
2. Should I also delete the test-db volume (500MB)?
3. Do you have a backup if you need to restore it?

Proceed with deletion? [YES/NO]"
```

#### Scenario 2: Configuration Change

```markdown
User: "Change the API port from 8080 to 9090"

✅ CORRECT AI Response:
"I'll change the API port, but let me check dependencies first:

Current state:
- API running on port 8080
- 3 services configured to connect to :8080
- No conflicts on port 9090

Impact:
- API will restart (30s downtime)
- Client services will need port updated
- Load balancer config may need update

Plan:
1. Update API config to port 9090
2. Test API starts on new port
3. Update client configs
4. Update load balancer (if needed)

Create checkpoint before proceeding? [YES/NO]"
```

---

## Tier-Specific Requirements

### Tier 1 (Observer) - Read-Only
- Pre-flight: Not required (read-only operations)
- Approval: Not required
- Validation: Recommended for data quality

### Tier 2 (Developer) - Dev Environment
- Pre-flight: Required for container/file operations
- Approval: Required for destructive operations
- Validation: MANDATORY after every change
- Scope: Limited to dev environment only

### Tier 3 (Operations) - Production
- Pre-flight: MANDATORY for ALL operations
- Approval: MANDATORY with change request ticket
- Validation: MANDATORY with health checks
- Rollback: MANDATORY documentation before change
- Incident Reporting: MANDATORY for any failure

### Tier 4 (Architect) - Design Changes
- Pre-flight: MANDATORY with architecture review
- Approval: MANDATORY from technical leadership
- Validation: MANDATORY with integration tests
- Documentation: MANDATORY design decision records
- Incident Reporting: MANDATORY for any regression

---

## Related Policies

- [Risk Catalog](risk-catalog.md) - AI-specific risks (RI-016: Configuration Drift)
- [Mitigation Catalog](mitigation-catalog.md) - MI-020: Change Management
- [Threat Modeling Guide](../workflows/threat-modeling/guide.md) - STRIDE analysis
- [Logging Policy](logging-policy.md) - Audit trail requirements

---

## Policy Review & Updates

**Review Cycle:** Quarterly or after major incidents
**Last Updated:** 2025-10-24
**Next Review:** 2026-01-24
**Version History:**
- v1.0 (2025-10-24) - Initial policy based on DevContainer incident

---

## Acknowledgments

This policy was developed in response to real-world AI agent safety incidents and incorporates lessons learned from:
- DevContainer rebuild failure (2025-10-24)
- Site Reliability Engineering (SRE) best practices
- Change Management frameworks (ITIL, COBIT)
- Chaos Engineering principles

---

**Remember: The goal is not to slow down AI agents, but to prevent costly mistakes that slow down users.**

**When in doubt, ASK. Always err on the side of caution.**
