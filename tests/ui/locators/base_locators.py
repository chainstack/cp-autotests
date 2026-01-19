"""Base locators for common UI elements across all pages."""


class BaseLocators:
    """Common locators shared across all pages."""
    
    # App container
    APP_CONTAINER = "#app"
    CP_SHELL = ".cp-shell"
    
    # Sidebar
    SIDEBAR = ".sidebar"
    SIDEBAR_TOP = ".sidebar-top"
    SIDEBAR_BOTTOM = ".sidebar-bottom"
    SIDEBAR_LOGO_BUTTON = ".sidebar-logo-button"
    SIDEBAR_VERSION = ".sidebar-version"
    
    # Navigation
    SIDEBAR_NAV = ".sidebar-nav"
    SIDEBAR_NAV_ITEM = ".sidebar-nav-item"
    SIDEBAR_NAV_ITEM_ACTIVE = ".sidebar-nav-item-active"
    SIDEBAR_NAV_LABEL = ".sidebar-nav-label"
    SIDEBAR_NAV_LABEL_ACTIVE = ".sidebar-nav-label-active"
    SIDEBAR_NAV_ICON = ".sidebar-nav-icon"
    
    # Main content
    CP_SHELL_MAIN = ".cp-shell-main"
    
    # SVG icons
    SVG_INLINE_ICON = ".svg-inline-icon"
    SVG_ICON = ".svg-icon"


class SidebarNavigationLocators:
    """Locators for sidebar navigation items."""
    
    # Navigation items by icon class
    NODES_NAV_ITEM = ".svg-inline-icon--nodes"
    MONITORING_NAV_ITEM = ".svg-inline-icon--statistics"
    DOCS_NAV_ITEM = ".svg-inline-icon--documentation"
    ACTIVITY_NAV_ITEM = ".svg-inline-icon--bell"
    SETTINGS_NAV_ITEM = ".svg-inline-icon--settings"
    
    # Navigation items by label text
    @staticmethod
    def nav_item_by_label(label: str) -> str:
        """Get navigation item by label text."""
        return f"button.sidebar-nav-item:has(.sidebar-nav-label:text('{label}'))"
    
    # Active navigation item
    ACTIVE_NAV_ITEM = ".sidebar-nav-item-active"
