# Devcontainer Templates - Vendor Image Patterns

This directory contains reusable devcontainer templates that emphasize **using existing vendor images** to reduce build time and token usage.

## Available Templates

### 1. `vendor-image-generator.json`
**Use when:** Your project needs to generate code from specifications (OpenAPI, gRPC, GraphQL, etc.)

**Features:**
- Uses vendor image with pre-installed generator tools
- Mounts specification files read-only
- Runs generation on container startup
- Outputs artifacts to configurable directory

**Example vendors:**
- `openapitools/openapi-generator-cli` - OpenAPI/Swagger code generation
- `swaggerapi/swagger-codegen-cli` - Alternative Swagger generator
- `bufbuild/buf` - Protocol Buffers/gRPC
- `asyncapi/generator` - AsyncAPI code generation

### 2. `vendor-image-base.json`
**Use when:** Standard development environment without code generation

**Features:**
- Uses official Microsoft/GitHub devcontainer base images
- Adds tools via features (not custom builds)
- Auto-detects and installs dependencies
- Includes common development tools

**Example base images:**
- `mcr.microsoft.com/devcontainers/python:3.11`
- `mcr.microsoft.com/devcontainers/javascript-node:20`
- `mcr.microsoft.com/devcontainers/go:1.21`
- `mcr.microsoft.com/devcontainers/typescript-node:20`

## Quick Start

### Step 1: Choose Template
```bash
# For code generation workflows
cp templates/.devcontainer/vendor-image-generator.json .devcontainer/devcontainer.json

# For standard development
cp templates/.devcontainer/vendor-image-base.json .devcontainer/devcontainer.json
```

### Step 2: Replace Placeholders

Open `.devcontainer/devcontainer.json` and replace all `{{PLACEHOLDER}}` values:

| Placeholder | Example | Description |
|-------------|---------|-------------|
| `{{PROJECT_NAME}}` | `my-api-client` | Your project name |
| `{{VENDOR_IMAGE}}` | `openapitools/openapi-generator-cli:v7.2.0` | Generator image |
| `{{BASE_IMAGE}}` | `mcr.microsoft.com/devcontainers/python:3.11` | Base dev image |
| `{{DIGEST}}` | See below | SHA256 image digest |
| `{{SPEC_FILE}}` | `openapi.yaml` | Specification file path |
| `{{CONFIG_FILE}}` | `generator-config.yaml` | Generator config path |
| `{{LANGUAGES}}` | `python,typescript` | Target languages |
| `{{OUT_DIR}}` | `generated/` | Output directory |

### Step 3: Get Image Digest

Pin your image by digest for reproducibility:

```bash
# Method 1: Using docker pull
docker pull openapitools/openapi-generator-cli:v7.2.0 --platform linux/amd64
docker inspect openapitools/openapi-generator-cli:v7.2.0 --format='{{.RepoDigests}}'

# Method 2: Using crane (recommended)
crane digest openapitools/openapi-generator-cli:v7.2.0

# Method 3: Using docker buildx
docker buildx imagetools inspect openapitools/openapi-generator-cli:v7.2.0 --format '{{json .Manifest.Digest}}'
```

Replace `{{DIGEST}}` with the returned SHA256 hash (e.g., `sha256:abc123...`).

### Step 4: Customize Generation Command

For `vendor-image-generator.json`, update `postCreateCommand` based on your generator:

#### OpenAPI Generator
```json
"postCreateCommand": "openapi-generator-cli generate -i {{SPEC_FILE}} -g python -o {{OUT_DIR}}/python -c {{CONFIG_FILE}}"
```

#### Buf (Protocol Buffers)
```json
"postCreateCommand": "buf generate --template {{CONFIG_FILE}} --output {{OUT_DIR}}"
```

#### AsyncAPI Generator
```json
"postCreateCommand": "ag {{SPEC_FILE}} @asyncapi/nodejs-template -o {{OUT_DIR}}"
```

### Step 5: Test Devcontainer

```bash
# Open in VS Code
code .

# Rebuild devcontainer
# Cmd/Ctrl + Shift + P -> "Dev Containers: Rebuild Container"
```

## Benefits Over Custom Builds

