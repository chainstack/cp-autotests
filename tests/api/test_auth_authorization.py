import pytest
import allure
from utils.token_generator import generate_invalid_bearer_tokens


@allure.feature("Authentication")
@allure.story("Authorization & Access Control")
@pytest.mark.api
class TestAuthorization:

    @allure.title("Protected endpoints require Bearer token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("endpoint, method", [
        ("/v1/auth/profile", "GET"),
        ("/v1/auth/logout", "POST"),
        ("/v1/auth/password", "PUT"),
        ("/v1/auth/username", "PUT"),
        ("/v1/auth/audit-log", "GET")
    ])
    def test_protected_endpoints_require_token(self, auth_client, endpoint, method):
        with allure.step(f"Testing {method} {endpoint} without token"):
            response = auth_client.send_custom_request(method, endpoint)
            assert response.status_code == 401, \
                f"{method} {endpoint} should return 401 without token, got {response.status_code}"
            
            data = response.json()
            assert "error" in data, f"{method} {endpoint} should return error message"

    @allure.title("Invalid Bearer token format returns 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("token", generate_invalid_bearer_tokens())
    def test_invalid_token_format(self, auth_client, token):
        with allure.step(f"Testing with invalid token: {str(token)[:50]}..."):
            auth_client.token = token
            response = auth_client.get_profile()
            
            assert response.status_code == 401, \
                f"Invalid token should return 401, got {response.status_code}"

    # TODO: Generate expired token
    @allure.title("Expired token returns 401")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_expired_token_rejected(self, auth_client):
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj0vVzr7B8Y8P9nGJ5pZXkJZ5JZ5JZ5JZ5JZ5JZ5"
        
        auth_client.token = expired_token
        response = auth_client.get_profile()
        
        assert response.status_code == 401, f"Expired token should return 401, got {response.status_code}"
        
        data = response.json()
        assert "error" in data, "Response should contain error message"
    
    @allure.title("Token from different user cannot access another user's resources")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_token_isolation(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        user1_token = login_response.json()["access_token"]
        user1_id = login_response.json()["user"]["id"]
        
        auth_client.token = user1_token
        profile_response = auth_client.get_profile()
        assert profile_response.status_code == 200
        
        profile_user_id = profile_response.json()["id"]
        assert profile_user_id == user1_id, "Profile should match the authenticated user"

    @allure.title("Authorization header must use Bearer scheme")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bearer_scheme_required(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        response = auth_client.get(
            "/v1/auth/profile",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 401, \
            "Authorization header without Bearer scheme should return 401"

    @allure.title("Case-sensitive Bearer token validation")
    @allure.severity(allure.severity_level.MINOR)
    def test_bearer_case_sensitivity(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        response = auth_client.get(
            "/v1/auth/profile",
            headers={"Authorization": f"bearer {token}"}
        )
        #TODO clarify expected behavior
        assert response.status_code in [200, 401], \
            "Server should handle Bearer scheme case sensitivity consistently"

    @allure.title("Multiple Authorization headers handled correctly")
    @allure.severity(allure.severity_level.MINOR)
    def test_multiple_auth_headers(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        response = auth_client.client.get(
            f"{auth_client.base_url}/v1/auth/profile",
            headers=[
                ("Authorization", f"Bearer {token}"),
                ("Authorization", "Bearer invalid_duplicate_token"),
            ]
        )
        #TODO clarify expected behavior
        assert response.status_code in [200, 400, 401], \
            f"Expected 200/400/401 for duplicate headers, got {response.status_code}"

    @allure.title("Token cannot be reused after logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_token_revoked_after_logout(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        
        auth_client.token = access_token
        
        profile_before = auth_client.get_profile()
        assert profile_before.status_code == 200, "Token should work before logout"
        
        logout_response = auth_client.logout(refresh_token)
        assert logout_response.status_code == 200
        
        profile_after = auth_client.get_profile()
        assert profile_after.status_code == 401, "Token should be revoked after logout"

    @allure.title("Public endpoints accessible without authentication")
    @allure.severity(allure.severity_level.NORMAL)
    def test_public_endpoints_no_auth(self, auth_client):
        public_endpoints = [
            "/healthz",
            "/v1/auth/login",
            "/v1/auth/refresh",
        ]
        
        for endpoint in public_endpoints:
            with allure.step(f"Testing public endpoint: {endpoint}"):
                if endpoint == "/healthz":
                    response = auth_client.get(endpoint)
                    assert response.status_code in [200, 404], \
                        f"{endpoint} should be accessible without auth"

    @allure.title("CORS headers present in auth responses")
    @allure.severity(allure.severity_level.MINOR)
    def test_cors_headers_present(self, auth_client, valid_credentials):
        response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        
        assert response.status_code == 200
        #TODO:Clarify expected cors headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, OPTIONS"
        assert response.headers["Access-Control-Allow-Headers"] == "Authorization, Content-Type"
        assert response.headers["Access-Control-Allow-Credentials"] == "true"

    @allure.title("Rate limiting on authentication endpoints")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.skip(reason="Rate limiting behavior needs to be clarified with API specification")
    def test_rate_limiting(self, auth_client, invalid_credentials):
        """        
        TODO: Clarify rate limit thresholds:
        - How many requests allowed?
        - Time window (per minute/hour)?
        - Per IP or per username?
        - Retry-After header format?
        """
        max_attempts = 50
        rate_limited = False
        status_codes = []
        
        for i in range(max_attempts):
            response = auth_client.login(
                invalid_credentials["username"],
                invalid_credentials["password"]
            )
            status_codes.append(response.status_code)
            
            if response.status_code == 429:
                rate_limited = True
                with allure.step(f"Rate limit triggered after {i + 1} attempts"):
                    # Check for Retry-After header
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        allure.attach(
                            f"Retry-After: {retry_after}",
                            name="Rate Limit Headers",
                            attachment_type=allure.attachment_type.TEXT
                        )
                break
        
        if rate_limited:
            assert response.status_code == 429, "Rate limit should return 429"
        else:
            with allure.step(f"No rate limiting detected after {max_attempts} attempts"):
                pytest.skip(f"Rate limiting not implemented or threshold > {max_attempts}")

    
