import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import AuditLogResponse, AuditLogEntry, ErrorResponse
from tests.api.cases.const import MAX_64_BIT_INT
from tests.api.cases.test_cases import NONINTEGER_CASES


@allure.feature("Authentication")
@allure.story("Audit Log")
@pytest.mark.api
class TestAuditLog:

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

    @allure.title("Get audit log requires authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_audit_log_requires_auth(self, auth_client):
        response = auth_client.get_audit_log()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())

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
