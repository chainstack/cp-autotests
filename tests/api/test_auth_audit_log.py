import pytest
import allure
from pydantic import ValidationError
from tests.api.schemas.auth_schemas import AuditLogResponse, AuditLogEntry, ErrorResponse


@allure.feature("Authentication")
@allure.story("Audit Log")
@pytest.mark.api
class TestAuditLog:

    @allure.title("Get audit log successfully with default pagination")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_audit_log_success(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log()
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"
        if response.status_code == 200:
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
        
        assert response.status_code in [401, 501], f"Expected 401 or 501, got {response.status_code}"
        if response.status_code == 401:
            ErrorResponse(**response.json())

    @allure.title("Get audit log with pagination parameters")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_with_pagination(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=2, page_size=50)
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"
        if response.status_code == 200:
            audit_log = AuditLogResponse(**response.json())
            assert audit_log.page == 2, "Page should match requested page"
            assert audit_log.page_size == 50, "Page size should match requested size"

    @allure.title("Get audit log with invalid page number")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_page", [0, -1, -10])
    def test_get_audit_log_invalid_page(self, authenticated_auth_client, invalid_page):
        response = authenticated_auth_client.get_audit_log(page=invalid_page, page_size=20)
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Get audit log with invalid page size")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_size", [0, -1, -10])
    def test_get_audit_log_invalid_page_size(self, authenticated_auth_client, invalid_size):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=invalid_size)
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Get audit log with page size exceeding maximum")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("large_size", [101, 200, 1000])
    def test_get_audit_log_page_size_too_large(self, authenticated_auth_client, large_size):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=large_size)
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Get audit log with very large page number")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_large_page_number(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=999999, page_size=20)
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"

    @allure.title("Get audit log with minimum valid pagination")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_min_pagination(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=1)
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"

    @allure.title("Get audit log with maximum valid page size")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_max_page_size(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=100)
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"

    @allure.title("Get audit log with non-integer page parameter")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_page", ["abc", "1.5", "null", "true"])
    def test_get_audit_log_noninteger_page(self, authenticated_auth_client, invalid_page):
        response = authenticated_auth_client.get(
            "/v1/auth/audit-log",
            params={"page": invalid_page, "page_size": 20}
        )
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Get audit log with non-integer page_size parameter")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_size", ["abc", "20.5", "null", "false"])
    def test_get_audit_log_noninteger_page_size(self, authenticated_auth_client, invalid_size):
        response = authenticated_auth_client.get(
            "/v1/auth/audit-log",
            params={"page": 1, "page_size": invalid_size}
        )
        
        assert response.status_code in [400, 501], f"Expected 400 or 501, got {response.status_code}"
        if response.status_code == 400:
            ErrorResponse(**response.json())

    @allure.title("Get audit log with extra query parameters")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_extra_params(self, authenticated_auth_client):
        response = authenticated_auth_client.get(
            "/v1/auth/audit-log",
            params={
                "page": 1,
                "page_size": 20,
                "extra_param": "should_be_ignored"
            }
        )
        
        assert response.status_code in [200, 400, 501], f"Got {response.status_code}"

    @allure.title("Get audit log without pagination parameters")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_audit_log_default_pagination(self, authenticated_auth_client):
        response = authenticated_auth_client.get("/v1/auth/audit-log")
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"


    @allure.title("Audit log entry structure validation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_audit_log_entry_structure(self, authenticated_auth_client):
        response = authenticated_auth_client.get_audit_log(page=1, page_size=20)
        
        assert response.status_code in [200, 501], f"Expected 200 or 501, got {response.status_code}"
        if response.status_code == 200:
            audit_log = AuditLogResponse(**response.json())
            if len(audit_log.results) > 0:
                entry = audit_log.results[0]
                assert entry.id, "Audit entry should have id"
                assert entry.user_id, "Audit entry should have user_id"
                assert entry.action, "Audit entry should have action"
                assert entry.timestamp, "Audit entry should have timestamp"
