# AI Agent Pattern: Debugging DevContainer Issues with Vendor Images

## Overview

This document captures a generalizable pattern for AI agents to diagnose and resolve DevContainer initialization failures when working with vendor-specific tooling (Splunk, Kubernetes, databases, CI/CD platforms, etc.).

**Problem Context:** DevContainers fail to initialize properly when developers bypass vendor entrypoint logic by using generic base images, overriding entry points, or mismanaging runtime configurations.

**Solution Pattern:** Always respect vendor assumptions (entrypoint, user, directory structure) and separate build-time vs runtime concerns.

---

## ⚠️ IMPORTANT: Safety Protocol

**Before applying any fixes from this document, AI agents MUST follow the [AI Agent Safety Policy](../policies/agent-safety-policies.md):**

1. ✅ **Pre-Flight Context Gathering** - List all running containers, volumes, and networks
2. ✅ **Scope Boundary Questions** - Ask about other projects that may be affected
3. ✅ **Explicit Approval** - Get user confirmation before destructive operations
4. ✅ **Create Checkpoints** - Backup configurations before changes
5. ✅ **Incremental Validation** - Test ONE change at a time
6. ✅ **Validation Gates** - Verify each change works before proceeding

**See:** [Agent Safety Policies](../policies/agent-safety-policies.md#mandatory-pre-flight-protocol)

---

## Problem Pattern Recognition

### Symptom Categories

**Indicators that suggest vendor image issues:**

1. **Missing expected binaries or environment variables**
   - Vendor tools not in `$PATH`
   - Configuration commands fail (`ansible --version`, `kubectl version`, `splunk status`)

2. **Permission/ownership errors on critical directories**
   - `Permission denied` on vendor-managed paths
   - World-readable temp file warnings from tools like Ansible

3. **Configuration tools warning about insecure paths**
   - Ansible: `"world-readable" tempfile warnings`
   - Kubernetes: `kubeconfig` permission errors

4. **Application fails to start despite correct code**
   - Vendor service won't start or exits immediately
   - Logs show initialization steps skipped

5. **WSL or generic base images used instead of vendor images**
   - `FROM ubuntu:latest` or `FROM alpine:latest` in Dockerfile
   - `"image": "mcr.microsoft.com/devcontainers/base:ubuntu"` when vendor image exists

### Root Cause Patterns

Developers bypass vendor entrypoint logic by:

1. **Using generic base images** (Ubuntu, Alpine, WSL) when vendor images exist
2. **Overriding ENTRYPOINT/CMD** in custom Dockerfile
3. **Baking runtime secrets into image layers** (environment variables, credentials)
4. **Ignoring vendor-specific directory structure and permissions** (e.g., `/opt/splunk/`, `/opt/kafka/`)

---

## Solution Pattern (Generalizable)

### 1. Always Start with Vendor Base Image

**Pattern:**

```json
{
  "image": "<vendor>/<product>:<tag>",  // ✅ Direct vendor image
  // OR if customization needed:
  "build": {
    "dockerfile": "Dockerfile",
    "context": "."
  }
}
```

**Dockerfile (if customization needed):**

```dockerfile
FROM <vendor>/<product>:<tag>

# Install dev tools as root
USER root
RUN <install dev tools only>

# Create directories and fix permissions
RUN <create directories, fix permissions>

# Switch back to vendor user
USER <vendor-user>

# ✅ CRITICAL: Do NOT override ENTRYPOINT or CMD
```

**Key Principle:** Vendor images contain critical initialization logic (license acceptance, first-boot setup, service registration). Let them run unchanged.

**Examples:**
- Splunk: `splunk/splunk:latest` (not `ubuntu:latest` with Splunk installed)
- Kubernetes: `rancher/k3s:latest` (not `alpine:latest` with kubectl)
- PostgreSQL: `postgres:15` (not custom build)
- Redis: `redis:7-alpine` (not custom build)

---

### 2. Externalize Runtime Secrets

**Anti-pattern:**

```dockerfile
# ❌ Baked into image - insecure and inflexible
ENV SECRET_PASSWORD="hardcoded123"
ENV API_KEY="pk_live_12345"
```

**Correct Pattern:**

```json
{
  "containerEnv": {
    "SECRET_PASSWORD": "${localEnv:SECRET_PASSWORD}",  // From host environment
    "API_KEY": "set-at-runtime"  // Placeholder, override at runtime
  },
  "runArgs": [
    "-e", "SECRET_PASSWORD=${SECRET_PASSWORD}"  // Pass from CI/CD
  ]
}
```

**Key Principle:** Secrets belong in runtime environment, not image layers (security + reusability).

---

### 3. Inject Configuration Files via Bind Mounts

**Problem:** Vendor images have default configs; team needs version-controlled overrides.

**Pattern:**

```json
{
  "mounts": [
    "source=${localWorkspaceFolder}/.ops/<config-file>,target=<vendor-config-path>,type=bind,consistency=cached"
  ]
}
```

**Examples:**

```json
// Splunk Ansible configuration
"mounts": [
  "source=${localWorkspaceFolder}/.ops/ansible.cfg,target=/opt/splunk/ansible.cfg,type=bind"
]

// Kubernetes kubeconfig
"mounts": [
  "source=${localWorkspaceFolder}/.kube/config,target=/home/user/.kube/config,type=bind"
]
```

**Key Principle:** Keep configs in repo, mount at runtime. Enables version control without rebuilding image.

---

### 4. Fix Permissions in postStartCommand

**Problem:** Vendor user/group IDs may not match host, causing permission errors on volumes.

**Pattern:**

```json
{
  "postStartCommand": "bash -lc 'set -e; <permission-fixes>; <ownership-fixes>; <directory-creation>'"
}
```

**Template:**

```bash
mkdir -p <critical-dirs>;
chown -R <vendor-user>:<vendor-group> <critical-dirs> || true;
chmod <mode> <critical-dirs> || true;
chown -R <vendor-user>:<vendor-group> <data-volume> || true
```

**Specific Example (Splunk):**
```bash
mkdir -p /opt/splunk/tmp;
chown splunk:splunk /opt/splunk/tmp || true;
chmod 700 /opt/splunk/tmp || true;
chown -R splunk:splunk /opt/splunk/var || true
```

**Key Principle:** Fix permissions *after* container starts, when volumes are mounted and vendor user exists.

---

### 5. Persist Data with Named Volumes

**Anti-pattern:**

```json
{
  "mounts": [
    // ❌ Host UID/GID mismatch causes permission errors
    "source=${localWorkspaceFolder}/data,target=/opt/product/var,type=bind"
  ]
}
```

**Correct Pattern:**

```json
{
  "mounts": [
    // ✅ Named volume avoids host UID/GID issues
    "source=<product>-data,target=<vendor-data-path>,type=volume"
  ],
  "postStartCommand": "chown -R <vendor-user>:<vendor-group> <vendor-data-path> || true"
}
```

**Key Principle:** Named volumes avoid host UID/GID mismatches. Fix ownership on every start.

---

### 6. Configure Passwordless Sudo for Vendor Users (When Needed)

**Problem:** Vendor containers often run initialization tasks (Ansible, setup scripts) that need elevated privileges but run as non-root user.

**Symptom:**
```
TASK [some_init_task] ***
fatal: [localhost]: FAILED! => {
  "msg": "sudo: a password is required"
}
```

**Detection:**
```bash
# Check who's running
docker exec <container> whoami

# Check sudo permissions
docker exec <container> sudo -l
```

**Solution:**

Add to Dockerfile (build-time):
```dockerfile
USER root
RUN echo "<vendor-user> ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/<vendor-user> \
    && chmod 0440 /etc/sudoers.d/<vendor-user>
USER <vendor-user>
```

**When to Apply:**

| Vendor | User | Needs Sudo | Reason |
|--------|------|-----------|--------|
| Splunk | `splunk` | ✅ Yes | Ansible tasks (chown, chmod) |
| Jenkins | `jenkins` | ⚠️ Sometimes | Plugin installation |
| Nginx | `nginx` | ✅ Yes | Port 80 binding (or use CAP_NET_BIND_SERVICE) |
| Postgres | `postgres` | ❌ No | Pre-configured |

**Security Note:** Passwordless sudo is acceptable in DevContainer environments (not production). Limit to specific vendors or commands if concerned.

**Key Principle:** Vendor initialization scripts may need sudo; configure it in Dockerfile if you see "password required" errors.

---

### 7. Use Active Monitoring for Async Initialization

**Problem:** Many vendor containers initialize asynchronously (Ansible, database setup, cluster formation). Single log checks miss errors that occur mid-process.

**Anti-pattern:**
```bash
# ❌ Single check misses errors during initialization
docker logs <container> | grep ERROR
```

**Correct Pattern:**
```bash
# ✅ Monitor continuously during critical initialization window
docker logs -f <container> 2>&1 | tee /tmp/init-log.txt &
MONITOR_PID=$!
sleep <initialization_duration>  # e.g., 30s for Splunk, 10s for Postgres
kill $MONITOR_PID

# Search for failures
grep -iE "fatal|failed|error|permission denied|timeout" /tmp/init-log.txt
```

**Trigger Words to Watch:**
- `fatal`, `FAILED!`, `error`
- `permission denied`
- `sudo: a password is required`
- `timeout`, `connection refused`
- `initialization failed`

**Initialization Durations by Vendor:**

| Vendor | Typical Duration | What's Happening |
|--------|-----------------|------------------|
| Splunk | ~30 seconds | Ansible playbooks, first-boot setup |
| Postgres | ~10 seconds | Database initialization, user creation |
| Jenkins | ~60 seconds | Plugin installation, configuration |
| Elasticsearch | ~20 seconds | Cluster formation, index creation |
| Redis | ~5 seconds | Configuration loading, AOF recovery |

**When to Use:**
- After `docker run` or DevContainer rebuild
- When logs show initialization steps
- When vendor documentation mentions first-boot process

**Key Principle:** Active monitoring during async initialization catches errors that passive checking misses.

---

## AI Agent Diagnostic Workflow

### Phase 1: Reconnaissance (Before Proposing Solution)

**Questions to Ask:**

1. What vendor/product is this? (Check for official Docker image)
2. Is there a `devcontainer.json` using a generic base image? (Red flag)
3. Is there a custom Dockerfile overriding ENTRYPOINT/CMD? (Red flag)
4. Are secrets hardcoded in Dockerfile/devcontainer.json? (Security issue)
5. What errors appear in `docker logs <container-name>`? (Permission, missing binary, config warnings)
6. What directories does the vendor expect? (Check vendor docs)

**Tools to Use:**
```bash
# Check current image
docker inspect <container> | jq '.[0].Config.Image'

# Check entrypoint override
docker inspect <container> | jq '.[0].Config.Entrypoint'

# ✅ CRITICAL: Active monitoring for initialization (not just one-time check)
docker logs -f <container> 2>&1 | tee /tmp/init-log.txt &
MONITOR_PID=$!
sleep 30  # Monitor full initialization cycle
kill $MONITOR_PID
grep -iE "fatal|failed|error|permission|sudo" /tmp/init-log.txt

# Check critical paths inside container
docker exec <container> stat -c '%U:%G %a %n' <critical-path>

# Check sudo permissions (if initialization failures occur)
docker exec <container> whoami
docker exec <container> sudo -l
```

---

### Phase 2: Solution Design

**Decision Tree:**

1. **Is there an official vendor image?**
   - YES → Use it directly in `devcontainer.json` (no Dockerfile)
   - NO → Build minimal Dockerfile FROM closest base, document assumptions

2. **Does team need custom dev tools?**
   - YES → Create Dockerfile FROM vendor image, install tools as root, switch back to vendor user
   - NO → Use vendor image directly

3. **Does team need custom configs?**
   - YES → Store in `.ops/` or `.config/`, mount via bind mount
   - NO → Use vendor defaults

4. **Are there permission errors?**
   - YES → Add `postStartCommand` with `chown`/`chmod` fixes
   - NO → Skip

5. **Are there secrets?**
   - YES → Use `containerEnv` with `${localEnv:VAR}` or CI runtime injection
   - NO → Skip

---

### Phase 3: Validation

**Checklist (Share with User):**

```markdown
### Verification Steps

After "Reopen in Container":

1. **Verify Vendor Initialization**
   ```bash
   docker logs -f <container-name>  # Should show clean startup
   ```

2. **Verify Configuration**
   ```bash
   <vendor-tool> --version  # e.g., ansible --version, kubectl version
   <vendor-tool> config view  # Shows active config
   ```

3. **Verify Permissions**
   ```bash
   stat -c '%U:%G %a %n' <critical-paths>
   # Should show vendor-user:vendor-group with appropriate mode
   ```

4. **Verify Secrets (without exposing them)**
   ```bash
   env | grep -i <secret-prefix>  # Should show set but not value
   ```

5. **Verify Application Starts**
   ```bash
   <vendor-service> status  # e.g., splunk status, systemctl status
   ```
```

---

## Generalization Summary

**When AI Agent Encounters DevContainer Issues:**

1. **Identify if vendor image exists** (Docker Hub, vendor registry)
2. **Propose using vendor image directly** (avoid custom Dockerfile unless necessary)
3. **Externalize all secrets** (runtime env, not image)
4. **Mount configs from repo** (version control + no rebuild)
5. **Fix permissions in postStartCommand** (after volumes mount)
6. **Use named volumes for data** (avoid UID/GID mismatches)
7. **Never override vendor ENTRYPOINT/CMD** (unless absolutely necessary and documented)
8. **Provide verification checklist** (user can confirm fix)

---

## Real-World Example: Splunk DevContainer Fix

### What Changed and Why

- Use the vendor image `splunk/splunk:latest` so the vendor entrypoint and first-boot logic run unchanged.
- Do not bake secrets (SPLUNK_PASSWORD) into the image; provide them at runtime via devcontainer env.
- Inject `ansible.cfg` from the repo (`.ops/ansible.cfg`) into `/opt/splunk/ansible.cfg` with a bind mount so the team can version and edit it.
- Ensure `/opt/splunk/tmp` exists, is mode 700, and owned by `splunk:splunk` to avoid Ansible world-readable temp warnings.
- Persist Splunk data with a named volume (`splunk-data` → `/opt/splunk/var`) and chown it on container start to avoid host UID/GID mismatches.
- Keep Dockerfile single-stage, install dev tools (git, vim, wget, net-tools or iproute) as root, create app dirs and tmp, then switch to splunk user; do not override ENTRYPOINT or CMD.

### Key Files

**.ops/ansible.cfg:**
```ini
[defaults]
pipelining = True
remote_tmp = /opt/splunk/tmp
allow_world_readable_tmpfiles = True

[privilege_escalation]
become = True
become_method = sudo
become_user = splunk
```

**.devcontainer/devcontainer.json (important bits):**
```json
{
  "image": "splunk/splunk:latest",
  "mounts": [
    "source=${localWorkspaceFolder}/.ops/ansible.cfg,target=/opt/splunk/ansible.cfg,type=bind,consistency=cached",
    "source=splunk-data,target=/opt/splunk/var,type=volume"
  ],
  "containerEnv": {
    "ANSIBLE_CONFIG": "/opt/splunk/ansible.cfg",
    "SPLUNK_GENERAL_TERMS": "--accept-sgt-current-at-splunk-com",
    "SPLUNK_START_ARGS": "--accept-license --answer-yes",
    "SPLUNK_PASSWORD": "set-at-runtime"
  },
  "postStartCommand": "bash -lc 'set -e; mkdir -p /opt/splunk/tmp; chown splunk:splunk /opt/splunk/tmp || true; chmod 700 /opt/splunk/tmp || true; chown -R splunk:splunk /opt/splunk/var || true'"
}
```

**Dockerfile (concise recommended):**
```dockerfile
FROM splunk/splunk:latest

# Build-time arguments (defaults kept for reproducible ownership)
ARG SPLUNK_USER=splunk
ARG SPLUNK_UID=41812
ARG SPLUNK_GID=41812

# Install development tools as root
USER root
RUN microdnf install -y git wget net-tools iproute sudo && microdnf clean all

# Configure passwordless sudo for splunk user (required for Ansible)
RUN echo "splunk ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/splunk \
    && chmod 0440 /etc/sudoers.d/splunk

# Create application and runtime directories and set ownership/permissions
RUN mkdir -p /opt/splunk/etc/apps/SA-SEC-eMASS \
    && mkdir -p /opt/splunk/tmp \
    && chown -R ${SPLUNK_UID}:${SPLUNK_GID} /opt/splunk/etc/apps/SA-SEC-eMASS \
    && chown -R ${SPLUNK_UID}:${SPLUNK_GID} /opt/splunk/tmp \
    && chmod 700 /opt/splunk/tmp

# Switch to splunk user for normal runtime
USER ${SPLUNK_USER}

# Do not override ENTRYPOINT or CMD from the vendor image
```

### Verification Steps

```bash
# Verify Ansible config
ansible --version | grep -i 'config file'  # Should show /opt/splunk/ansible.cfg

# Verify config values
ansible-config dump | egrep 'pipelining|remote_tmp|become'

# Verify permissions
stat -c '%U:%G %a %n' /opt/splunk/ansible.cfg /opt/splunk/tmp /opt/splunk/var

# Watch Splunk initialization
docker logs -f splunk-ucc-dev
```

---

## Meta-Learning for AI Agents

### Key Insight

This pattern resolved the issue because:
1. **Respected vendor assumptions** (entrypoint, user, directory structure)
2. **Separated concerns** (build-time vs runtime, secrets vs code)
3. **Used Docker best practices** (named volumes, bind mounts, no secret baking)
4. **Provided verifiable steps** (user could confirm fix independently)

### Reusable for:

Splunk, Kubernetes (k3s/kind), Postgres, Redis, Elastic, Kafka, any vendor image with complex initialization.

### Not applicable for:

Pure language runtimes (python:3.12, node:20) which have minimal initialization logic.

---

## See Also

- [Devcontainer Vendor Image Workflow](DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md)
- [Devcontainer Governance Integration](DEVCONTAINER-GOVERNANCE-INTEGRATION.md)
- [Devcontainer Quick Start](DEVCONTAINER-QUICKSTART.md)

---

**Built for AI agents who need to debug DevContainer issues systematically and efficiently.**
