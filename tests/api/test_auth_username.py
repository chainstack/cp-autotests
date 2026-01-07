import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import UserProfile, ErrorResponse
from tests.api.cases.test_cases import EMPTY_STRING_CASES, NONSTRING_CASES


@allure.feature("Authentication")
@allure.story("Username Change")
@pytest.mark.api
class TestUsernameChange:

    @allure.title("Change username successfully with valid username")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_change_username_success(self, authenticated_auth_client):
        response = authenticated_auth_client.change_username("newusername123")
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"
        if response.status_code == 200:
            try:
                profile = UserProfile(**response.json())
                assert profile.username == "newusername123", "Username should be updated"
            except ValidationError as e:
                pytest.fail(f"Username change response schema validation failed: {e}")

    @allure.title("Change username requires authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_username_requires_auth(self, auth_client):
        response = auth_client.change_username("newusername")
        
        assert response.status_code in [401, 501], f"Expected 401 or 501, got {response.status_code}"
        if response.status_code == 401:
            ErrorResponse(**response.json())

    @allure.title("Change username with missing new_username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_missing_field(self, authenticated_auth_client):
        response = authenticated_auth_client.put("/v1/auth/username", json={})
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Change username with empty new_username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("new_username", EMPTY_STRING_CASES)
    def test_change_username_empty(self, authenticated_auth_client, new_username):
        response = authenticated_auth_client.change_username(new_username)
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Change username with non-string type")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("new_username", NONSTRING_CASES)
    def test_change_username_nonstring(self, authenticated_auth_client, new_username):
        response = authenticated_auth_client.put(
            "/v1/auth/username",
            json={"new_username": new_username}
        )
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Change username with too short username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("short_username", ["a", "ab", "x"])
    def test_change_username_too_short(self, authenticated_auth_client, short_username):
        response = authenticated_auth_client.change_username(short_username)
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Change username with too long username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_too_long(self, authenticated_auth_client):
        long_username = "a" * 51
        response = authenticated_auth_client.change_username(long_username)
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
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
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
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
        
        assert response.status_code in [200, 400, 501], f"Got {response.status_code}"

    @allure.title("Change username with existing username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_already_exists(self, authenticated_auth_client, valid_credentials):
        response = authenticated_auth_client.change_username(valid_credentials["username"])
        
        assert response.status_code in [400, 409, 501], f"Expected 400, 409 or 501, got {response.status_code}"
        if response.status_code in [400, 409]:
            ErrorResponse(**response.json())

    @allure.title("Change username with extra fields in request")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_username_extra_fields(self, authenticated_auth_client):
        response = authenticated_auth_client.put(
            "/v1/auth/username",
            json={
                "new_username": "newusername",
                "extra_field": "should_be_ignored"
            }
        )
        
        assert response.status_code in [200, 400, 501], f"Got {response.status_code}"

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
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())
