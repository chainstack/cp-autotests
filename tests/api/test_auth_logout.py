import pytest
import allure


@allure.feature("Authentication")
@allure.story("Logout")
@pytest.mark.api
class TestLogout:

    @allure.title("Successfully logout with valid token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_logout_success(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        
        auth_client.token = access_token
        logout_response = auth_client.logout(refresh_token)
        
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        
        data = logout_response.json()
        assert "message" in data, "Response should contain message"
        assert data["message"], "Message should not be empty"

    @allure.title("Successfully logout without providing refresh token in body")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_without_refresh_token_in_body(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        
        auth_client.token = access_token
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        
        data = logout_response.json()
        assert "message" in data, "Response should contain message"

    @allure.title("Logout fails without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_logout_without_auth_token(self, auth_client):
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        
        data = logout_response.json()
        assert "error" in data, "Response should contain error message"

    @allure.title("Logout fails with invalid authentication token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_with_invalid_token(self, auth_client):
        auth_client.token = "invalid.token.here"
        
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        
        data = logout_response.json()
        assert "error" in data, "Response should contain error message"

    @allure.title("Logout fails with expired authentication token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_with_expired_token(self, auth_client):
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj0vVzr7B8Y8P9nGJ5pZXkJZ5JZ5JZ5JZ5JZ5JZ5"
        auth_client.token = expired_token
        
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        
        data = logout_response.json()
        assert "error" in data, "Response should contain error message"

    @allure.title("Token is invalidated after logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_token_invalidated_after_logout(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        
        auth_client.token = access_token
        
        profile_response_before = auth_client.get_profile()
        assert profile_response_before.status_code == 200, "Token should work before logout"
        
        logout_response = auth_client.logout(refresh_token)
        assert logout_response.status_code == 200
        
        profile_response_after = auth_client.get_profile()
        assert profile_response_after.status_code == 401, "Token should be invalid after logout"

    @allure.title("Refresh token is invalidated after logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_refresh_token_invalidated_after_logout(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        
        auth_client.token = access_token
        logout_response = auth_client.logout(refresh_token)
        assert logout_response.status_code == 200
        
        auth_client.token = None
        refresh_response = auth_client.refresh_token(refresh_token)
        assert refresh_response.status_code == 401, "Refresh token should be invalid after logout"

    @allure.title("Multiple logout calls with same token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_multiple_times(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        
        auth_client.token = access_token
        
        logout_response1 = auth_client.logout(refresh_token)
        assert logout_response1.status_code == 200
        
        logout_response2 = auth_client.logout(refresh_token)
        assert logout_response2.status_code == 401, "Second logout should fail with 401"
