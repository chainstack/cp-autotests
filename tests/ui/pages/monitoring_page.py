import allure
from playwright.sync_api import Page
from tests.ui.pages.base_page import BasePage
from tests.ui.locators.monitoring_locators import (
    MonitoringPageLocators,
    MonitoringCommandsLocators,
    MonitoringMetricsLocators
)


class MonitoringPage(BasePage):
    """Monitoring page object."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = MonitoringPageLocators()
        self.commands = MonitoringCommandsLocators()
        self.metrics = MonitoringMetricsLocators()

    @allure.step("Open monitoring page")
    def open(self):
        """Navigate to monitoring page."""
        self.navigate("/monitoring")
        self.wait_for_load()

    @allure.step("Verify page loaded")
    def verify_page_loaded(self):
        """Verify monitoring page is loaded."""
        self.verify_element_visible(self.locators.MONITORING_HEADER)
        self.verify_element_visible(self.locators.MONITORING_TITLE)

    @allure.step("Verify monitoring steps visible")
    def verify_steps_visible(self):
        """Verify monitoring setup steps are visible."""
        self.verify_element_visible(self.locators.MONITORING_STEPS_CARD)
        self.verify_element_visible(self.locators.MONITORING_STEP)

    @allure.step("Get step count")
    def get_step_count(self) -> int:
        """Get the number of monitoring steps."""
        return self.page.locator(self.locators.MONITORING_STEP).count()

    @allure.step("Verify step: {step_number}")
    def verify_step_visible(self, step_number: int):
        """Verify a specific step is visible."""
        step_selector = self.locators.step_by_number(step_number)
        self.verify_element_visible(step_selector)

    @allure.step("Get command text from step: {step_number}")
    def get_command_text(self, step_number: int) -> str:
        """Get command text from a specific step."""
        step_selector = self.locators.step_by_number(step_number)
        command_selector = f"{step_selector} {self.locators.MONITORING_COMMAND_TEXT}"
        return self.get_text(command_selector)

    @allure.step("Click copy button for command")
    def click_copy_command(self):
        """Click the copy button for a command."""
        self.click(self.locators.COPY_BUTTON)

    @allure.step("Verify install exporters command visible")
    def verify_install_exporters_command_visible(self):
        """Verify the install exporters command is visible."""
        self.verify_element_visible(self.commands.INSTALL_EXPORTERS_COMMAND)

    @allure.step("Get install exporters command")
    def get_install_exporters_command(self) -> str:
        """Get the install exporters command text."""
        return self.get_text(self.commands.INSTALL_EXPORTERS_COMMAND)

    @allure.step("Verify kubectl command visible")
    def verify_kubectl_command_visible(self):
        """Verify kubectl command is visible."""
        self.verify_element_visible(self.commands.KUBECTL_COMMAND)

    @allure.step("Verify curl command visible")
    def verify_curl_command_visible(self):
        """Verify curl command is visible."""
        self.verify_element_visible(self.commands.CURL_COMMAND)

    @allure.step("Click external link: {link_text}")
    def click_external_link(self, link_text: str):
        """Click an external documentation link."""
        link_selector = f"a:has-text('{link_text}')"
        self.click(link_selector)

    @allure.step("Verify Grafana docs link visible")
    def verify_grafana_docs_link_visible(self):
        """Verify Grafana documentation link is visible."""
        self.verify_element_visible(self.locators.GRAFANA_DOCS_LINK)

    @allure.step("Get metrics count")
    def get_metrics_count(self) -> int:
        """Get the number of metrics displayed."""
        return self.page.locator(self.metrics.METRIC_ITEM).count()

    @allure.step("Verify metric visible: {metric_name}")
    def verify_metric_visible(self, metric_name: str):
        """Verify a specific metric is visible."""
        metric_selector = f".metric-item:has(.metric-label:text('{metric_name}'))"
        self.verify_element_visible(metric_selector)

    @allure.step("Get metric value: {metric_name}")
    def get_metric_value(self, metric_name: str) -> str:
        """Get the value of a specific metric."""
        metric_selector = f".metric-item:has(.metric-label:text('{metric_name}')) .metric-value-text"
        return self.get_text(metric_selector)

    @allure.step("Click refresh button")
    def click_refresh(self):
        """Click the refresh button."""
        self.click(self.metrics.REFRESH_BUTTON)

    @allure.step("Select time range: {range_name}")
    def select_time_range(self, range_name: str):
        """Select a time range for metrics."""
        range_selector = f".time-range-button:has-text('{range_name}')"
        self.click(range_selector)

    @allure.step("Click export button")
    def click_export(self):
        """Click the export button."""
        self.click(self.metrics.EXPORT_BUTTON)

    @allure.step("Export as CSV")
    def export_as_csv(self):
        """Export metrics as CSV."""
        self.click(self.metrics.EXPORT_CSV)

    @allure.step("Verify chart visible")
    def verify_chart_visible(self):
        """Verify metrics chart is visible."""
        self.verify_element_visible(self.metrics.CHART_CONTAINER)

    @allure.step("Toggle auto-refresh")
    def toggle_auto_refresh(self):
        """Toggle auto-refresh for metrics."""
        self.click(self.metrics.AUTO_REFRESH_TOGGLE)

    @allure.step("Apply filter: {filter_type} = {filter_value}")
    def apply_filter(self, filter_type: str, filter_value: str):
        """Apply a filter to metrics."""
        if filter_type == "node":
            self.click(self.metrics.FILTER_BY_NODE)
        elif filter_type == "type":
            self.click(self.metrics.FILTER_BY_TYPE)
        elif filter_type == "status":
            self.click(self.metrics.FILTER_BY_STATUS)
        
        # Select filter value
        filter_option = f"[role='option']:has-text('{filter_value}')"
        self.click(filter_option)
