import pytest
from pathlib import Path
from dotenv import load_dotenv

from config.settings import Settings

load_dotenv()

pytest_plugins = [
    "fixtures.playwright_fixtures",
    "fixtures.api_fixtures",
    "fixtures.eth_fixtures",
    "fixtures.k8s_fixtures",
    "fixtures.ui_fixtures",
]


def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "browser(name): mark test to run on specific browser"
    )


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def config():
    """Load and provide test configuration."""
    return Settings()
