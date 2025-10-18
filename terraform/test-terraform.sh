#!/bin/bash
# Test Terraform Configuration
# AI Agent Governance Framework v2.1

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Terraform Configuration Test Suite"
echo "AI Agent Governance Framework v2.1"
echo "=========================================="
echo ""

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

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
        sed 's/^/    /' /tmp/test-output.log | head -20
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# Test 1: Prerequisites
# ============================================================================
echo "Test Suite 1: Prerequisites"
echo "----------------------------"

run_test "Terraform installed" "command -v terraform > /dev/null"

if command -v terraform > /dev/null; then
    run_test "Terraform version >= 1.5.0" "terraform version | grep -q 'Terraform v1\.[5-9]\|Terraform v[2-9]'"
fi

run_test "AWS CLI installed" "command -v aws > /dev/null"

echo ""

# ============================================================================
# Test 2: Module Structure
# ============================================================================
echo "Test Suite 2: Module Structure"
echo "-------------------------------"

run_test "modules/kms exists" "test -d modules/kms"
run_test "modules/secrets_manager exists" "test -d modules/secrets_manager"
run_test "modules/cloudtrail exists" "test -d modules/cloudtrail"
run_test "modules/s3_audit_logs exists" "test -d modules/s3_audit_logs"

run_test "modules/kms/main.tf exists" "test -f modules/kms/main.tf"
run_test "modules/secrets_manager/main.tf exists" "test -f modules/secrets_manager/main.tf"
run_test "modules/cloudtrail/main.tf exists" "test -f modules/cloudtrail/main.tf"
run_test "modules/s3_audit_logs/main.tf exists" "test -f modules/s3_audit_logs/main.tf"

echo ""

# ============================================================================
# Test 3: Main Configuration Files
# ============================================================================
echo "Test Suite 3: Main Configuration Files"
echo "---------------------------------------"

run_test "main-modular-v2.tf exists" "test -f main-modular-v2.tf"
run_test "variables-modular-v2.tf exists" "test -f variables-modular-v2.tf"
run_test "outputs-modular-v2.tf exists" "test -f outputs-modular-v2.tf"
run_test "README-MODULES.md exists" "test -f README-MODULES.md"

echo ""

# ============================================================================
# Test 4: Terraform Syntax Validation
# ============================================================================
echo "Test Suite 4: Terraform Syntax"
echo "-------------------------------"

if command -v terraform > /dev/null; then
    # Create temporary test directory
    TEST_DIR=$(mktemp -d)
    trap "rm -rf $TEST_DIR" EXIT

    # Copy files to test directory
    cp -r modules $TEST_DIR/
    cp main-modular-v2.tf $TEST_DIR/main.tf
    cp variables-modular-v2.tf $TEST_DIR/variables.tf
    cp outputs-modular-v2.tf $TEST_DIR/outputs.tf

    cd $TEST_DIR

    # Create dummy backend configuration
    cat > backend.tf <<EOF
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
EOF

    run_test "Terraform init (local backend)" "terraform init"
    run_test "Terraform fmt check" "terraform fmt -check -recursive"
    run_test "Terraform validate" "terraform validate"

    cd - > /dev/null
fi

echo ""

# ============================================================================
# Test 5: Module Variable Validation
# ============================================================================
echo "Test Suite 5: Module Variables"
echo "-------------------------------"

# Check for required variables in KMS module
run_test "KMS module has key_alias var" "grep -q 'variable \"key_alias\"' modules/kms/main.tf"
run_test "KMS module has control_ids var" "grep -q 'variable \"control_ids\"' modules/kms/main.tf"
run_test "KMS module has jira_cr_id var" "grep -q 'variable \"jira_cr_id\"' modules/kms/main.tf"
run_test "KMS module has audit_id var" "grep -q 'variable \"audit_id\"' modules/kms/main.tf"

# Check for required variables in Secrets Manager module
run_test "Secrets module has agent_id var" "grep -q 'variable \"agent_id\"' modules/secrets_manager/main.tf"
run_test "Secrets module has jira_cr_id var" "grep -q 'variable \"jira_cr_id\"' modules/secrets_manager/main.tf"
run_test "Secrets module has audit_id var" "grep -q 'variable \"audit_id\"' modules/secrets_manager/main.tf"

# Check for required variables in CloudTrail module
run_test "CloudTrail module has trail_name var" "grep -q 'variable \"trail_name\"' modules/cloudtrail/main.tf"
run_test "CloudTrail module has jira_cr_id var" "grep -q 'variable \"jira_cr_id\"' modules/cloudtrail/main.tf"
run_test "CloudTrail module has audit_id var" "grep -q 'variable \"audit_id\"' modules/cloudtrail/main.tf"

echo ""

# ============================================================================
# Test 6: Module Outputs
# ============================================================================
echo "Test Suite 6: Module Outputs"
echo "-----------------------------"

