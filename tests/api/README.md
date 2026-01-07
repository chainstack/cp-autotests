# API Authentication Tests

Comprehensive API test suite for authentication endpoints following the test strategy defined in `concept.md`.

## Test Coverage

### 1. Login Tests (`test_auth_login.py`)
- ✅ Successful login with valid credentials
- ✅ Failed login with invalid username
- ✅ Failed login with invalid password
- ✅ Failed login with both invalid credentials
- ✅ Missing required fields (username/password)
- ✅ Empty credentials validation
- ✅ Malformed JSON handling
- ✅ CORS headers validation
- ✅ Multiple login token generation

**Total: 11 test cases**

### 2. Token Refresh Tests (`test_auth_refresh.py`)
- ✅ Successful token refresh with valid refresh token
- ✅ Failed refresh with invalid token
- ✅ Failed refresh with missing token
- ✅ Failed refresh with empty token
- ✅ Failed refresh with expired token
- ✅ Multiple refresh requests generate different tokens
- ✅ Malformed JSON handling
- ✅ Refreshed token validity verification

**Total: 8 test cases**

### 3. Logout Tests (`test_auth_logout.py`)
- ✅ Successful logout with valid token
- ✅ Logout without refresh token in body
- ✅ Failed logout without authentication
- ✅ Failed logout with invalid token
- ✅ Failed logout with expired token
- ✅ Access token invalidation after logout
- ✅ Refresh token invalidation after logout
- ✅ Multiple logout attempts

**Total: 8 test cases**

### 4. Profile Tests (`test_auth_profile.py`)
- ✅ Successful profile retrieval with valid token
- ✅ Failed profile access without token
- ✅ Failed profile access with invalid token
- ✅ Failed profile access with expired token
- ✅ Failed profile access with malformed token
- ✅ Profile data consistency with login response
- ✅ Profile data consistency across multiple calls
- ✅ Email format validation
- ✅ UUID format validation
- ✅ Tenant role validation

**Total: 10 test cases**

### 5. Authorization Tests (`test_auth_authorization.py`)
- ✅ Protected endpoints require Bearer token
- ✅ Invalid token format rejection
- ✅ Expired token rejection
- ✅ Token isolation between users
- ✅ Bearer scheme requirement
- ✅ Bearer case sensitivity
- ✅ Multiple authorization headers handling
- ✅ Token revocation after logout
- ✅ Public endpoints accessibility
- ✅ CORS headers presence
- ✅ Rate limiting on auth endpoints
- ✅ Tampered token rejection

**Total: 12 test cases**

### 6. Not Implemented Endpoints (`test_auth_not_implemented.py`)
Tests for endpoints that return 501 Not Implemented:
- ✅ Change password endpoint (501)
- ✅ Change username endpoint (501)
- ✅ Get audit log endpoint (501)
- ✅ Validation tests for future implementation
- ✅ Skipped tests ready for when endpoints are implemented

**Total: 19 test cases**

## Running the Tests

### Run all auth API tests
```bash
pytest tests/api/ -v
```

### Run specific test file
```bash
pytest tests/api/test_auth_login.py -v
pytest tests/api/test_auth_refresh.py -v
pytest tests/api/test_auth_logout.py -v
pytest tests/api/test_auth_profile.py -v
pytest tests/api/test_auth_authorization.py -v
pytest tests/api/test_auth_not_implemented.py -v
```

### Run with markers
```bash
# Run only smoke tests
pytest tests/api/ -v -m smoke

# Run only API tests
pytest tests/api/ -v -m api

# Run critical tests
pytest tests/api/ -v -m "api and critical"
```

### Run with Allure reporting
```bash
pytest tests/api/ -v --alluredir=allure-results
allure serve allure-results
```

### Run in parallel
```bash
pytest tests/api/ -v -n auto
```

## Test Configuration

### Required Environment Variables
Set these in `.env` file:

```env
CP_NODES_API_URL=http://localhost:8080
USER_LOG=your_username
USER_PASS=your_password
```

### Test Fixtures

The tests use the following fixtures from `fixtures/api_fixtures.py`:

- `auth_client`: Unauthenticated auth API client
- `authenticated_auth_client`: Pre-authenticated auth API client
- `valid_credentials`: Valid username and password from config
- `invalid_username`: Randomly generated invalid username
- `invalid_password`: Randomly generated invalid password
- `invalid_credentials`: Both invalid username and password

## Test Strategy Alignment

These tests align with **Stage 1** of the test strategy from `concept.md`:

### Authorization and Basic Accessibility
✅ UI/token path: all public /v1/auth/* endpoints accept token
✅ Checks: 200 with valid token; 401 without/expired token
✅ Correct CORS and headers validation

### Key Validations
- **Authentication Flow**: Login → Token → Refresh → Logout
- **Token Lifecycle**: Generation, validation, refresh, revocation
- **Error Handling**: 400 (bad request), 401 (unauthorized), 501 (not implemented)
- **Security**: Token isolation, expiration, tampering detection
- **API Contract**: Request/response schema validation per OpenAPI spec

## Test Markers

- `@pytest.mark.api` - All API tests
- `@pytest.mark.smoke` - Critical smoke tests
- `@pytest.mark.slow` - Slow-running tests (rate limiting, etc.)
- `@pytest.mark.skip` - Tests for future implementation

## OpenAPI Specification

Tests are based on the authentication endpoints defined in `openapi.yaml`:

- `POST /v1/auth/login` - User authentication
- `POST /v1/auth/refresh` - Token refresh
- `POST /v1/auth/logout` - User logout
- `GET /v1/auth/profile` - Get user profile
- `PUT /v1/auth/password` - Change password (501)
- `PUT /v1/auth/username` - Change username (501)
- `GET /v1/auth/audit-log` - Get audit log (501)

## Future Enhancements

When the following endpoints are implemented in cp-auth service:

1. **Password Change** - Enable skipped tests in `test_auth_not_implemented.py`
2. **Username Change** - Enable skipped tests in `test_auth_not_implemented.py`
3. **Audit Log** - Enable skipped tests in `test_auth_not_implemented.py`

## CI/CD Integration

These tests are designed to run in CI pipeline:

```yaml
# Example CircleCI config
- run:
    name: Run Auth API Tests
    command: pytest tests/api/ -v -m "api and smoke"
```

## Total Test Count

**68 test cases** covering all authentication scenarios including positive, negative, edge cases, and security validations.
