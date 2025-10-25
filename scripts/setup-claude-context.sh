#!/bin/bash

# Setup Claude Code auto-loading context for a new project
# Usage: ./setup-claude-context.sh [project-path]

set -e

PROJECT_PATH="${1:-.}"
CLAUDE_DIR="${PROJECT_PATH}/.claude"
PROMPTS_DIR="${CLAUDE_DIR}/prompts"
COMMANDS_DIR="${CLAUDE_DIR}/commands"

echo "Setting up Claude Code context for: ${PROJECT_PATH}"

# Create directories
mkdir -p "${PROMPTS_DIR}"
mkdir -p "${COMMANDS_DIR}"

# Copy template if project-context.md doesn't exist
if [ ! -f "${PROMPTS_DIR}/project-context.md" ]; then
    if [ -f "$(dirname "$0")/../.claude/prompts/template-project-context.md" ]; then
        cp "$(dirname "$0")/../.claude/prompts/template-project-context.md" \
           "${PROMPTS_DIR}/project-context.md"
        echo "✓ Created ${PROMPTS_DIR}/project-context.md from template"
        echo "  → Edit this file to customize your project context"
    else
        cat > "${PROMPTS_DIR}/project-context.md" << 'EOF'
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
        echo "✓ Created ${PROMPTS_DIR}/project-context.md with basic template"
        echo "  → Edit this file to add your project details"
    fi
else
    echo "✓ ${PROMPTS_DIR}/project-context.md already exists"
fi

# Create settings.local.json if it doesn't exist
if [ ! -f "${CLAUDE_DIR}/settings.local.json" ]; then
    cat > "${CLAUDE_DIR}/settings.local.json" << 'EOF'
{
  "permissions": {
    "allow": [],
    "deny": [],
    "ask": []
  }
}
EOF
    echo "✓ Created ${CLAUDE_DIR}/settings.local.json"
    echo "  → Add permission rules as needed"
else
    echo "✓ ${CLAUDE_DIR}/settings.local.json already exists"
fi

echo ""
echo "✅ Claude Code context setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit ${PROMPTS_DIR}/project-context.md to describe your project"
echo "2. (Optional) Add custom commands to ${COMMANDS_DIR}/"
echo "3. (Optional) Configure permissions in ${CLAUDE_DIR}/settings.local.json"
echo ""
echo "When you open this project in Claude Code, the context will load automatically!"
