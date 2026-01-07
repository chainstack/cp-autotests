import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import ChangePasswordResponse, ErrorResponse
from tests.api.cases.test_cases import EMPTY_STRING_CASES, NONSTRING_CASES

fake = Faker()

@allure.feature("Authentication")
@allure.story("Password Change")
@pytest.mark.api
class TestPasswordChange:

    @allure.title("Change password successfully with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    # TODO: clarify credentials requirements
    def test_change_password_success(self, authenticated_auth_client, valid_credentials, valid_password):
        response = authenticated_auth_client.change_password(
            old_password=valid_credentials["password"],
            new_password=valid_password
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        try:
            change_response = ChangePasswordResponse(**response.json())
            assert change_response.message, "Response should contain success message"
            valid_credentials["password"] = valid_password
        except ValidationError as e:
            pytest.fail(f"Password change response schema validation failed: {e}")

    @allure.title("Change password requires authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_password_requires_auth(self, auth_client, valid_credentials, valid_password):
        response = auth_client.change_password(
            old_password=valid_credentials["password"],
            new_password=valid_password
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with missing old password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_password_missing_old_password(self, authenticated_auth_client, valid_password):
        response = authenticated_auth_client.change_password(
            new_password=valid_password
        )
        
        assert response.status_code== 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with missing new password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_password_missing_new_password(self, authenticated_auth_client, valid_credentials):
        response = authenticated_auth_client.change_password(
            old_password=valid_credentials["password"]
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Change password with empty old password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("old_password", EMPTY_STRING_CASES)
    def test_change_password_empty_old_password(self, authenticated_auth_client, old_password, valid_password):
        response = authenticated_auth_client.change_password(
            old_password=old_password,
            new_password=valid_password
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with empty new password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("new_password", EMPTY_STRING_CASES)
    def test_change_password_empty_new_password(self, authenticated_auth_client, valid_credentials, new_password):
        response = authenticated_auth_client.change_password(
            old_password=valid_credentials["password"],
            new_password=new_password
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with non-string old password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("old_password", NONSTRING_CASES)
    def test_change_password_nonstring_old_password(self, authenticated_auth_client, old_password, valid_password):
        response = authenticated_auth_client.change_password(
            old_password=old_password,
            new_password=valid_password
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with non-string new password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("new_password", NONSTRING_CASES)
    def test_change_password_nonstring_new_password(self, authenticated_auth_client, valid_credentials, new_password):
        response = authenticated_auth_client.change_password(
            old_password=valid_credentials["password"],
            new_password=new_password
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with weak new password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("weak_password", WEAK_PASSWORD_CASES)
    def test_change_password_weak_password(self, authenticated_auth_client, valid_credentials, weak_password):
        response = authenticated_auth_client.change_password(
            old_password=valid_credentials["password"],
            new_password=weak_password
        )
        
        assert response.status_code == 400, f"Expected 400 or 501, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with same old and new password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_password_same_passwords(self, authenticated_auth_client, valid_credentials):
        response = authenticated_auth_client.change_password(
            old_password=valid_credentials["password"],
            new_password=valid_credentials["password"]
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Change password with extra fields in request")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("extra_field, extra_value", [("extra_field", "extra_value"), ("extra_field2", "extra_value2"), ("extra_field3", "extra_value3")])
    def test_change_password_extra_fields(self, authenticated_auth_client, valid_credentials, valid_password, extra_field, extra_value):
        response = authenticated_auth_client.send_custom_request(
            method="PUT",
            url="/v1/auth/password",
            json={
                "old_password": valid_credentials["password"],
                "new_password": valid_password,
                extra_field: extra_value
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert extra_field not in response.json(), f"Extra field {extra_field} should not be in response"


    @allure.title("Change password with incorrect old password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_password_wrong_old_password(self, authenticated_auth_client, valid_password, invalid_password):
        response = authenticated_auth_client.change_password(
            old_password=invalid_password,
            new_password=valid_password
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())
