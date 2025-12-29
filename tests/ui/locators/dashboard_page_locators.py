class DashboardPageLocators:
    # Main container
    welcome_page = ".welcome-page"
    welcome_header = ".welcome-header"
    
    # Logo
    chainstack_logo = ".welcome-header img"
    
    # Feature cards
    feature_cards = ".welcome-feature-card-protocols"
    protocols_section = ".protocols"
    
    # Feature card labels
    one_click_deployment_label = ".welcome-feature-label:has-text('One-click')"
    resource_management_label = ".welcome-feature-label:has-text('Flexible client')"
    healthcheck_label = ".welcome-feature-label:has-text('Healthcheck')"
    
    # Right side - Setup form
    welcome_right = ".welcome-right"
    welcome_card = ".welcome-card"
    welcome_card_title = ".welcome-card-title"
    
    # Form sections
    contact_section = ".welcome-card-section:has-text('Contact information')"
    privacy_section = ".welcome-card-section:has-text('Privacy')"
    license_section = ".welcome-card-section:has-text('License')"
    
    # Form inputs
    email_input = "input[type='text'][autocomplete='email']"
    password_input = "input[type='password'][autocomplete='new-password']"
    password_repeat_input = "input[type='password'][autocomplete='new-password']:nth-of-type(2)"
    license_key_input = "input[placeholder='License key']"
    
    # Password toggle
    password_toggle = ".password-toggle"
    
    # Buttons
    submit_button = ".primary-button"
    chainstack_console_link = "a:has-text('Chainstack console')"
    
    # Validation messages
    form_mandatory = ".form-mandatory"
    error_message = ".error-message, [role='alert']"
    
    # Protocol icons (feature cards)
    mouse_icon = ".svg-inline-icon--mouse-icon"
    resources_icon = ".svg-inline-icon--resources-icon"
    status_icon = ".svg-inline-icon--Status-icon"
