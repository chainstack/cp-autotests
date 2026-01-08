import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import LoginResponse, ErrorResponse
from tests.api.cases.test_cases import EMPTY_STRING_CASES, NONSTRING_CASES


@allure.feature("Authentication")
@allure.story("Login")
@pytest.mark.api
class TestLogin:

    @allure.title("Successful login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_success(self, auth_client, valid_credentials):
        response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        try:
            login_data = LoginResponse(**response.json())
            assert login_data.access_token, "access_token should not be empty"
            assert login_data.refresh_token, "refresh_token should not be empty"
            #TODO add token TTL check
        except ValidationError as e:
            pytest.fail(f"Response schema validation failed: {e}")

    @allure.title("Successful recurrent login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_success(self, auth_client, valid_credentials, authenticated_auth_client):

        logout_response = authenticated_auth_client.logout()
        
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}"
        
        login_response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        ) 
        
        assert login_response.status_code == 200, f"Expected 200, got {login_response.status_code}"
        LoginResponse(**login_response.json())

    @allure.title("Login fails with invalid username")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_invalid_username(self, auth_client, invalid_username, valid_credentials):
        response = auth_client.login(
            invalid_username,
            valid_credentials["password"]
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())


    @allure.title("Login fails with invalid password")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_invalid_password(self, auth_client, valid_credentials, invalid_password):
        response = auth_client.login(
            valid_credentials["username"],
            invalid_password
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with both invalid credentials")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_invalid_credentials(self, auth_client, invalid_credentials):
        response = auth_client.login(
            invalid_credentials["username"],
            invalid_credentials["password"]
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with stripcases for username and password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username, password", [
        (f" {valid_credentials["username"]}", valid_credentials["password"]),
        (f"{valid_credentials["username"]} ", valid_credentials["password"]),
        (f" {valid_credentials["username"]} ", valid_credentials["password"]),
        (valid_credentials["username"], f" {valid_credentials["password"]}"),
        (valid_credentials["username"], f"{valid_credentials["password"]} "),
        (valid_credentials["username"], f" {valid_credentials["password"]} "),
        (f" {valid_credentials["username"]}", f" {valid_credentials["password"]}"),
        (f"{valid_credentials["username"]} ", f"{valid_credentials["password"]} "),
        (f" {valid_credentials["username"]} ", f" {valid_credentials["password"]} "),
        ])
    def test_login_stripcases(self, auth_client, username, password):
        response = auth_client.login(username, password)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with wrong case for username and password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username, password", [
        (valid_credentials["username"].upper(), valid_credentials["password"]),
        (valid_credentials["username"].lower(), valid_credentials["password"]),
        (valid_credentials["username"], valid_credentials["password"].upper()),
        (valid_credentials["username"], valid_credentials["password"].lower()),
        (valid_credentials["username"].upper(), valid_credentials["password"].upper()),
        (valid_credentials["username"].lower(), valid_credentials["password"].lower()),
        (valid_credentials["username"].upper(), valid_credentials["password"].lower()),
        (valid_credentials["username"].lower(), valid_credentials["password"].upper()),
        (valid_credentials["username"].swapcase(), valid_credentials["password"]),
        (valid_credentials["username"], valid_credentials["password"].swapcase()),
        (valid_credentials["username"].swapcase(), valid_credentials["password"].swapcase())
    ])
    def test_login_wrong_case(self, auth_client, username, password):
        response = auth_client.login(username, password)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())


    @allure.title("Login fails with bad type username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username", NONSTRING_CASES)
    def test_login_bad_type_username(self, auth_client, username, valid_credentials):
        response = auth_client.login(username, valid_credentials["password"])
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with bad type password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("password", NONSTRING_CASES)
    def test_login_bad_type_password(self, auth_client, valid_credentials, password):
        response = auth_client.login(valid_credentials["username"], password)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with missing username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_missing_username(self, auth_client, valid_credentials):
        response = auth_client.login(password=valid_credentials["password"])
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with missing password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_missing_password(self, auth_client, valid_credentials):
        response = auth_client.login(password=valid_credentials["password"])
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with empty username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username", EMPTY_STRING_CASES)
    def test_login_empty_username(self, auth_client, valid_credentials, username):
        response = auth_client.login(username, valid_credentials["password"])
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Login fails with empty password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("password", EMPTY_STRING_CASES)
    def test_login_empty_password(self, auth_client, valid_credentials, password):
        response = auth_client.login(valid_credentials["username"], password)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())
    
    @allure.title("Login fails with malformed JSON")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("json", [
                "",                                 
                "{}",                               
                "{",                                
                "}",                                
                '{"username": "user"',              
                '{"username": "user",}',             
                '{"username": user}',                
                "{username: \"user\"}",              
                '{"username": "user", "password": }',
                '["username", "password"',           
                '{"username": "user" "password": "1"}', 
                '{"username": "юзер", "password": "пароль"', 
                "null",                              
                "true",                              
                "123",                               
            ])
    def test_login_malformed_json(self, auth_client, json):
        response = auth_client.client.post(
            f"{auth_client.base_url}/v1/auth/login",
            content=json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @allure.title("Login response contains correct CORS headers")
    @allure.severity(allure.severity_level.MINOR)
    def test_login_cors_headers(self, auth_client, valid_credentials):
        response = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        cors_headers = response.headers
        #TODO clarify partial CORS headers
        assert cors_headers["Access-Control-Allow-Origin"] == "*"
        assert cors_headers["Access-Control-Allow-Methods"] == "GET, POST, PUT, DELETE, OPTIONS"
        assert cors_headers["Access-Control-Allow-Headers"] == "Content-Type, Authorization"
        assert cors_headers["Access-Control-Allow-Credentials"] == "true"

    @allure.title("Multiple successful logins generate different tokens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_multiple_tokens(self, auth_client, valid_credentials, authenticated_auth_client):
        response1 = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        
        response2 = auth_client.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        
        assert token1 != token2, "Multiple logins should generate different access tokens"

        authenticated_auth_client.token = token1
        get_profile_response = authenticated_auth_client.get_profile()
        
        assert get_profile_response.status_code == 200
        ProfileResponse(**get_profile_response.json())
        
        authenticated_auth_client.token = token2
        get_profile_response = authenticated_auth_client.get_profile()
        
        assert get_profile_response.status_code == 200
        ProfileResponse(**get_profile_response.json())


