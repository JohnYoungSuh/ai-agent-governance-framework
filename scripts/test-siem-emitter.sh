#!/bin/bash
# Test OpenTelemetry SIEM Emitter
# AI Agent Governance Framework v2.1
# Controls: AU-002, AU-012, G-03

set -e

echo "=========================================="
echo "OpenTelemetry SIEM Emitter Test Suite"
echo "AI Agent Governance Framework v2.1"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OTEL_SCRIPT="$SCRIPT_DIR/otel-siem-emitter.py"
OUTPUT_DIR="$SCRIPT_DIR/../test-output/siem-events"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local expected_result="$2"  # pass or fail
    shift 2
    local cmd="$@"

    echo -n "Testing: $test_name ... "

    if eval "$cmd" > /dev/null 2>&1; then
        if [ "$expected_result" = "pass" ]; then
            echo -e "${GREEN}✅ PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ FAIL (expected failure, got success)${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        if [ "$expected_result" = "fail" ]; then
            echo -e "${GREEN}✅ PASS (expected failure)${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ FAIL${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    fi
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ python3 not found${NC}"
    exit 1
fi
echo "✅ python3 found"

if ! [ -f "$OTEL_SCRIPT" ]; then
    echo -e "${RED}❌ Script not found: $OTEL_SCRIPT${NC}"
    exit 1
fi
echo "✅ SIEM emitter script found"

# Check Python dependencies (optional - don't fail if missing)
if python3 -c "import opentelemetry" 2>/dev/null; then
    echo "✅ OpenTelemetry installed"
    OTEL_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  OpenTelemetry not installed (install with: pip3 install -r requirements-otel.txt)${NC}"
    echo "   Tests will run in dry-run mode only"
    OTEL_AVAILABLE=false
fi

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Set test environment variables
export OTEL_SERVICE_NAME="ai-agent-governance-test"
export OTEL_ENVIRONMENT="test"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"

# TEST 1: Basic compliance check event (dry-run)
run_test "Basic compliance check event (dry-run)" "pass" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id test-agent \
        --control-id SEC-001 \
        --event-type compliance_check \
        --severity info \
        --description 'KMS key rotation enabled' \
        --audit-id audit-test-001 \
        --jira-cr-id CR-2025-1042 \
        --tier 3 \
        --compliance-result pass \
        --output '$OUTPUT_DIR/test-01-compliance-check.json' \
        --dry-run 2>/dev/null"

# TEST 2: Security finding with high severity
run_test "Security finding (high severity)" "pass" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id security-agent \
        --control-id SEC-001 \
        --event-type security_finding \
        --severity high \
        --description 'Unencrypted S3 bucket detected' \
        --audit-id audit-test-002 \
        --tier 3 \
        --compliance-result fail \
        --resource-arn 'arn:aws:s3:::my-bucket' \
        --output '$OUTPUT_DIR/test-02-security-finding.json' \
        --dry-run"

# TEST 3: IAM change event
run_test "IAM change event" "pass" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id ops-agent \
        --control-id SEC-001 \
        --event-type iam_change \
        --severity medium \
        --description 'IAM role policy updated' \
        --audit-id audit-test-003 \
        --jira-cr-id CR-2025-1043 \
        --tier 4 \
        --compliance-result pass \
        --resource-arn 'arn:aws:iam::123456789012:role/ai-agent-role' \
        --output '$OUTPUT_DIR/test-03-iam-change.json' \
        --dry-run"

# TEST 4: API call with custom payload
run_test "API call with JSON payload" "pass" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id architect-agent \
        --control-id APP-001 \
        --event-type api_call \
        --severity low \
        --description 'Lambda function invoked' \
        --audit-id audit-test-004 \
        --tier 4 \
        --compliance-result pass \
        --resource-arn 'arn:aws:lambda:us-east-1:123456789012:function:my-function' \
        --payload-json '{\"request_id\":\"req-123\",\"duration_ms\":450}' \
        --output '$OUTPUT_DIR/test-04-api-call.json' \
        --dry-run"

# TEST 5: Missing required argument (should fail)
run_test "Missing required argument (negative test)" "fail" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id test-agent \
        --event-type compliance_check \
        --severity info \
        --description 'Test' \
        --dry-run"

