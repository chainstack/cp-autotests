# Control Panel Test Strategy

# Stage 0. Foundation (test infrastructure)

## **Goals**

A unified BDD framework, fast local runs, reproducible environments.

- Tools
    - **pytest + pytest-bdd**
    - **HTTP client:** httpx (preferable) or requests.
    - **API validation against the specification:** schemathesis (OpenAPI → property-based tests).
    - **UI:** Playwright (smoke and critical flows).
    - **Container fixtures:** testcontainers (PostgreSQL, NATS) if needed.
    - **Data generation:** factories (factory_boy), pytest fixtures.
    - **Reporting:** allure-pytest.
    - **Load/perfomance:** Locust, apache benchmark for short manual checks
    - **CI:** CircleCI — parallel jobs following the test pyramid.

## Quality Control

Test pyramid: unit → contract/integration → e2e.

CI gates: PR blocked if fast checks fail.

# Stage 0.5 Customer Environment Simulation (on-prem specifics)

- **What we verify**
    
    Main aim is to test product in conditions that are as close as possible to real on-prem deployments
    
    - Supported Kubernetes versions (min/max; k8s API deprecations)
    - Limited CPU/memory per namespace
    - Storage limitations (ReadWriteOnce vs RWX)
    - Slow disks
    - Unstable network (latency, rate limits)
    - Various distros: Ubuntu, RHEL, Amazon Linux, Debian
- Methodology
    - Test manifests that simulate “low-resource” and “restricted” clusters.
    - Network: tc/netem profiles for packet loss & latency.
    - Automated validation of requirements: minimum resources, k8s version, presence of ingress/storage classes.

Comment: need to research platforms (host/OS) && versions (Helm, k8s etc) to support @Ilia Gabushev @Alex G @Max Kureikin 

# Stage 1. Core, already prepared: ETH node deployment + basic authorization + customer environment simulation

- **Functional features (BDD)**
    - Node creation (EVM/Solana preset in the future), state transitions:
        
        pending → running (success),
        
        pending → failed (workflow error),
        
        running → maintenance (PUT /ui/nodes/{id}),
        
        deletion: running → deleting → deleted (schedule-delete → confirm, see specification).
        
    - Listing/details of deployments, filtering by state.
    - Basic authorization (Bearer token for UI endpoints; X-API-Key for internal ones — verify denial without the key).
