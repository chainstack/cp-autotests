import pytest
from clients.api_client import NodesAPIClient, InternalAPIClient, AuthAPIClient
from config.settings import Settings
from faker import Faker

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