# TEST 6: Invalid event type (should fail)
run_test "Invalid event type (negative test)" "fail" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id test-agent \
        --control-id SEC-001 \
        --event-type invalid_type \
        --severity info \
        --description 'Test' \
        --dry-run"

# TEST 7: Invalid severity (should fail)
run_test "Invalid severity (negative test)" "fail" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id test-agent \
        --control-id SEC-001 \
        --event-type compliance_check \
        --severity invalid_severity \
        --description 'Test' \
        --dry-run"

# TEST 8: Invalid JSON payload (should fail)
run_test "Invalid JSON payload (negative test)" "fail" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id test-agent \
        --control-id SEC-001 \
        --event-type api_call \
        --severity info \
        --description 'Test' \
        --payload-json 'not valid json' \
        --dry-run"

# TEST 9: Authentication event
run_test "Authentication event" "pass" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id deployment-agent \
        --control-id APP-001 \
        --event-type authentication \
        --severity info \
        --description 'Jira CR approval validated' \
        --audit-id audit-test-009 \
        --jira-cr-id CR-2025-1044 \
        --tier 3 \
        --compliance-result pass \
        --output '$OUTPUT_DIR/test-09-authentication.json' \
        --dry-run"

# TEST 10: Resource access event
run_test "Resource access event" "pass" \
    "python3 '$OTEL_SCRIPT' \
        --agent-id it-ops-agent \
        --control-id MI-003 \
        --event-type resource_access \
        --severity low \
        --description 'Secret accessed from Secrets Manager' \
        --audit-id audit-test-010 \
        --tier 2 \
        --compliance-result pass \
        --resource-arn 'arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret' \
        --output '$OUTPUT_DIR/test-10-resource-access.json' \
        --dry-run"

echo ""
echo "=========================================="
echo "Validating Output Files"
echo "=========================================="
echo ""

# Validate generated JSON files against schema
SCHEMA_FILE="$SCRIPT_DIR/../policies/schemas/siem-event.json"

if [ -f "$SCHEMA_FILE" ]; then
    echo "Validating SIEM events against schema..."

    for json_file in "$OUTPUT_DIR"/*.json; do
        if [ -f "$json_file" ]; then
            echo -n "  $(basename "$json_file"): "

            # Check if file is valid JSON using Python
            if python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
                echo -e "${GREEN}✅ Valid JSON${NC}"

                # Check required fields using Python
                VALIDATION=$(python3 <<EOF
import json
import sys
try:
    with open('$json_file') as f:
        data = json.load(f)

    # Check required fields
    required_fields = ['siem_event_id', 'timestamp', 'ocsf_mapping']
    missing = [field for field in required_fields if field not in data]

    if missing:
        print(f"MISSING:{','.join(missing)}")
        sys.exit(1)

    # Get OCSF values
    category_uid = data['ocsf_mapping'].get('category_uid', 0)
    severity_id = data['ocsf_mapping'].get('severity_id', 0)

    print(f"OCSF:{category_uid}:{severity_id}")
except Exception as e:
    print(f"ERROR:{e}")
    sys.exit(1)
EOF
)
                if echo "$VALIDATION" | grep -q "^OCSF:"; then
                    echo "     - Required fields present ✅"

                    # Extract and validate OCSF values
                    category_uid=$(echo "$VALIDATION" | cut -d':' -f2)
                    severity_id=$(echo "$VALIDATION" | cut -d':' -f3)

                    if [ "$category_uid" -ge 1 ] && [ "$category_uid" -le 6 ]; then
                        echo "     - OCSF category_uid: $category_uid ✅"
                    else
                        echo -e "     ${RED}- Invalid OCSF category_uid: $category_uid ❌${NC}"
                    fi

                    if [ "$severity_id" -ge 1 ] && [ "$severity_id" -le 5 ]; then
                        echo "     - OCSF severity_id: $severity_id ✅"
                    else
                        echo -e "     ${RED}- Invalid OCSF severity_id: $severity_id ❌${NC}"
                    fi
                else
                    echo -e "     ${RED}- Missing required fields ❌${NC}"
                fi
            else
                echo -e "${RED}❌ Invalid JSON${NC}"
                TESTS_FAILED=$((TESTS_FAILED + 1))
            fi
            echo ""
        fi
    done
else
    echo -e "${YELLOW}⚠️  Schema file not found: $SCHEMA_FILE${NC}"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""
echo "Test output files: $OUTPUT_DIR"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
