# Devcontainer Vendor Image Pattern - Quick Start Guide

## Why This Matters

Using **existing vendor Docker images** instead of custom builds in your devcontainer setup saves:

- ⚡ **85% build time** (1-3 min vs 8-12 min)
- 💰 **96% token usage** (~15 vs ~425 tokens per rebuild)
- 🔒 **Security** (vendor images receive regular patches)
- 📈 **Consistency** (digest pinning ensures reproducibility)

**Annual savings per developer:** ~$410 (based on 100 rebuilds/year)

## Quick Decision Tree

```
Do you need to generate code from specs? (OpenAPI, gRPC, GraphQL, etc.)
│
├─ YES → Use generator vendor image
│         Examples: openapitools/openapi-generator-cli, bufbuild/buf
│         Template: templates/.devcontainer/vendor-image-generator.json
│
└─ NO  → Use base development image
          Examples: mcr.microsoft.com/devcontainers/python:3.11
          Template: templates/.devcontainer/vendor-image-base.json
```

## 5-Minute Setup

### Step 1: Copy Template

```bash
# For code generation (OpenAPI, gRPC, etc.)
cp templates/.devcontainer/vendor-image-generator.json .devcontainer/devcontainer.json

# For standard development
cp templates/.devcontainer/vendor-image-base.json .devcontainer/devcontainer.json
```

### Step 2: Choose Your Image

**Common vendor images:**

| Use Case | Vendor Image | Purpose |
|----------|-------------|---------|
| OpenAPI/REST | `openapitools/openapi-generator-cli:v7.2.0` | Generate API clients |
| gRPC/Protobuf | `bufbuild/buf:1.28.1` | Generate gRPC code |
| Python | `mcr.microsoft.com/devcontainers/python:3.11` | Python development |
| Node.js | `mcr.microsoft.com/devcontainers/javascript-node:20` | JavaScript/TypeScript |
| Go | `mcr.microsoft.com/devcontainers/go:1.21` | Go development |

### Step 3: Get Digest

```bash
# Use the helper script
./scripts/get-image-digest.sh openapitools/openapi-generator-cli:v7.2.0

# Output shows digest and devcontainer snippet
```

### Step 4: Update devcontainer.json

Replace placeholders in `.devcontainer/devcontainer.json`:

```json
{
  "name": "my-api-client",
  "image": "openapitools/openapi-generator-cli:v7.2.0@sha256:abc123...",
  // ... rest of config
}
```

### Step 5: Open in VS Code

```bash
code .
# Then: Cmd/Ctrl + Shift + P → "Dev Containers: Rebuild Container"
```

## Common Scenarios

### Scenario 1: OpenAPI Code Generation

```json
{
  "name": "My API Client",
  "image": "openapitools/openapi-generator-cli:v7.2.0@sha256:{{DIGEST}}",
  "mounts": [
    "source=openapi.yaml,target=/workspace/spec.yaml,type=bind,readonly"
  ],
  "postCreateCommand": "openapi-generator-cli generate -i spec.yaml -g python -o generated/"
}
```

**Get digest:** `./scripts/get-image-digest.sh openapitools/openapi-generator-cli:v7.2.0`

### Scenario 2: Python Development

```json
{
  "name": "Python Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.11@sha256:{{DIGEST}}",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install -r requirements.txt"
}
```

**Get digest:** `./scripts/get-image-digest.sh mcr.microsoft.com/devcontainers/python:3.11`

### Scenario 3: gRPC with Buf

```json
{
  "name": "gRPC Service",
  "image": "bufbuild/buf:1.28.1@sha256:{{DIGEST}}",
  "mounts": [
    "source=buf.yaml,target=/workspace/buf.yaml,type=bind"
  ],
  "postCreateCommand": "buf generate"
}
```

**Get digest:** `./scripts/get-image-digest.sh bufbuild/buf:1.28.1`

## What NOT to Do

