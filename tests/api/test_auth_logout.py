import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import LogoutResponse, ErrorResponse, LoginResponse, UserProfile
from tests.api.cases.test_cases import EMPTY_STRING_CASES
from utils.token_generator import generate_invalid_refresh_tokens, generate_expired_token


@allure.feature("Authentication")
@allure.story("Logout")
@pytest.mark.api
class TestLogoutGeneral:

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


class TestLogoutRefreshToken:
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

    @allure.title("Logout with empty string refresh token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("empty_string", EMPTY_STRING_CASES)
    def test_logout_with_empty_string_refresh_token_in_body(self, authenticated_auth_client, empty_string):
        logout_response = authenticated_auth_client.logout(empty_string)
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

    
    @allure.title("Logout with wrong method")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("method", ["PUT", "PATCH"])
    def test_logout_with_wrong_method(self, authenticated_auth_client, method):
        logout_response = authenticated_auth_client.send_custom_request(method, "/v1/auth/logout", json={"refresh_token": authenticated_auth_client.refresh_token})
        assert logout_response.status_code == 405, f"Expected 405, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())

@allure.feature("Authentication")
@allure.story("Logout")
@pytest.mark.api
class TestLogoutAcess:
    
    @allure.title("Logout without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_without_auth_token(self, authenticated_auth_client):
        token = authenticated_auth_client.token
        authenticated_auth_client.token = None
        logout_response = authenticated_auth_client.logout()
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())
        authenticated_auth_client.token = token

    @allure.title("Logout with invalid authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_refresh_tokens())
    def test_logout_with_invalid_token(self, authenticated_auth_client, invalid_token):
        token = authenticated_auth_client.token
        authenticated_auth_client.token = invalid_token
        logout_response = authenticated_auth_client.logout()
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())
        authenticated_auth_client.token = token

    @allure.title("Logout with with wrong auth type")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_with_invalid_schema(self, authenticated_auth_client):
        token = authenticated_auth_client.token
        authenticated_auth_client.token = "Basic " + base64.b64encode(token.encode()).decode()
        logout_response = authenticated_auth_client.logout()
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())
        authenticated_auth_client.token = token

    @allure.title("Logout with wrong auth format")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_with_invalid_auth_format(self, authenticated_auth_client):
        token = authenticated_auth_client.token
        authenticated_auth_client.token = "Bearer " + base64.b64encode(token.encode()).decode()
        logout_response = authenticated_auth_client.logout()
        assert logout_response.status_code == 401, f"Expected 401, got {logout_response.status_code}"
        ErrorResponse(**logout_response.json())
        authenticated_auth_client.token = token

    @allure.title("Logout with too long access token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_with_too_long_access_token(self, authenticated_auth_client):
        headers = authenticated_auth_client.headers.copy() 
        headers["Authorization"] = "Bearer " + "a" * 20480 
        response = authenticated_auth_client.logout()       
        assert response.status_code == 431, f"Expected 431, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Logout check response headers")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_check_response_headers(self, authenticated_auth_client):
        response = authenticated_auth_client.logout()       
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers["Cache-Control"] == "no-store", "Cache-Control should be no-store"
        assert response.headers["Expires"] == "0", "Expires should be 0"
        assert response.headers["Pragma"] == "no-cache", "Pragma should be no-cache"

class TestLogoutRaceConditions:
    
    @allure.title("Logout with multiple requests")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_multiple_times(self, authenticated_auth_client):
        logout_response1 = authenticated_auth_client.logout(refresh_token=authenticated_auth_client.refresh_token)
        logout_response2 = authenticated_auth_client.logout(refresh_token=authenticated_auth_client.refresh_token)

        assert logout_response1.status_code == 200, f"Expected 200, got {logout_response1.status_code}"
        LogoutResponse(**logout_response1.json())
        assert logout_response2.status_code == 401, f"Expected 401, got {logout_response2.status_code}"
        ErrorResponse(**logout_response2.json())

    @allure.title("Logout and refresh token at the same time")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_and_refresh_token_at_the_same_time(self, authenticated_auth_client):
        logout_response = authenticated_auth_client.logout(refresh_token=authenticated_auth_client.refresh_token)
        refresh_response = authenticated_auth_client.refresh_token(refresh_token=authenticated_auth_client.refresh_token)
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        LogoutResponse(**logout_response.json())
        assert refresh_response.status_code == 401, f"Expected 401, got {refresh_response.status_code}"
        ErrorResponse(**refresh_response.json())

    
@allure.feature("Authentication")
@allure.story("Logout")
@pytest.mark.api
class TestLogoutQueryManipulation:

    @allure.title("Logout fails with malformed JSON")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("json", [
                "",                                 
                "{}",                               
                "{",                                
                "}",                                
                '{"refresh_token": "qwerty"',              
                '{"refresh_token": "qwerty",}',             
                '{"refresh_token": qwerty}',                
                "{refresh_token: \"qwerty\"}",              
                '{"refresh_token": "qwerty", "refresh_token": }',
                '["refresh_token",',           
                '{"refresh_token": }', 
                '{"refresh_token": "юникод"}',
                "null",                              
                "true",                              
                "123",                               
            ])
    def test_logout_malformed_json(self, auth_client, json):
        response = auth_client.client.post(
            f"{auth_client.base_url}/v1/auth/logout",
            content=json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @allure.title("Logout without content type")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_without_content_type(self, auth_client):
        headers = auth_client.headers.copy() 
        headers.pop("Content-Type")
        response = auth_client.logout()       
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())
        auth_client.headers = headers

    @allure.title("Logout with wrong content type")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("content_type", ["text/plain", "application/xml", "application/json; charset=utf-8"])
    def test_logout_with_wrong_content_type(self, auth_client, content_type):
        headers = auth_client.headers.copy() 
        headers["Content-Type"] = content_type
        response = auth_client.logout()       
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())
        auth_client.headers = headers

    @allure.title("Logout check cache")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_check_cache(self, auth_client):
        response = auth_client.logout()       
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate", "Cache-Control header should be set to no-cache, no-store, must-revalidate"
        assert response.headers["Pragma"] == "no-cache", "Pragma header should be set to no-cache"

