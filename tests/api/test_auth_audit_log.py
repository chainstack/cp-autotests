import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import AuditLogResponse, ErrorResponse
from tests.api.cases.const import MAX_64_BIT_INT
from tests.api.cases.test_cases import NONINTEGER_CASES
from utils.token_generator import generate_invalid_bearer_tokens
import base64


@allure.feature("Authentication")
@allure.story("Audit Log")
@pytest.mark.api
class TestAuditLogGeneral:

    @allure.title("Get audit log successfully with default pagination")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_audit_log_success(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        try:
            audit_log = AuditLogResponse(**response.json())
            assert isinstance(audit_log.results, list), "Results should be a list"
            assert audit_log.total >= 0, "Total should be non-negative"
            assert audit_log.page >= 1, "Page should be at least 1"
            assert audit_log.page_size > 0, "Page size should be positive"
        except ValidationError as e:
            pytest.fail(f"Audit log response schema validation failed: {e}")

@allure.feature("Authentication")
@allure.story("Audit Log")
@pytest.mark.api
class TestAuditLogPaginationQueryParams:

    @allure.title("Get audit log with valid pagination parameters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("page", [1, 2, 10, 50, 100, MAX_64_BIT_INT-1])
    @pytest.mark.parametrize("page_size", [10, 20, 50, MAX_64_BIT_INT-1])
    def test_get_audit_log_with_pagination(self, authenticated_auth_client, page, page_size):
        response = authenticated_auth_client.get_audit_log(page=page, page_size=page_size)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        audit_log = AuditLogResponse(**response.json())
        assert audit_log.page == page, "Page should match requested page"
        assert audit_log.page_size == page_size, "Page size should match requested size"

    @allure.title("Get audit log handler handles 64 bit integer")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("page, page_size", [(MAX_64_BIT_INT, MAX_64_BIT_INT), (MAX_64_BIT_INT+1, MAX_64_BIT_INT+1)])
    def test_get_audit_log_with_64_bit_int(self, authenticated_auth_client, page, page_size):
        response = authenticated_auth_client.get_audit_log(page=page, page_size=page_size)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        audit_log = AuditLogResponse(**response.json())
        assert audit_log.page == page, "Page should match requested page"
        assert audit_log.page_size == page_size, "Page size should match requested size"

    @allure.title("Get audit log with invalid page number")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_page", [0, -1, -10])
    def test_get_audit_log_invalid_page(self, authenticated_auth_client, invalid_page):
        response = authenticated_auth_client.get_audit_log(page=invalid_page, page_size=20)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get audit log with invalid page size")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_size", [0, -1, -10])
    def test_get_audit_log_invalid_page_size(self, authenticated_auth_client, invalid_size):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=invalid_size)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())    

    @allure.title("Get audit log with non-integer page parameter")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_page", NONINTEGER_CASES)
    def test_get_audit_log_noninteger_page(self, authenticated_auth_client, invalid_page):
        response = authenticated_auth_client.get_audit_log(page=invalid_page, page_size=20)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get audit log with non-integer page_size parameter")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_size", NONINTEGER_CASES)
    def test_get_audit_log_noninteger_page_size(self, authenticated_auth_client, invalid_size):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=invalid_size)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get audit log handles request with page param only")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_page_only(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=1)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        AuditLogResponse(**response.json())

    @allure.title("Get audit log handles request with page_size param only")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_page_size_only(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page_size=20)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        AuditLogResponse(**response.json())

    @allure.title("Get audit log with extra query parameters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("extra_field, extra_param", [("extra_field", "extra_param"), ("test", "test"), ("page_length", "1"), ("page_volume", "20")])
    def test_get_audit_log_extra_params(self, authenticated_auth_client, extra_field, extra_param):
        response = authenticated_auth_client.send_custom_request(
            "GET",
            "/v1/auth/audit-log",
            params={
                "page": 1,
                "page_size": 20,
                extra_field: extra_param
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert extra_field not in response.json(), f"Extra field {extra_field} should not be in response"
        AuditLogResponse(**response.json())

@allure.feature("Authentication")
@allure.story("Audit Log")
@pytest.mark.api
class TestAuditLogStructure:
    @allure.title("Audit log entry structure validation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_audit_log_entry_structure(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=20)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        audit_log = AuditLogResponse(**response.json())
        if len(audit_log.results) > 0:
            entry = audit_log.results[0]
            assert entry.id, "Audit entry should have id"
            assert entry.user_id, "Audit entry should have user_id"
            assert entry.action, "Audit entry should have action"
            assert entry.timestamp, "Audit entry should have timestamp"

    @allure.title("Audit log updates as expected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_audit_log_entry_structure_with_user_actions(self, authenticated_auth_client, valid_credentials, valid_username):
        authenticated_auth_client.logout()
        authenticated_auth_client.login(valid_credentials["username"], valid_credentials["password"])
        authenticated_auth_client.change_username(valid_username)
        valid_credentials["username"] = valid_username
        response = authenticated_auth_client.get_audit_log()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json()["results"][0]["action"] == "change_username", "Audit log should have change_username action"
        assert response.json()["results"][0]["user_id"] == valid_credentials["user_id"], "Audit log should have user_id"
        assert response.json()["results"][0]["timestamp"] == valid_credentials["timestamp"], "Audit log should have timestamp"
        assert response.json()["results"][1]["action"] == "login", "Audit log should have login action"
        assert response.json()["results"][1]["user_id"] == valid_credentials["user_id"], "Audit log should have user_id"
        assert response.json()["results"][1]["timestamp"] == valid_credentials["timestamp"], "Audit log should have timestamp"
        assert response.json()["results"][2]["action"] == "logout", "Audit log should have logout action"
        assert response.json()["results"][2]["user_id"] == valid_credentials["user_id"], "Audit log should have user_id"
        assert response.json()["results"][2]["timestamp"] == valid_credentials["timestamp"], "Audit log should have timestamp"    

@allure.feature("Authentication")
@allure.story("Audit Log")
@pytest.mark.api
class TestAuditLogAccess:

    @allure.title("Get audit log without access token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_audit_log_without_access_token(self, auth_client):
        response = auth_client.get_audit_log()        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @allure.title("Get audit log with invalid access token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_bearer_tokens())
    def test_get_audit_log_with_invalid_access_token(self, auth_client, invalid_token):
        response = auth_client.get_audit_log(token=invalid_token)        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

    #TODO Add cases for IDOR / Broken access control when user creation flow will be clarified

    
    @allure.title("Get audit log with wrong auth type")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_with_wrong_auth_type(self, authenticated_auth_client):
        headers = authenticated_auth_client.headers.copy() 
        headers["Authorization"] = "Basic " + base64.b64encode(authenticated_auth_client.token.encode()).decode() 
        response = authenticated_auth_client.get_audit_log()       
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Get audit log with wrong auth format")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_with_wrong_auth_format(self, authenticated_auth_client):
        headers = authenticated_auth_client.headers.copy() 
        authenticated_auth_client.headers["Authorization"] = "Bearer " + base64.b64encode(authenticated_auth_client.token.encode()).decode() 
        response = authenticated_auth_client.get_audit_log()       
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Get audit log with too long access token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_with_too_long_access_token(self, authenticated_auth_client):
        headers = authenticated_auth_client.headers.copy() 
        authenticated_auth_client.headers["Authorization"] = "Bearer " + "a" * 20480 
        response = authenticated_auth_client.get_audit_log()       
        assert response.status_code == 431, f"Expected 431, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.headers = headers

    @allure.title("Get audit log with revoked access token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_with_revoked_access_token(self, authenticated_auth_client):
        authenticated_auth_client.logout()
        response = authenticated_auth_client.get_audit_log()       
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_auth_client.login()

    @allure.title("Get audit log check response headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_check_response_headers(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log()       
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers["Cache-Control"] == "no-store", "Cache-Control should be no-store"
        assert response.headers["Expires"] == "0", "Expires should be 0"
        assert response.headers["Pragma"] == "no-cache", "Pragma should be no-cache"


    


    
