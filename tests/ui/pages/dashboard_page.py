import allure
from playwright.sync_api import Page
from tests.ui.pages.base_page import BasePage
from tests.ui.locators.dashboard_page_locators import DashboardPageLocators
from tests.ui.constants.ui_constants import TIMEOUT_MAX


class DashboardPage(BasePage):
    """Dashboard/Welcome page object."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = DashboardPageLocators()

    @allure.step("Open dashboard page")
    def open(self):
        """Navigate to dashboard page."""
        self.navigate("/")
        self.wait_for_load()

    @allure.step("Verify page loaded")
    def verify_page_loaded(self):
        """Verify dashboard page is loaded."""
        self.verify_element_visible(self.locators.welcome_page)
        self.verify_element_visible(self.locators.welcome_header)

    @allure.step("Fill setup form")
    def fill_setup_form(self, email: str, password: str, password_repeat: str, license_key: str):
        """Fill the initial setup form."""
        self.wait_for_element(self.locators.email_input)
        self.fill(self.locators.email_input, email)
        self.fill(self.locators.password_input, password)
        self.fill(self.locators.password_repeat_input, password_repeat)
        self.fill(self.locators.license_key_input, license_key)

    @allure.step("Submit setup form")
    def submit_setup_form(self):
        """Click submit button."""
        self.click(self.locators.submit_button)

    @allure.step("Toggle password visibility")
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        self.click(self.locators.password_toggle)

    @allure.step("Verify feature cards visible")
    def verify_feature_cards_visible(self):
        """Verify all feature cards are displayed."""
        self.verify_element_visible(self.locators.one_click_deployment_label)
        self.verify_element_visible(self.locators.resource_management_label)
        self.verify_element_visible(self.locators.healthcheck_label)

    @allure.step("Click Chainstack console link")
    def click_chainstack_console_link(self):
        """Click the Chainstack console link."""
        self.click(self.locators.chainstack_console_link)

    @allure.step("Verify form validation error")
    def verify_form_error(self, expected_error: str = None):
        """Verify form validation error is displayed."""
        self.wait_for_element(self.locators.error_message, timeout=TIMEOUT_MAX)
        error_text = self.get_text(self.locators.error_message)
        allure.attach(error_text, "Form Error", allure.attachment_type.TEXT)
        
        if expected_error:
            assert expected_error in error_text, f"Expected '{expected_error}' in error, got '{error_text}'"
