"""API tests for Create Node endpoint - POST /v1/ui/nodes."""
import pytest
import allure
import base64
from pydantic import ValidationError
from tests.api.schemas.node_schemas import CreateNodeResponse, ErrorResponse
from tests.api.cases.test_cases import EMPTY_STRING_CASES, NONSTRING_CASES


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
@allure.story("Create Node")
@pytest.mark.api
class TestNodesCreateGeneral:

    @allure.title("Create node successfully with valid preset")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_node_success(self, authenticated_nodes_client, valid_eth_preset_instance_id, cleanup_created_node):
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_eth_preset_instance_id
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        try:
            create_response = CreateNodeResponse(**response.json())
            assert create_response.deployment_id, "Deployment ID should not be empty"
            assert create_response.initial_revision_id, "Initial revision ID should not be empty"
            assert create_response.state, "State should not be empty"
            # Store for cleanup
            cleanup_created_node["deployment_id"] = create_response.deployment_id
        except ValidationError as e:
            pytest.fail(f"Create node response schema validation failed: {e}")

    @allure.title("Create node with override values")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_with_overrides(self, authenticated_nodes_client, valid_preset_instance_id, cleanup_created_node):
        override_values = {"custom_key": "custom_value"}
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id,
            preset_override_values=override_values
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        create_response = CreateNodeResponse(**response.json())
        cleanup_created_node["deployment_id"] = create_response.deployment_id

    @allure.title("Create node with nested override values")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_with_nested_overrides(self, authenticated_nodes_client, valid_preset_instance_id, cleanup_created_node):
        override_values = {
            "config": {
                "setting_a": "value_a",
                "setting_b": {"nested_key": "nested_value"}
            }
        }
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id,
            preset_override_values=override_values
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        create_response = CreateNodeResponse(**response.json())
        cleanup_created_node["deployment_id"] = create_response.deployment_id

    @allure.title("Create node check response headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_check_response_headers(self, authenticated_nodes_client, valid_preset_instance_id, cleanup_created_node):
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "Content-Type should be application/json"
        cleanup_created_node["deployment_id"] = response.json().get("deployment_id")


@allure.feature("Nodes")
@allure.story("Create Node")
@pytest.mark.api
class TestNodesCreateValidation:

    @allure.title("Create node with missing preset_instance_id")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_missing_preset_id(self, authenticated_nodes_client):
        response = authenticated_nodes_client.post("/v1/ui/nodes", json={})
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Create node with empty preset_instance_id")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("empty_value", EMPTY_STRING_CASES)
    def test_create_node_empty_preset_id(self, authenticated_nodes_client, empty_value):
        response = authenticated_nodes_client.create_node(preset_instance_id=empty_value)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Create node with non-string preset_instance_id")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("non_string_value", NONSTRING_CASES)
    def test_create_node_nonstring_preset_id(self, authenticated_nodes_client, non_string_value):
        response = authenticated_nodes_client.post(
            "/v1/ui/nodes",
            json={"preset_instance_id": non_string_value}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Create node with invalid preset_instance_id")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_invalid_preset_id(self, authenticated_nodes_client):
        response = authenticated_nodes_client.create_node(
            preset_instance_id="invalid-preset-id-that-does-not-exist"
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Create node with SQL injection in preset_instance_id")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("malicious_value", [
        "'; DROP TABLE nodes; --",
        "1 OR 1=1",
        "<script>alert('xss')</script>",
    ])
    def test_create_node_sql_injection(self, authenticated_nodes_client, malicious_value):
        response = authenticated_nodes_client.create_node(preset_instance_id=malicious_value)
        
        # Should be rejected with 400, not 500
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Create node with extra unexpected fields")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("extra_field,extra_value", [
        ("extra_field", "extra_value"),
        ("__proto__", {"polluted": True}),
        ("constructor", {"prototype": {}}),
    ])
    def test_create_node_extra_fields(self, authenticated_nodes_client, valid_preset_instance_id, extra_field, extra_value, cleanup_created_node):
        response = authenticated_nodes_client.send_custom_request(
            method="POST",
            endpoint="/v1/ui/nodes",
            json={
                "preset_instance_id": valid_preset_instance_id,
                extra_field: extra_value
            }
        )
        
        # Server should either accept (ignoring extra fields) or reject
        assert response.status_code in [201, 400], f"Expected 201 or 400, got {response.status_code}"
        if response.status_code == 201:
            cleanup_created_node["deployment_id"] = response.json().get("deployment_id")
            assert extra_field not in response.json(), f"Extra field {extra_field} should not be in response"


@allure.feature("Nodes")
@allure.story("Create Node")
@pytest.mark.api
class TestNodesCreateAccess:

    @allure.title("Create node without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_node_without_auth_token(self, authenticated_nodes_client, valid_preset_instance_id):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = None
        
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("Create node with invalid authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_tokens())
    def test_create_node_with_invalid_token(self, authenticated_nodes_client, valid_preset_instance_id, invalid_token):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = invalid_token
        
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("Create node with wrong auth type (Basic instead of Bearer)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_node_with_wrong_auth_type(self, authenticated_nodes_client, valid_preset_instance_id):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = "Basic " + base64.b64encode(token.encode()).decode()
        
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token


@allure.feature("Nodes")
@allure.story("Create Node")
@pytest.mark.api
class TestNodesCreateContentType:

    @allure.title("Create node without content type header")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_without_content_type(self, authenticated_nodes_client, valid_preset_instance_id):
        headers = authenticated_nodes_client.headers.copy()
        if "Content-Type" in authenticated_nodes_client.headers:
            del authenticated_nodes_client.headers["Content-Type"]
        
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id
        )
        
        # Content-Type should be required for POST with body
        assert response.status_code in [400, 415], f"Expected 400/415, got {response.status_code}"
        authenticated_nodes_client.headers = headers

    @allure.title("Create node with wrong content type")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("content_type", [
        "text/plain",
        "application/xml",
        "application/x-www-form-urlencoded",
    ])
    def test_create_node_with_wrong_content_type(self, authenticated_nodes_client, valid_preset_instance_id, content_type):
        headers = authenticated_nodes_client.headers.copy()
        authenticated_nodes_client.headers["Content-Type"] = content_type
        
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_preset_instance_id
        )
        
        assert response.status_code in [400, 415], f"Expected 400/415, got {response.status_code}"
        authenticated_nodes_client.headers = headers
