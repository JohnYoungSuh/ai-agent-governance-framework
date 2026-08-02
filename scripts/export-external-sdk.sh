#!/usr/bin/env bash
# ==============================================================================
# AI Agent Governance Framework — External SDK Exporter
# ==============================================================================
# Purpose: Safely exports proven framework components to an external release
#          directory while stripping unproven conceptual IP, trade secrets, and
#          pre-patent disclosures.
#
# Rule Enforcement:
# - PROVEN → EXTERNAL (Schemas, GPIS PDP, Helm charts, OCSF SIEM emitter, tests)
# - CONCEPTUAL / UNPROVEN → INTERNAL (Game theory algorithms, distillation prompts, patent applications)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGET_DIR="${1:-${ROOT_DIR}/dist/ai-agent-governance-framework-external}"

echo "======================================================================"
echo "🚀 AI Agent Governance Framework — IP Boundary Exporter"
echo "======================================================================"
echo "Source: ${ROOT_DIR}"
echo "Target: ${TARGET_DIR}"
echo "----------------------------------------------------------------------"

# 1. Clean & Prepare Target Directory
if [ -d "${TARGET_DIR}" ]; then
  echo "🧹 Cleaning previous export target directory..."
  rm -rf "${TARGET_DIR}"
fi
mkdir -p "${TARGET_DIR}"

# 2. Export Proven Core Framework Layers
echo "📦 Exporting Proven Core Framework Layers..."

mkdir -p "${TARGET_DIR}/app"
cp -r "${ROOT_DIR}/app/"* "${TARGET_DIR}/app/"

mkdir -p "${TARGET_DIR}/deploy"
cp -r "${ROOT_DIR}/deploy/"* "${TARGET_DIR}/deploy/"

mkdir -p "${TARGET_DIR}/policies"
cp -r "${ROOT_DIR}/policies/"* "${TARGET_DIR}/policies/"

mkdir -p "${TARGET_DIR}/agents"
cp -r "${ROOT_DIR}/agents/"* "${TARGET_DIR}/agents/"

mkdir -p "${TARGET_DIR}/compliance"
cp -r "${ROOT_DIR}/compliance/"* "${TARGET_DIR}/compliance/"

mkdir -p "${TARGET_DIR}/tests"
cp -r "${ROOT_DIR}/tests/"* "${TARGET_DIR}/tests/"

mkdir -p "${TARGET_DIR}/config"
cp -r "${ROOT_DIR}/config/"* "${TARGET_DIR}/config/"

# 3. Export Public Documentation & Base Metadata
echo "📄 Exporting Proven Documentation & Metadata..."
for file in README.md CHANGELOG.md LICENSE CONTRIBUTING.md CODEMAP.md SESSION_START.md requirements.txt; do
  if [ -f "${ROOT_DIR}/${file}" ]; then
    cp "${ROOT_DIR}/${file}" "${TARGET_DIR}/"
  fi
done

# Export non-confidential docs
mkdir -p "${TARGET_DIR}/docs"
for doc in TOKEN-EFFICIENT-IMPLEMENTATION.md GOVERNANCE-AGENT-ARCHITECTURE.md AI-GATEKEEPER-SYSTEM.md CMDB-ARCHITECTURE.md QUICK-REFERENCE.md; do
  if [ -f "${ROOT_DIR}/docs/${doc}" ]; then
    cp "${ROOT_DIR}/docs/${doc}" "${TARGET_DIR}/docs/"
  fi
done

# 4. Export Proven Automation Scripts (Excluding Trade Secrets)
echo "🛠️ Exporting Proven Automation Scripts..."
mkdir -p "${TARGET_DIR}/scripts"

PROVEN_SCRIPTS=(
  "governance_router.py"
  "otel-siem-emitter.py"
  "qa-agent.py"
  "benchmark_token_savings.py"
  "compliance-check-enhanced.sh"
  "test-siem-emitter.sh"
  "identity-bootstrap.sh"
  "validate-manifest.py"
  "validate-jira-approval.py"
  "jira-webhook-receiver.py"
  "kill-switch-validator.py"
  "shared_utils.py"
  "setup-agent.sh"
  "get-image-digest.sh"
  "deploy-agents.sh"
  "deploy-monitoring.sh"
  "requirements-otel.txt"
)

