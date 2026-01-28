from tests.ui.locators.base_locators import BaseLocators


class NodeDeploymentLocators(BaseLocators):
    """Locators for node deployment wizard flow."""
    
    # Protocol selection page
    NODE_SELECTION = ".node-selection"
    NODE_SELECTION_TITLE = ".node-selection-title"
    NODE_SELECTION_SUBTITLE = ".node-selection-subtitle"
    PROTOCOL_SEARCH = ".node-selection-search-input"
    PROTOCOL_LIST = ".node-selection-protocol-list"
    PROTOCOL_CARD = ".node-selection-protocol-card"
    PROTOCOL_NAME = ".node-selection-protocol-name"
    SELECT_CONFIG_BUTTON = "button:has-text('Select configuration')"

    # Configuration selection page
    NODE_CONFIGURATION = ".node-configuration"
    NODE_CONFIGURATION_TITLE = ".node-configuration-title"
    NODE_CONFIGURATION_SUBTITLE = ".node-configuration-subtitle"
    CONFIG_CARD_GRID = ".node-configuration-card-grid"
    CONFIG_CARD = ".node-configuration-card"
    CONFIG_PILL = ".node-configuration-pill"
    CONFIG_SPEC_LIST = ".node-configuration-spec-list"
    CONFIG_SPEC_ITEM = ".node-configuration-spec-item"
    CONFIG_CLIENTS = ".node-configuration-clients"
    CONFIG_BACK_BUTTON = ".node-configuration-footer-back"
    SHOW_SUMMARY_BUTTON = "button:has-text('Show summary')"

    # Summary page
    NODE_SUMMARY = ".node-summary"
    NODE_SUMMARY_TITLE = ".node-summary-title"
    NODE_SUMMARY_SUBTITLE = ".node-summary-subtitle"
    SUMMARY_CARD = ".node-summary-card"
    SUMMARY_ROW = ".node-summary-row"
    SUMMARY_ROW_LABEL = ".node-summary-row-label"
    SUMMARY_ROW_VALUE = ".node-summary-row-value"
    SUMMARY_BACK_BUTTON = ".node-summary-footer-back"
    CREATE_NODE_BUTTON = "button:has-text('Create node')"
    
    # Node overview page
    NODE_DETAILS_LAYOUT = ".node-details-layout"
    NODE_DETAILS_HEADER = ".node-details-header"
    NODE_DETAILS_TITLE = ".node-details-title"
    NODE_DETAILS_BREADCRUMB = ".node-details-breadcrumb"
    NODE_DETAILS_STATUS = ".node-details-status-chip"
    NODE_DETAILS_META = ".node-details-meta"
    NODE_DETAILS_TABS = ".node-details-tabs"
    NODE_DETAILS_TAB = ".node-details-tab"
    NODE_DETAILS_TAB_ACTIVE = ".node-details-tab-active"
    NODE_OVERVIEW = ".node-overview"
    NODE_OVERVIEW_INFO_CARD = ".node-overview-info-card"
    NODE_OVERVIEW_ENDPOINTS = ".node-overview-endpoints"

    @staticmethod
    def tab_by_name(name: str) -> str:
        """Get tab by name."""
        return f".node-details-tab:has-text('{name}')"
    
    # Info card specific fields
    NODE_INFO_GRID = ".node-overview-info-grid"
    NODE_INFO_CELL = ".node-overview-info-cell"
    NODE_INFO_LABEL = ".node-overview-info-label"
    NODE_INFO_VALUE = ".node-overview-info-value"
    NODE_INFO_NET_VALUE = ".node-overview-info-net-value"
    
    # Wizard stepper
    WIZARD_STEPPER = ".wizard-stepper"
    WIZARD_STEP = ".wizard-step"
    WIZARD_STEP_ACTIVE = ".wizard-step.is-active"
    WIZARD_STEP_COMPLETED = ".wizard-step.is-completed"
    WIZARD_STEP_LABEL = ".wizard-step-label"

    @staticmethod
    def wizard_step_by_name(name: str) -> str:
        """Get wizard step by name."""
        return f".wizard-step:has(.wizard-step-label:text('{name}'))"

    @staticmethod
    def protocol_card_by_name(name: str) -> str:
        """Get protocol card by name."""
        return f".node-selection-protocol-card:has(.node-selection-protocol-name:text('{name}'))"

    @staticmethod
    def config_card_by_name(name: str) -> str:
        """Get configuration card by name."""
        return f".node-configuration-card:has(.node-configuration-pill:text('{name}'))"
    
    # Node settings page
    NODE_SETTINGS = ".node-settings"
    NODE_SETTINGS_SECTION = ".node-settings-section"
    NODE_SETTINGS_DELETE_BLOCK = ".node-settings-delete-block"
    DELETE_NODE_BUTTON = "button:has-text('Delete node')"
    
    # Delete confirmation dialog
    DELETE_CONFIRM_CARD = ".node-settings-delete-confirm-card"
    DELETE_CONFIRM_TEXT = ".node-settings-delete-text"
    DELETE_CANCEL_BUTTON = ".primary-button--cancel"
    DELETE_CONFIRM_BUTTON = ".node-settings-delete-confirm-card .primary-button--danger"
    
    # Nodes list page
    NODES_LIST_PAGE = ".nodes-list-page"
    NODES_LIST_HEADER = ".nodes-list-header"
    NODE_ITEM = ".node-item"
    NODE_ITEM_TITLE = ".node-item-title"
    NODE_STATUS_DROPDOWN = ".nodes-status-dropdown"
    STATUS_DROPDOWN_OPTION = ".nodes-status-option"
    ADD_NODE_BUTTON = "button:has-text('+ Add node')"

    @staticmethod
    def node_by_name(name: str) -> str:
        """Get node item by name using text search in list body."""
        return f".nodes-list-body >> text='{name}'"
    
    @staticmethod
    def dropdown_option_by_name(name: str) -> str:
        """Get dropdown option by name."""
        return f".nodes-status-option:has(.nodes-status-option-label:text('{name}'))"
        

