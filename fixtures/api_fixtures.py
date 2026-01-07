import pytest
from utils.api_client import NodesAPIClient, InternalAPIClient, AuthAPIClient
from config.settings import Settings
from faker import Faker

fake = Faker()

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


@pytest.fixture
def authenticated_client(config: Settings):
    client = NodesAPIClient(config)
    yield client
    client.close()


@pytest.fixture
def auth_client(config: Settings):
    client = AuthAPIClient(config)
    yield client
    client.close()


@pytest.fixture
def authenticated_auth_client(config: Settings):
    client = AuthAPIClient(config)
    if config.user_log and config.user_pass:
        response = client.login(config.user_log, config.user_pass)
        if response.status_code == 200:
            token = response.json().get("access_token")
            client.token = token
    yield client
    client.close()


@pytest.fixture
def valid_credentials(config: Settings):
    return {
        "username": config.user_log,
        "password": config.user_pass
    }


@pytest.fixture
def invalid_username():
    return fake.email()


@pytest.fixture
def invalid_password():
    return fake.password()


@pytest.fixture
def invalid_credentials(invalid_username, invalid_password):
    return {
        "username": invalid_username,
        "password": invalid_password
    }