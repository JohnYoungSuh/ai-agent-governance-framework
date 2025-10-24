# DevContainer Frequently Asked Questions (FAQ)

**Last Updated:** October 2024
**Maintained By:** AI Agent Governance Framework

---

## General DevContainer Questions

### Q: What is a DevContainer?

**A:** A DevContainer is a Docker-based development environment configuration that ensures all developers (and AI agents) work in identical, reproducible environments. It's defined by `.devcontainer/devcontainer.json` and optionally a `Dockerfile`.

**Benefits:**
- ✅ Consistent environment across team
- ✅ No "works on my machine" issues
- ✅ Onboarding: clone + open = ready to code
- ✅ Vendor tools pre-configured
- ✅ VS Code extensions auto-installed

---

### Q: When should I use a DevContainer vs local development?

**A:** Use DevContainers when:

| Scenario | DevContainer | Local Dev |
|----------|-------------|-----------|
| **Team has >2 members** | ✅ Recommended | ⚠️ Drift risk |
| **Complex dependencies** (Splunk, K8s, databases) | ✅ Essential | ❌ Difficult |
| **Multiple tool versions** (Python 3.9 + 3.12, Node 18 + 20) | ✅ Isolates versions | ⚠️ Conflicts |
| **AI agent collaboration** | ✅ Reproducible | ❌ Unpredictable |
| **Simple scripts** (single file, no deps) | ⚠️ Overkill | ✅ Faster |

---

## Vendor Image Questions

### Q: Why does VS Code create two Docker images?

**A:** This is **normal and expected** when using a custom Dockerfile.

**What Happens:**
```
VS Code sees:
  "build": {"dockerfile": "Dockerfile"}

VS Code creates:
  vsc-<folder>-<hash>-uid (custom image)
    ├── Your customizations (~200MB)
    └── FROM vendor/image:latest (6.5GB)
         └── Vendor base image
```

**Why Both Exist?**
- Docker layer caching (efficiency)
- Custom image **inherits** from vendor base
- Multiple devcontainers share vendor base
- Actual disk usage ≈ customizations only (~200MB)

**When Hash Changes:**
- devcontainer.json modified
- Dockerfile modified
- Build context changes

**Is This a Problem?**
- ❌ No - This is Docker's layered architecture working correctly
- ✅ Saves disk space through layer sharing
- ✅ Faster rebuilds (only custom layers rebuild)

---

### Q: Should I use `"image"` or `"build"` in devcontainer.json?

**A:** Depends on whether you need customization:

| Approach | When to Use | Example |
|----------|------------|---------|
| **Direct Image** | No customization needed | `"image": "postgres:15"` |
| **Build (Dockerfile)** | Need dev tools, sudo, custom setup | `"build": {"dockerfile": "Dockerfile"}` |

**Decision Tree:**
```
Do you need to install system packages (git, vim, sudo)?
├─ YES → Use Dockerfile
└─ NO → Do you need to change user permissions?
    ├─ YES → Use Dockerfile
    └─ NO → Use direct image
```

**Example: Postgres**
```json
// ✅ Direct image (no customization needed)
{
  "image": "postgres:15",
  "containerEnv": {
    "POSTGRES_PASSWORD": "${localEnv:POSTGRES_PASSWORD}"
  }
}
```

**Example: Splunk**
```json
// ✅ Build (needs dev tools + sudo)
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": "."
  },
  "containerEnv": {
    "SPLUNK_PASSWORD": "${localEnv:SPLUNK_PASSWORD}"
  }
}
```

---

### Q: Why should I NOT override vendor ENTRYPOINT/CMD?

**A:** Vendor images (Splunk, Postgres, Jenkins, etc.) have critical initialization logic in their entrypoints.

**What Happens If You Override:**

```dockerfile
# ❌ BAD: Overrides vendor initialization
FROM splunk/splunk:latest
ENTRYPOINT ["/bin/bash"]
CMD ["sleep", "infinity"]
```

**Consequences:**
- ❌ License acceptance skipped
- ❌ First-boot setup never runs
- ❌ Configuration files not created
- ❌ Service doesn't start
- ❌ Vendor tooling broken