### ❌ Bad: Custom Dockerfile Build

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  }
}
```

**Why avoid:**
- 8-12 minute builds
- ~425 tokens per rebuild
- Maintenance burden
- Inconsistent across team

### ✅ Good: Vendor Image

```json
{
  "image": "mcr.microsoft.com/devcontainers/python:3.11@sha256:abc123..."
}
```

**Benefits:**
- 1-3 minute setup
- ~15 tokens per rebuild
- Vendor maintains image
- Consistent everywhere

## Troubleshooting

### "Image not found"

```bash
# Verify image exists
docker pull openapitools/openapi-generator-cli:v7.2.0
```

### Digest mismatch

```bash
# Get fresh digest
./scripts/get-image-digest.sh openapitools/openapi-generator-cli:v7.2.0
```

### Missing tools

Add via `postCreateCommand` or use features:

```json
{
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  }
}
```

## Governance Compliance

This pattern is **required** for all projects in the AI Agent Governance Framework:

✅ **Approved by default** - Projects using vendor images with pinned digests
⚠️ **Requires justification** - Custom Dockerfiles need written explanation
❌ **Blocked** - Unpinned images or unnecessary custom builds

See: [docs/DEVCONTAINER-GOVERNANCE-INTEGRATION.md](DEVCONTAINER-GOVERNANCE-INTEGRATION.md)

## Need Help?

| Resource | Link |
|----------|------|
| **Full Workflow Guide** | [DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md](DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md) |
| **Governance Integration** | [DEVCONTAINER-GOVERNANCE-INTEGRATION.md](DEVCONTAINER-GOVERNANCE-INTEGRATION.md) |
| **Template README** | [templates/.devcontainer/README.md](../templates/.devcontainer/README.md) |
| **Helper Script** | `./scripts/get-image-digest.sh --help` |
| **Governance Policy** | [GOVERNANCE-POLICY.md](GOVERNANCE-POLICY.md) |

## Checklist

Before submitting a PR with devcontainer changes:

- [ ] Using vendor image (not custom Dockerfile)
- [ ] Image pinned by SHA256 digest
- [ ] Digest retrieved using `./scripts/get-image-digest.sh`
- [ ] Specifications mounted as read-only
- [ ] Project name placeholder replaced
- [ ] Tested: "Rebuild Container" works
- [ ] Documented: Why this vendor image was chosen

## Examples by Framework

### OpenAPI/Swagger
```bash
cp templates/.devcontainer/vendor-image-generator.json .devcontainer/devcontainer.json
# Edit: Use openapitools/openapi-generator-cli
./scripts/get-image-digest.sh openapitools/openapi-generator-cli:v7.2.0
```

### GraphQL
```bash
cp templates/.devcontainer/vendor-image-base.json .devcontainer/devcontainer.json
# Edit: Use mcr.microsoft.com/devcontainers/javascript-node:20
./scripts/get-image-digest.sh mcr.microsoft.com/devcontainers/javascript-node:20
```

### gRPC/Protocol Buffers
```bash
cp templates/.devcontainer/vendor-image-generator.json .devcontainer/devcontainer.json
# Edit: Use bufbuild/buf
./scripts/get-image-digest.sh bufbuild/buf:1.28.1
```

### Python Data Science
```bash
cp templates/.devcontainer/vendor-image-base.json .devcontainer/devcontainer.json
# Edit: Use mcr.microsoft.com/devcontainers/python:3.11
./scripts/get-image-digest.sh mcr.microsoft.com/devcontainers/python:3.11
```

## Remember

**Vendor images are:**
- ✅ Faster to set up
- ✅ Cheaper to run (96% token savings)
- ✅ More secure (regular vendor updates)
- ✅ Easier to maintain
- ✅ Required by governance policy

**Custom builds are:**
- ❌ Slow to build (8-12 min)
- ❌ Expensive (~425 tokens/rebuild)
- ❌ Hard to maintain
- ❌ Inconsistent across team
- ❌ Require special approval

---

**Quick action:** Copy a template, get a digest, open in VS Code. Done in 5 minutes!

```bash
# One-liner for Python projects
cp templates/.devcontainer/vendor-image-base.json .devcontainer/devcontainer.json && \
./scripts/get-image-digest.sh mcr.microsoft.com/devcontainers/python:3.11
```
