import pytest
import allure
from playwright.sync_api import Page, expect

from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.settings_page import SettingsPage
from tests.ui.constants.ui_constants import TIMEOUT_MAX
from tests.ui.constants.ui_errors import SettingsErrors

@pytest.fixture
def generate_valid_password(faker):
    return faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)


@allure.feature("Settings")
@allure.story("Settings page functionality validation")
@pytest.mark.ui
@pytest.mark.smoke_ui
class TestSettingsPageGeneral:

    @allure.title("Successfully change password and verify")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_password_success(self, page: Page, base_url: str, config, password_reset_teardown, generate_valid_password):

        new_password = generate_valid_password
        password_reset_teardown["new_password"] = new_password
        
        with allure.step("Login to the application"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
        
        with allure.step("Navigate to settings page"):
            settings_page = SettingsPage(page, base_url)
            settings_page.open()
            settings_page.verify_page_loaded()
        
        with allure.step("Fill password change form"):
            settings_page.fill_new_password(new_password)
            settings_page.fill_repeat_password(new_password)
            settings_page.fill_current_password(config.admin_pass)
        
        with allure.step("Verify save button is enabled"):
            settings_page.verify_save_button_enabled()
        
        with allure.step("Click save button"):
            settings_page.click_save()
        
        with allure.step("Verify success toast with 'Saved' message"):
            settings_page.verify_success_message("Saved")
        
        with allure.step("Logout & login with new password"):
            login_page.logout()
            login_page.login(config.admin_log, new_password)
    
    @allure.title("Navigate to settings page and validate it")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_validate_settings_page(self, page: Page, base_url: str, config, generate_valid_password):

        with allure.step("Login to the application"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
        
        with allure.step("Navigate to settings page"):
            settings_page = SettingsPage(page, base_url)
            settings_page.open()
            settings_page.verify_page_loaded()
        
            expect(page).to_have_url(f"{base_url}/settings", timeout=TIMEOUT_MAX)
     
        with allure.step("Verify username is pre-filled"):
            username_value = settings_page.get_username_value()
            assert username_value == config.admin_log, \
                f"Expected username '{config.admin_log}', got '{username_value}'"
               
        with allure.step("Clear username field"):
            settings_page.clear_username()
            page.locator(settings_page.locators.USERNAME_INPUT).blur()
                
        with allure.step("Verify error message appears"):
            settings_page.verify_username_error(SettingsErrors.empty_username_error)

        with allure.step("Enter invalid password"):
            invalid_password = "abc"
            settings_page.fill_new_password(invalid_password)
            page.locator(settings_page.locators.NEW_PASSWORD_INPUT).blur()
        
        with allure.step("Verify error message appears"):
            settings_page.verify_password_error(SettingsErrors.invalid_password_error)
        
        with allure.step("Enter valid password in new password field"):
            new_password = generate_valid_password
            settings_page.fill_new_password(new_password)
        
        with allure.step("Enter different password in repeat field"):
            mismatched_password = generate_valid_password + "1"
            settings_page.fill_repeat_password(mismatched_password)
            page.locator(settings_page.locators.REPEAT_PASSWORD_INPUT).blur()
        
        with allure.step("Verify error message appears"):
            settings_page.verify_repeat_password_error(SettingsErrors.password_mismatch_error)
        
        with allure.step("Verify save button is initially disabled"):
            settings_page.verify_save_button_disabled()
        
        with allure.step("Fill in new password and repeat password, but leave current password empty"):
            settings_page.fill_new_password(new_password)
            settings_page.fill_repeat_password(new_password)
        
        with allure.step("Verify save button is still disabled (current password is empty)"):
            settings_page.verify_save_button_disabled()

        with allure.step("Fill in new password and repeat password, fill current password, check save button"):
            settings_page.fill_username(config.admin_log)
            settings_page.fill_new_password(new_password)
            settings_page.fill_repeat_password(new_password)
            settings_page.fill_current_password(config.admin_pass)
            settings_page.verify_save_button_enabled()


@allure.feature("Settings")
@allure.story("Settings page form validation")
@pytest.mark.ui
@pytest.mark.regression_ui
class TestSettingsFormValidation:

    @allure.title("Settings page shows Personal Information section")
    @allure.severity(allure.severity_level.NORMAL)
    def test_personal_info_section_visible(self, page: Page, base_url: str, config):
        with allure.step("Login to the application"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
        
        with allure.step("Navigate to settings page"):
            settings_page = SettingsPage(page, base_url)
            settings_page.open()
            settings_page.verify_page_loaded()
        
        with allure.step("Verify Personal Information section is visible"):
            settings_page.verify_personal_info_section_visible(config.admin_log)

@allure.feature("Settings")
@allure.story("Settings page error messages validation")
@pytest.mark.ui
@pytest.mark.regression_ui
class TestSettingsErrorsValidation:

    @allure.title("Settings page shows error messages when requements are not met")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_password, expected_error", [
        ("abc", SettingsErrors.invalid_password_error),
        ("abracadabra!", SettingsErrors.lowercase_password_error),
        ("ABRACADABRA!", SettingsErrors.uppercase_password_error),
        ("abraCADABRA!", SettingsErrors.number_password_error),
        ("abraCADABRA1", SettingsErrors.special_character_password_error),
    ])
    def test_settings_errors_validation(self, page: Page, base_url: str, config, invalid_password, expected_error):
        
        with allure.step("Login to the application"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
        
        with allure.step("Navigate to settings page"):
            settings_page = SettingsPage(page, base_url)
            settings_page.open()
            settings_page.verify_page_loaded()

        with allure.step("Enter invalid password"):
            settings_page.fill_new_password(invalid_password)
            page.locator(settings_page.locators.NEW_PASSWORD_INPUT).blur()

        with allure.step("Verify error message appears"):
            settings_page.verify_password_error(expected_error)

    @allure.title("Settings page shows error message when current password is incorrect")
    @allure.severity(allure.severity_level.NORMAL)
    def test_settings_current_password_error(self, page: Page, base_url: str, config):
        current_invalid_password = config.admin_pass + "1"
        
        with allure.step("Login to the application"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
        
        with allure.step("Navigate to settings page"):
            settings_page = SettingsPage(page, base_url)
            settings_page.open()
            settings_page.verify_page_loaded()

        with allure.step("Fill password change form"):
            settings_page.fill_new_password("NewSecurePass123!")
            settings_page.fill_repeat_password("NewSecurePass123!")
        
        with allure.step("Enter invalid current password"):
            settings_page.fill_current_password(current_invalid_password)
            settings_page.click_save()
        
        with allure.step("Verify error message appears"):
            settings_page.verify_current_password_error(SettingsErrors.invalid_current_password_error)        
      