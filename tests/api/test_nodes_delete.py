import pytest
import allure
import base64
from uuid import uuid4
from pydantic import ValidationError
from tests.api.schemas.node_schemas import ScheduleDeleteNodeResponse, ErrorResponse
from tests.api.cases.test_cases import INVALID_UUID_CASES
from utils.token_generator import generate_invalid_bearer_tokens
from control_panel.node import NodeState

def generate_random_uuid():
    return str(uuid4())


@allure.feature("Nodes")
@allure.story("Delete Node")
@pytest.mark.api
class TestNodesDeleteGeneral:

    @allure.title("Schedule node deletion successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_schedule_delete_node_success(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        try:
            delete_response = ScheduleDeleteNodeResponse(**response.json())
            assert delete_response.deployment_id == existing_node_id, "Deployment ID should match"
            assert delete_response.state, "State should not be empty"
        except ValidationError as e:
            pytest.fail(f"Delete node response schema validation failed: {e}")

    @allure.title("Schedule delete check response headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_schedule_delete_check_headers(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "Content-Type should be application/json"

    @pytest.mark.xfail(reason="https://chainstack.myjetbrains.com/youtrack/issue/CORE-13622")
    @allure.title("Schedule delete same node twice")
    @allure.severity(allure.severity_level.NORMAL)
    def test_schedule_delete_twice(self, authenticated_nodes_client, existing_node_id):
        response1 = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        assert response1.status_code == 200, f"First delete: Expected 200, got {response1.status_code}"
        
        response2 = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        assert response2.status_code in [400, 404], \
            f"Second delete: Expected 400/404, got {response2.status_code}"


@allure.feature("Nodes")
@allure.story("Delete Node")
@pytest.mark.api
class TestNodesDeleteValidation:

    @allure.title("Delete node with uppercase UUID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_node_uppercase_uuid(self, authenticated_nodes_client, existing_node_id):        
        node_status = authenticated_nodes_client.get_node(existing_node_id).json()["status"]
        if node_status == NodeState.PENDING:
            authenticated_nodes_client._wait_node_until_status(existing_node_id, NodeState.RUNNING)
        
        uppercase_id = existing_node_id.upper()
        response = authenticated_nodes_client.schedule_delete_node(uppercase_id)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    @allure.title("Delete node with mixed case UUID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_node_mixed_case_uuid(self, authenticated_nodes_client, existing_node_id):
        node_status = authenticated_nodes_client.get_node(existing_node_id).json()["status"]
        if node_status == NodeState.PENDING:
            authenticated_nodes_client._wait_node_until_status(existing_node_id, NodeState.RUNNING)

        mid = len(existing_node_id) // 2
        mixed_id = existing_node_id[:mid].upper() + existing_node_id[mid:].lower()
        
        response = authenticated_nodes_client.schedule_delete_node(mixed_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    @pytest.mark.xfail(reason="chainstack.myjetbrains.com/youtrack/issue/CORE-13624")
    @allure.title("Schedule delete with invalid UUID format")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_id", INVALID_UUID_CASES)
    def test_schedule_delete_invalid_id_format(self, authenticated_nodes_client, invalid_id):
        response = authenticated_nodes_client.schedule_delete_node(invalid_id)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        ErrorResponse(**response.json())

    @pytest.mark.xfail(reason="chainstack.myjetbrains.com/youtrack/issue/CORE-13624")
    @allure.title("Schedule delete with non-existent node ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_schedule_delete_not_found(self, authenticated_nodes_client):
        non_existent_id = str(uuid4())
        response = authenticated_nodes_client.schedule_delete_node(non_existent_id)
        
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"
        ErrorResponse(**response.json())

    @allure.title("Schedule delete with SQL injection attempt in ID")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("malicious_id", [
        "'; DROP TABLE nodes; --",
        "1 OR 1=1",
        "00000000-0000-0000-0000-000000000000' OR '1'='1",
        "<script>alert('xss')</script>",
    ])
    def test_schedule_delete_sql_injection(self, authenticated_nodes_client, malicious_id):
        response = authenticated_nodes_client.schedule_delete_node(malicious_id)
        
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"
        if "application/json" in response.headers.get("Content-Type", ""):
            ErrorResponse(**response.json())

    @allure.title("Schedule delete with invalid method")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("method", ["GET", "PUT", "PATCH", "DELETE"])
    def test_schedule_delete_invalid_method(self, authenticated_nodes_client, existing_node_id, method):
        response = authenticated_nodes_client.send_custom_request(endpoint=f"/v1/ui/nodes/{existing_node_id}/schedule-delete", method=method)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@allure.feature("Nodes")
@allure.story("Delete Node")
@pytest.mark.api
class TestNodesDeleteAccess:

    @allure.title("Schedule delete without authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_schedule_delete_without_auth_token(self, authenticated_nodes_client, existing_node_id):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = None
        
        response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("Schedule delete with invalid authentication token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("invalid_token", generate_invalid_bearer_tokens())
    def test_schedule_delete_with_invalid_token(self, authenticated_nodes_client, existing_node_id, invalid_token):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = invalid_token
        
        response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token

    @allure.title("Schedule delete with wrong auth type (Basic instead of Bearer)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_schedule_delete_with_wrong_auth_type(self, authenticated_nodes_client, existing_node_id):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = "Basic " + base64.b64encode(token.encode()).decode()
        
        response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        ErrorResponse(**response.json())
        authenticated_nodes_client.token = token   