**Correct Pattern:**

```dockerfile
# ✅ GOOD: Let vendor entrypoint run
FROM splunk/splunk:latest
USER root
RUN <install custom tools>
USER splunk
# Do NOT override ENTRYPOINT or CMD
```

**When You MUST Override:**
- Document WHY in comments
- Understand what vendor entrypoint does
- Reproduce critical initialization steps
- Test thoroughly

---

## Configuration & Secrets Questions

### Q: How do I handle secrets in DevContainers?

**A:** **NEVER** hardcode secrets. Use runtime injection.

**❌ WRONG: Hardcoded in Dockerfile**
```dockerfile
ENV SPLUNK_PASSWORD="hardcoded123"  # Baked into image layers
ENV API_KEY="pk_live_12345"         # Visible in `docker history`
```

**✅ CORRECT: Runtime Injection**

```json
// devcontainer.json
{
  "containerEnv": {
    "SPLUNK_PASSWORD": "${localEnv:SPLUNK_PASSWORD}",  // From host environment
    "API_KEY": "${localEnv:API_KEY:default-value}"      // With fallback
  }
}
```

**Setup:**
```bash
# Option 1: Export in shell
export SPLUNK_PASSWORD="YourSecurePassword"

# Option 2: Create .env file (add to .gitignore!)
echo "SPLUNK_PASSWORD=YourSecurePassword" > .env

# Option 3: CI/CD runtime injection
docker run -e SPLUNK_PASSWORD=$VAULT_SECRET ...
```

**Why This Matters:**
- 🔒 Secrets not in version control
- 🔒 Secrets not in image layers
- 🔒 Different secrets per environment (dev/staging/prod)
- 🔒 Rotate secrets without rebuilding image

---

### Q: How do I version-control configuration files?

**A:** Use **bind mounts** to inject configs from repo.

**Pattern:**

```
repo/
├── .ops/
│   └── ansible.cfg        # Version-controlled config
└── .devcontainer/
    └── devcontainer.json
```

```json
// devcontainer.json
{
  "mounts": [
    "source=${localWorkspaceFolder}/.ops/ansible.cfg,target=/opt/splunk/ansible.cfg,type=bind,consistency=cached"
  ]
}
```

**Benefits:**
- ✅ Config changes tracked in git
- ✅ No image rebuild needed
- ✅ Team can review config changes in PR
- ✅ Easy to revert

**Applicable To:**
- Ansible configs → `/opt/splunk/ansible.cfg`
- Kubernetes configs → `/home/user/.kube/config`
- Nginx configs → `/etc/nginx/conf.d/custom.conf`
- Database init scripts → `/docker-entrypoint-initdb.d/init.sql`

---

## Troubleshooting Questions

### Q: My DevContainer fails during initialization. How do I debug?

**A:** Use **active monitoring**, not passive log checks.

**❌ WRONG: Passive Check**
```bash
docker logs my-container | grep ERROR
# Misses errors that occur mid-initialization
```

**✅ CORRECT: Active Monitoring**
```bash
# Monitor full initialization cycle
docker logs -f my-container 2>&1 | tee /tmp/init-log.txt &
MONITOR_PID=$!
sleep 30  # Wait for full initialization
kill $MONITOR_PID

# Check for failures
grep -iE "fatal|failed|error|permission|sudo" /tmp/init-log.txt
```

**Common Init Durations:**
- Splunk: ~30 seconds (Ansible playbooks)
- Postgres: ~10 seconds (database initialization)
- Jenkins: ~60 seconds (plugin installation)
- Elasticsearch: ~20 seconds (cluster formation)

**Trigger Words to Search For:**
- `fatal`, `FAILED!`, `error`
- `permission denied`
- `sudo: a password is required`
- `timeout`, `connection refused`

---

### Q: I see "sudo: a password is required" during initialization. What do I do?

**A:** Vendor initialization scripts need sudo. Configure passwordless sudo in Dockerfile.

