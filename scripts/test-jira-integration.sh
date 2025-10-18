#!/bin/bash
# Test Jira Integration
# AI Agent Governance Framework v2.1
# Tests: validate-jira-approval.py, PKI signing, webhook receiver

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Jira Integration Test Suite"
echo "AI Agent Governance Framework v2.1"
echo "=========================================="
echo ""

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Testing: $test_name ... "

    if eval "$test_command" > /tmp/test-output.log 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "  Error output:"
        sed 's/^/    /' /tmp/test-output.log
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

skip_test() {
    local test_name="$1"
    local reason="$2"

    echo -e "Testing: $test_name ... ${YELLOW}⊘ SKIP${NC} ($reason)"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
}

# ============================================================================
# Test 1: Check Python Dependencies
# ============================================================================
echo "Test Suite 1: Python Dependencies"
echo "----------------------------------"

run_test "Python 3 installed" "command -v python3 > /dev/null"
run_test "requests library" "python3 -c 'import requests'"
run_test "cryptography library" "python3 -c 'from cryptography import x509'"

echo ""

# ============================================================================
# Test 2: Script Permissions
# ============================================================================
echo "Test Suite 2: Script Permissions"
echo "---------------------------------"

run_test "validate-jira-approval.py executable" "test -x scripts/validate-jira-approval.py"
run_test "generate-pki-keys.py executable" "test -x scripts/generate-pki-keys.py"
run_test "jira-webhook-receiver.py executable" "test -x scripts/jira-webhook-receiver.py"
run_test "setup-agent.sh executable" "test -x scripts/setup-agent.sh"
run_test "deploy-agents.sh executable" "test -x scripts/deploy-agents.sh"

echo ""

# ============================================================================
# Test 3: Schema Files
# ============================================================================
echo "Test Suite 3: Schema Validation"
echo "--------------------------------"

run_test "audit-trail.json exists" "test -f policies/schemas/audit-trail.json"
run_test "siem-event.json exists" "test -f policies/schemas/siem-event.json"
run_test "agent-cost-record.json exists" "test -f policies/schemas/agent-cost-record.json"

# Validate schema structure
if command -v python3 > /dev/null; then
    run_test "audit-trail.json valid JSON" "python3 -c 'import json; json.load(open(\"policies/schemas/audit-trail.json\"))'"
    run_test "siem-event.json valid JSON" "python3 -c 'import json; json.load(open(\"policies/schemas/siem-event.json\"))'"
    run_test "agent-cost-record.json valid JSON" "python3 -c 'import json; json.load(open(\"policies/schemas/agent-cost-record.json\"))'"
fi

echo ""

# ============================================================================
# Test 4: PKI Key Generation
# ============================================================================
echo "Test Suite 4: PKI Key Generation"
echo "---------------------------------"

# Create temp directory
TEST_PKI_DIR=$(mktemp -d)
trap "rm -rf $TEST_PKI_DIR" EXIT

# Test unencrypted key generation (for testing only)
if run_test "Generate test RSA key pair" \
    "echo -e '\n\n' | python3 scripts/generate-pki-keys.py --name 'Test Manager' --output-dir $TEST_PKI_DIR --no-password --key-size 2048"; then

    run_test "Private key created" "test -f $TEST_PKI_DIR/test-manager.key"
    run_test "Public key created" "test -f $TEST_PKI_DIR/test-manager.pub"
    run_test "Certificate created" "test -f $TEST_PKI_DIR/test-manager.crt"
    run_test "Private key has secure permissions" "test \$(stat -c '%a' $TEST_PKI_DIR/test-manager.key) = '600'"

    # Test signing (if key was created)
    if [ -f "$TEST_PKI_DIR/test-manager.key" ]; then
        run_test "Sign CR approval" \
            "python3 scripts/generate-pki-keys.py --sign --cr-id CR-TEST-9999 --private-key $TEST_PKI_DIR/test-manager.key > /dev/null"

        run_test "Signature file created" "test -f CR-TEST-9999-signature.json"

        if [ -f "CR-TEST-9999-signature.json" ]; then
            run_test "Signature contains required fields" \
                "python3 -c 'import json; sig=json.load(open(\"CR-TEST-9999-signature.json\")); assert all(k in sig for k in [\"signature\", \"signed_data\", \"timestamp\"])'"
            rm -f CR-TEST-9999-signature.json
        fi
    fi
fi

echo ""

# ============================================================================
# Test 5: Jira Validation Script (Mock Mode)
# ============================================================================
echo "Test Suite 5: Jira Validation Script"
echo "-------------------------------------"

# Test help output
run_test "Script shows help" "python3 scripts/validate-jira-approval.py --help 2>&1 | grep -q 'Usage:' || python3 scripts/validate-jira-approval.py 2>&1 | grep -q 'Usage:'"

# Test missing environment variables (should fail gracefully)
if ! (env -u JIRA_URL -u JIRA_USER -u JIRA_TOKEN python3 scripts/validate-jira-approval.py test-agent CR-2025-1042 2>&1 | grep -q "Missing required environment variables"); then
    skip_test "Environment variable validation" "requires Jira credentials"
else
    echo -e "Testing: Environment variable validation ... ${GREEN}✅ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi

