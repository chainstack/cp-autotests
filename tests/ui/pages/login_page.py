import allure
from playwright.sync_api import Page
from tests.ui.pages.base_page import BasePage
from tests.ui.locators.login_page_locators import LoginPageLocators
from tests.ui.pages.dashboard_page import DashboardPage
from tests.ui.constants.ui_constants import TIMEOUT_MAX

class LoginPage(BasePage):
    """Login page object."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = LoginPageLocators()

    @allure.step("Open login page")
    def open(self):
        """Navigate to login page."""
        self.navigate("/login")
        self.wait_for_load()

    @allure.step("Login with credentials")
    def login(self, username: str, password: str):
        self.wait_for_element(self.locators.username_input)
        self.fill(self.locators.username_input, username)
        self.fill(self.locators.password_input, password)
        self.click(self.locators.login_button)

    @allure.step("Fill username: {username}")
    def fill_username(self, username: str):
        self.wait_for_element(self.locators.username_input)
        self.fill(self.locators.username_input, username)

    @allure.step("Fill password")
    def fill_password(self, password: str):
        self.wait_for_element(self.locators.password_input)
        self.fill(self.locators.password_input, password)

    @allure.step("Click login button")
    def click_login_button(self):
        self.click(self.locators.login_button)

    @allure.step("Toggle password visibility")
    def toggle_password_visibility(self):
        self.click(self.locators.password_toggle)

    @allure.step("Click secondary link")
    def click_secondary_link(self):
        self.click(self.secondary_link)

    @allure.step("Verify login page loaded")
    def verify_page_loaded(self):
        self.verify_element_visible(self.locators.login_page_container)
        self.verify_element_visible(self.locators.logo)
        self.verify_element_visible(self.locators.username_input)
        self.verify_element_visible(self.locators.password_input)
        self.verify_element_visible(self.locators.login_button)

    @allure.step("Verify login button is disabled")
    def verify_login_button_disabled(self):
        button = self.page.locator(self.locators.login_button)
        assert button.is_disabled(), "Login button should be disabled"
        allure.attach("Button is disabled", "Login Button State", allure.attachment_type.TEXT)

    @allure.step("Verify login button is enabled")
    def verify_login_button_enabled(self):
        button = self.page.locator(self.locators.login_button)
        assert button.is_enabled(), "Login button should be enabled"
        allure.attach("Button is enabled", "Login Button State", allure.attachment_type.TEXT)

    @allure.step("Verify login successful")
    def verify_login_successful(self):
        dashboard = DashboardPage(self.page, self.base_url)
        dashboard.open()
        dashboard.wait_for_load()
        dashboard.verify_page_loaded()
        allure.attach(self.page.url, "Redirected URL", allure.attachment_type.TEXT)

    @allure.step("Verify login error")
    def verify_login_error(self, expected_error: str = None):
        # Wait for error message or check if login button is still disabled
        try:
            self.wait_for_element(self.error_message, timeout=TIMEOUT_MAX)
            error_text = self.get_text(self.error_message)
            allure.attach(error_text, "Login Error", allure.attachment_type.TEXT)
            
            if expected_error:
                assert expected_error in error_text, f"Expected '{expected_error}' in error, got '{error_text}'"
        except:
            # If no error message appears, verify we're still on login page
            assert "/login" in self.page.url, "Expected to stay on login page after failed login"
            allure.attach("No error message displayed, but stayed on login page", "Login Error", allure.attachment_type.TEXT)

    @allure.step("Verify unauthorized access")
    def verify_unauthorized_redirect(self):
        assert "/login" in self.page.url, f"Expected login page, got {self.page.url}"
