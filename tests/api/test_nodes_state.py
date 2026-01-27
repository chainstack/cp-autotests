import pytest
import allure
import time
from pydantic import ValidationError
from tests.api.schemas.node_schemas import Node, ErrorResponse
from control_panel.node import NodeState


@allure.feature("Nodes")
@allure.story("State Transitions")
@pytest.mark.api
class TestNodesStateTransitions:

    @pytest.mark.xfail(reason="https://chainstack.myjetbrains.com/youtrack/issue/CORE-13625/Control-panelNodes-API-500-when-POST-schedule-delete-with-pending-status")
    @allure.title("Cannot delete node in pending state")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cannot_delete_pending_node(self, authenticated_nodes_client, valid_eth_preset_instance_id):
        create_response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_eth_preset_instance_id
        )
        assert create_response.status_code == 201, f"Failed to create node: {create_response.status_code}"
        node_id = create_response.json()["deployment_id"]
        
        get_response = authenticated_nodes_client.get_node(node_id)
        assert get_response.status_code == 200
        assert get_response.json()["status"] == NodeState.PENDING, "Node should be in pending state"
        
        delete_response = authenticated_nodes_client.schedule_delete_node(node_id)
        
        assert delete_response.status_code == 400, \
            f"Expected 400 for pending node deletion, got {delete_response.status_code}"

    @allure.title("Running node can be scheduled for deletion")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_running_node_can_be_deleted(self, authenticated_nodes_client, existing_node_id):
        node_status = authenticated_nodes_client.get_node(existing_node_id).json()["status"]
        if node_status == NodeState.PENDING:
            authenticated_nodes_client._wait_node_until_status(existing_node_id, NodeState.RUNNING)
        
        get_response = authenticated_nodes_client.get_node(existing_node_id)
        assert get_response.json()["status"] == NodeState.RUNNING, "Node should be running"
        
        delete_response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        assert delete_response.status_code == 200, \
            f"Expected 200 for running node deletion, got {delete_response.status_code}"

    @allure.title("Get deleted node shows deleted status")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_deleted_node_shows_deleted_status(self, authenticated_nodes_client, existing_node_id):
        node_status = authenticated_nodes_client.get_node(existing_node_id).json()["status"]
        if node_status == NodeState.PENDING:
            authenticated_nodes_client._wait_node_until_status(existing_node_id, NodeState.RUNNING)
        
        get_response = authenticated_nodes_client.get_node(existing_node_id)
        assert get_response.json()["status"] == NodeState.RUNNING, "Node should be running"
        
        delete_response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        assert delete_response.status_code == 200
        assert delete_response.json()["state"] == NodeState.DELETING
        
        authenticated_nodes_client._wait_node_until_status(existing_node_id, NodeState.DELETED)
        
        get_response = authenticated_nodes_client.get_node(existing_node_id)
        assert get_response.status_code == 200
        node_status = get_response.json()["status"]
        assert node_status == NodeState.DELETED, \
            f"Expected deleted status, got {node_status}"

    @allure.title("Node in pending state eventually transitions to running")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pending_node_transitions_to_running(self, authenticated_nodes_client, valid_eth_preset_instance_id):
        create_response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_eth_preset_instance_id
        )
        assert create_response.status_code == 201
        node_id = create_response.json()["deployment_id"]
        
        get_response = authenticated_nodes_client.get_node(node_id)
        assert get_response.status_code == 200
        initial_status = get_response.json()["status"]
        assert initial_status == NodeState.PENDING, f"Expected pending, got {initial_status}"
        
        authenticated_nodes_client._wait_node_until_status(node_id, NodeState.RUNNING)
        
        get_response = authenticated_nodes_client.get_node(node_id)
        assert get_response.status_code == 200
        final_status = get_response.json()["status"]
        assert final_status == NodeState.RUNNING, f"Expected running, got {final_status}"
        
