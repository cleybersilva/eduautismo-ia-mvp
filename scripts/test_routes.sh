#!/bin/bash
#
# Test Routes - EduAutismo IA
# Automated testing script for all API routes
#
# Usage: ./scripts/test_routes.sh [API_URL]
# Example: ./scripts/test_routes.sh http://localhost:8000

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${1:-http://localhost:8000}"
API_V1="$API_URL/api/v1"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}Testing:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓ PASS${NC} - $1"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ FAIL${NC} - $1"
    ((TESTS_FAILED++))
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_status=${4:-200}
    local data=$5

    print_test "$description"

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" -eq "$expected_status" ]; then
        print_success "$description (Status: $status_code)"
        echo "  Response: $(echo $body | jq -c '.' 2>/dev/null || echo $body | head -c 100)"
    else
        print_error "$description (Expected: $expected_status, Got: $status_code)"
        echo "  Response: $(echo $body | jq -c '.' 2>/dev/null || echo $body)"
    fi

    echo ""
}

# Main script
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   EduAutismo IA - Route Testing       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo -e "${NC}API URL: ${YELLOW}$API_URL${NC}\n"

# Check if API is reachable
print_header "0. Connectivity Check"
if curl -s -f "$API_URL" > /dev/null; then
    print_success "API is reachable"
else
    print_error "API is not reachable at $API_URL"
    echo ""
    echo "Please ensure:"
    echo "  1. Docker services are running: make dev"
    echo "  2. API is accessible at $API_URL"
    echo ""
    exit 1
fi

# ============================================================================
# 1. Root Endpoints
# ============================================================================
print_header "1. Root Endpoints"

test_endpoint "GET" "$API_URL/" "Root endpoint"

# ============================================================================
# 2. Health Check Endpoints
# ============================================================================
print_header "2. Health Check Endpoints"

test_endpoint "GET" "$API_V1/health" "Basic health check"
test_endpoint "GET" "$API_V1/health/" "Basic health check (with trailing slash)"
test_endpoint "GET" "$API_V1/health/detailed" "Detailed health check"
test_endpoint "GET" "$API_V1/health/ready" "Readiness check"
test_endpoint "GET" "$API_V1/health/live" "Liveness check"
test_endpoint "GET" "$API_V1/health/startup" "Startup check"

# ============================================================================
# 3. Authentication Endpoints
# ============================================================================
print_header "3. Authentication Endpoints"

# Register new user
print_test "Register new user"
TIMESTAMP=$(date +%s)
TEST_EMAIL="test_${TIMESTAMP}@example.com"
TEST_PASSWORD="SecurePass123!"
REGISTER_DATA='{
    "email": "'$TEST_EMAIL'",
    "password": "'$TEST_PASSWORD'",
    "full_name": "Test User",
    "role": "teacher"
}'

test_endpoint "POST" "$API_V1/auth/register" "Register new user" 201 "$REGISTER_DATA"

# Login
print_test "User login"
LOGIN_DATA="username=$TEST_EMAIL&password=$TEST_PASSWORD"
login_response=$(curl -s -w "\n%{http_code}" -X POST "$API_V1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "$LOGIN_DATA")

login_status=$(echo "$login_response" | tail -n1)
login_body=$(echo "$login_response" | sed '$d')

if [ "$login_status" -eq "200" ]; then
    print_success "User login (Status: $login_status)"
    ACCESS_TOKEN=$(echo $login_body | jq -r '.access_token')
    REFRESH_TOKEN=$(echo $login_body | jq -r '.refresh_token')
    echo "  Access Token: ${ACCESS_TOKEN:0:50}..."
    echo "  Refresh Token: ${REFRESH_TOKEN:0:50}..."
else
    print_error "User login (Expected: 200, Got: $login_status)"
    echo "  Response: $login_body"
fi
echo ""

# Get current user (authenticated)
if [ -n "$ACCESS_TOKEN" ]; then
    print_test "Get current user info (authenticated)"
    me_response=$(curl -s -w "\n%{http_code}" -X GET "$API_V1/auth/me" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    me_status=$(echo "$me_response" | tail -n1)
    me_body=$(echo "$me_response" | sed '$d')

    if [ "$me_status" -eq "200" ]; then
        print_success "Get current user info (Status: $me_status)"
        echo "  Response: $(echo $me_body | jq -c '.')"
    else
        print_error "Get current user info (Expected: 200, Got: $me_status)"
        echo "  Response: $me_body"
    fi
    echo ""
fi

# Refresh token
if [ -n "$REFRESH_TOKEN" ]; then
    REFRESH_DATA='{"refresh_token": "'$REFRESH_TOKEN'"}'
    test_endpoint "POST" "$API_V1/auth/refresh" "Refresh access token" 200 "$REFRESH_DATA"
fi

# Password reset request
RESET_DATA='{"email": "'$TEST_EMAIL'"}'
test_endpoint "POST" "$API_V1/auth/password-reset" "Password reset request" 200 "$RESET_DATA"

# ============================================================================
# 4. Student Endpoints (if token available)
# ============================================================================
if [ -n "$ACCESS_TOKEN" ]; then
    print_header "4. Student Endpoints (Authenticated)"

    # List students
    print_test "List students"
    students_response=$(curl -s -w "\n%{http_code}" -X GET "$API_V1/students/" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    students_status=$(echo "$students_response" | tail -n1)
    students_body=$(echo "$students_response" | sed '$d')

    if [ "$students_status" -eq "200" ]; then
        print_success "List students (Status: $students_status)"
        echo "  Response: $(echo $students_body | jq -c '.' 2>/dev/null || echo $students_body | head -c 100)"
    else
        print_error "List students (Expected: 200, Got: $students_status)"
        echo "  Response: $students_body"
    fi
    echo ""
fi

# ============================================================================
# 5. Documentation Endpoints
# ============================================================================
print_header "5. Documentation Endpoints"

test_endpoint "GET" "$API_URL/docs" "Swagger UI" 200
test_endpoint "GET" "$API_URL/redoc" "ReDoc" 200
test_endpoint "GET" "$API_URL/openapi.json" "OpenAPI schema" 200

# ============================================================================
# Summary
# ============================================================================
print_header "Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($TESTS_PASSED/$TOTAL_TESTS)*100}")

echo -e "Total Tests:  ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
echo -e "Pass Rate:    ${YELLOW}$PASS_RATE%${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the output above.${NC}"
    exit 1
fi
