import pytest
import time
from clients.api_client import NodesAPIClient, InternalAPIClient, AuthAPIClient
from config.settings import Settings
from faker import Faker
from control_panel.node import NodeState

@pytest.fixture(scope="session")
def faker():
    return Faker()

@pytest.fixture(scope="session")
def nodes_api_client(config: Settings):
    client = NodesAPIClient(config)
    yield client
    client.close()


@pytest.fixture(scope="session")
def internal_api_client(config: Settings):
    client = InternalAPIClient(config)
    yield client
    client.close()


@pytest.fixture(scope="session")
def authenticated_nodes_client(config: Settings):
    client = NodesAPIClient(config)
    yield client
    client.close()


@pytest.fixture(scope="function")
def auth_client(config: Settings):
    client = AuthAPIClient(config)
    yield client
    client.close()


@pytest.fixture(scope="function")
def authenticated_auth_client(config: Settings):
    client = AuthAPIClient(config)
    if config.user_log and config.user_pass:
        response = client.login(config.user_log, config.user_pass)
        if response.status_code == 200:
            token = response.json().get("access_token")
            refresh_token = response.json().get("refresh_token")
            client.token = token
            client.refresh_token = refresh_token
        else:
            raise Exception("Login failed")
    yield client
    client.close()


@pytest.fixture
def valid_credentials(config: Settings):
    return {
        "username": config.user_log,
        "password": config.user_pass
    }


@pytest.fixture(scope="function")
def invalid_username(faker):
    return faker.email()

@pytest.fixture(scope="function")
def valid_username(faker):
    return faker.name()

@pytest.fixture(scope="function")
def valid_password(faker):
    return faker.password()


@pytest.fixture(scope="function")
def invalid_password(faker):
    return faker.password()


@pytest.fixture(scope="function")
def invalid_credentials(invalid_username, invalid_password):
    return {
        "username": invalid_username,
        "password": invalid_password
    }

@pytest.fixture(scope="function")
def password_reset_teardown(config: Settings):
    """
    Fixture to reset password after a test that changes it.
    
    Usage:
        def test_change_password(password_reset_teardown):
            new_password = "NewSecurePass123!"
            password_reset_teardown["new_password"] = new_password
            # ... test changes password via UI ...
    
    After test completes, this fixture reverts the password via API.
    """
    context = {
        "original_password": config.admin_pass,
        "new_password": None,  # Test must set this
        "username": config.admin_log,
    }
    
    yield context
    
    # Teardown: Revert password via API
    if context["new_password"]:
        # Use cp_nodes_api_url if set, otherwise derive from cp_ui_url
        api_url = config.cp_nodes_api_url if config.cp_nodes_api_url else config.cp_ui_url.rstrip('/')
        client = AuthAPIClient(Settings())
        client.base_url = api_url.rstrip('/')
        # Login with new password to get token
        login_response = client.login(context["username"], context["new_password"])
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            client.token = token
            # Change password back to original
            reset_response = client.change_password(
                old_password=context["new_password"],
                new_password=context["original_password"]
            )
            if reset_response.status_code != 200:
                print(f"WARNING: Failed to reset password: {reset_response.text}")
        else:
            print(f"WARNING: Failed to login with new password for reset: {login_response.text}")
        client.close()

# Node-specific fixtures

@pytest.fixture(scope="function")
def authenticated_nodes_client(config: Settings):
    from clients.api_client import AuthAPIClient, NodesAPIClient
    
    auth_client = AuthAPIClient(config)
    response = auth_client.login(config.admin_log, config.admin_pass)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        client = NodesAPIClient(config, token=token)
        yield client
        client.close()
    else:
        raise Exception(f"Failed to authenticate for nodes client: {response.status_code}")
    auth_client.close()


@pytest.fixture(scope="function")
def existing_node_id(authenticated_nodes_client, valid_eth_preset_instance_id):
    response = authenticated_nodes_client.list_nodes()
    if response.status_code == 200:
        nodes = response.json().get("results", [])
        if nodes:
            return nodes[0]["id"]
        return authenticated_nodes_client.create_node(preset_instance_id=valid_eth_preset_instance_id).json()["id"]
    raise Exception("Failed to get existing node ID")


@pytest.fixture(scope="session")
def valid_eth_preset_instance_id():
    return "gts.c.cp.presets.blockchain_preset.v1.0~c.cp.presets.evm_preset.v1.0~c.cp.presets.evm_reth_prysm.v1.0~c.cp.presets.ethereum_mainnet.v1.0"

@pytest.fixture(scope="session")
def invalid_eth_preset_instance_id():
    return "gts.c.cp.presets.blockchain_preset.v0.0~c.cp.presets.evm_preset.v0.0~c.cp.presets.evm_reth_prysm.v0.0~c.cp.presets.ethereum_mainnet.v0.0"


@pytest.fixture(scope="function")
def cleanup_created_node(authenticated_nodes_client):
    """Fixture to cleanup nodes created during tests.""" 
    node_data = {}
    yield node_data
    # Cleanup: schedule delete if node was created
    if "deployment_id" in node_data:
        try:
            # Wait until node is no longer pending before deleting (max 30 seconds)
            max_wait = 30
            waited = 0
            while waited < max_wait:
                response = authenticated_nodes_client.get_node(node_data["deployment_id"])
                if response.status_code == 200:
                    # API returns 'status' not 'state'
                    current_status = response.json().get("status")
                    if current_status != NodeState.PENDING:
                        break
                time.sleep(1)
                waited += 1
            
            authenticated_nodes_client.schedule_delete_node(node_data["deployment_id"])
        except Exception:
            pass  # Ignore cleanup errors

@pytest.fixture(scope="function")
def created_node_for_deletion(authenticated_nodes_client, valid_eth_preset_instance_id):
    """Create a node specifically for deletion tests."""
    deployment_response = authenticated_nodes_client.create_node(
        preset_instance_id=valid_eth_preset_instance_id
    )
    if deployment_response.status_code == 201:
        max_wait = 30
        waited = 0
        while waited < max_wait:
            response = authenticated_nodes_client.get_node(deployment_response.json()["deployment_id"])
            if response.status_code == 200:
                current_status = response.json().get("status")
                if current_status != NodeState.PENDING:
                    break
            time.sleep(1)
            waited += 1
        # Use deployment_response for deployment_id (get_node returns 'id', not 'deployment_id')
        yield {"deployment_id": deployment_response.json()["deployment_id"]}
    else:
        pytest.skip(f"Could not create node for deletion test: {deployment_response.status_code}")
