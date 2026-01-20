"""API tests for Node List endpoint - GET /v1/ui/nodes."""
import pytest
import allure
import base64
from pydantic import ValidationError
from tests.api.schemas.node_schemas import NodeListResponse, NodeListItem, ErrorResponse


# Helper functions for invalid token generation
def generate_invalid_tokens():
    return [
        "invalid_token",
        "Bearer invalid",
        "",
        "null",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    ]


@allure.feature("Nodes")
@allure.story("List Nodes")
@pytest.mark.api
class TestNodesListGeneral:

    @allure.title("List nodes successfully with valid authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_list_nodes_success(self, authenticated_nodes_client):
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        try:
            list_response = NodeListResponse(**response.json())
            assert isinstance(list_response.results, list), "Results should be a list"
            assert isinstance(list_response.total, int), "Total should be an integer"
            assert list_response.total >= 0, "Total should be non-negative"
        except ValidationError as e:
            pytest.fail(f"Node list response schema validation failed: {e}")

    @allure.title("List nodes returns total matching results count")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_nodes_total_matches_results(self, authenticated_nodes_client):
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Total should match the number of results or indicate pagination
        assert data.get("total", 0) >= len(data.get("results", [])), \
            "Total should be >= results count"

    @allure.title("List nodes validates each node item structure")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_nodes_validates_item_structure(self, authenticated_nodes_client):
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        for item in data.get("results", []):
            try:
                node_item = NodeListItem(**item)
                assert node_item.id, "Node ID should not be empty"
                assert node_item.name, "Node name should not be empty"
                assert node_item.protocol, "Protocol should not be empty"
                assert node_item.network, "Network should not be empty"
                assert node_item.status, "Status should not be empty"
            except ValidationError as e:
                pytest.fail(f"Node item validation failed: {e}")

    @allure.title("List nodes check response headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_nodes_check_response_headers(self, authenticated_nodes_client):
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "Content-Type should be application/json"


@allure.feature("Nodes")
@allure.story("List Nodes")
@pytest.mark.api
class TestNodesListAccess:

    @allure.title("List nodes without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_list_nodes_without_auth_token(self, authenticated_nodes_client):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = None
        
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("List nodes with invalid authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_tokens())
    def test_list_nodes_with_invalid_token(self, authenticated_nodes_client, invalid_token):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = invalid_token
        
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("List nodes with wrong auth type (Basic instead of Bearer)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_list_nodes_with_wrong_auth_type(self, authenticated_nodes_client):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = "Basic " + base64.b64encode(token.encode()).decode()
        
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("List nodes with expired token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_list_nodes_with_expired_token(self, authenticated_nodes_client):
        token = authenticated_nodes_client.token
        # Expired JWT token (exp claim in the past)
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.2H1gL8Yy0N8Zr8VqPy8gQ9Y5HvL7R3z3q2w0u8y111c"
        authenticated_nodes_client.token = expired_token
        
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("List nodes with too long token")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_nodes_with_too_long_token(self, authenticated_nodes_client):
        headers = authenticated_nodes_client.headers.copy()
        authenticated_nodes_client.headers["Authorization"] = "Bearer " + "a" * 20480
        
        response = authenticated_nodes_client.list_nodes()
        
        # Could be 401, 413, or 431 depending on implementation
        assert response.status_code in [401, 413, 431], f"Expected 401/413/431, got {response.status_code}"
        authenticated_nodes_client.headers = headers
