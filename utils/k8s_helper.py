import allure
from typing import Optional, Dict, List
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time

class KubernetesHelper:

    def __init__(self, kubeconfig_path: Optional[str] = None, namespace: str = "default"):
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
        
        self.namespace = namespace
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    @allure.step("Get pod {pod_name}")
    def get_pod(self, pod_name: str, namespace: Optional[str] = None) -> Optional[client.V1Pod]:
        ns = namespace or self.namespace
        try:
            pod = self.core_v1.read_namespaced_pod(pod_name, ns)
            allure.attach(str(pod.status.phase), f"Pod {pod_name} Status", allure.attachment_type.TEXT)
            return pod
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return None

    @allure.step("List pods with label {label_selector}")
    def list_pods(self, label_selector: Optional[str] = None, 
                  namespace: Optional[str] = None) -> List[client.V1Pod]:
        ns = namespace or self.namespace
        try:
            pods = self.core_v1.list_namespaced_pod(ns, label_selector=label_selector)
            allure.attach(str(len(pods.items)), "Pod Count", allure.attachment_type.TEXT)
            return pods.items
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return []

    @allure.step("Check if pod {pod_name} is ready")
    def is_pod_ready(self, pod_name: str, namespace: Optional[str] = None) -> bool:
        pod = self.get_pod(pod_name, namespace)
        if not pod:
            return False
        
        if pod.status.conditions:
            for condition in pod.status.conditions:
                if condition.type == "Ready" and condition.status == "True":
                    return True
        return False

    @allure.step("Get pod logs for {pod_name}")
    def get_pod_logs(self, pod_name: str, namespace: Optional[str] = None, 
                     tail_lines: Optional[int] = 100) -> str:
        ns = namespace or self.namespace
        try:
            logs = self.core_v1.read_namespaced_pod_log(
                pod_name, ns, tail_lines=tail_lines
            )
            allure.attach(logs, f"Logs for {pod_name}", allure.attachment_type.TEXT)
            return logs
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return ""

    @allure.step("Get service {service_name}")
    def get_service(self, service_name: str, namespace: Optional[str] = None) -> Optional[client.V1Service]:
        ns = namespace or self.namespace
        try:
            service = self.core_v1.read_namespaced_service(service_name, ns)
            allure.attach(str(service.spec.cluster_ip), f"Service {service_name} IP", 
                         allure.attachment_type.TEXT)
            return service
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return None

    @allure.step("Check service {service_name} endpoints")
    def get_service_endpoints(self, service_name: str, 
                             namespace: Optional[str] = None) -> Optional[client.V1Endpoints]:
        ns = namespace or self.namespace
        try:
            endpoints = self.core_v1.read_namespaced_endpoints(service_name, ns)
            return endpoints
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return None

    @allure.step("Get deployment {deployment_name}")
    def get_deployment(self, deployment_name: str, 
                      namespace: Optional[str] = None) -> Optional[client.V1Deployment]:
        ns = namespace or self.namespace
        try:
            deployment = self.apps_v1.read_namespaced_deployment(deployment_name, ns)
            allure.attach(
                f"Ready: {deployment.status.ready_replicas}/{deployment.status.replicas}",
                f"Deployment {deployment_name} Status",
                allure.attachment_type.TEXT
            )
            return deployment
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return None

    @allure.step("Wait for pod {pod_name} to be ready")
    def wait_for_pod_ready(self, pod_name: str, namespace: Optional[str] = None, 
                          timeout: int = 300) -> bool:
        ns = namespace or self.namespace
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_pod_ready(pod_name, ns):
                return True
            time.sleep(5)
        
        return False

    @allure.step("Get resource usage for pod {pod_name}")
    def get_pod_metrics(self, pod_name: str, namespace: Optional[str] = None) -> Optional[Dict]:
        ns = namespace or self.namespace
        try:
            custom_api = client.CustomObjectsApi()
            metrics = custom_api.get_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=ns,
                plural="pods",
                name=pod_name
            )
            allure.attach(str(metrics), f"Metrics for {pod_name}", allure.attachment_type.JSON)
            return metrics
        except ApiException as e:
            allure.attach(str(e), "API Exception", allure.attachment_type.TEXT)
            return None
