import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import UserProfile, ErrorResponse
from tests.api.cases.test_cases import EMPTY_STRING_CASES, NONSTRING_CASES


@allure.feature("Authentication")
@allure.story("Username Change")
@pytest.mark.api
class TestUsernameChangeGeneral:
    #TODO clarify username requirements
    @allure.title("Change username successfully with valid username")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_change_username_success(self, authenticated_auth_client, valid_username, valid_credentials):
        response = authenticated_auth_client.change_username(valid_username)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        try:
            profile = UserProfile(**response.json())
            assert profile.username == valid_username, "Username should be updated"
            valid_credentials["username"] = valid_username
        except ValidationError as e:
            pytest.fail(f"Username change response schema validation failed: {e}")

@allure.feature("Authentication")
@allure.story("Username Change")
@pytest.mark.api
class TestUsernameChangeUsernameValidation:  

    @allure.title("Change username with missing new_username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_missing_field(self, authenticated_auth_client):
        response = authenticated_auth_client.change_username(None)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with empty new_username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("new_username", EMPTY_STRING_CASES)
    def test_change_username_empty(self, authenticated_auth_client, new_username):
        response = authenticated_auth_client.change_username(new_username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with non-string type")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("new_username", NONSTRING_CASES)
    def test_change_username_nonstring(self, authenticated_auth_client, new_username):
        response = authenticated_auth_client.change_username(new_username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with too short username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("short_username", ["a", "ab", "abc"])
    def test_change_username_too_short(self, authenticated_auth_client, short_username):
        response = authenticated_auth_client.change_username(short_username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with too long username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username", ["a" * 51, "a" * 100])
    def test_change_username_too_long(self, authenticated_auth_client, username):
        response = authenticated_auth_client.change_username(username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with invalid characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_username", [
        "user@name",
        "user name",
        "user#name",
        "user$name",
        "user%name",
        "user!name",
        "user*name",
        "user(name)",
        "user[name]",
        "user{name}",
    ])
    def test_change_username_invalid_characters(self, authenticated_auth_client, invalid_username):
        response = authenticated_auth_client.change_username(invalid_username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with special characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("special_username", [
        "user.name",
        "user_name",
        "user-name",
        "user123",
        "123user",
    ])
    def test_change_username_special_characters(self, authenticated_auth_client, special_username):
        response = authenticated_auth_client.change_username(special_username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with existing username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_already_exists(self, authenticated_auth_client, valid_credentials):
        response = authenticated_auth_client.change_username(valid_credentials["username"])
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change username with extra fields in request")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("extra_field, extra_value", [("extra_field", "extra_value"), ("is_admin", True), ("test_field", "test_value")])
    def test_change_username_extra_fields(self, authenticated_auth_client, valid_username, extra_field, extra_value):
        response = authenticated_auth_client.send_custom_request(
            "PUT",
            "/v1/auth/username",
            json={
                "new_username": valid_username,
                extra_field: extra_value
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert extra_field not in response.json(), f"Extra field {extra_field} should not be in response"

    @allure.title("Change username with SQL injection attempt")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("malicious_username", [
        "admin'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'--",
        "1' UNION SELECT * FROM users--",
    ])
    def test_change_username_sql_injection(self, authenticated_auth_client, malicious_username):
        response = authenticated_auth_client.change_username(malicious_username)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

@allure.feature("Authentication")
@allure.story("Username Change")
@pytest.mark.api
class TestUsernameChangeAccess:
    
    @allure.title("Change username fails without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_change_username_without_token(self, authenticated_auth_client, valid_username):
        token = authenticated_auth_client.token
        authenticated_auth_client.token = None
        
        response = authenticated_auth_client.change_username(valid_username)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.token = token

    @allure.title("Change username fails with invalid access token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_tokens())
    def test_change_username_invalid_token(self, authenticated_auth_client, invalid_token, valid_username):
        token = authenticated_auth_client.token
        authenticated_auth_client.token = invalid_token
        response = authenticated_auth_client.change_username(valid_username)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.token = token

    #TODO add expired token generation
    @allure.title("Change username fails with expired access token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_expired_token(self, authenticated_auth_client, valid_username):
        token = authenticated_auth_client.token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj0vVzr7B8Y8P9nGJ5pZXkJZ5JZ5JZ5JZ5JZ5JZ5"
        authenticated_auth_client.token = expired_token
        
        response = authenticated_auth_client.change_username(valid_username)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.token = token

    @allure.title("Change username with wrong auth type")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_with_wrong_auth_type(self, authenticated_auth_client, valid_username):
        headers = authenticated_auth_client.headers.copy() 
        headers["Authorization"] = "Basic " + base64.b64encode(authenticated_auth_client.token.encode()).decode() 
        response = authenticated_auth_client.change_username(valid_username)       
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Change username with wrong auth format")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_with_wrong_auth_format(self, authenticated_auth_client, valid_username):
        headers = authenticated_auth_client.headers.copy() 
        headers["Authorization"] = "Bearer " + base64.b64encode(authenticated_auth_client.token.encode()).decode() 
        response = authenticated_auth_client.change_username(valid_username)    
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Change username with too long access token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_with_too_long_access_token(self, authenticated_auth_client, valid_username):
        headers = authenticated_auth_client.headers.copy() 
        headers["Authorization"] = "Bearer " + "a" * 20480 
        response = authenticated_auth_client.change_username(valid_username)       
        assert response.status_code == 431, f"Expected 431, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Change username with revoked refresh token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_with_revoked_refresh_token(self, authenticated_auth_client, valid_username):
        authenticated_auth_client.logout()
        response = authenticated_auth_client.change_username(valid_username)       
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.login()

@allure.feature("Authentication")
@allure.story("Username Change")
@pytest.mark.api
class TestChangeUsernameHeaders:

    @allure.title("Change username without content type")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_without_content_type(self, authenticated_auth_client, valid_username):
        headers = authenticated_auth_client.headers.copy() 
        headers.pop("Content-Type")
        response = authenticated_auth_client.change_username(valid_username)  
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Change username with wrong content type")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("content_type", ["text/plain", "application/xml", "application/json; charset=utf-8"])
    def test_change_username_with_wrong_content_type(self, authenticated_auth_client, content_type, valid_username):
        headers = authenticated_auth_client.headers.copy() 
        headers["Content-Type"] = content_type
        response = authenticated_auth_client.change_username(valid_username)       
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Change username check cache")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_check_cache(self, authenticated_auth_client, valid_username):
        response = authenticated_auth_client.change_username(valid_username)       
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate", "Cache-Control header should be set to no-cache, no-store, must-revalidate"
        assert response.headers["Pragma"] == "no-cache", "Pragma header should be set to no-cache"
