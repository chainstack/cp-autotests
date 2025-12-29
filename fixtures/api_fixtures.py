import pytest
from utils.api_client import NodesAPIClient, InternalAPIClient
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
def invalid_username():
    return fake.email()

@pytest.fixture
def invalid_password():
    return fake.password()