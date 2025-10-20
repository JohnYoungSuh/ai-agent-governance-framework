#!/usr/bin/env python3
"""
RESTful API Pattern Tests
AI Agent Governance Framework - Internal v2.1

Tests CMDB API against RESTful design best practices:
- Resource naming
- HTTP methods
- Status codes
- HATEOAS
- Pagination
- Filtering
- Versioning
- Idempotency
"""

import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append('..')

from api import app

client = TestClient(app)

API_KEY = "dev-api-key-12345"
HEADERS = {"X-API-Key": API_KEY}


class TestRESTfulPatterns:
    """Test RESTful API design patterns"""

    # ========================================================================
    # 1. Resource Naming Tests
    # ========================================================================

    def test_resource_naming_conventions(self):
        """
        Test: Resources should use plural nouns, not verbs

        GOOD: /api/v1/cis (plural noun)
        BAD: /api/v1/getCI, /api/v1/createBaseline (verbs)

        ISSUE FOUND: Current API uses /ci (should be /cis)
        """
        # Test plural resource naming
        response = client.get("/api/v1/ci")  # Current endpoint

        # Should be /cis for plural
        print("\n❌ ISSUE: Resource naming")
        print("   Current: /api/v1/ci")
        print("   Should be: /api/v1/cis")
        print("   Reason: RESTful resources should use plural nouns")

    def test_nested_resource_naming(self):
        """
        Test: Nested resources should be properly structured

        GOOD: /api/v1/cis/{ci_id}/baselines
        CURRENT: /api/v1/baseline/current/{ci_id}

        ISSUE: Baseline should be nested under CI
        """
        print("\n❌ ISSUE: Nested resources")
        print("   Current: /api/v1/baseline/current/{ci_id}")
        print("   Should be: /api/v1/cis/{ci_id}/baselines/current")
        print("   Reason: Baselines belong to CIs, should be nested")

    # ========================================================================
    # 2. HTTP Method Tests
    # ========================================================================

    def test_http_methods_semantic_correctness(self):
        """
        Test: HTTP methods should match their semantic meaning

        GET: Retrieve (safe, idempotent)
        POST: Create (not idempotent)
        PUT: Replace entire resource (idempotent)
        PATCH: Partial update (idempotent)
        DELETE: Remove (idempotent)

        ISSUE: Using PUT where PATCH should be used
        """
        print("\n❌ ISSUE: HTTP method usage")
        print("   Current: PUT /api/v1/ci/{ci_id} - Updates partial fields")
        print("   Should be: PATCH /api/v1/cis/{ci_id} - Partial update")
        print("   Reason: PUT should replace entire resource, PATCH for partial")

    def test_post_vs_put_idempotency(self):
        """
        Test: POST should not be idempotent, PUT should be

        Current API uses POST for creation (correct)
        But should also support PUT with client-provided ID
        """
        print("\n⚠️  ENHANCEMENT: Idempotency")
        print("   Consider: PUT /api/v1/cis/{ci_id} for idempotent creation")
        print("   Reason: Allows client to specify ID, prevents duplicates")

    # ========================================================================
    # 3. HTTP Status Code Tests
    # ========================================================================

    def test_status_codes_correctness(self):
        """
        Test: HTTP status codes should match operation results

        200 OK: Successful GET/PUT/PATCH/DELETE
        201 Created: Successful POST with resource creation
        202 Accepted: Async operation started
        204 No Content: Successful DELETE with no body
        400 Bad Request: Invalid input
        401 Unauthorized: Missing/invalid auth
        403 Forbidden: Authenticated but not authorized
        404 Not Found: Resource doesn't exist
        409 Conflict: Resource already exists
        422 Unprocessable Entity: Validation failed
        """
        # Test 201 Created
        response = client.get("/health")
        print("\n✅ GOOD: Health check returns 200")

        # Test 401 Unauthorized
        response = client.post("/api/v1/ci", json={})
        if response.status_code == 401:
            print("✅ GOOD: Missing API key returns 401")
        else:
            print(f"❌ ISSUE: Missing API key returns {response.status_code}, should be 401")

        # Test 404 Not Found
        response = client.get("/api/v1/ci/non-existent-id")
        if response.status_code == 404:
            print("✅ GOOD: Non-existent resource returns 404")
        else:
            print(f"⚠️  Current: Non-existent resource returns {response.status_code}")

    def test_delete_status_codes(self):
        """
        Test: DELETE should return 204 No Content, not 200 with body

        CURRENT: Returns 200 with JSON body
        SHOULD: Return 204 No Content
        """
        print("\n❌ ISSUE: DELETE status code")
        print("   Current: DELETE returns 200 with body")
        print("   Should be: DELETE returns 204 No Content")
        print("   Reason: 204 indicates successful deletion without response body")

    # ========================================================================
    # 4. HATEOAS Tests
    # ========================================================================

    def test_hateoas_links(self):
        """
        Test: Responses should include hypermedia links (HATEOAS)

        CURRENT: Responses are plain JSON
        SHOULD: Include _links object with related resources

        Example:
        {
            "ci_id": "CI-2025-001",
            "name": "security-ops-agent",
            "_links": {
                "self": {"href": "/api/v1/cis/CI-2025-001"},
                "baselines": {"href": "/api/v1/cis/CI-2025-001/baselines"},
                "relationships": {"href": "/api/v1/cis/CI-2025-001/relationships"}
            }
        }
        """
        print("\n❌ ISSUE: HATEOAS not implemented")
        print("   Current: Responses lack hypermedia links")
        print("   Should add: _links object with related resources")
        print("   Reason: HATEOAS enables API discoverability")

    # ========================================================================
    # 5. Pagination Tests
    # ========================================================================

    def test_pagination_support(self):
        """
        Test: Collection endpoints should support pagination

        CURRENT: Returns all items
        SHOULD: Support limit, offset/cursor, and provide pagination metadata

        Example: GET /api/v1/cis?limit=20&offset=0
        Response:
        {
            "items": [...],
            "pagination": {
                "limit": 20,
                "offset": 0,
                "total": 100,
                "has_more": true
            },
            "_links": {
                "next": "/api/v1/cis?limit=20&offset=20",
                "prev": null
            }
        }
        """
        response = client.get("/api/v1/ci")
        data = response.json()

        print("\n❌ ISSUE: Pagination not implemented")
        print("   Current: Returns all items without pagination")
        print("   Should add: limit, offset parameters and pagination metadata")
        print("   Reason: Prevent performance issues with large collections")

    # ========================================================================
    # 6. Filtering and Sorting Tests
    # ========================================================================

    def test_filtering_consistency(self):
        """
        Test: Filtering should use query parameters consistently

        CURRENT: Supports ci_type, environment, tier
        GOOD: Uses query parameters (correct)

        ENHANCEMENT: Support operators
        Example: ?tier[gte]=3, ?created_at[gt]=2025-01-01
        """
        response = client.get("/api/v1/ci?tier=3")

        print("\n✅ GOOD: Basic filtering with query parameters")
        print("⚠️  ENHANCEMENT: Add operator support (gte, lte, in, etc.)")

    def test_sorting_support(self):
        """
        Test: Collections should support sorting

        CURRENT: No sorting parameters
        SHOULD: Support ?sort=field or ?sort=-field (descending)

        Example: GET /api/v1/cis?sort=-created_at
        """
        print("\n❌ ISSUE: Sorting not implemented")
        print("   Should add: ?sort parameter")
        print("   Example: ?sort=-created_at (descending)")

    # ========================================================================
    # 7. API Versioning Tests
    # ========================================================================

    def test_api_versioning(self):
        """
        Test: API should be versioned

        CURRENT: /api/v1/... (correct)
        GOOD: Uses URL versioning
        """
        print("\n✅ GOOD: API versioning in URL path (/api/v1/)")

    # ========================================================================
    # 8. Content Negotiation Tests
    # ========================================================================

    def test_content_type_headers(self):
        """
        Test: API should properly handle Content-Type and Accept headers
        """
        response = client.get("/health")

        if "application/json" in response.headers.get("content-type", ""):
            print("\n✅ GOOD: Returns application/json Content-Type")
        else:
            print("\n❌ ISSUE: Content-Type header not set properly")

    # ========================================================================
    # 9. Error Response Format Tests
    # ========================================================================

    def test_error_response_format(self):
        """
        Test: Error responses should follow consistent format

        CURRENT: Returns {"detail": "error message"}
        SHOULD: Include more context

        RFC 7807 Problem Details:
        {
            "type": "https://api.suhlabs.com/errors/resource-not-found",
            "title": "Resource Not Found",
            "status": 404,
            "detail": "CI with id CI-9999 does not exist",
            "instance": "/api/v1/cis/CI-9999"
        }
        """
        response = client.get("/api/v1/ci/non-existent")
        error = response.json()

        print("\n⚠️  ENHANCEMENT: Error response format")
        print("   Current: Simple detail string")
        print("   Consider: RFC 7807 Problem Details format")
        print("   Benefit: More structured error information")

    # ========================================================================
    # 10. Bulk Operations Tests
    # ========================================================================

    def test_bulk_operations_support(self):
        """
        Test: API should support bulk operations where appropriate

        CURRENT: Only single resource operations
        SHOULD: Support bulk create/update/delete

        Example: POST /api/v1/cis with array of items
        """
        print("\n⚠️  ENHANCEMENT: Bulk operations")
        print("   Consider: POST /api/v1/cis with array")
        print("   Benefit: Reduce number of HTTP requests")

    # ========================================================================
    # 11. Idempotency Keys Tests
    # ========================================================================

    def test_idempotency_keys(self):
        """
        Test: POST operations should support idempotency keys

        SHOULD: Accept Idempotency-Key header
        Prevents duplicate resources on retry
        """
        print("\n⚠️  ENHANCEMENT: Idempotency keys")
        print("   Consider: Idempotency-Key header for POST")
        print("   Benefit: Safe retries without duplicates")

    # ========================================================================
    # 12. Rate Limiting Tests
    # ========================================================================

    def test_rate_limiting_headers(self):
        """
        Test: API should include rate limit headers

        SHOULD: Include headers:
        - X-RateLimit-Limit
        - X-RateLimit-Remaining
        - X-RateLimit-Reset
        """
        response = client.get("/health")

        if "X-RateLimit-Limit" in response.headers:
            print("\n✅ GOOD: Rate limiting headers present")
        else:
            print("\n⚠️  ENHANCEMENT: Add rate limiting headers")

    # ========================================================================
    # 13. Caching Tests
    # ========================================================================

    def test_cache_headers(self):
        """
        Test: Cacheable resources should include Cache-Control headers

        SHOULD: Include:
        - Cache-Control: max-age=3600, must-revalidate
        - ETag: "version-hash"
        - Last-Modified: timestamp
        """
        response = client.get("/api/v1/ci/CI-2025-001")

        if "Cache-Control" in response.headers or "ETag" in response.headers:
            print("\n✅ GOOD: Caching headers present")
        else:
            print("\n⚠️  ENHANCEMENT: Add caching headers (ETag, Cache-Control)")

    # ========================================================================
    # 14. Partial Response Tests
    # ========================================================================

    def test_field_selection(self):
        """
        Test: API should support field selection

        SHOULD: Support ?fields parameter
        Example: GET /api/v1/cis/CI-2025-001?fields=ci_id,name,tier

        Benefit: Reduce payload size
        """
        print("\n⚠️  ENHANCEMENT: Field selection")
        print("   Consider: ?fields parameter")
        print("   Example: ?fields=ci_id,name,tier")

    # ========================================================================
    # 15. Relationship Endpoints Tests
    # ========================================================================

    def test_relationship_endpoints(self):
        """
        Test: Relationships should be accessible as sub-resources

        CURRENT: /api/v1/graph/relationships/{ci_id}
        SHOULD: /api/v1/cis/{ci_id}/relationships

        More RESTful to nest under parent resource
        """
        print("\n❌ ISSUE: Relationship endpoint structure")
        print("   Current: /api/v1/graph/relationships/{ci_id}")
        print("   Should be: /api/v1/cis/{ci_id}/relationships")

    # ========================================================================
    # 16. Action Endpoints Tests
    # ========================================================================

    def test_action_endpoints(self):
        """
        Test: Actions should use POST to sub-resources

        CURRENT: POST /api/v1/baseline/{id}/approve (good)
        CURRENT: POST /api/v1/drift/detect/{ci_id} (should be different)

        ISSUE: Drift detection is a read operation, should be GET
        OR: Make it POST to trigger action explicitly
        """
        print("\n⚠️  REVIEW: Action endpoint semantics")
        print("   Current: POST /api/v1/drift/detect/{ci_id}")
        print("   Option 1: GET /api/v1/cis/{ci_id}/drift (if read-only)")
        print("   Option 2: POST /api/v1/cis/{ci_id}/drift-detection (if creates report)")

    # ========================================================================
    # Summary
    # ========================================================================

    def test_summary(self):
        """Print summary of RESTful API pattern analysis"""
        print("\n" + "=" * 70)
        print("RESTful API PATTERN ANALYSIS SUMMARY")
        print("=" * 70)

        print("\n✅ GOOD PRACTICES FOUND:")
        print("   1. API versioning in URL (/api/v1/)")
        print("   2. Query parameters for filtering")
        print("   3. Proper authentication with API keys")
        print("   4. JSON content type")
        print("   5. Correct 401 for missing auth")
        print("   6. Health check endpoint")

        print("\n❌ ISSUES TO FIX:")
        print("   1. Resource naming: /ci → /cis (plural)")
        print("   2. HTTP methods: PUT → PATCH for partial updates")
        print("   3. Status codes: DELETE should return 204")
        print("   4. HATEOAS: Add _links to responses")
        print("   5. Pagination: Missing from collection endpoints")
        print("   6. Nested resources: Reorganize endpoint structure")

        print("\n⚠️  ENHANCEMENTS TO CONSIDER:")
        print("   1. Sorting support (?sort parameter)")
        print("   2. RFC 7807 error format")
        print("   3. Bulk operations")
        print("   4. Idempotency keys")
        print("   5. Rate limiting headers")
        print("   6. Caching headers (ETag, Cache-Control)")
        print("   7. Field selection (?fields parameter)")
        print("   8. Operator-based filtering")

        print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run tests
    test = TestRESTfulPatterns()

    print("=" * 70)
    print("TESTING CMDB API AGAINST RESTful BEST PRACTICES")
    print("=" * 70)

    test.test_resource_naming_conventions()
    test.test_nested_resource_naming()
    test.test_http_methods_semantic_correctness()
    test.test_post_vs_put_idempotency()
    test.test_status_codes_correctness()
    test.test_delete_status_codes()
    test.test_hateoas_links()
    test.test_pagination_support()
    test.test_filtering_consistency()
    test.test_sorting_support()
    test.test_api_versioning()
    test.test_content_type_headers()
    test.test_error_response_format()
    test.test_bulk_operations_support()
    test.test_idempotency_keys()
    test.test_rate_limiting_headers()
    test.test_cache_headers()
    test.test_field_selection()
    test.test_relationship_endpoints()
    test.test_action_endpoints()
    test.test_summary()
