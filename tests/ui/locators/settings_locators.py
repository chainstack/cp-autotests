"""Locators for Settings page elements."""


class SettingsPageLocators:
    """Locators specific to the Settings page."""
    
    # Page structure
    SETTINGS_WRAPPER = ".nodes-list-page"
    SETTINGS_HEADER = ".nodes-list-header"
    SETTINGS_TITLE = ".nodes-list-title"
    
    # Tabs
    SETTINGS_TABS = ".nodes-list-tabs"
    SETTINGS_TAB = ".nodes-list-tab"
    SETTINGS_TAB_ACTIVE = ".nodes-list-tab-active"
    PERSONAL_TAB = "button.nodes-list-tab:has-text('Personal')"
    
    # Welcome/Settings section
    WELCOME_RIGHT = ".welcome-right"
    WELCOME_CARD = ".welcome-card"
    WELCOME_CARD_TITLE = ".welcome-card-title"
    WELCOME_CARD_SECTION = ".welcome-card-section"
    WELCOME_CARD_SECTION_GRID = ".welcome-card-section-grid"
    WELCOME_CARD_SECTION_TITLE = ".welcome-card-section-title"
    WELCOME_CARD_SECTION_SUBTITLE = ".welcome-card-section-subtitle"
    
    # Form fields
    FORM_FIELD = ".form-field"
    WELCOME_INPUT = ".welcome-input"
    FORM_INPUT_WRAP = ".form-input-wrap"
    FORM_INPUT = ".form-input"
    FORM_FLOATING_LABEL = ".form-floating-label"
    FORM_INPUT_HAS_VALUE = ".form-input.has-value"
    FORM_LABEL_FLOATED = ".form-floating-label.is-floated"
    
    # Specific input fields
    USERNAME_INPUT = "input[autocomplete='username']"
    EMAIL_INPUT = "input[autocomplete='email']"
    PASSWORD_INPUT = "input[type='password']"
    
    # Buttons
    SAVE_BUTTON = "button:has-text('Save')"
    CANCEL_BUTTON = "button:has-text('Cancel')"
    CHANGE_PASSWORD_BUTTON = "button:has-text('Change password')"
    
    # Sections by title
    @staticmethod
    def section_by_title(title: str) -> str:
        """Get section by title text."""
        return f".welcome-card:has(.welcome-card-title:text('{title}'))"
    
    PERSONAL_INFO_SECTION = ".welcome-card:has(.welcome-card-title:text('Personal Information'))"
    SECURITY_SECTION = ".welcome-card:has(.welcome-card-title:text('Security'))"
    PREFERENCES_SECTION = ".welcome-card:has(.welcome-card-title:text('Preferences'))"
    
    # Input by placeholder
    @staticmethod
    def input_by_placeholder(placeholder: str) -> str:
        """Get input field by placeholder text on parent form-field."""
        return f".form-field[placeholder='{placeholder}'] .form-input"
    
    @staticmethod
    def input_by_label(label: str) -> str:
        """Get input field by label text."""
        return f".form-field:has(label:text('{label}')) input"


class SettingsFormLocators:
    """Locators for form elements in Settings."""
    
    # Form validation
    FORM_ERROR = ".form-error"
    FORM_SUCCESS = ".form-success"
    FORM_HELPER_TEXT = ".form-helper-text"
    
    # Input states
    INPUT_INVALID = "input[aria-invalid='true']"
    INPUT_VALID = "input[aria-invalid='false']"
    INPUT_DISABLED = "input:disabled"
    INPUT_READONLY = "input:read-only"
    
    # Field groups
    FIELD_GROUP = ".field-group"
    FIELD_ROW = ".field-row"
    FIELD_COLUMN = ".field-column"
    
    # Action buttons
    SUBMIT_BUTTON = "button[type='submit']"
    RESET_BUTTON = "button[type='reset']"
    
    # Modals/Dialogs
    MODAL = ".modal"
    MODAL_HEADER = ".modal-header"
    MODAL_BODY = ".modal-body"
    MODAL_FOOTER = ".modal-footer"
    MODAL_CLOSE = ".modal-close"
    
    # Confirmation dialogs
    CONFIRM_DIALOG = ".confirm-dialog"
    CONFIRM_YES = "button:has-text('Yes')"
    CONFIRM_NO = "button:has-text('No')"
    CONFIRM_OK = "button:has-text('OK')"
    CONFIRM_CANCEL = "button:has-text('Cancel')"
