# Control Panel Autotests

Comprehensive test suite for the Control Panel project, covering UI, API, and end-to-end testing for Ethereum node deployment and management.

## Project Structure

```
cp-autotests/
├── config/                 # Configuration management
│   └── settings.py        # Pydantic settings with .env support
├── fixtures/              # Pytest fixtures
│   ├── api_fixtures.py    # API client fixtures
│   ├── eth_fixtures.py    # Ethereum client fixtures
│   ├── k8s_fixtures.py    # Kubernetes helper fixtures
│   └── playwright_fixtures.py  # Playwright/UI fixtures
├── utils/                 # Utility modules
│   ├── api_client.py      # HTTP API clients
│   ├── eth_client.py      # Ethereum JSON-RPC client
│   ├── k8s_helper.py      # Kubernetes operations
│   └── wait_helper.py     # Wait/polling utilities
├── tests/                 # Test suites
│   ├── ui/               # UI tests (Playwright)
│   │   ├── pages/        # Page Object Models
│   │   ├── test_auth.py
│   │   ├── test_node_lifecycle.py
│   │   └── test_error_states.py
│   ├── core/             # Core API and node tests
│   ├── rbac/             # RBAC and license tests
│   ├── workers/          # Worker and workflow tests
│   └── nonfunctional/    # Performance, chaos, security tests
├── features/             # BDD feature files (future)
├── .env.example          # Environment variables template
├── pyproject.toml        # Project config, dependencies, and uv scripts
└── docker-compose.yml   # Test infrastructure (PostgreSQL, NATS)
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Docker & Docker Compose (for test infrastructure)
- kubectl (for Kubernetes tests)
- Access to Control Panel services

**Install uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### 2. Installation

```bash
# Clone the repository
cd cp-autotests

# One-command setup (installs deps + browsers + creates .env)
uv run setup

# Or step by step:
uv sync                          # Install dependencies
uv run install-browsers          # Install Playwright browsers
cp .env.example .env             # Create config file
```

### 3. Configuration

Edit `.env` file with your environment settings:

```bash
# Base URLs
CP_NODES_API_URL=http://localhost:8080
CP_UI_URL=http://localhost:3000

# Authentication
API_TOKEN=your-token-here
API_KEY=your-api-key-here

# Ethereum (optional for full e2e tests)
ETH_RPC_TESTNET_URL=https://sepolia.infura.io/v3/YOUR-PROJECT-ID
ETH_PRIVATE_KEY=your-test-private-key

# Kubernetes
KUBECONFIG=~/.kube/config
K8S_NAMESPACE=default
```

### 4. Start Test Infrastructure (Optional)

```bash
# Start PostgreSQL and NATS for integration tests
uv run infra-up

# Check status
docker-compose ps

# View logs
uv run infra-logs

# Stop infrastructure
uv run infra-down
```

### 5. Run Tests

```bash
# Run all tests
uv run test

# Run UI tests only
uv run test-ui

# Run smoke tests
uv run test-smoke

# Run critical tests
uv run test-critical

# Run tests in parallel
uv run test-parallel

# Generate and open Allure report
uv run report
```

## Test Categories

### UI Tests (`tests/ui/`)

Playwright-based UI tests covering:
- **Authentication**: Login, logout, token validation
- **Node Lifecycle**: Create, view, update, delete nodes
- **Error States**: Form validation, backend errors, network issues
- **Presets**: Browse and select node presets

**Cross-browser support**: Tests run on Chromium, Firefox, and WebKit (Safari) by default.

**Markers**: `@pytest.mark.ui`, `@pytest.mark.smoke`, `@pytest.mark.critical`

**Run**: `uv run test-ui` or `uv run pytest -m ui`

**Browser-specific runs**:
```bash
# Run on specific browser only
pytest tests/ui/ --browser chromium
pytest tests/ui/ --browser firefox
pytest tests/ui/ --browser webkit

# Run on multiple browsers
pytest tests/ui/ --browser chromium --browser firefox

# Run with headed mode (see browser)
pytest tests/ui/ --headed

# Run on all browsers (default)
pytest tests/ui/
```

### Core Tests (`tests/core/`)

API and node functionality tests:
- Node creation and state transitions
- Authorization (Bearer token, X-API-Key)
- Data consistency (API ↔ K8s ↔ RPC)
- EVM JSON-RPC compliance
- Smart contract deployment
- Transaction testing

**Markers**: `@pytest.mark.api`, `@pytest.mark.core`

**Run**: `uv run test-core` or `uv run pytest -m core`

### RBAC Tests (`tests/rbac/`)

License and role-based access control:
- License validation and expiration
- Role permissions (owner, editor, viewer)
- Tenant isolation
- Audit logging

**Markers**: `@pytest.mark.rbac`

**Run**: `uv run test-rbac` or `uv run pytest -m rbac`

### Worker Tests (`tests/workers/`)

Worker and workflow validation:
- Worker auto-registration
- Workflow state transitions
- Retry and error handling
- Horizontal scaling
- Temporal workflow tests

**Markers**: `@pytest.mark.workers`

**Run**: `uv run test-workers` or `uv run pytest -m workers`

### Non-Functional Tests (`tests/nonfunctional/`)

Performance, reliability, and security:
- Performance (SLO, load testing)
- Chaos tests (component restarts)
- Security (token validation, rate limits)
- Disaster recovery
- Observability (metrics, logs)

**Markers**: `@pytest.mark.nonfunctional`, `@pytest.mark.slow`

**Run**: `uv run test-nonfunctional` or `uv run pytest -m nonfunctional`

## Page Object Model

UI tests use the Page Object pattern for maintainability:

```python
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.node_creation_page import NodeCreationPage

