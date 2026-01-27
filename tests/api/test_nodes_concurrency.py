import pytest
import allure
import concurrent.futures
import threading
from tests.api.schemas.node_schemas import CreateNodeResponse


@allure.feature("Nodes")
@allure.story("Concurrency")
@pytest.mark.api
class TestNodesConcurrency:

    @allure.title("Concurrent node creation requests")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_create_requests(self, authenticated_nodes_client, valid_eth_preset_instance_id):

        num_concurrent = 3
        created_nodes = []
        errors = []
        lock = threading.Lock()

        def create_node():
            try:
                response = authenticated_nodes_client.create_node(
                    preset_instance_id=valid_eth_preset_instance_id
                )
                with lock:
                    if response.status_code == 201:
                        created_nodes.append(response.json()["deployment_id"])
                    else:
                        errors.append(f"Status {response.status_code}: {response.text}")
            except Exception as e:
                with lock:
                    errors.append(str(e))

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(create_node) for _ in range(num_concurrent)]
            concurrent.futures.wait(futures)

        assert len(errors) == 0, f"Errors during concurrent creation: {errors}"
        assert len(created_nodes) == num_concurrent, \
            f"Expected {num_concurrent} nodes, got {len(created_nodes)}"
        
        assert len(set(created_nodes)) == len(created_nodes), \
            f"Duplicate node IDs returned: {created_nodes}"

    @pytest.mark.xfail(reason="https://chainstack.myjetbrains.com/youtrack/issue/CORE-13622/Control-panelNodes-API-500-when-repeated-node-deletion")
    @allure.title("Concurrent delete requests on same node")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_delete_same_node(self, authenticated_nodes_client, existing_node_id):

        authenticated_nodes_client._wait_node_until_ready(existing_node_id)
        
        num_concurrent = 3
        responses = []
        lock = threading.Lock()

        def delete_node():
            try:
                response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
                with lock:
                    responses.append(response.status_code)
            except Exception as e:
                with lock:
                    responses.append(str(e))

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(delete_node) for _ in range(num_concurrent)]
            concurrent.futures.wait(futures)

        success_count = responses.count(200)
        assert success_count >= 1, f"Expected at least one successful delete, got: {responses}"
        assert 500 not in responses, f"Internal server error during concurrent delete: {responses}"

    @allure.title("Concurrent get requests on same node")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_get_same_node(self, authenticated_nodes_client, existing_node_id):
        num_concurrent = 5
        responses = []
        lock = threading.Lock()

        def get_node():
            response = authenticated_nodes_client.get_node(existing_node_id)
            with lock:
                responses.append(response.json() if response.status_code == 200 else None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(get_node) for _ in range(num_concurrent)]
            concurrent.futures.wait(futures)
        assert all(r is not None for r in responses), "Some requests failed"
        
        node_ids = [r["id"] for r in responses]
        assert all(id == existing_node_id for id in node_ids), \
            "Inconsistent node data returned"
