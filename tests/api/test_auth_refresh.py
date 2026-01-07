import pytest
import allure
import time
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import LoginResponse, RefreshTokenResponse, ErrorResponse, UserProfile
from utils.token_generator import generate_invalid_refresh_tokens

@allure.feature("Authentication")
@allure.story("Token Refresh")
@pytest.mark.api
class TestTokenRefresh:

    @allure.title("Successfully refresh access token with valid refresh token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_refresh_token_success(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        login_data = LoginResponse(**login_response.json())
        
        refresh_response = auth_client.refresh_token(login_data.refresh_token)
        
        assert refresh_response.status_code == 200, f"Expected 200, got {refresh_response.status_code}"
        
        try:
            refresh_data = RefreshTokenResponse(**refresh_response.json())
            assert refresh_data.access_token, "access_token is empty"
            assert refresh_data.access_token != login_data.access_token, "New access token should be different from old one"
        except ValidationError as e:
            pytest.fail(f"Refresh token response schema validation failed: {e}")

    @allure.title("Refresh token fails with invalid refresh token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("invalid_token", generate_invalid_refresh_tokens())
    def test_refresh_token_invalid(self, auth_client, invalid_token):
        response = auth_client.refresh_token(invalid_token)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Refresh token fails with missing refresh token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_refresh_token_missing(self, auth_client):
        response = auth_client.post("/v1/auth/refresh", json={})
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Refresh token fails with empty refresh token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_refresh_token_empty(self, auth_client):
        response = auth_client.refresh_token("")
        
        assert response.status_code in [400, 401], f"Expected 400 or 401, got {response.status_code}"
        ErrorResponse(**response.json())

    #TODO generate expired refresh tokens
    @allure.title("Refresh token fails with expired refresh token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    def test_refresh_token_expired(self, auth_client):
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj0vVzr7B8Y8P9nGJ5pZXkJZ5JZ5JZ5JZ5JZ5JZ5"
        
        response = auth_client.refresh_token(expired_token)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Multiple refresh requests with same token generate different access tokens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_refresh_token_multiple_times(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        login_data = LoginResponse(**login_response.json())
        
        refresh_response1 = auth_client.refresh_token(login_data.refresh_token)
        time.sleep(1)
        refresh_response2 = auth_client.refresh_token(login_data.refresh_token)
        
        assert refresh_response1.status_code == 200
        assert refresh_response2.status_code == 200
        
        refresh_data1 = RefreshTokenResponse(**refresh_response1.json())
        refresh_data2 = RefreshTokenResponse(**refresh_response2.json())
        
        assert refresh_data1.access_token != refresh_data2.access_token, "Multiple refresh requests should generate different access tokens"

    @allure.title("Refreshed access token is valid for API calls")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_refreshed_token_is_valid(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        login_data = LoginResponse(**login_response.json())
        
        refresh_response = auth_client.refresh_token(login_data.refresh_token)
        assert refresh_response.status_code == 200
        
        refresh_data = RefreshTokenResponse(**refresh_response.json())
        
        auth_client.token = refresh_data.access_token
        profile_response = auth_client.get_profile()
        
        assert profile_response.status_code == 200, "Refreshed token should be valid for API calls"
        UserProfile(**profile_response.json())

    @allure.title("Old access token is invalid for API calls after refresh")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_old_token_is_invalid(self, auth_client, valid_credentials):
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        login_data = LoginResponse(**login_response.json())
        
        refresh_response = auth_client.refresh_token(login_data.refresh_token)
        assert refresh_response.status_code == 200
        
        auth_client.token = login_data.access_token
        profile_response = auth_client.get_profile()
        
        assert profile_response.status_code == 401, "Old token should be invalid for API calls after refresh"
        ErrorResponse(**profile_response.json())