**Problem:**
```
TASK [change_ownership] ***
fatal: [localhost]: FAILED! => {"msg": "sudo: a password is required"}
```

**Solution:**

```dockerfile
FROM splunk/splunk:latest

USER root
RUN echo "splunk ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/splunk \
    && chmod 0440 /etc/sudoers.d/splunk
USER splunk
```

**Which Vendors Need This?**

| Vendor | User | Needs Sudo | Why |
|--------|------|-----------|-----|
| Splunk | `splunk` | ✅ Yes | Ansible tasks (chown, chmod) |
| Jenkins | `jenkins` | ⚠️ Sometimes | Plugin installation |
| Nginx | `nginx` | ✅ Yes | Port 80 binding |
| Postgres | `postgres` | ❌ No | Pre-configured |

**Security Note:** Passwordless sudo is acceptable in DevContainer environments (not production).

---

### Q: Container starts but port isn't accessible. What's wrong?

**A:** Check port forwarding configuration.

**Required in devcontainer.json:**

```json
{
  "runArgs": [
    "-p", "8000:8000",  // Host:Container
    "-p", "8088:8088"
  ],
  "forwardPorts": [
    8000,
    8088
  ]
}
```

**Verification:**

```bash
# 1. Check container is running
docker ps | grep my-container

# 2. Check port mapping
docker port my-container

# 3. Check service is listening inside container
docker exec my-container netstat -tulpn | grep 8000

# 4. Test from host
curl -I http://localhost:8000

# 5. Check VS Code port forwarding
# Look for "Ports" tab in VS Code terminal panel
```

---

### Q: I get "Permission denied" on mounted volumes. How do I fix?

**A:** Use **named volumes** instead of bind mounts for data, and fix ownership in `postStartCommand`.

**❌ WRONG: Bind Mount to Data Directory**
```json
{
  "mounts": [
    "source=${localWorkspaceFolder}/data,target=/opt/splunk/var,type=bind"
  ]
}
// Causes host UID/GID mismatch
```

**✅ CORRECT: Named Volume + Ownership Fix**
```json
{
  "mounts": [
    "source=splunk-data,target=/opt/splunk/var,type=volume"
  ],
  "postStartCommand": "chown -R splunk:splunk /opt/splunk/var || true"
}
```

**Why This Works:**
- Named volumes managed by Docker (no UID/GID issues)
- `postStartCommand` runs AFTER volumes mounted
- `|| true` prevents failure if chown not needed

---

## Advanced Questions

### Q: How do I mount project-specific apps into vendor directories?

**A:** Use **intermediate mount + symlink** pattern to avoid conflicts.

**Problem:** Direct mount overwrites vendor built-in apps

**❌ WRONG: Direct Mount**
```json
{
  "mounts": [
    "source=${localWorkspaceFolder}/apps,target=/opt/splunk/etc/apps,type=bind"
  ]
}
// Overwrites vendor built-in apps!
```

**✅ CORRECT: Intermediate Mount + Symlink**
```json
{
  "mounts": [
    "source=${localWorkspaceFolder}/apps,target=/opt/splunk/etc/apps-external,type=bind"
  ],
  "postStartCommand": "bash -lc 'if [ -d /opt/splunk/etc/apps-external ]; then for app in /opt/splunk/etc/apps-external/*; do app_name=$(basename \"$app\"); if [ ! -e \"/opt/splunk/etc/apps/$app_name\" ]; then sudo ln -sf \"$app\" \"/opt/splunk/etc/apps/$app_name\"; fi; done; fi'"
}
```

**Pattern:**
1. Mount to intermediate location (`apps-external`)
2. Use `postStartCommand` to symlink into vendor directory
3. Check for existing apps (avoid overwriting)

**Applicable To:**
- Splunk apps → `/opt/splunk/etc/apps/`
- Nginx configs → `/etc/nginx/conf.d/`
- Postgres init scripts → `/docker-entrypoint-initdb.d/`

---

### Q: How do I run commands as root in a vendor container?

**A:** Switch users temporarily, then switch back.

