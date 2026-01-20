from tests.ui.locators.base_locators import BaseLocators


class MonitoringPageLocators(BaseLocators):
    """Locators specific to the Monitoring page."""
    
    # Page structure
    MONITORING_WRAPPER = "div[data-v-3904b986]"
    MONITORING_HEADER = ".monitoring-header"
    MONITORING_TITLE = ".monitoring-title"
    MONITORING_SUBTITLE = ".monitoring-subtitle"
    
    # Sections
    MONITORING_SECTION = ".monitoring-section"
    MONITORING_SECTION_TITLE = ".monitoring-section-title"
    
    # Steps card
    MONITORING_STEPS_CARD = ".monitoring-steps-card"
    MONITORING_STEP = ".monitoring-step"
    MONITORING_STEP_NUMBER = ".monitoring-step-number"
    MONITORING_STEP_CONTENT = ".monitoring-step-content"
    MONITORING_STEP_TITLE = ".monitoring-step-title"
    MONITORING_STEP_TEXT = ".monitoring-step-text"
    
    # Command section
    MONITORING_COMMAND_ROW = ".monitoring-command-row"
    MONITORING_COMMAND_TEXT = ".monitoring-command-text"
    MONITORING_ICON_BUTTON = ".monitoring-icon-button"
    
    # Buttons
    COPY_BUTTON = "button:has(.monitoring-icon-button)"
    
    # Specific steps
    @staticmethod
    def step_by_number(number: int) -> str:
        """Get monitoring step by number."""
        return f".monitoring-step:has(.monitoring-step-number:text('{number}'))"
    
    INSTALL_EXPORTERS_STEP = ".monitoring-step:has(.monitoring-step-title:text('Install Exporters'))"
    CONFIGURE_GRAFANA_STEP = ".monitoring-step:has(.monitoring-step-title:text('Configure Grafana'))"
    ADD_DATASOURCE_STEP = ".monitoring-step:has(.monitoring-step-title:text('Add Data Source'))"
    
    # Code/Command blocks
    CODE_BLOCK = "code"
    COMMAND_CODE = "code.monitoring-command-text"
    
    # Links
    MONITORING_LINK = ".monitoring-link"
    EXTERNAL_LINK = "a[target='_blank']"
    
    # Documentation links
    GRAFANA_DOCS_LINK = "a:has-text('Grafana')"
    PROMETHEUS_DOCS_LINK = "a:has-text('Prometheus')"
    
    # Metrics section
    METRICS_SECTION = ".metrics-section"
    METRICS_CARD = ".metrics-card"
    METRICS_TITLE = ".metrics-title"
    METRICS_VALUE = ".metrics-value"
    METRICS_CHART = ".metrics-chart"
    
    # Dashboard section
    DASHBOARD_SECTION = ".dashboard-section"
    DASHBOARD_CARD = ".dashboard-card"
    DASHBOARD_TITLE = ".dashboard-title"
    DASHBOARD_PREVIEW = ".dashboard-preview"


class MonitoringCommandsLocators:
    """Locators for monitoring commands and code snippets."""
    
    # Command types
    KUBECTL_COMMAND = "code:has-text('kubectl')"
    CURL_COMMAND = "code:has-text('curl')"
    DOCKER_COMMAND = "code:has-text('docker')"
    
    # Copy functionality
    COPY_ICON = ".monitoring-icon-button svg"
    COPY_SUCCESS_MESSAGE = ".copy-success"
    COPY_ERROR_MESSAGE = ".copy-error"
    
    # Command sections
    @staticmethod
    def command_by_text(text: str) -> str:
        """Get command element by partial text."""
        return f"code:has-text('{text}')"
    
    # Specific commands
    INSTALL_EXPORTERS_COMMAND = "code:has-text('curl -sSL https://get.chainstack.com/monitoring')"
    KUBECTL_APPLY_COMMAND = "code:has-text('kubectl apply')"
    
    # Command output
    COMMAND_OUTPUT = ".command-output"
    COMMAND_SUCCESS = ".command-success"
    COMMAND_ERROR = ".command-error"


class MonitoringMetricsLocators:
    """Locators for monitoring metrics and dashboards."""
    
    # Metrics display
    METRIC_ITEM = ".metric-item"
    METRIC_LABEL = ".metric-label"
    METRIC_VALUE_TEXT = ".metric-value-text"
    METRIC_UNIT = ".metric-unit"
    METRIC_TREND = ".metric-trend"
    
    # Chart elements
    CHART_CONTAINER = ".chart-container"
    CHART_CANVAS = "canvas"
    CHART_LEGEND = ".chart-legend"
    CHART_TOOLTIP = ".chart-tooltip"
    
    # Time range selector
    TIME_RANGE_SELECTOR = ".time-range-selector"
    TIME_RANGE_BUTTON = ".time-range-button"
    TIME_RANGE_CUSTOM = ".time-range-custom"
    
    # Refresh controls
    REFRESH_BUTTON = "button:has-text('Refresh')"
    AUTO_REFRESH_TOGGLE = ".auto-refresh-toggle"
    REFRESH_INTERVAL = ".refresh-interval"
    
    # Export options
    EXPORT_BUTTON = "button:has-text('Export')"
    EXPORT_CSV = "button:has-text('Export CSV')"
    EXPORT_PNG = "button:has-text('Export PNG')"
    EXPORT_PDF = "button:has-text('Export PDF')"
    
    # Filters
    METRICS_FILTER = ".metrics-filter"
    FILTER_BY_NODE = ".filter-by-node"
    FILTER_BY_TYPE = ".filter-by-type"
    FILTER_BY_STATUS = ".filter-by-status"