### Time Savings
| Approach | First Build | Subsequent Builds | Total Time (10 rebuilds) |
|----------|-------------|-------------------|--------------------------|
| Custom Dockerfile | 8-12 min | 2-5 min | ~40-70 min |
| Vendor Image | 1-3 min | 10-30 sec | ~5-10 min |

### Token Usage Savings
| Operation | Custom Build | Vendor Image | Savings |
|-----------|--------------|--------------|---------|
| Per rebuild | ~425 tokens | ~15 tokens | 96% |
| 10 rebuilds | ~4,250 tokens | ~150 tokens | 96% |

### Additional Benefits
- ✅ Security patches from vendor
- ✅ Consistent across team
- ✅ Faster onboarding
- ✅ Reproducible builds
- ✅ Less maintenance

## Common Use Cases

### OpenAPI/REST API Clients
```json
{
  "image": "openapitools/openapi-generator-cli:v7.2.0@sha256:{{DIGEST}}",
  "mounts": ["source=openapi.yaml,target=/spec.yaml,type=bind,readonly"],
  "postCreateCommand": "openapi-generator-cli generate -i /spec.yaml -g python -o /workspace/client"
}
```

### gRPC Services
```json
{
  "image": "bufbuild/buf:1.28.1@sha256:{{DIGEST}}",
  "mounts": ["source=buf.yaml,target=/workspace/buf.yaml,type=bind"],
  "postCreateCommand": "buf generate"
}
```

### GraphQL Clients
```json
{
  "image": "mcr.microsoft.com/devcontainers/javascript-node:20@sha256:{{DIGEST}}",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {"version": "20"}
  },
  "postCreateCommand": "npm install && npm run codegen"
}
```

### Python Data Science
```json
{
  "image": "mcr.microsoft.com/devcontainers/python:3.11@sha256:{{DIGEST}}",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {"version": "3.11"}
  },
  "postCreateCommand": "pip install -r requirements.txt"
}
```

## Troubleshooting

### "Image not found" error
- Verify image name and tag are correct
- Check if you need authentication for private registries
- Try pulling manually: `docker pull {{VENDOR_IMAGE}}`

### Digest mismatch
- Image was updated by vendor
- Get new digest: `crane digest {{VENDOR_IMAGE}}:{{TAG}}`
- Update devcontainer.json with new digest

### Generation command fails
- Check if mounts are correct
- Verify specification file syntax
- Run command manually in container: `docker run -it {{VENDOR_IMAGE}} /bin/bash`

### Missing tools
- Add via `postCreateCommand`: `apt-get update && apt-get install -y {{TOOL}}`
- Or use devcontainer features
- Consider if a different vendor image includes the tool

## Best Practices Checklist

- [ ] Use vendor image instead of custom Dockerfile
- [ ] Pin image by SHA256 digest
- [ ] Mount specifications as read-only
- [ ] Document why specific vendor image was chosen
- [ ] Use devcontainer features for additional tools
- [ ] Configure `.dockerignore` to exclude unnecessary files
- [ ] Test devcontainer build on fresh clone
- [ ] Document required environment variables
- [ ] Include `postCreateCommand` for dependency installation
- [ ] Set up appropriate VS Code extensions

## Related Documentation

- [Devcontainer Vendor Image Workflow](../docs/DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md) - Full workflow documentation
- [Token Accountability Policy](../policies/token-accountability-policy.md) - Token usage governance
- [AI Project Evaluation](../policies/schemas/ai-project-evaluation.json) - Project quality criteria

## Governance Alignment

This template pattern supports the AI Agent Governance Framework by:

1. **Reducing waste** - Minimizes token usage on repetitive builds
2. **Improving auditability** - Pinned digests provide reproducible environments
3. **Enhancing security** - Vendor images receive regular security updates
4. **Accelerating delivery** - Faster setup means faster time-to-value

## Need Help?

If you're unsure which template to use or how to configure it:

1. Review the [decision flow diagram](../docs/DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md#decision-flow)
2. Check if your use case matches a [common example](#common-use-cases)
3. Consult the [troubleshooting guide](#troubleshooting)
4. Open an issue with the `devcontainer` label

---

**Remember:** Always prefer vendor images over custom builds. Your future self (and your token budget) will thank you!
