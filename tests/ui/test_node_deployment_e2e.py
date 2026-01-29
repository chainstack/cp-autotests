import pytest
import allure
from playwright.sync_api import Page, expect

from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.nodes_page import NodesListPage
from tests.ui.pages.node_deployment_page import NodeDeploymentPage
from tests.ui.constants.ui_constants import TIMEOUT_MAX, NODE_STATUS_MAX_WAIT


@allure.feature("Nodes")
@allure.story("Node Deployment E2E Flow")
@pytest.mark.ui
@pytest.mark.smoke_ui
class TestNodeDeploymentE2E:

    @allure.title("Complete node deployment flow - {protocol_name}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("protocol_name,config_name", [
        ("Ethereum Sepolia Reth Prysm", "Ethereum Sepolia Reth Prysm Nano"),
        ("Ethereum Mainnet Reth Prysm", "Ethereum Mainnet Reth Prysm Nano"),
        ("Ethereum Hoodi Reth Prysm", "Ethereum Hoodi Reth Prysm Nano"),
    ])
    def test_complete_node_deployment_flow(self, page: Page, base_url: str, config, nodes_api_client, protocol_name: str, config_name: str):
        
        with allure.step("Login to the application"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
        
        with allure.step("Navigate to nodes list page"):
            nodes_page = NodesListPage(page, base_url)
            nodes_page.open()
            nodes_page.verify_page_loaded()
        
        with allure.step("Click 'Add node' button"):
            page.click("button:has-text('+ Add node')")
        
        deployment_page = NodeDeploymentPage(page, base_url)
        
        with allure.step("Verify protocol selection page loaded"):
            deployment_page.verify_protocol_page_loaded()
            deployment_page.verify_wizard_step_active("Protocol")
        
        with allure.step(f"Select protocol: {protocol_name}"):
            deployment_page.select_protocol(protocol_name)
            deployment_page.verify_protocol_selected(protocol_name)
        
        with allure.step("Click 'Select configuration' button"):
            deployment_page.click_select_configuration()
        
        with allure.step("Verify configuration page loaded"):
            deployment_page.verify_configuration_page_loaded()
            deployment_page.verify_wizard_step_active("Configuration")
            deployment_page.verify_wizard_step_completed("Protocol")
        
        with allure.step(f"Select configuration: {config_name}"):
            deployment_page.select_configuration(config_name)
            deployment_page.verify_configuration_specs()
        
        with allure.step("Click 'Show summary' button"):
            deployment_page.click_show_summary()
        
        with allure.step("Verify summary page loaded"):
            deployment_page.verify_summary_page_loaded()
            deployment_page.verify_wizard_step_active("Summary")
            deployment_page.verify_wizard_step_completed("Configuration")
        
        with allure.step(f"Verify summary shows protocol: {protocol_name}"):
            deployment_page.verify_summary_protocol(protocol_name)
        
        with allure.step("Click 'Create node' button"):
            deployment_page.click_create_node()
        
        with allure.step("Verify node overview page loaded"):
            deployment_page.wait_for_node_creation(timeout=NODE_STATUS_MAX_WAIT)
            deployment_page.verify_overview_page_loaded()
            node_name = deployment_page.get_node_name_from_title()
            node_id = deployment_page.get_node_id_from_url()
            deployment_page.verify_node_info_card(api_client=nodes_api_client, node_id=node_id)

        with allure.step("Verify node status shows Bootstrapping"):
            deployment_page.verify_node_status("Bootstrapping")
        
        with allure.step("Wait for node status to show Running"):
            deployment_page.wait_for_particular_status("Running", timeout=NODE_STATUS_MAX_WAIT)
            deployment_page.verify_node_status("Running")
        
        with allure.step("Navigate to nodes list and verify deployed node is present"):
            nodes_page.open()
            nodes_page.verify_page_loaded()
            deployment_page.verify_node_in_list(node_name)
        
        with allure.step("Verify node info in list matches API data"):
            deployment_page.verify_node_list_info(
                node_name=node_name,
                api_client=nodes_api_client,
                node_id=node_id
            )
        
        with allure.step("Click on deployed node to open details"):
            deployment_page.click_node_in_list(node_name)
            deployment_page.verify_overview_page_loaded()
        
        with allure.step("Go to Settings tab and delete node"):
            deployment_page.click_tab("Settings")
            deployment_page.verify_active_tab("Settings")
            deployment_page.delete_node()
        
        with allure.step("Verify redirected to nodes list page"):
            nodes_page.verify_page_loaded()
        
        with allure.step("Select 'Deleted' status filter and verify deleted node appears"):
            deployment_page.select_status_filter("Deleted")
            deployment_page.verify_node_in_list(node_name, timeout=NODE_STATUS_MAX_WAIT)


@allure.feature("Nodes")
@allure.story("Node Deployment Wizard Navigation")
@pytest.mark.ui
@pytest.mark.regression_ui
class TestNodeDeploymentNavigation:

    @allure.title("Wizard back navigation - Config to Protocol")
    @allure.severity(allure.severity_level.NORMAL)
    def test_wizard_back_config_to_protocol(self, page: Page, base_url: str, config):
        """Test back navigation from configuration to protocol selection."""
        protocol_name = "Ethereum Sepolia Reth Prysm"
        
        with allure.step("Login and navigate to protocol selection"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
            
            nodes_page = NodesListPage(page, base_url)
            nodes_page.open()
            page.click("button:has-text('+ Add node')")
        
        deployment_page = NodeDeploymentPage(page, base_url)
        
        with allure.step("Select protocol and proceed to configuration"):
            deployment_page.select_protocol(protocol_name)
            deployment_page.click_select_configuration()
            deployment_page.verify_configuration_page_loaded()
        
        with allure.step("Click back button"):
            deployment_page.click_config_back()
        
        with allure.step("Verify returned to protocol selection"):
            deployment_page.verify_protocol_page_loaded()
            deployment_page.verify_wizard_step_active("Protocol")

    @allure.title("Wizard back navigation - Summary to Config")
    @allure.severity(allure.severity_level.NORMAL)
    def test_wizard_back_summary_to_config(self, page: Page, base_url: str, config):
        """Test back navigation from summary to configuration selection."""
        protocol_name = "Ethereum Sepolia Reth Prysm"
        config_name = "Ethereum Sepolia Reth Prysm Nano"
        
        with allure.step("Login and navigate through wizard to summary"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
            
            nodes_page = NodesListPage(page, base_url)
            nodes_page.open()
            page.click("button:has-text('+ Add node')")
        
        deployment_page = NodeDeploymentPage(page, base_url)
        
        with allure.step("Navigate through wizard to summary"):
            deployment_page.select_protocol(protocol_name)
            deployment_page.click_select_configuration()
            deployment_page.select_configuration(config_name)
            deployment_page.click_show_summary()
            deployment_page.verify_summary_page_loaded()
        
        with allure.step("Click back button"):
            deployment_page.click_summary_back()
        
        with allure.step("Verify returned to configuration selection"):
            deployment_page.verify_configuration_page_loaded()
            deployment_page.verify_wizard_step_active("Configuration")


@allure.feature("Nodes")
@allure.story("Node Deployment Validation")
@pytest.mark.ui
@pytest.mark.regression_ui
class TestNodeDeploymentValidation:

    @allure.title("Select configuration button disabled until protocol selected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_select_config_disabled_until_protocol_selected(self, page: Page, base_url: str, config):
        """Verify 'Select configuration' button is disabled until protocol is selected."""
        
        with allure.step("Login and navigate to protocol selection"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
            
            nodes_page = NodesListPage(page, base_url)
            nodes_page.open()
            page.click("button:has-text('+ Add node')")
        
        deployment_page = NodeDeploymentPage(page, base_url)
        
        with allure.step("Verify 'Select configuration' button is initially disabled"):
            expect(page.locator(deployment_page.locators.SELECT_CONFIG_BUTTON)).to_be_disabled()
        
        with allure.step("Select a protocol"):
            deployment_page.select_protocol("Ethereum Sepolia Reth Prysm")
        
        with allure.step("Verify 'Select configuration' button is now enabled"):
            expect(page.locator(deployment_page.locators.SELECT_CONFIG_BUTTON)).to_be_enabled()

    @allure.title("Show summary button disabled until configuration selected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_show_summary_disabled_until_config_selected(self, page: Page, base_url: str, config):
        """Verify 'Show summary' button is disabled until configuration is selected."""
        protocol_name = "Ethereum Sepolia Reth Prysm"
        
        with allure.step("Login and navigate to configuration selection"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
            
            nodes_page = NodesListPage(page, base_url)
            nodes_page.open()
            page.click("button:has-text('+ Add node')")
        
        deployment_page = NodeDeploymentPage(page, base_url)
        
        with allure.step("Select protocol and proceed to configuration"):
            deployment_page.select_protocol(protocol_name)
            deployment_page.click_select_configuration()
        
        with allure.step("Verify 'Show summary' button is initially disabled"):
            expect(page.locator(deployment_page.locators.SHOW_SUMMARY_BUTTON)).to_be_disabled()
        
        with allure.step("Select a configuration"):
            deployment_page.select_configuration("Ethereum Sepolia Reth Prysm Nano")
        
        with allure.step("Verify 'Show summary' button is now enabled"):
            expect(page.locator(deployment_page.locators.SHOW_SUMMARY_BUTTON)).to_be_enabled()


@allure.feature("Nodes")
@allure.story("Node Overview Page")
@pytest.mark.ui
@pytest.mark.regression_ui
class TestNodeOverviewPage:

    @allure.title("Node overview page shows correct tabs")
    @allure.severity(allure.severity_level.NORMAL)
    def test_node_overview_tabs(self, page: Page, base_url: str, config, existing_node_ui):
        """Verify node overview page shows correct tabs."""
        node_id = existing_node_ui
        
        with allure.step("Login and navigate to node overview"):
            login_page = LoginPage(page, base_url)
            login_page.open()
            login_page.login(config.admin_log, config.admin_pass)
            page.goto(f"{base_url}/nodes/{node_id}")
        
        deployment_page = NodeDeploymentPage(page, base_url)
        
        with allure.step("Verify overview page loaded"):
            deployment_page.verify_overview_page_loaded()
        
        with allure.step("Verify 'Overview' tab is active"):
            deployment_page.verify_active_tab("Overview")
        
        with allure.step("Click 'Settings' tab"):
            deployment_page.click_tab("Settings")
        
        with allure.step("Verify 'Settings' tab is now active"):
            deployment_page.verify_active_tab("Settings")