def test_create_node(page, base_url):
    # Login
    login_page = LoginPage(page, base_url)
    login_page.open()
    login_page.login("your-token")
    
    # Create node
    creation_page = NodeCreationPage(page, base_url)
    creation_page.open()
    creation_page.create_node(
        name="my-eth-node",
        preset="ethereum-mainnet",
        network="mainnet"
    )
    creation_page.verify_creation_successful()
```

## API Client Usage

```python
from utils.api_client import NodesAPIClient

def test_create_node_api(config):
    client = NodesAPIClient(config)
    
    response = client.create_node({
        "name": "test-node",
        "preset": "ethereum-mainnet",
        "network": "mainnet"
    })
    
    assert response.status_code == 200
    node_data = response.json()
    assert node_data["status"] == "pending"
```

## Ethereum Client Usage

```python
from utils.eth_client import EthereumClient

def test_eth_node_rpc(eth_client):
    # Check connectivity
    assert eth_client.is_connected()
    
    # Verify chain ID
    chain_id = eth_client.get_chain_id()
    assert chain_id == 1  # Mainnet
    
    # Check block number
    block_num = eth_client.get_block_number()
    assert block_num > 0
```

## Wait Helpers

```python
from utils.wait_helper import WaitHelper

# Wait for condition
WaitHelper.wait_for_condition(
    lambda: node_status() == "running",
    timeout=300,
    poll_interval=5,
    description="node to be running"
)

# Wait for state transition
WaitHelper.wait_for_state_transition(
    state_func=lambda: get_node_status(node_id),
    target_state="running",
    timeout=600
)
```

## Kubernetes Helper

```python
from utils.k8s_helper import KubernetesHelper

def test_pod_ready(k8s_helper):
    # Check pod status
    assert k8s_helper.is_pod_ready("eth-node-pod")
    
    # Get pod logs
    logs = k8s_helper.get_pod_logs("eth-node-pod", tail_lines=100)
    
    # Wait for pod
    k8s_helper.wait_for_pod_ready("eth-node-pod", timeout=300)
```

## Allure Reporting

Tests automatically generate Allure reports with:
- Request/response attachments
- Screenshots on failure
- Step-by-step execution
- Test categorization

```bash
# Generate and view report
uv run report

# Or separately:
uv run report-generate    # Generate report
uv run report-open        # Open in browser
```

## CI/CD Integration (CircleCI - Planned)

```yaml
# .circleci/config.yml example
version: 2.1

jobs:
  test-smoke:
    docker:
      - image: ghcr.io/astral-sh/uv:python3.10-bookworm
    steps:
      - checkout
      - run: uv sync
      - run: uv run install-browsers
      - run: uv run test-smoke
      - store_artifacts:
          path: allure-results

  test-ui:
    docker:
      - image: ghcr.io/astral-sh/uv:python3.10-bookworm
    steps:
      - checkout
      - run: uv sync
      - run: uv run install-browsers
      - run: uv run test-ui
      - store_artifacts:
          path: allure-results
```

## Development

### Adding New Tests

1. **UI Test**: Create in `tests/ui/`, use page objects from `tests/ui/pages/`
2. **API Test**: Create in appropriate directory, use fixtures from `fixtures/`
3. **Add markers**: Use `@pytest.mark.{category}` decorators
4. **Add Allure annotations**: `@allure.feature()`, `@allure.story()`, `@allure.title()`

### Creating Page Objects

```python
from tests.ui.pages.base_page import BasePage

class MyPage(BasePage):
    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.my_button = "[data-testid='my-button']"
    
    @allure.step("Click my button")
    def click_my_button(self):
        self.click(self.my_button)
```

### Creating Fixtures

```python
# fixtures/my_fixtures.py
import pytest

@pytest.fixture
def my_fixture(config):
    # Setup
    resource = create_resource(config)
    yield resource
    # Teardown
    resource.cleanup()
```

## Troubleshooting

### Playwright Issues

```bash
# Reinstall browsers
uv run install-browsers

# Run with headed mode for debugging
HEADLESS=false uv run test-ui

# Enable slow motion
SLOW_MO=1000 uv run test-ui
```

### Connection Issues

```bash
# Check services are running
docker-compose ps

# Check Kubernetes connectivity
kubectl get pods -n default

# Verify URLs in .env
cat .env | grep URL
```

### Test Failures

```bash
# Run with verbose output
uv run pytest -vv

# Show print statements
uv run pytest -s

# Run single test
uv run pytest tests/ui/test_auth.py::TestAuthentication::test_login_success

# Keep test artifacts on failure
uv run pytest --screenshot=on --video=retain-on-failure
```

## Contributing

1. Follow existing code structure and patterns
2. Add appropriate markers and Allure annotations
3. Use page objects for UI tests
4. Include docstrings and type hints
5. Update README if adding new features

## License

Internal project - see company license.