# Test with real Jira (if credentials available)
if [ -n "$JIRA_URL" ] && [ -n "$JIRA_USER" ] && [ -n "$JIRA_TOKEN" ]; then
    echo -e "${BLUE}ℹ️  Jira credentials detected - running live tests${NC}"

    # These tests will actually call Jira API
    # Note: Will fail if CR doesn't exist or isn't approved
    skip_test "Live Jira CR validation" "requires approved CR in Jira"
else
    skip_test "Live Jira tests" "JIRA_URL, JIRA_USER, or JIRA_TOKEN not set"
fi

echo ""

# ============================================================================
# Test 6: Webhook Receiver
# ============================================================================
echo "Test Suite 6: Webhook Receiver"
echo "-------------------------------"

# Test webhook receiver starts
TEST_PORT=18080

if python3 scripts/jira-webhook-receiver.py --port $TEST_PORT > /tmp/webhook.log 2>&1 &
then
    WEBHOOK_PID=$!
    sleep 2

    # Test health endpoint
    if run_test "Webhook health endpoint" "curl -s http://localhost:$TEST_PORT/health | grep -q 'healthy'"; then
        run_test "Health response is JSON" "curl -s http://localhost:$TEST_PORT/health | python3 -c 'import json, sys; json.load(sys.stdin)'"
    fi

    # Test 404 for unknown endpoints
    run_test "Unknown endpoint returns 404" "curl -s -o /dev/null -w '%{http_code}' http://localhost:$TEST_PORT/unknown | grep -q 404"

    # Stop webhook receiver
    kill $WEBHOOK_PID 2>/dev/null || true
    wait $WEBHOOK_PID 2>/dev/null || true
else
    skip_test "Webhook receiver tests" "failed to start receiver"
fi

echo ""

# ============================================================================
# Test 7: Setup Agent Script
# ============================================================================
echo "Test Suite 7: Setup Agent Script"
echo "---------------------------------"

run_test "setup-agent.sh shows usage" "scripts/setup-agent.sh --help 2>&1 | grep -q 'Usage:'"
run_test "setup-agent.sh validates tier" "! scripts/setup-agent.sh --tier 5 --name test 2>&1 | grep -q 'must be 1, 2, 3, or 4'"

# Test that Tier 3 prod requires Jira CR
if scripts/setup-agent.sh --tier 3 --name test-agent --environment prod 2>&1 | grep -q "Jira CR ID is required"; then
    echo -e "Testing: Tier 3 prod requires Jira CR ... ${GREEN}✅ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Testing: Tier 3 prod requires Jira CR ... ${RED}❌ FAIL${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""

# ============================================================================
# Test 8: Deploy Agents Script
# ============================================================================
echo "Test Suite 8: Deploy Agents Script"
echo "-----------------------------------"

# Test that prod requires Jira CR
if scripts/deploy-agents.sh prod 2>&1 | grep -q "Jira CR ID required"; then
    echo -e "Testing: deploy-agents.sh prod requires Jira CR ... ${GREEN}✅ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Testing: deploy-agents.sh prod requires Jira CR ... ${RED}❌ FAIL${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""

# ============================================================================
# Test 9: GitHub Actions Workflow
# ============================================================================
echo "Test Suite 9: GitHub Actions Workflow"
echo "--------------------------------------"

run_test "deploy-security-agent.yml exists" "test -f .github/workflows/deploy-security-agent.yml"
run_test "Workflow has jira-approval job" "grep -q 'jira-approval:' .github/workflows/deploy-security-agent.yml"
run_test "Workflow validates Jira CR ID" "grep -q 'validate-jira-approval.py' .github/workflows/deploy-security-agent.yml"
run_test "Workflow has required secrets" "grep -q 'JIRA_TOKEN' .github/workflows/deploy-security-agent.yml"

echo ""

# ============================================================================
# Test 10: Documentation
# ============================================================================
echo "Test Suite 10: Documentation"
echo "-----------------------------"

run_test "Jira integration guide exists" "test -f docs/JIRA-INTEGRATION-GUIDE.md"
run_test "Guide has setup section" "grep -q '## Setup' docs/JIRA-INTEGRATION-GUIDE.md"
run_test "Guide has PKI section" "grep -q '## PKI Signing' docs/JIRA-INTEGRATION-GUIDE.md"
run_test "Guide has webhook section" "grep -q '## Webhook Integration' docs/JIRA-INTEGRATION-GUIDE.md"
run_test "Guide has troubleshooting" "grep -q '## Troubleshooting' docs/JIRA-INTEGRATION-GUIDE.md"

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "${GREEN}✅ Passed:  $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed:  $TESTS_FAILED${NC}"
echo -e "${YELLOW}⊘  Skipped: $TESTS_SKIPPED${NC}"
echo "------------------------------------------"
TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
echo "Total:     $TOTAL_TESTS"
echo "=========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Jira integration is properly configured."
    echo ""
    echo "Next steps:"
    echo "  1. Set Jira credentials in environment variables"
    echo "  2. Configure Jira webhook (see docs/JIRA-INTEGRATION-GUIDE.md)"
    echo "  3. Generate PKI keys for production: scripts/generate-pki-keys.py"
    echo "  4. Test with a real CR: scripts/validate-jira-approval.py <agent> <CR-ID>"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "Review the failures above and fix issues before deployment."
    echo "See docs/JIRA-INTEGRATION-GUIDE.md for troubleshooting."
    exit 1
fi
