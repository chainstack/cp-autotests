import allure
from playwright.sync_api import Page, expect
import re
from tests.ui.pages.base_page import BasePage
from tests.ui.locators.node_deployment_locators import NodeDeploymentLocators
from tests.ui.constants.ui_constants import TIMEOUT_MAX


class NodeDeploymentPage(BasePage):
    """Page object for the node deployment wizard flow."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = NodeDeploymentLocators()

    # Protocol Selection Page Methods
    @allure.step("Verify protocol selection page loaded")
    def verify_protocol_page_loaded(self):
        """Verify protocol selection page is loaded."""
        self.verify_element_visible(self.locators.NODE_SELECTION)
        self.verify_element_visible(self.locators.PROTOCOL_LIST)

    @allure.step("Search for protocol: {protocol_name}")
    def search_protocol(self, protocol_name: str):
        """Search for a protocol."""
        self.fill(self.locators.PROTOCOL_SEARCH, protocol_name)

    @allure.step("Select protocol: {protocol_name}")
    def select_protocol(self, protocol_name: str):
        """Select a protocol by name."""
        card_selector = self.locators.protocol_card_by_name(protocol_name)
        self.click(card_selector)

    @allure.step("Click 'Select configuration' button")
    def click_select_configuration(self):
        """Click the select configuration button."""
        self.click(self.locators.SELECT_CONFIG_BUTTON)

    @allure.step("Verify protocol card selected: {protocol_name}")
    def verify_protocol_selected(self, protocol_name: str):
        """Verify a protocol card is selected."""
        card_selector = self.locators.protocol_card_by_name(protocol_name)
        # After selection, button should be enabled
        expect(self.page.locator(self.locators.SELECT_CONFIG_BUTTON)).to_be_enabled()

    # Configuration Selection Page Methods
    @allure.step("Verify configuration page loaded")
    def verify_configuration_page_loaded(self):
        """Verify configuration selection page is loaded."""
        self.verify_element_visible(self.locators.NODE_CONFIGURATION)
        self.verify_element_visible(self.locators.CONFIG_CARD_GRID)

    @allure.step("Select configuration: {config_name}")
    def select_configuration(self, config_name: str):
        """Select a configuration by name."""
        card_selector = self.locators.config_card_by_name(config_name)
        self.click(card_selector)

    @allure.step("Click 'Show summary' button")
    def click_show_summary(self):
        """Click the show summary button."""
        self.click(self.locators.SHOW_SUMMARY_BUTTON)

    @allure.step("Click back button on configuration page")
    def click_config_back(self):
        """Click the back button on configuration page."""
        self.click(self.locators.CONFIG_BACK_BUTTON)

    @allure.step("Verify configuration specs visible")
    def verify_configuration_specs(self):
        """Verify configuration specs are visible."""
        self.verify_element_visible(self.locators.CONFIG_SPEC_LIST)
        self.verify_element_visible(self.locators.CONFIG_CLIENTS)

    # Summary Page Methods
    @allure.step("Verify summary page loaded")
    def verify_summary_page_loaded(self):
        """Verify summary page is loaded."""
        self.verify_element_visible(self.locators.NODE_SUMMARY)
        self.verify_element_visible(self.locators.SUMMARY_CARD)

    @allure.step("Verify summary shows protocol: {protocol_name}")
    def verify_summary_protocol(self, protocol_name: str):
        """Verify summary shows correct protocol."""
        summary_text = self.get_text(self.locators.SUMMARY_CARD)
        assert protocol_name in summary_text, f"Expected '{protocol_name}' in summary, got '{summary_text}'"

    @allure.step("Click 'Create node' button")
    def click_create_node(self):
        """Click the create node button."""
        self.click(self.locators.CREATE_NODE_BUTTON)

    @allure.step("Click back button on summary page")
    def click_summary_back(self):
        """Click the back button on summary page."""
        self.click(self.locators.SUMMARY_BACK_BUTTON)

    # Node Overview Page Methods
    @allure.step("Verify node overview page loaded")
    def verify_overview_page_loaded(self):
        """Verify node overview page is loaded."""
        self.verify_element_visible(self.locators.NODE_DETAILS_LAYOUT)
        self.verify_element_visible(self.locators.NODE_DETAILS_HEADER)

    @allure.step("Get node status")
    def get_node_status(self) -> str:
        """Get the current node status."""
        return self.get_text(self.locators.NODE_DETAILS_STATUS)

    @allure.step("Verify node status is: {expected_status}")
    def verify_node_status(self, expected_status: str):
        """Verify node has expected status."""
        status = self.get_node_status()
        assert expected_status.lower() in status.lower(), f"Expected '{expected_status}' in status, got '{status}'"

    @allure.step("Verify node name in header: {node_name}")
    def verify_node_name(self, node_name: str):
        """Verify node name is displayed in header."""
        title = self.get_text(self.locators.NODE_DETAILS_TITLE)
        assert node_name in title, f"Expected '{node_name}' in title, got '{title}'"

    def get_node_info_from_ui(self) -> dict:
        """Extract node info from UI info card."""
        info = {}
        
        # Get all info cells
        cells = self.page.locator(self.locators.NODE_INFO_CELL).all()
        
        for cell in cells:
            label = cell.locator(self.locators.NODE_INFO_LABEL).text_content() or ""
            # Try net-value first (for Protocol which has icon), then regular value
            value_locator = cell.locator(self.locators.NODE_INFO_NET_VALUE)
            if value_locator.count() > 0:
                value = value_locator.text_content() or ""
            else:
                value = cell.locator(self.locators.NODE_INFO_VALUE).text_content() or ""
            
            info[label.strip()] = value.strip()
        
        return info

    @allure.step("Verify node info card")
    def verify_node_info_card(self, api_client=None, node_id: str = None):
        """
        Verify node info card is visible and optionally compare with API data.
        
        Args:
            api_client: Optional API client instance. If provided with node_id, 
                       compares UI data with API response.
            node_id: Optional node ID to fetch from API for comparison.
        """
        self.verify_element_visible(self.locators.NODE_OVERVIEW_INFO_CARD)
        
        if api_client and node_id:
            api_response = api_client.get_node(node_id)
            assert api_response.status_code == 200, f"Failed to get node from API: {api_response.status_code}"
            api_data = api_response.json()
            
            ui_data = self.get_node_info_from_ui()
            
            if "Protocol" in ui_data:
                assert api_data["protocol"] in ui_data["Protocol"], \
                    f"Protocol mismatch: API='{api_data['protocol']}', UI='{ui_data['Protocol']}'"
            
            if "Network" in ui_data:
                assert api_data["network"] in ui_data["Network"], \
                    f"Network mismatch: API='{api_data['network']}', UI='{ui_data['Network']}'"
            
            if "Deployment ID" in ui_data:
                assert api_data["id"] in ui_data["Deployment ID"], \
                    f"Deployment ID mismatch: API='{api_data['id']}', UI='{ui_data['Deployment ID']}'"
            
            if "Revision ID" in ui_data and "revision" in api_data:
                assert api_data["revision"]["id"] in ui_data["Revision ID"], \
                    f"Revision ID mismatch: API='{api_data['revision']['id']}', UI='{ui_data['Revision ID']}'"
            
            allure.attach(
                str(api_data),
                "API Data",
                allure.attachment_type.JSON
            )
            allure.attach(
                str(ui_data),
                "UI Data",
                allure.attachment_type.JSON
            )

    @allure.step("Click tab: {tab_name}")
    def click_tab(self, tab_name: str):
        """Click a tab by name."""
        tab_selector = self.locators.tab_by_name(tab_name)
        self.click(tab_selector)

    @allure.step("Verify active tab: {tab_name}")
    def verify_active_tab(self, tab_name: str):
        """Verify the active tab."""
        active_tab_text = self.get_text(self.locators.NODE_DETAILS_TAB_ACTIVE)
        assert tab_name in active_tab_text, f"Expected '{tab_name}' in active tab, got '{active_tab_text}'"

    # Wizard Stepper Methods
    @allure.step("Verify wizard step active: {step_name}")
    def verify_wizard_step_active(self, step_name: str):
        """Verify a wizard step is active."""
        active_step_label = self.get_text(f"{self.locators.WIZARD_STEP_ACTIVE} .wizard-step-label")
        assert step_name in active_step_label, f"Expected '{step_name}' in active step, got '{active_step_label}'"

    @allure.step("Verify wizard step completed: {step_name}")
    def verify_wizard_step_completed(self, step_name: str):
        """Verify a wizard step is completed."""
        step_selector = self.locators.wizard_step_by_name(step_name)
        self.verify_element_visible(step_selector)

    @allure.step("Wait for node creation to start")
    def wait_for_node_creation(self, timeout: int = TIMEOUT_MAX):
        """Wait for node creation process to start and redirect to overview."""
        self.page.wait_for_selector(self.locators.NODE_DETAILS_LAYOUT, timeout=timeout)

    @allure.step("Wait for node to reach {expected_status} status")
    def wait_for_particular_status(self, expected_status: str, timeout: int = 120000):
        """Wait for node to reach particular status (polling)."""
        status_locator = self.page.locator(self.locators.NODE_DETAILS_STATUS)
        expect(status_locator).to_contain_text(re.compile(expected_status, re.IGNORECASE), timeout=timeout)

    # Node Settings & Deletion Methods
    @allure.step("Click 'Delete node' button")
    def click_delete_node(self):
        """Click the delete node button on settings page."""
        self.click(self.locators.DELETE_NODE_BUTTON)

    @allure.step("Confirm node deletion")
    def confirm_delete_node(self):
        """Click 'Yes, I'm sure' to confirm deletion."""
        self.verify_element_visible(self.locators.DELETE_CONFIRM_CARD)
        self.click(self.locators.DELETE_CONFIRM_BUTTON)

    @allure.step("Cancel node deletion")
    def cancel_delete_node(self):
        """Click 'Cancel' to cancel deletion."""
        self.click(self.locators.DELETE_CANCEL_BUTTON)

    @allure.step("Delete node with confirmation")
    def delete_node(self):
        """Complete node deletion flow: click delete button, then confirm."""
        self.click_delete_node()
        self.confirm_delete_node()

    # Nodes List Methods
    @allure.step("Click 'Add node' button")
    def click_add_node(self):
        """Click the add node button on nodes list page."""
        self.click(self.locators.ADD_NODE_BUTTON)

    @allure.step("Verify node exists in list: {node_name}")
    def verify_node_in_list(self, node_name: str, timeout: int = TIMEOUT_MAX):
        """Verify a node exists in the nodes list."""
        node_locator = self.page.locator(self.locators.node_by_name(node_name))
        expect(node_locator.first).to_be_visible(timeout=timeout)

    @allure.step("Verify node not in list: {node_name}")
    def verify_node_not_in_list(self, node_name: str):
        """Verify a node does not exist in the nodes list."""
        node_locator = self.page.locator(self.locators.node_by_name(node_name))
        expect(node_locator).to_have_count(0)

    @allure.step("Click node in list: {node_name}")
    def click_node_in_list(self, node_name: str):
        """Click a node in the nodes list."""
        node_locator = self.page.locator(self.locators.node_by_name(node_name))
        node_locator.first.click()

    @allure.step("Select status filter: {status}")
    def select_status_filter(self, status: str):
        """Select a status from the dropdown filter."""
        select_locator = self.page.locator(".nodes-list-filter-select")
        select_locator.select_option(label=status)
        self.page.wait_for_timeout(1000)

    @allure.step("Get node name from title")
    def get_node_name_from_title(self) -> str:
        """Extract node name from the page title."""
        title = self.get_text(self.locators.NODE_DETAILS_TITLE)
        return title.strip()
