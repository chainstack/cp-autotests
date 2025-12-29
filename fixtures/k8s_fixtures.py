import pytest
from utils.k8s_helper import KubernetesHelper
from config.settings import Settings


@pytest.fixture(scope="session")
def k8s_helper(config: Settings):
    return KubernetesHelper(
        kubeconfig_path=config.kubeconfig,
        namespace=config.k8s_namespace
    )


@pytest.fixture
def k8s_namespace(config: Settings):
    return config.k8s_namespace