run_test "KMS module has audit_metadata output" "grep -q 'output \"audit_metadata\"' modules/kms/main.tf"
run_test "Secrets module has audit_metadata output" "grep -q 'output \"audit_metadata\"' modules/secrets_manager/main.tf"
run_test "CloudTrail module has audit_metadata output" "grep -q 'output \"audit_metadata\"' modules/cloudtrail/main.tf"
run_test "S3 module has audit_metadata output" "grep -q 'output \"audit_metadata\"' modules/s3_audit_logs/main.tf"

echo ""

# ============================================================================
# Test 7: Control ID Tagging
# ============================================================================
echo "Test Suite 7: Control ID Tagging"
echo "---------------------------------"

run_test "KMS module tags resources with control_id" "grep -q 'control_id.*=' modules/kms/main.tf"
run_test "Secrets module tags resources with control_id" "grep -q 'control_id.*=' modules/secrets_manager/main.tf"
run_test "CloudTrail module tags resources with control_id" "grep -q 'control_id.*=' modules/cloudtrail/main.tf"
run_test "S3 module tags resources with control_id" "grep -q 'control_id.*=' modules/s3_audit_logs/main.tf"

run_test "KMS module tags with jira_cr_id" "grep -q 'jira_cr_id.*=' modules/kms/main.tf"
run_test "Secrets module tags with jira_cr_id" "grep -q 'jira_cr_id.*=' modules/secrets_manager/main.tf"
run_test "CloudTrail module tags with jira_cr_id" "grep -q 'jira_cr_id.*=' modules/cloudtrail/main.tf"

run_test "KMS module tags with audit_id" "grep -q 'audit_id.*=' modules/kms/main.tf"
run_test "Secrets module tags with audit_id" "grep -q 'audit_id.*=' modules/secrets_manager/main.tf"
run_test "CloudTrail module tags with audit_id" "grep -q 'audit_id.*=' modules/cloudtrail/main.tf"

echo ""

# ============================================================================
# Test 8: Audit Correlation in Outputs
# ============================================================================
echo "Test Suite 8: Audit Correlation Outputs"
echo "----------------------------------------"

run_test "Main outputs has audit_metadata" "grep -q 'output \"audit_metadata\"' outputs-modular-v2.tf"
run_test "Main outputs has jira_reference" "grep -q 'output \"jira_reference\"' outputs-modular-v2.tf"
run_test "Main outputs has control_implementation_summary" "grep -q 'output \"control_implementation_summary\"' outputs-modular-v2.tf"

run_test "jira_reference output includes cr_id" "grep -A 10 'output \"jira_reference\"' outputs-modular-v2.tf | grep -q 'cr_id'"
run_test "jira_reference output includes audit_id" "grep -A 10 'output \"jira_reference\"' outputs-modular-v2.tf | grep -q 'audit_id'"

echo ""

# ============================================================================
# Test 9: Security Best Practices
# ============================================================================
echo "Test Suite 9: Security Best Practices"
echo "--------------------------------------"

run_test "KMS module enables key rotation" "grep -q 'enable_key_rotation.*=.*true' modules/kms/main.tf"
run_test "S3 module blocks public access" "grep -q 'block_public_acls.*=.*true' modules/s3_audit_logs/main.tf"
run_test "S3 module enables versioning" "grep -q 'versioning_configuration' modules/s3_audit_logs/main.tf"
run_test "CloudTrail enables log validation" "grep -q 'enable_log_file_validation' modules/cloudtrail/main.tf"
run_test "CloudTrail is multi-region" "grep -q 'is_multi_region_trail.*=.*true' modules/cloudtrail/main.tf"

echo ""

# ============================================================================
# Test 10: Documentation
# ============================================================================
echo "Test Suite 10: Documentation"
echo "-----------------------------"

run_test "README has deployment guide" "grep -q '## Deployment Guide' README-MODULES.md"
run_test "README has module documentation" "grep -q '## Modules' README-MODULES.md"
run_test "README has outputs documentation" "grep -q '## Outputs and Audit Correlation' README-MODULES.md"
run_test "README has compliance section" "grep -q '## Compliance and Security' README-MODULES.md"
run_test "README has troubleshooting" "grep -q '## Troubleshooting' README-MODULES.md"

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "${GREEN}✅ Passed:  $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed:  $TESTS_FAILED${NC}"
echo "------------------------------------------"
TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo "Total:     $TOTAL_TESTS"
echo "=========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Terraform modules are properly configured."
    echo ""
    echo "Next steps:"
    echo "  1. Set environment variables (see README-MODULES.md)"
    echo "  2. Initialize: terraform init"
    echo "  3. Validate: terraform validate"
    echo "  4. Plan: terraform plan"
    echo "  5. Apply: terraform apply"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "Review the failures above and fix issues before deployment."
    exit 1
fi