**In Dockerfile:**
```dockerfile
FROM splunk/splunk:latest

# Switch to root for installations
USER root
RUN microdnf install -y git vim sudo && microdnf clean all

# ALWAYS switch back to vendor user
USER splunk
```

**In postStartCommand:**
```json
{
  "postStartCommand": "sudo chown -R splunk:splunk /opt/splunk/var || true"
}
```

**⚠️ Important:**
- Always switch back to vendor user
- Don't run application as root (security risk)
- Use `sudo` for specific commands only

---

### Q: My DevContainer rebuilds slowly. How can I speed it up?

**A:** Optimize Dockerfile layer caching and use multi-stage builds sparingly.

**Layer Caching Tips:**

```dockerfile
FROM vendor/image:latest

# ✅ GOOD: Put rarely-changing installs first
USER root
RUN microdnf install -y git vim wget net-tools sudo && microdnf clean all

# ✅ GOOD: Separate frequently-changing steps
RUN mkdir -p /opt/app
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# ❌ BAD: Combines changing and stable steps
# RUN mkdir -p /opt/app && \
#     pip install -r /tmp/requirements.txt && \
#     microdnf install -y git vim
```

**Use `postCreateCommand` for Development Tools:**
```json
{
  "postCreateCommand": "pip install --user black pylint pytest"
}
```

**Benefits:**
- Runs after container created (not during build)
- Doesn't invalidate Docker layer cache
- Faster iteration

---

## Best Practices Questions

### Q: What's the recommended DevContainer structure?

**A:**

```
project/
├── .devcontainer/
│   ├── devcontainer.json       # Main configuration
│   ├── Dockerfile              # Custom image (if needed)
│   └── docker-compose.yml      # Multi-container (optional)
├── .ops/
│   └── <vendor>.cfg            # Vendor-specific configs
├── .env.example                # Secret template (version-controlled)
├── .env                        # Actual secrets (in .gitignore)
└── .gitignore                  # Must include .env
```

**devcontainer.json template:**
```json
{
  "name": "project-name",
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "workspaceFolder": "/workspace",
  "mounts": [
    "source=${localWorkspaceFolder}/.ops/<config>,target=<vendor-config-path>,type=bind",
    "source=<project>-data,target=<vendor-data-path>,type=volume"
  ],
  "containerEnv": {
    "SECRET": "${localEnv:SECRET:default}"
  },
  "postStartCommand": "chown -R user:group <data-path> || true",
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python"]
    }
  }
}
```

---

### Q: How do I validate my DevContainer setup?

**A:** Use this checklist:

```bash
# 1. Container Health
docker ps | grep <container-name>                    # Running?
docker inspect --format='{{.RestartCount}}' <name>  # Not restarting?

# 2. Vendor Initialization
docker logs <container> 2>&1 | grep -i "ready\|complete\|initialization"

# 3. User & Permissions
docker exec <container> whoami                       # Correct user?
docker exec <container> sudo -l                      # Sudo works?
docker exec <container> ls -la /workspace            # Workspace readable?

# 4. Mounts & Volumes
docker inspect <container> | jq '.[0].Mounts'        # Volumes mounted?
docker exec <container> ls -la <bind-mount-path>     # Bind mounts accessible?

# 5. Ports & Network
docker port <container>                              # Ports forwarded?
curl -I http://localhost:<port>                      # Service responding?

# 6. Application Health
docker exec <container> <vendor-command> status      # Service running?
docker exec <container> <vendor-command> --version   # Tools available?
```

**Automated Verification Script:**

Create `.devcontainer/verify-setup.sh` (see SA-SEC-eMASS example).

---

## See Also

- [DevContainer Debugging Patterns](DEVCONTAINER-DEBUGGING-PATTERNS.md)
- [DevContainer Vendor Image Workflow](DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md)
- [DevContainer Case Study: Splunk](DEVCONTAINER-CASE-STUDY-SPLUNK.md)
- [AI Agent Safety Policies](../policies/agent-safety-policies.md)

---

**Built for developers and AI agents working with vendor-based DevContainers.**
