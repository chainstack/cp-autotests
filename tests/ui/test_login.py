import pytest
import allure
from playwright.sync_api import Page, expect
from tests.ui.pages.login_page import LoginPage



@allure.feature("Authentication")
@allure.story("Login Page")
@pytest.mark.ui
@pytest.mark.smoke
class TestLoginPage:

    @allure.title("Login page loads correctly")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_loads(self, page: Page, base_url: str):
        login_page = LoginPage(page, base_url)
        login_page.open()
        login_page.verify_page_loaded()

    @allure.title("Login page displays logo")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_page_logo(self, page: Page, base_url: str):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        logo = page.locator(login_page.locators.logo)
        expect(logo).to_be_visible()
        
        logo_src = logo.get_attribute("src")
        assert "Chainstack-logo" in logo_src, f"Expected Chainstack logo, got {logo_src}"

    @allure.title("Password toggle button is present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_password_toggle(self, page: Page, base_url: str):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        toggle_button = page.locator(login_page.locators.password_toggle)
        expect(toggle_button).to_be_visible()
        
        aria_label = toggle_button.get_attribute("aria-label")
        assert aria_label == "Show password", f"Expected aria-label='Show password', got {aria_label}"

    @allure.title("Login button is disabled when form is empty")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_button_disabled_empty_form(self, page: Page, base_url: str):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.verify_login_button_disabled()

    @allure.title("Login button is disabled with only username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_button_disabled_username_only(self, page: Page, base_url: str, invalid_username):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.fill_username(invalid_username)
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_disabled()

    @allure.title("Login button is disabled with only password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_button_disabled_password_only(self, page: Page, base_url: str, invalid_password):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.fill_password(invalid_password)
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_disabled()

    @allure.title("Secondary link is present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_secondary_link(self, page: Page, base_url: str):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        secondary_link = page.locator(login_page.locators.secondary_link)
        expect(secondary_link).to_be_visible()
        
        link_text = secondary_link.text_content().strip()
        normalized_text = link_text.replace('\u2019', "'")
        assert "don't have credentials" in normalized_text.lower(), \
            f"Expected text to contain credentials message, got '{link_text}'"

    @allure.title("Form labels are displayed correctly")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_labels(self, page: Page, base_url: str):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        username_label = page.locator(login_page.locators.username_label)
        password_label = page.locator(login_page.locators.password_label)
        
        expect(username_label).to_be_visible()
        expect(password_label).to_be_visible()
        
        expect(username_label).to_contain_text("Username")
        expect(password_label).to_contain_text("Password")

    @allure.title("Login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, page: Page, base_url: str, config):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.login(config.user_log, config.user_pass)
        login_page.verify_login_successful()

    @allure.title("Login with invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_invalid_credentials(self, page: Page, base_url: str, invalid_username, invalid_password):
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.login(invalid_username, invalid_password)
        login_page.verify_login_error()

    @allure.title("Login with empty username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_username(self, page: Page, base_url: str, ):
        """Test that login button stays disabled with empty username."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.fill_password("password123")
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_disabled()

    @allure.title("Login with empty password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_password(self, page: Page, base_url: str):
        """Test that login button stays disabled with empty password."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.fill_username("testuser")
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_disabled()

    @allure.title("Clear username field")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_username(self, page: Page, base_url: str):
        """Test clearing username field disables login button."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.fill_username("testuser")
        login_page.fill_password("password123")
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_enabled()
        
        login_page.fill_username("")
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_disabled()

    @allure.title("Clear password field")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_password(self, page: Page, base_url: str):
        """Test clearing password field disables login button."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_page.fill_username("testuser")
        login_page.fill_password("password123")
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_enabled()
        
        login_page.fill_password("")
        page.wait_for_timeout(500)
        
        login_page.verify_login_button_disabled()


@allure.feature("Authentication")
@allure.story("Login Page Accessibility")
@pytest.mark.ui
class TestLoginPageAccessibility:
    """Login page accessibility tests."""

    @allure.title("Password field has proper ARIA attributes")
    @allure.severity(allure.severity_level.NORMAL)
    def test_password_aria_attributes(self, page: Page, base_url: str):
        """Test password field has proper ARIA attributes."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        password_input = page.locator(login_page.locators.password_input)
        aria_invalid = password_input.get_attribute("aria-invalid")
        
        assert aria_invalid == "false", f"Expected aria-invalid='false', got {aria_invalid}"

    @allure.title("Username field has proper ARIA attributes")
    @allure.severity(allure.severity_level.NORMAL)
    def test_username_aria_attributes(self, page: Page, base_url: str):
        """Test username field has proper ARIA attributes."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        username_input = page.locator(login_page.locators.username_input)
        aria_invalid = username_input.get_attribute("aria-invalid")
        
        assert aria_invalid == "false", f"Expected aria-invalid='false', got {aria_invalid}"

    @allure.title("Password toggle has proper ARIA label")
    @allure.severity(allure.severity_level.NORMAL)
    def test_password_toggle_aria_label(self, page: Page, base_url: str):
        """Test password toggle button has proper ARIA label."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        toggle_button = page.locator(login_page.locators.password_toggle)
        aria_label = toggle_button.get_attribute("aria-label")
        aria_pressed = toggle_button.get_attribute("aria-pressed")
        
        assert aria_label == "Show password", f"Expected aria-label='Show password', got {aria_label}"
        assert aria_pressed == "false", f"Expected aria-pressed='false', got {aria_pressed}"

    @allure.title("Login button has proper text")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_button_text(self, page: Page, base_url: str):
        """Test login button has proper text."""
        login_page = LoginPage(page, base_url)
        login_page.open()
        
        login_button = page.locator(login_page.locators.login_button)
        expect(login_button).to_contain_text("Log in")
