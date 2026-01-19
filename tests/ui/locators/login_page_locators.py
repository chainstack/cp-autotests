class LoginPageLocators:
    # Main container
    login_page_container = ".login-page"
    
    # Logo
    logo = "role=img[name='logo']"
    logo_fallback = ".login-logo-icon"
    
    # Form inputs
    username_input = "input[autocomplete='username']"
    password_input = "input[type='password']"
    
    # Labels
    username_label = "text=Username"
    password_label = "text=Password"
    
    # Password toggle
    password_toggle = "role=button[name='Show password']"
    
    # Buttons
    login_button = "role=button[name=/log in/i]"
    secondary_link = "role=button[name=/don.?t have credentials/i]"
    
    # Error messages
    error_message = "role=alert"
    error_message_fallback = ".toast-region, .error-message"