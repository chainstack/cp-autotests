from tests.ui.locators.base_locators import BaseLocators


class NodesPageLocators(BaseLocators):
    """Locators specific to the Nodes page."""
    
    # Page wrapper
    NODES_WRAPPER = ".nodes-wrapper"
    
    # First login screen
    NODES_FIRST_LOGIN = ".nodes-first-login"
    NODES_TITLE = ".nodes-title"
    NODES_SUBTITLE = ".nodes-subtitle"
    NODES_DESCRIPTION = ".nodes-description"
    NODES_HEADER = ".nodes-header"
    NODES_HEADER_TEXT = ".nodes-header-text"
    
    # Buttons
    NODES_CREATE_BUTTON = ".nodes-create-button"
    NODES_LINK_BUTTON = ".nodes-link-button"
    PRIMARY_BUTTON = ".primary-button"
    
    # Bottom cards
    NODES_BOTTOM_CARDS = ".nodes-bottom-cards"
    INFO_CARD = ".info-card"
    INFO_CARD_HEADER = ".info-card-header"
    INFO_CARD_TITLE = ".info-card-title"
    INFO_CARD_ICON = ".info-card-icon"
    INFO_CARD_TEXT = ".info-card-text"
    
    # Specific buttons by text
    @staticmethod
    def button_by_text(text: str) -> str:
        """Get button by text content."""
        return f"button:has-text('{text}')"
    
    # Create node button
    CREATE_NODE_BUTTON = "button:has-text('Create node')"
    READ_MORE_BUTTON = "button:has-text('Read more about deploying nodes')"
    
    # Info cards
    LEARN_ABOUT_NODES_CARD = "button.info-card:has(.info-card-title:text('Learn about nodes'))"
    DOCUMENTATION_CARD = "button.info-card:has(.info-card-title:text('Documentation'))"
    SUPPORT_CARD = "button.info-card:has(.info-card-title:text('Support'))"


class NodesListLocators:
    """Locators for nodes list view."""
    
    # List page
    NODES_LIST_PAGE = ".nodes-list-page"
    NODES_LIST_HEADER = ".nodes-list-header"
    NODES_LIST_TITLE = ".nodes-list-title"
    
    # Tabs
    NODES_LIST_TABS = ".nodes-list-tabs"
    NODES_LIST_TAB = ".nodes-list-tab"
    NODES_LIST_TAB_ACTIVE = ".nodes-list-tab-active"
    
    # Node items
    NODE_ITEM = ".node-item"
    NODE_ITEM_HEADER = ".node-item-header"
    NODE_ITEM_TITLE = ".node-item-title"
    NODE_ITEM_STATUS = ".node-item-status"
    NODE_ITEM_ACTIONS = ".node-item-actions"
    
    # Filters and search
    NODES_SEARCH = ".nodes-search"
    NODES_FILTER = ".nodes-filter"
    NODES_SORT = ".nodes-sort"
