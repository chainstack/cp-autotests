import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import LogoutResponse, ErrorResponse, LoginResponse, UserProfile
from utils.token_generator import generate_invalid_bearer_tokens


@allure.feature("Authentication")
@allure.story("Logout")
@pytest.mark.api
class TestLogout:

    @allure.title("Successfully logout with valid token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_logout_success(self, authenticated_auth_client):
        logout_response = authenticated_auth_client.logout(authenticated_auth_client.refresh_token)
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        
        try:
            logout_data = LogoutResponse(**logout_response.json())
            assert logout_data.message, "Message should not be empty"
        except ValidationError as e:
            pytest.fail(f"Logout response schema validation failed: {e}")

    @allure.title("Successfully logout without providing refresh token in body")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_without_refresh_token_in_body(self, authenticated_auth_client):
        logout_response = authenticated_auth_client.logout()
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        
        try:
            logout_data = LogoutResponse(**logout_response.json())
            assert logout_data.message, "Message should not be empty"
        except ValidationError as e:
            pytest.fail(f"Logout response schema validation failed: {e}")

    @allure.title("Logout fails without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_logout_without_auth_token(self, auth_client):
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())

    @allure.title("Logout fails with invalid authentication token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_bearer_tokens())
    def test_logout_with_invalid_token(self, auth_client, invalid_token):
        auth_client.token = invalid_token
        
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())

    # TODO: generate_expired_token
    @allure.title("Logout fails with expired authentication token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("expired_token", generate_expired_token())
    def test_logout_with_expired_token(self, auth_client, expired_token):
        auth_client.token = expired_token
        
        logout_response = auth_client.logout()
        
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())

    @allure.title("Token is invalidated after logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_token_invalidated_after_logout(self, authenticated_auth_client):
        profile_response_before = authenticated_auth_client.get_profile()
        assert profile_response_before.status_code == 200, "Token should work before logout"
        
        logout_response = authenticated_auth_client.logout(authenticated_auth_client.refresh_token)
        
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        LogoutResponse(**logout_response.json())
        
        profile_response_after = authenticated_auth_client.get_profile()
        assert profile_response_after.status_code == 401, f"Expected 401, got {profile_response_after.status_code}"
        ErrorResponse(**profile_response_after.json())      
        

    @allure.title("Refresh token is invalidated after logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_refresh_token_invalidated_after_logout(self,authenticated_auth_client):
        logout_response = authenticated_auth_client.logout(authenticated_auth_client.refresh_token)
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        LogoutResponse(**logout_response.json())
        
        refresh_response = authenticated_auth_client.refresh_token(authenticated_auth_client.refresh_token)
        assert refresh_response.status_code == 401, f"Expected 401, got {refresh_response.status_code}"
        ErrorResponse(**refresh_response.json())

    @allure.title("Multiple logout calls with same token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_multiple_times(self, authenticated_auth_client):
        logout_response = authenticated_auth_client.logout(authenticated_auth_client.refresh_token)
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        LogoutResponse(**logout_response.json())
        
        logout_response2 = authenticated_auth_client.logout(authenticated_auth_client.refresh_token)
        assert logout_response2.status_code == 401, f"Expected 401, got {logout_response2.status_code}"
        ErrorResponse(**logout_response2.json())
