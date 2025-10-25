# Devcontainer Vendor Image Workflow Pattern

## Overview

This workflow pattern emphasizes **reusing existing vendor or published Docker images** in VS Code devcontainer configurations. By preferring pre-built, trusted images over custom builds, projects achieve:

- ⚡ **Faster onboarding** - Pull instead of build
- 💰 **Reduced token usage** - Avoid authentication overhead
- 🔒 **Better security** - Use verified vendor images
- 🔄 **Consistency** - Pin images by digest for reproducibility

## Decision Flow

```mermaid
graph TD
    Start([{{PROJECT_NAME}}]) --> Decision{Need to generate<br/>artifacts from spec?}

    Decision -->|Yes| UseVendor[Use vendor image:<br/>'{{VENDOR_IMAGE}}']
    Decision -->|No| UseBase[Use base image:<br/>'{{BASE_IMAGE}}']

    UseVendor --> Mount[Mount configuration:<br/>- {{SPEC_FILE}}<br/>- {{CONFIG_FILE}}]
    Mount --> Generate[Run generator on startup]
    Generate --> Output[Generate outputs for:<br/>{{LANGUAGES}}]
    Output --> Write[Write results to:<br/>{{OUT_DIR}}]

    UseBase --> Converge[Artifacts ready]
    Write --> Converge

    Converge --> Use[Use in application]
    Use --> Examples[Examples:<br/>CLI | SDK | API | Addon]

    style Start fill:#e1f5ff
    style UseVendor fill:#c8e6c9
    style UseBase fill:#fff9c4
    style Converge fill:#f8bbd0
```

## Workflow Pattern

### Step 1: Identify Image Needs

**Decision Point:** Does your project need to generate code/artifacts from specifications?

#### Path A: Generation Required (Use Vendor Image)
```yaml
# Use vendor image with generation tools
image: "{{VENDOR_IMAGE}}@sha256:{{DIGEST}}"

# Example placeholders:
# - openapitools/openapi-generator-cli
# - swaggerapi/swagger-codegen-cli
# - asyncapi/generator
# - buf.build/bufbuild/buf
```

#### Path B: Simple Development (Use Base Image)
```yaml
# Use lightweight base image
image: "{{BASE_IMAGE}}@sha256:{{DIGEST}}"

# Example placeholders:
# - mcr.microsoft.com/devcontainers/python
# - mcr.microsoft.com/devcontainers/javascript-node
# - mcr.microsoft.com/devcontainers/go
```

### Step 2: Mount Required Files

For generation workflows, mount specifications and configurations:

```json
{
  "mounts": [
    "source={{SPEC_FILE}},target=/workspace/{{SPEC_FILE}},type=bind",
    "source={{CONFIG_FILE}},target=/workspace/{{CONFIG_FILE}},type=bind"
  ]
}
```

### Step 3: Configure Startup Commands

Run generators on container startup:

```json
{
  "postCreateCommand": "generate-artifacts --spec {{SPEC_FILE}} --config {{CONFIG_FILE}} --languages {{LANGUAGES}} --output {{OUT_DIR}}"
}
```

### Step 4: Use Generated Artifacts

The generated code is now available in `{{OUT_DIR}}` for:
- CLI tools
- SDK libraries
- API clients
- IDE addons
- Application code

## Complete Example Template

### devcontainer.json (Generation Workflow)

```json
{
  "name": "{{PROJECT_NAME}} - Generator",

  // ✅ PREFER: Use existing vendor image
  "image": "{{VENDOR_IMAGE}}@sha256:{{DIGEST}}",

  // ❌ AVOID: Building custom images unnecessarily
  // "build": {
  //   "dockerfile": "Dockerfile"
  // },

  "mounts": [
    "source={{SPEC_FILE}},target=/workspace/{{SPEC_FILE}},type=bind,readonly",
    "source={{CONFIG_FILE}},target=/workspace/{{CONFIG_FILE}},type=bind,readonly"
  ],

  "postCreateCommand": "bash -c 'generator --input {{SPEC_FILE}} --config {{CONFIG_FILE}} --languages {{LANGUAGES}} --output {{OUT_DIR}}'",

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-vscode.vscode-json-languageservice"
      ]
    }
  },

  "forwardPorts": [8080],

  "remoteUser": "vscode"
}
```

### devcontainer.json (Base Workflow)

```json
{
  "name": "{{PROJECT_NAME}} - Development",

  // ✅ PREFER: Use official base images
  "image": "{{BASE_IMAGE}}@sha256:{{DIGEST}}",

  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },

  "postCreateCommand": "npm install",

  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint"
      ]
    }
  },

  "remoteUser": "vscode"
}
```

