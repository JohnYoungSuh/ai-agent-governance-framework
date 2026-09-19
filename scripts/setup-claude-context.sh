#!/bin/bash

# Setup Multi-Assistant AI Governance Context (.agents/, .cursorrules, .claude/)
# Usage: ./setup-claude-context.sh [project-path]

set -e

PROJECT_PATH="${1:-.}"
AGENTS_DIR="${PROJECT_PATH}/.agents"
RULES_DIR="${AGENTS_DIR}/rules"
SKILLS_DIR="${AGENTS_DIR}/skills"
CLAUDE_DIR="${PROJECT_PATH}/.claude"

echo "Setting up Multi-Assistant AI Governance context for: ${PROJECT_PATH}"

# Create directories
mkdir -p "${RULES_DIR}"
mkdir -p "${SKILLS_DIR}"
mkdir -p "${CLAUDE_DIR}"

# Copy template if project-context.md doesn't exist
if [ ! -f "${RULES_DIR}/project-context.md" ]; then
    TEMPLATE_SOURCE="$(dirname "$0")/../.agents/rules/template-project-context.md"
    if [ -f "${TEMPLATE_SOURCE}" ]; then
        cp "${TEMPLATE_SOURCE}" "${RULES_DIR}/project-context.md"
        echo "✓ Created ${RULES_DIR}/project-context.md from template"
        echo "  → Edit this file to customize your project context"
    else
        cat > "${RULES_DIR}/project-context.md" << 'EOF'
# Project Context

## Project Overview
[Add your project description here]

## Tech Stack
- Language: [e.g., Python, TypeScript]
- Framework: [e.g., FastAPI, React]
- Infrastructure: [e.g., AWS, Kubernetes]

## Key File Paths
- Main entry: [path]
- Config: [path]
- Tests: [path]

## Development Workflow
- Setup: [command]
- Run: [command]
- Test: [command]
- Build: [command]

## Common Tasks
[List common development tasks]

## Governance
- Code style: [standards]
- Testing: [requirements]
- Review process: [workflow]
EOF
        echo "✓ Created ${RULES_DIR}/project-context.md with basic template"
        echo "  → Edit this file to add your project details"
    fi
else
    echo "✓ ${RULES_DIR}/project-context.md already exists"
fi

# Create .cursorrules adapter if it doesn't exist
if [ ! -f "${PROJECT_PATH}/.cursorrules" ]; then
    cat > "${PROJECT_PATH}/.cursorrules" << 'EOF'
# Cursor Rules — AI Agent Governance Framework
# Canonical governance rules reside in .agents/rules/
# See .agents/rules/project-context.md for project overview and agent constraints.
EOF
    echo "✓ Created ${PROJECT_PATH}/.cursorrules adapter"
fi

# Create settings.local.json with include if it doesn't exist
if [ ! -f "${CLAUDE_DIR}/settings.local.json" ]; then
    cat > "${CLAUDE_DIR}/settings.local.json" << 'EOF'
{
  "include": [
    ".agents/rules/*"
  ],
  "permissions": {
    "allow": [],
    "deny": [],
    "ask": []
  }
}
EOF
    echo "✓ Created ${CLAUDE_DIR}/settings.local.json importing .agents/rules/*"
else
    echo "✓ ${CLAUDE_DIR}/settings.local.json already exists"
fi

echo ""
echo "✅ Multi-Assistant context setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit ${RULES_DIR}/project-context.md to describe your project"
echo "2. Add project-specific rules to ${RULES_DIR}/"
echo "3. Add project-specific skills to ${SKILLS_DIR}/"
echo ""
echo "Multi-Assistant Support:"
echo "- Antigravity IDE / Gemini: reads .agents/rules/ and .agents/skills/ natively"
echo "- Cursor: reads .cursorrules"
echo "- Claude Code: loads .agents/rules/* via .claude/settings.local.json"
echo ""
