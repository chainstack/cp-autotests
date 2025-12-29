# Justfile for cp-autotests
# Alternative to Makefile for those who prefer just

# Show available commands
default:
    @just --list

# Setup environment (install + browsers + .env)
setup:
    uv sync
    uv run install-browsers
    cp .env.example .env || true
    @echo "Setup complete! Please edit .env with your configuration."

# Install dependencies
install:
    uv sync

# Install Playwright browsers
install-browsers:
    uv run install-browsers

# Run all tests
test:
    uv run test

# Run UI tests
test-ui:
    uv run test-ui

# Run API tests
test-api:
    uv run test-api

# Run smoke tests
test-smoke:
    uv run test-smoke

# Run critical tests
test-critical:
    uv run test-critical

# Run tests in parallel
test-parallel:
    uv run test-parallel

# Generate and open Allure report
report:
    uv run report

# Clean test artifacts
clean:
    uv run clean

# Lint code
lint:
    uv run lint

# Format code
format:
    uv run format

# Run all quality checks
check:
    uv run check

# Start test infrastructure
infra-up:
    uv run infra-up

# Stop test infrastructure
infra-down:
    uv run infra-down

# View infrastructure logs
infra-logs:
    uv run infra-logs
