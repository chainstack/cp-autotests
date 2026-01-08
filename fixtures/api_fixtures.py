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
            refresh_token = response.json().get("refresh_token")
            client.token = token
            client.refresh_token = refresh_token
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