## Best Practices

### 1. Pin Images by Digest

✅ **Good:**
```json
"image": "mcr.microsoft.com/devcontainers/python:3.11@sha256:abc123..."
```

❌ **Avoid:**
```json
"image": "python:latest"
```

### 2. Use Official/Vendor Registries

**Trusted Sources:**
- Microsoft Container Registry: `mcr.microsoft.com/devcontainers/*`
- GitHub Container Registry: `ghcr.io/*`
- Docker Hub verified: `docker.io/library/*`
- Vendor-specific: `openapitools/*`, `swaggerapi/*`, etc.

### 3. Prefer Features Over Custom Builds

```json
{
  "image": "{{BASE_IMAGE}}",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},
    "ghcr.io/devcontainers/features/python:1": {}
  }
}
```

### 4. Document Image Selection

```json
{
  "// Image Selection": [
    "Using {{VENDOR_IMAGE}} because:",
    "- Pre-installed {{TOOL_NAME}} generator",
    "- Maintained by {{VENDOR}}",
    "- Updated monthly with security patches",
    "- Avoids 5-10 minute custom build time"
  ],
  "image": "{{VENDOR_IMAGE}}@sha256:{{DIGEST}}"
}
```

## Token Usage Considerations

### Scenario: Custom Build
```bash
# Every devcontainer rebuild:
- Authentication to registries: ~50 tokens
- Build context upload: ~100 tokens
- Layer caching checks: ~75 tokens
- Build log parsing: ~200 tokens
Total per rebuild: ~425 tokens
```

### Scenario: Vendor Image Pull
```bash
# Every devcontainer rebuild:
- Image pull (cached): ~10 tokens
- Container start: ~5 tokens
Total per rebuild: ~15 tokens
```

**Savings:** ~96% reduction in token usage per rebuild

## Common Placeholders Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Your project name | `my-api-client` |
| `{{VENDOR_IMAGE}}` | Vendor/generator image | `openapitools/openapi-generator-cli` |
| `{{BASE_IMAGE}}` | Base development image | `mcr.microsoft.com/devcontainers/python:3.11` |
| `{{SPEC_FILE}}` | Specification file | `openapi.yaml` |
| `{{CONFIG_FILE}}` | Generator config | `generator-config.yaml` |
| `{{LANGUAGES}}` | Target languages | `python,typescript,go` |
| `{{OUT_DIR}}` | Output directory | `generated/` |
| `{{DIGEST}}` | Image SHA256 digest | `sha256:abc123def456...` |

## Integration with AI Governance

This workflow pattern aligns with token accountability policies:

1. **Reduces waste** - Fewer tokens spent on repetitive builds
2. **Improves audit trail** - Pinned digests provide reproducibility
3. **Enhances security** - Vendor images undergo security scanning
4. **Accelerates onboarding** - New contributors get started faster

See also:
- [Token Accountability Policy](../policies/token-accountability-policy.md)
- [AI Project Evaluation Schema](../policies/schemas/ai-project-evaluation.json)

## Examples by Use Case

### OpenAPI Code Generation
```json
{
  "image": "openapitools/openapi-generator-cli:latest@sha256:{{DIGEST}}",
  "mounts": ["source=openapi.yaml,target=/workspace/spec.yaml,type=bind"],
  "postCreateCommand": "openapi-generator-cli generate -i spec.yaml -g python -o generated/"
}
```

### gRPC/Protobuf Development
```json
{
  "image": "bufbuild/buf:latest@sha256:{{DIGEST}}",
  "mounts": ["source=buf.yaml,target=/workspace/buf.yaml,type=bind"],
  "postCreateCommand": "buf generate"
}
```

### GraphQL Code Generation
```json
{
  "image": "node:20@sha256:{{DIGEST}}",
  "postCreateCommand": "npm install && npm run codegen",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {}
  }
}
```

## Troubleshooting

### Image Pull Failures
- Verify digest is current: `docker pull {{VENDOR_IMAGE}}:tag --platform linux/amd64`
- Check registry authentication
- Ensure network connectivity

### Missing Tools in Vendor Image
- Add via `postCreateCommand`: `apt-get update && apt-get install -y {{TOOL}}`
- Or use devcontainer features
- Document why custom installation is needed

### Performance Issues
- Check if image includes unnecessary tools
- Consider using slim/alpine variants
- Profile startup time with different images

---

**Remember:** Always prefer pulling existing vendor images over building custom ones. This saves time, tokens, and ensures consistency across the team.
