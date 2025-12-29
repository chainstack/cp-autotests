import pytest
from utils.eth_client import EthereumClient
from config.settings import Settings


@pytest.fixture(scope="session")
def eth_mainnet_client(config: Settings):
    if not config.eth_rpc_mainnet_url:
        pytest.skip("ETH_RPC_MAINNET_URL not configured")
    return EthereumClient(config.eth_rpc_mainnet_url)


@pytest.fixture(scope="session")
def eth_testnet_client(config: Settings):
    if not config.eth_rpc_testnet_url:
        pytest.skip("ETH_RPC_TESTNET_URL not configured")
    return EthereumClient(config.eth_rpc_testnet_url)


@pytest.fixture
def eth_client(config: Settings):
    rpc_url = config.eth_rpc_testnet_url or config.eth_rpc_mainnet_url
    if not rpc_url:
        pytest.skip("No Ethereum RPC URL configured")
    return EthereumClient(rpc_url)
