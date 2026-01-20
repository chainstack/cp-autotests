"""API tests for Get Node endpoint - GET /v1/ui/nodes/{id}."""
import pytest
import allure
import base64
from pydantic import ValidationError
from tests.api.schemas.node_schemas import Node, ErrorResponse


# Helper functions for invalid token generation
def generate_invalid_tokens():
    return [
        "invalid_token",
        "Bearer invalid",
        "",
        "null",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    ]


INVALID_UUID_CASES = [
    "invalid-uuid",
    "12345",
    "not-a-uuid",
    "",
    " ",
    "00000000-0000-0000-0000-00000000000g",
    "00000000_0000_0000_0000_000000000000",
    "00000000-0000-0000-0000-0000000000001",  # Too many digits
    "00000000-0000-0000-0000-00000000000",   # Too few digits
]


@allure.feature("Nodes")
@allure.story("Get Node")
@pytest.mark.api
class TestNodesGetGeneral:

    @allure.title("Get node successfully with valid ID")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_node_success(self, authenticated_nodes_client, existing_node_id, valid_preset_instance_id):
        node_response = authenticated_nodes_client.create_node(preset_instance_id=valid_preset_instance_id)
        node_id = node_response.json()["id"]
        response = authenticated_nodes_client.get_node(node_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        try:
            node = Node(**response.json())
            assert node.id == node_id, f"Node ID mismatch"
            assert node.name, "Node name should not be empty"
            assert node.protocol, "Protocol should not be empty"
            assert node.network, "Network should not be empty"
            assert node.status, "Status should not be empty"
        except ValidationError as e:
            pytest.fail(f"Node response schema validation failed: {e}")

    @allure.title("Get node contains revision with metadata")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_node_has_revision(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "revision" in data, "Node should have revision field"
        revision = data["revision"]
        assert "id" in revision, "Revision should have ID"
        assert "metadata" in revision, "Revision should have metadata"
        assert isinstance(revision["metadata"], list), "Metadata should be a list"

    @allure.title("Get node includes correct timestamps")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_node_has_timestamps(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "created_at" in data, "Node should have created_at"
        assert "updated_at" in data, "Node should have updated_at"

    @allure.title("Get node check response headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_node_check_response_headers(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "Content-Type should be application/json"


@allure.feature("Nodes")
@allure.story("Get Node")
@pytest.mark.api
class TestNodesGetValidation:

    @allure.title("Get node with invalid UUID format")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_id", INVALID_UUID_CASES)
    def test_get_node_invalid_id_format(self, authenticated_nodes_client, invalid_id):
        response = authenticated_nodes_client.get_node(invalid_id)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get node with non-existent ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_node_not_found(self, authenticated_nodes_client):
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_nodes_client.get_node(non_existent_id)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get node with SQL injection attempt in ID")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("malicious_id", [
        "'; DROP TABLE nodes; --",
        "1 OR 1=1",
        "00000000-0000-0000-0000-000000000000' OR '1'='1",
        "<script>alert('xss')</script>",
    ])
    def test_get_node_sql_injection(self, authenticated_nodes_client, malicious_id):
        response = authenticated_nodes_client.get_node(malicious_id)
        
        # Should be rejected with 400, not 500
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Get node with path traversal attempt")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("malicious_id", [
        "../../../etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "00000000-0000-0000-0000-000000000000/../",
    ])
    def test_get_node_path_traversal(self, authenticated_nodes_client, malicious_id):
        response = authenticated_nodes_client.get_node(malicious_id)
        
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"


@allure.feature("Nodes")
@allure.story("Get Node")
@pytest.mark.api
class TestNodesGetAccess:

    @allure.title("Get node without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_node_without_auth_token(self, authenticated_nodes_client, existing_node_id):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = None
        
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("Get node with invalid authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_tokens())
    def test_get_node_with_invalid_token(self, authenticated_nodes_client, existing_node_id, invalid_token):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = invalid_token
        
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("Get node with wrong auth type (Basic instead of Bearer)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_node_with_wrong_auth_type(self, authenticated_nodes_client, existing_node_id):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = "Basic " + base64.b64encode(token.encode()).decode()
        
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token
