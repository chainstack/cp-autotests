import allure
from playwright.sync_api import Page, expect
from typing import Optional


class BasePage:

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')

    @allure.step("Navigate to {path}")
    def navigate(self, path: str = ""):
        url = f"{self.base_url}{path}"
        self.page.goto(url)
        allure.attach(url, "Navigated to URL", allure.attachment_type.TEXT)

    @allure.step("Wait for page load")
    def wait_for_load(self, timeout: int = 30000):
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    @allure.step("Take screenshot: {name}")
    def screenshot(self, name: str):
        screenshot_bytes = self.page.screenshot()
        allure.attach(screenshot_bytes, name, allure.attachment_type.PNG)

    @allure.step("Check for error message")
    def get_error_message(self) -> Optional[str]:
        error_selectors = [
            "[role='alert']",
            ".error-message",
            ".alert-error",
            "[data-testid='error-message']"
        ]
        
        for selector in error_selectors:
            if self.page.locator(selector).is_visible():
                return self.page.locator(selector).text_content()
        
        return None

    @allure.step("Verify no errors on page")
    def verify_no_errors(self):
        error_msg = self.get_error_message()
        if error_msg:
            allure.attach(error_msg, "Unexpected Error", allure.attachment_type.TEXT)
            raise AssertionError(f"Unexpected error on page: {error_msg}")

    @allure.step("Wait for element: {selector}")
    def wait_for_element(self, selector: str, timeout: int = 30000):
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    @allure.step("Click element: {selector}")
    def click(self, selector: str):
        self.page.click(selector)

    @allure.step("Fill input: {selector}")
    def fill(self, selector: str, value: str):
        self.page.fill(selector, value)

    @allure.step("Get text from: {selector}")
    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).text_content() or ""

    @allure.step("Verify element visible: {selector}")
    def verify_element_visible(self, selector: str):
        expect(self.page.locator(selector)).to_be_visible()

    @allure.step("Verify element not visible: {selector}")
    def verify_element_not_visible(self, selector: str):
        expect(self.page.locator(selector)).not_to_be_visible()

    @allure.step("Verify text contains: {text}")
    def verify_text_contains(self, selector: str, text: str):
        expect(self.page.locator(selector)).to_contain_text(text)

    @allure.step("Logout")
    def logout(self):
        self.click(self.locators.AVATAR_BUTTON)
        self.click(self.locators.LOGOUT_BUTTON)
    
