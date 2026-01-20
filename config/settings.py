import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    cp_nodes_api_url: str = "http://localhost:8080"
    cp_ui_url: str
    cp_internal_api_url: str = "http://localhost:8081"

    user_log: Optional[str] = None
    user_pass: Optional[str] = None

    admin_log: Optional[str] = None
    admin_pass: Optional[str] = None

    api_token: Optional[str] = None
    api_key: Optional[str] = None
    license_key: Optional[str] = None

    eth_rpc_mainnet_url: Optional[str] = None
    eth_rpc_testnet_url: Optional[str] = None
    eth_private_key: Optional[str] = None
    eth_test_address: Optional[str] = None

    kubeconfig: str = "~/.kube/config"
    k8s_namespace: str = "default"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "cp_nodes"
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None

    nats_url: str = "nats://localhost:4222"

    temporal_host: str = "localhost"
    temporal_port: int = 7233
    temporal_namespace: str = "default"

    test_timeout: int = 300
    node_creation_slo: int = 600
    parallel_deployments: int = 5

    log_level: str = "INFO"

    headless: bool = True
    browser: str = "chromium"
    slow_mo: int = 0
    video: str = "off"
    screenshot: str = "only-on-failure"

    allure_results_dir: str = "allure-results"

    @property
    def login_page_url(self) -> str:
        return f"{self.cp_ui_url}/login"

    @property
    def dashboard_url(self) -> str:
        return f"{self.cp_ui_url}/welcome"

    @property
    def postgres_url(self) -> str:
        if not self.postgres_user or not self.postgres_password:
            return ""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def temporal_url(self) -> str:
        return f"{self.temporal_host}:{self.temporal_port}"
