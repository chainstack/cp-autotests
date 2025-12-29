import pytest
from playwright.sync_api import Page
from config.settings import Settings


@pytest.fixture(scope="session")
def browser_context_args(config: Settings):
    return {
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone_id": "UTC",
        "permissions": [],
        "record_video_dir": "videos/" if config.video != "off" else None,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(config: Settings):
    return {
        "headless": config.headless,
        "slow_mo": config.slow_mo,
    }


@pytest.fixture
def authenticated_page(page: Page, config: Settings):
    if config.api_token:
        page.context.add_cookies([{
            "name": "auth_token",
            "value": config.api_token,
            "domain": "localhost",
            "path": "/"
        }])
    yield page


@pytest.fixture(scope="session")
def base_url(config: Settings):
    return config.cp_ui_url
