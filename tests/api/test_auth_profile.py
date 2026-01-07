import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import UserProfile, ErrorResponse
from utils.token_generator import generate_invalid_tokens


@allure.feature("Authentication")
@allure.story("User Profile")
@pytest.mark.api
class TestProfile:

    @allure.title("Successfully retrieve user profile with valid token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_profile_success(self, authenticated_auth_client):
        response = authenticated_auth_client.get_profile()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        try:
            profile = UserProfile(**response.json())
            assert profile.id, "User id should not be empty"
            assert profile.username, "Username should not be empty"
            assert profile.email, "Email should not be empty"
            # assert profile.tenant_id, "Tenant id should not be empty"
            # assert profile.tenant_name, "Tenant name should not be empty"
            # assert profile.tenant_role, "Tenant role should not be empty"
        except ValidationError as e:
            pytest.fail(f"Profile schema validation failed: {e}")

    @allure.title("Get profile fails without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_profile_without_token(self, auth_client):
        response = auth_client.get_profile()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get profile fails with invalid token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_tokens())
    def test_get_profile_invalid_token(self, auth_client, invalid_token):
        auth_client.token = invalid_token
        
        response = auth_client.get_profile()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    #TODO add expired token generation
    @allure.title("Get profile fails with expired token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_profile_expired_token(self, auth_client):
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj0vVzr7B8Y8P9nGJ5pZXkJZ5JZ5JZ5JZ5JZ5JZ5"
        auth_client.token = expired_token
        
        response = auth_client.get_profile()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Profile data matches login response user data")
    @allure.severity(allure.severity_level.NORMAL)
    def test_profile_matches_login_data(self, auth_client, valid_credentials):
        from tests.api.schemas.auth_schemas import LoginResponse
        
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        assert login_response.status_code == 200
        
        login_data = LoginResponse(**login_response.json())
        
        auth_client.token = login_data.access_token
        profile_response = auth_client.get_profile()
        assert profile_response.status_code == 200
        
        profile = UserProfile(**profile_response.json())
        
        assert profile.id == login_data.user.id, "User ID should match"
        assert profile.username == login_data.user.username, "Username should match"
        assert profile.email == login_data.user.email, "Email should match"
        assert profile.tenant_id == login_data.user.tenant_id, "Tenant ID should match"
        assert profile.tenant_name == login_data.user.tenant_name, "Tenant name should match"
        assert profile.tenant_role == login_data.user.tenant_role, "Tenant role should match"

    @allure.title("Profile endpoint returns consistent data on multiple calls")
    @allure.severity(allure.severity_level.NORMAL)
    def test_profile_consistency(self, authenticated_auth_client):
        response1 = authenticated_auth_client.get_profile()
        response2 = authenticated_auth_client.get_profile()
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        profile1 = UserProfile(**response1.json())
        profile2 = UserProfile(**response2.json())
        
        assert profile1.model_dump() == profile2.model_dump(), "Profile data should be consistent across multiple calls"

    @allure.title("Profile contains valid email format")
    @allure.severity(allure.severity_level.MINOR)
    def test_profile_email_format(self, authenticated_auth_client):
        response = authenticated_auth_client.get_profile()
        
        assert response.status_code == 200
        
        profile = UserProfile(**response.json())
        assert "@" in profile.email, "Email should contain @ symbol"
        assert "." in profile.email.split("@")[1], "Email domain should contain a dot"

    @allure.title("Profile contains valid UUID format for IDs")
    @allure.severity(allure.severity_level.MINOR)
    def test_profile_uuid_format(self, authenticated_auth_client):
        import uuid
        
        response = authenticated_auth_client.get_profile()
        
        assert response.status_code == 200
        
        profile = UserProfile(**response.json())
        
        try:
            uuid.UUID(profile.id)
            uuid.UUID(profile.tenant_id)
        except ValueError:
            pytest.fail("User ID and Tenant ID should be valid UUIDs")

    @allure.title("Profile contains valid tenant role")
    @allure.severity(allure.severity_level.NORMAL)
    def test_profile_tenant_role(self, authenticated_auth_client):
        response = authenticated_auth_client.get_profile()
        
        assert response.status_code == 200
        
        profile = UserProfile(**response.json())
        valid_roles = ["owner", "admin", "editor", "viewer"]
        
        assert profile.tenant_role, "Tenant role should not be empty"
