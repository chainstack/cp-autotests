import allure
from playwright.sync_api import Page
from tests.ui.pages.base_page import BasePage
from tests.ui.locators.settings_locators import SettingsPageLocators, SettingsFormLocators
from tests.ui.constants.ui_constants import TIMEOUT_MAX


class SettingsPage(BasePage):
    """Settings page object."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = SettingsPageLocators()
        self.form_locators = SettingsFormLocators()

    @allure.step("Open settings page")
    def open(self):
        """Navigate to settings page."""
        self.navigate("/settings")
        self.wait_for_load()

    @allure.step("Verify page loaded")
    def verify_page_loaded(self):
        """Verify settings page is loaded."""
        self.verify_element_visible(self.locators.SETTINGS_WRAPPER)
        self.verify_element_visible(self.locators.SETTINGS_TITLE)

    @allure.step("Click tab: {tab_name}")
    def click_tab(self, tab_name: str):
        """Click a settings tab."""
        tab_selector = f".nodes-list-tab:has-text('{tab_name}')"
        self.click(tab_selector)

    @allure.step("Verify active tab: {tab_name}")
    def verify_active_tab(self, tab_name: str):
        """Verify the active tab."""
        active_tab_text = self.get_text(self.locators.SETTINGS_TAB_ACTIVE)
        assert tab_name in active_tab_text, f"Expected '{tab_name}' in active tab, got '{active_tab_text}'"

    @allure.step("Fill username: {username}")
    def fill_username(self, username: str):
        """Fill username field."""
        self.wait_for_element(self.locators.USERNAME_INPUT)
        self.fill(self.locators.USERNAME_INPUT, username)

    @allure.step("Fill email: {email}")
    def fill_email(self, email: str):
        """Fill email field."""
        self.wait_for_element(self.locators.EMAIL_INPUT)
        self.fill(self.locators.EMAIL_INPUT, email)

    @allure.step("Fill password")
    def fill_password(self, password: str):
        """Fill password field."""
        self.wait_for_element(self.locators.PASSWORD_INPUT)
        self.fill(self.locators.PASSWORD_INPUT, password)

    @allure.step("Click save button")
    def click_save(self):
        """Click save button."""
        self.click(self.locators.SAVE_BUTTON)

    @allure.step("Click cancel button")
    def click_cancel(self):
        """Click cancel button."""
        self.click(self.locators.CANCEL_BUTTON)

    @allure.step("Click change password button")
    def click_change_password(self):
        """Click change password button."""
        self.click(self.locators.CHANGE_PASSWORD_BUTTON)

    @allure.step("Get username value")
    def get_username_value(self) -> str:
        """Get current username value."""
        return self.page.locator(self.locators.USERNAME_INPUT).input_value()

    @allure.step("Get email value")
    def get_email_value(self) -> str:
        """Get current email value."""
        return self.page.locator(self.locators.EMAIL_INPUT).input_value()

    @allure.step("Verify personal info section visible")
    def verify_personal_info_section_visible(self):
        """Verify personal information section is visible."""
        self.verify_element_visible(self.locators.PERSONAL_INFO_SECTION)

    @allure.step("Verify form error: {expected_error}")
    def verify_form_error(self, expected_error: str = None):
        """Verify form validation error."""
        self.wait_for_element(self.form_locators.FORM_ERROR, timeout=TIMEOUT_MAX)
        error_text = self.get_text(self.form_locators.FORM_ERROR)
        allure.attach(error_text, "Form Error", allure.attachment_type.TEXT)
        
        if expected_error:
            assert expected_error in error_text, f"Expected '{expected_error}' in error, got '{error_text}'"

    @allure.step("Verify form success")
    def verify_form_success(self):
        """Verify form submission success."""
        self.wait_for_element(self.form_locators.FORM_SUCCESS, timeout=TIMEOUT_MAX)
        success_text = self.get_text(self.form_locators.FORM_SUCCESS)
        allure.attach(success_text, "Form Success", allure.attachment_type.TEXT)

    @allure.step("Verify input invalid: {field_name}")
    def verify_input_invalid(self, field_name: str):
        """Verify input field is marked as invalid."""
        input_selector = self.locators.input_by_label(field_name)
        invalid_input = self.page.locator(input_selector).get_attribute("aria-invalid")
        assert invalid_input == "true", f"Expected input '{field_name}' to be invalid"

    @allure.step("Update personal information")
    def update_personal_info(self, username: str = None, email: str = None):
        """Update personal information."""
        if username:
            self.fill_username(username)
        if email:
            self.fill_email(email)
        self.click_save()

    @allure.step("Verify section visible: {section_title}")
    def verify_section_visible(self, section_title: str):
        """Verify a section is visible by title."""
        section_selector = self.locators.section_by_title(section_title)
        self.verify_element_visible(section_selector)

    @allure.step("Open confirmation dialog")
    def verify_confirmation_dialog(self):
        """Verify confirmation dialog is displayed."""
        self.verify_element_visible(self.form_locators.CONFIRM_DIALOG)

    @allure.step("Confirm action")
    def confirm_action(self):
        """Click confirm/yes button in dialog."""
        self.click(self.form_locators.CONFIRM_YES)

    @allure.step("Cancel action")
    def cancel_action(self):
        """Click cancel/no button in dialog."""
        self.click(self.form_locators.CONFIRM_NO)