for script in "${PROVEN_SCRIPTS[@]}"; do
  if [ -f "${ROOT_DIR}/scripts/${script}" ]; then
    cp "${ROOT_DIR}/scripts/${script}" "${TARGET_DIR}/scripts/"
  fi
done

# Copy prompts directory (excluding distillation prompt trade secret)
if [ -d "${ROOT_DIR}/scripts/prompts" ]; then
  mkdir -p "${TARGET_DIR}/scripts/prompts"
  cp "${ROOT_DIR}/scripts/prompts/cache_classifier.txt" "${TARGET_DIR}/scripts/prompts/" 2>/dev/null || true
  cp "${ROOT_DIR}/scripts/prompts/intent_router.txt" "${TARGET_DIR}/scripts/prompts/" 2>/dev/null || true
fi

# 5. STRIP & EXCLUDE INTERNAL TRADE SECRETS / UNPROVEN CONCEPTUAL IP
echo "🔒 Stripping Trade Secrets & Pre-Patent Disclosures..."

STRIPPED_ITEMS=(
  "${TARGET_DIR}/scripts/game_theory"
  "${TARGET_DIR}/scripts/prompts/distillation.txt"
  "${TARGET_DIR}/docs/US-PATENT-APPLICATION.md"
  "${TARGET_DIR}/docs/PATENT-DISCLOSURE.md"
  "${TARGET_DIR}/NEXT_RELEASE_TODO.md"
  "${TARGET_DIR}/LESSONS_LEARNED.md"
  "${TARGET_DIR}/.agents"
  "${TARGET_DIR}/.claude"
  "${TARGET_DIR}/UNIFIED-AI-AGENT-GOVERNANCE-FRAMEWORK-v3.0.md"
)

for item in "${STRIPPED_ITEMS[@]}"; do
  if [ -e "${item}" ]; then
    rm -rf "${item}"
    echo "  - Removed trade secret / internal item: $(basename "${item}")"
  fi
done

# Remove temporary python cache and test artifacts
find "${TARGET_DIR}" -type d -name "__pycache__" -exec rm -rf {} +
find "${TARGET_DIR}" -type d -name ".pytest_cache" -exec rm -rf {} +
find "${TARGET_DIR}" -type d -name ".mypy_cache" -exec rm -rf {} +
find "${TARGET_DIR}" -type d -name ".ruff_cache" -exec rm -rf {} +
find "${TARGET_DIR}" -type f -name "*.pyc" -delete

# 6. Security Audit Scan on Exported Bundle
echo "🔍 Running Pre-Release Security Audit on Exported Directory..."

SECRET_PATTERNS=(
  "suhlabs-super-secret-governance-key"
  "AKIA[0-9A-Z]{16}"
  "eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"
  "ghp_[A-Za-z0-9]{36}"
)

FOUND_SECRETS=0
for pattern in "${SECRET_PATTERNS[@]}"; do
  if grep -rE "${pattern}" "${TARGET_DIR}" --exclude="*.sh" > /dev/null 2>&1; then
    echo "❌ SECURITY WARNING: Potential secret matched pattern '${pattern}' in exported bundle!"
    FOUND_SECRETS=$((FOUND_SECRETS + 1))
  fi
done

if [ ${FOUND_SECRETS} -eq 0 ]; then
  echo "✅ Security Check Passed: Zero raw secrets or sensitive patterns detected."
else
  echo "⚠️ Security Check Warning: ${FOUND_SECRETS} potential secret matches found. Please review exported directory."
fi

# 7. Final Summary Report
echo "======================================================================"
echo "🎉 Export Complete!"
echo "======================================================================"
echo "External SDK Path : ${TARGET_DIR}"
echo "Exported Files    : $(find "${TARGET_DIR}" -type f | wc -l) files"
echo "Exported Size     : $(du -sh "${TARGET_DIR}" | cut -f1)"
echo "----------------------------------------------------------------------"
echo "🔒 Stripped Trade Secrets / Unproven Conceptual IP:"
echo "   • scripts/game_theory/ (Unproven cooperative Pareto algorithms)"
echo "   • scripts/prompts/distillation.txt (Proprietary pattern distillation prompt)"
echo "   • docs/US-PATENT-APPLICATION.md & PATENT-DISCLOSURE.md (Pre-patent drafts)"
echo "   • Internal backlog & session logs (NEXT_RELEASE_TODO.md, LESSONS_LEARNED.md)"
echo "======================================================================"
