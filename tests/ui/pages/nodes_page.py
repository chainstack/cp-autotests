import allure
from playwright.sync_api import Page
from tests.ui.pages.base_page import BasePage
from tests.ui.locators.nodes_locators import NodesPageLocators, NodesListLocators


class NodesPage(BasePage):
    """Nodes page object (first login/welcome screen)."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = NodesPageLocators()

    @allure.step("Open nodes page")
    def open(self):
        """Navigate to nodes page."""
        self.navigate("/nodes")
        self.wait_for_load()

    @allure.step("Verify page loaded")
    def verify_page_loaded(self):
        """Verify nodes welcome page is loaded."""
        self.verify_element_visible(self.locators.NODES_FIRST_LOGIN)
        self.verify_element_visible(self.locators.NODES_TITLE)
        self.verify_element_visible(self.locators.NODES_CREATE_BUTTON)

    @allure.step("Click create node button")
    def click_create_node(self):
        """Click the create node button."""
        self.click(self.locators.NODES_CREATE_BUTTON)

    @allure.step("Click read more button")
    def click_read_more(self):
        """Click the read more about deploying nodes button."""
        self.click(self.locators.NODES_LINK_BUTTON)

    @allure.step("Verify welcome message")
    def verify_welcome_message(self):
        """Verify welcome message is displayed."""
        title_text = self.get_text(self.locators.NODES_TITLE)
        assert "Welcome" in title_text, f"Expected 'Welcome' in title, got '{title_text}'"
        
        subtitle_text = self.get_text(self.locators.NODES_SUBTITLE)
        assert "deploy" in subtitle_text.lower(), f"Expected 'deploy' in subtitle, got '{subtitle_text}'"

    @allure.step("Verify info cards visible")
    def verify_info_cards_visible(self):
        """Verify info cards are displayed."""
        self.verify_element_visible(self.locators.NODES_BOTTOM_CARDS)
        self.verify_element_visible(self.locators.INFO_CARD)

    @allure.step("Click info card: {card_title}")
    def click_info_card(self, card_title: str):
        """Click an info card by title."""
        card_selector = f".info-card:has(.info-card-title:text('{card_title}'))"
        self.click(card_selector)


class NodesListPage(BasePage):
    """Nodes list page object."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.locators = NodesListLocators()

    @allure.step("Open nodes list page")
    def open(self):
        """Navigate to nodes list page."""
        self.navigate("/nodes")
        self.wait_for_load()

    @allure.step("Verify page loaded")
    def verify_page_loaded(self):
        """Verify nodes list page is loaded."""
        self.verify_element_visible(self.locators.NODES_LIST_PAGE)
        self.verify_element_visible(self.locators.NODES_LIST_HEADER)

    @allure.step("Click tab: {tab_name}")
    def click_tab(self, tab_name: str):
        """Click a tab by name."""
        tab_selector = f".nodes-list-tab:has-text('{tab_name}')"
        self.click(tab_selector)

    @allure.step("Verify active tab: {tab_name}")
    def verify_active_tab(self, tab_name: str):
        """Verify the active tab."""
        active_tab_text = self.get_text(self.locators.NODES_LIST_TAB_ACTIVE)
        assert tab_name in active_tab_text, f"Expected '{tab_name}' in active tab, got '{active_tab_text}'"

    @allure.step("Search for node: {search_term}")
    def search_nodes(self, search_term: str):
        """Search for nodes."""
        self.fill(self.locators.NODES_SEARCH, search_term)

    @allure.step("Get node count")
    def get_node_count(self) -> int:
        """Get the number of nodes displayed."""
        return self.page.locator(self.locators.NODE_ITEM).count()

    @allure.step("Click node: {node_name}")
    def click_node(self, node_name: str):
        """Click a node by name."""
        node_selector = f".node-item:has(.node-item-title:text('{node_name}'))"
        self.click(node_selector)

    @allure.step("Verify node exists: {node_name}")
    def verify_node_exists(self, node_name: str):
        """Verify a node exists in the list."""
        node_selector = f".node-item:has(.node-item-title:text('{node_name}'))"
        self.verify_element_visible(node_selector)

    @allure.step("Verify no nodes displayed")
    def verify_no_nodes(self):
        """Verify no nodes are displayed."""
        count = self.get_node_count()
        assert count == 0, f"Expected 0 nodes, found {count}"