- Basic checks
    
    **Authorization and basic accessibility**
    
    - UI/token path: all public /ui/* endpoints accept token.
        
        Checks: 200 with valid token; 401 without/expired token; correct CORS and headers.
        
    - Internal endpoints (if accessible for testing): rejection without X-API-Key.
    
    **Node management and state machine**
    
    Verify declared transitions:
    
    - Creating a node → pending.
    - Successful workflow run → running.
    - Workflow error → failed (with informative code/message).
    - Update (PUT /nodes/{id}) to “maintenance” → maintenance.
    - Deletion: schedule-delete → deleting → final deleted (internal confirm).
    
    Assertions:
    
    - Idempotency: repeated POST of the same operation does not break state; duplicates → 409/422 (as defined).
    - Timing guarantees: SLO for pending→running (e.g., ≤ N minutes for minimal configuration).
    - Correct response codes: 200 for acceptance, 400 for invalid presets, 404 for unknown id.
    
    **Node data consistency (end-to-end)**
    
    Goal — UI/API must reflect actual system state.
    
    Comparison layers:
    
    - API (/nodes, /nodes/{id}): name, preset, status, creation time, revisions.
    - EVM JSON-RPC: node responds to key methods (see section 4).
    - Storage/DB (if accessible): deployment/revision record matches API.
    
    Invariants:
    
    - When running: pods Ready=1/1, services reachable, health endpoints OK.
    - Chain ID/Network ID match preset (e.g., Ethereum Mainnet).
    - Minimum peer count satisfied (≥ threshold).
    - Logs contain no repeating critical errors after startup.
    
    **EVM JSON-RPC compliance (node functionality)**
    
    Required methods (smoke):
    
    - web3_clientVersion, net_version, eth_chainId, eth_syncing (expect false for a synced node or sync progress).
    - eth_blockNumber increases over time.
    - eth_getBlockByNumber(latest, …) returns valid block (number, hash, timestamp).
    - eth_getBalance — correct for a well-known address.
    - eth_gasPrice / eth_feeHistory — values > 0.
    - (If possible) eth_maxPriorityFeePerGas.
    
    Negative checks:
    
    - Invalid params → correct JSON-RPC errors.
    - Rate limit/timeout (if configured) → correct degradation.
    
    **Smart contract deployment (full e2e)**
    
    Goal — ensure node not only responds via RPC but includes transactions in blocks.
    
    Preparation:
    
    - Network choice:
        
        If mainnet — private key with minimal balance + real gas; limited budget.
        
        Prefer devnet/testnet (Goerli/Sepolia/local) — cheaper and predictable.
        
    - Compile simple contract (ERC20 or “Storage”).
    
    Checks during deployment:
    
    - eth_estimateGas returns reasonable estimate.
    - Transaction enters mempool, txHash obtained.
    - receipt.status == 1, contractAddress not empty, blockNumber ≥ current.
    - Inclusion time ≤ N seconds/blocks (testnet threshold).
    - Event logs (e.g., Transfer) decode correctly and match expectations.
    
    **Transaction testing (traffic and correctness)**
    
    Scenarios:
    
    - Simple ETH transfer:
        
        sender balance decreases by value + fee, recipient increases by value;
        
        nonce monotonic.
        
    - Replace-by-fee: second tx with same nonce & higher maxFeePerGas replaces first.
    - Revert transaction (require(false)):
        
        receipt.status == 0, gas spent, state unchanged.
        
    - Parallel transactions:
        
        Send N tx in sequence; validate nonce correctness, all confirmed within T blocks.
        
    - Event logs:
        
        Contract invocation generates expected events; eth_getLogs/topics returns correct set.
        
    
    Metrics/validators:
    
    - Ratio of successful/failed txs; avg/95-percentile confirmation times.
        
        Consistency between eth_feeHistory and actual fees in receipts.
        
    
    Upgrade the ETH node
    
    - Proper transition to maintenance,
    - Data migration (if needed),
    - Return to running state.
    
    Upgrade the ETH node (negative)
    
    - Check rollback behavior in case of an upgrade failure
- Acceptance criteria (Definition of Done for stage 1)
    
    Successful runs:
    
    - Node create/update/delete (API) — green.
    - Consistency across layers (API↔k8s↔RPC) — confirmed.
    - JSON-RPC smoke — green.
    - Contract deployment and tx scenarios — green for chosen network.
    - Allure report without critical defects; retries do not mask systemic issues.
    - Node creation time fits agreed SLO.

# Stage 2. Incoming: licenses and roles (RBAC)

- **Licenses**
    - Sending `license_key` in the `Authorization: Bearer <license_key>` header (for workers and/or tenant-based filtering).
    - Behavior without key: 401/403.
    - Tenant isolation: each key can access only its own nodes/presets.
- **Roles (user service)**
    - Roles: owner/admin, editor, viewer (example set).
    - Permission matrix: who can create/update/delete, who can only read.
    - Inheritance/combination (if groups are supported).
- Basic checks
    - Check the maximum number of nodes allowed by the license.
    - License expiration → API access must be correctly blocked (401/403 expected).
    - License without permission for a specific preset (if actual).
    - A user without the proper role must not see nodes belonging to other tenants.
    - Attempt to create a node that violates limits (CPU/memory/preset restrictions).
- Audit logging
    - Every UI/API request is logged, including forbidden operations.
    - All RBAC errors are recorded as separate audit events.
    - Verify the integrity of logs after component restarts.

**Implementation**

- Fixtures create test licenses and users through the user service.
- In staging e2e tests we verify end-to-end tokens (license_key AND/OR token) and data separation in the database.

# **Stage 3. Workers, auto-registration, and workflow**

- **What we verify**
    - Automatic worker registration via `PUT /internal/workers/{id}`, including status and environment validation.
    - Workflow transitions and idempotency: repeated events must not break state.
    - Retries and error handling (pending → failed, new revision → recovery).
    - Verify accessibility of images && and their location
- Worker pool validation
    - Horizontal scaling of the worker pool (2→5→1).
    - Verification of correct task distribution.
    - Task deduplication during network failures.
    - Tests for a “stuck worker” (activity timeout → retry).
- Temporal workflow tests
    - Verification of activity timeout / retry policy / backoffs.
    - Check that the workflow correctly recalculates the node state after recovery.
    - Simulation of a Temporal failure (kill namespace) → workflows recover → nodes return to the correct status.

**Approach**

- BDD scenarios based on waiting for expected node events/states.
- Fault-injection: force an activity failure (mock), expect correct transition to failed; then “fix” it, create a revision — node must move to running.

# **Stage 4. Crossbrowser (especially Safari) UI E2E (smoke / critical paths)**

- **Goals**
    - ‘Happy paths’ as a part of E2E tests (~30%): login, preset browsing, create ETH node from preset, delete node, basic authorization errors.
    - Error state coverage:
    1. Authorization/token errors.
    2. Backend unavailability errors (5xx).
    3. Temporal/worker errors (a node stays in pending for too long).
    4. License errors: no permissions, limit exceeded, license expired.
    5. Network errors (timeout / lost connection): the UI must show a retry/notification.
    6. Form errors (invalid presets, invalid names).
    7. Incompatible component version (when attempting an upgrade).
    - Playwright with stable selectors (roles/aria labels).
    - Execution in CI on schedule and on release branches.

# **Stage 5. Non-functional tests**

- **Performance**
    - Time to reach running (SLO).
    - Parallel deployments (N).
    - Degradation under load.
    - Tools: Locust for API load, long-workflow timing.
- **Reliability**
    - Chaos tests: worker/component restarts must not break workflow state.
    - Resilience to transient network issues (temporary 5xx from kube-api).
    - Basic RPC stability under load.
- **Security**
    - Token/secret linting, header checks, rate-limit behavior, basic DAST (OWASP ZAP).
- DR
    - Loss of the cp-nodes-api pod → state must be restored from the database.
    - Loss of Postgres → verify backup recovery (if implemented).
    - Loss of the worker pool → workflows must not break data consistency.
- Observability
    - Verify that Prometheus metrics work correctly.
    - Service logs: structured logs with proper levels (info/warn/error).
    - Alerts for stuck workflows / long-pending nodes.
- Documentation Validation
    - Check that documentation (OpenAPI/Swagger etc) matches the actual API behavior.
    - Verify that the README, install guide, and hardware requirements do not contradict real test results.
    - Check that preset descriptions are up to date.

## Artifacts and reporting

- Allure reports with request/response attachments.
- UI snapshots (Playwright trace).
- For e2e: store workflow event logs / Temporal history for analysis.

## **Gates and regression strategy**

- PR: unit + contract + partial BDD (mock/fast).
- Nightly: full BDD on staging, light performance scenarios.
- Release branches: UI E2E + upgrade tests from previous minor version.