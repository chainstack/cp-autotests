import httpx
import allure
from typing import Optional, Dict, Any
from config.settings import Settings
from utils.http_logger import LogHTTPResponse
import time
from control_panel.node import NodeState


class APIClient:

    def __init__(self, base_url: str, token: Optional[str] = None, refresh_token: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.refresh_token = refresh_token
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)
        self.headers = self._get_headers()

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers

    def _log_response(self, response: httpx.Response, stage: str) -> httpx.Response:
        LogHTTPResponse(response, stage)
        return response

    @allure.step("GET {endpoint}")
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(headers)
        
        with allure.step(f"Request: GET {url}"):
            allure.attach(str(params), "Query Parameters", allure.attachment_type.JSON)
            response = self.client.get(url, params=params, headers=request_headers)
            allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        
        return self._log_response(response, f"GET {endpoint}")

    @allure.step("POST {endpoint}")
    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(headers)
        
        with allure.step(f"Request: POST {url}"):
            allure.attach(str(json), "Request Body", allure.attachment_type.JSON)
            response = self.client.post(url, json=json, headers=request_headers)
            allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        
        return self._log_response(response, f"POST {endpoint}")


    @allure.step("PUT {endpoint}")
    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(headers)
        
        with allure.step(f"Request: PUT {url}"):
            allure.attach(str(json), "Request Body", allure.attachment_type.JSON)
            response = self.client.put(url, json=json, headers=request_headers)
            allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        
        return self._log_response(response, f"PUT {endpoint}")

    @allure.step("DELETE {endpoint}")
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(headers)
        
        with allure.step(f"Request: DELETE {url}"):
            response = self.client.delete(url, headers=request_headers)
            allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        
        return self._log_response(response, f"DELETE {endpoint}")

    @allure.step("PATCH {endpoint}")
    def patch(self, endpoint: str, json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(headers)
        
        with allure.step(f"Request: PATCH {url}"):
            allure.attach(str(json), "Request Body", allure.attachment_type.JSON)
            response = self.client.patch(url, json=json, headers=request_headers)
            allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        
        return self._log_response(response, f"PATCH {endpoint}")

    @allure.step("Custom Request {method} {endpoint}")
    def send_custom_request(self, method: str, endpoint: str, 
                           json: Optional[Dict[str, Any]] = None,
                           params: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        if method.upper() == "GET":
            return self.get(endpoint, params=params, headers=headers)
        elif method.upper() == "POST":
            return self.post(endpoint, json=json, headers=headers)
        elif method.upper() == "PUT":
            return self.put(endpoint, json=json, headers=headers)
        elif method.upper() == "PATCH":
            return self.patch(endpoint, json=json, headers=headers)
        elif method.upper() == "DELETE":
            return self.delete(endpoint, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def set_cookies(self, cookies: Dict[str, str]):
        for name, value in cookies.items():
            self.client.cookies.set(name, value)

    def get_cookies(self) -> Dict[str, str]:
        return dict(self.client.cookies)

    def clear_cookies(self):
        self.client.cookies.clear()

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class NodesAPIClient(APIClient):
    def __init__(self, settings: Settings, token: Optional[str] = None):
        super().__init__(
            base_url=settings.cp_nodes_api_url,
            token=token or settings.api_token
        )
        self.nodes_list = []
        self.sleep_period = 1
        self.node_status_timeout = 60

    def create_node(self, preset_instance_id: str, preset_override_values: Optional[Dict[str, Any]] = None) -> httpx.Response:
        payload = {"preset_instance_id": preset_instance_id}
        if preset_override_values:
            payload["preset_override_values"] = preset_override_values
        response = self.post("/v1/ui/nodes", json=payload)
        if response.status_code == 201:
            self.nodes_list.append(response.json()["deployment_id"])
        return response

    def list_nodes(self) -> httpx.Response:
        return self.get("/v1/ui/nodes")

    def get_node(self, node_id: str) -> httpx.Response:
        return self.get(f"/v1/ui/nodes/{node_id}")

    def schedule_delete_node(self, node_id: str) -> httpx.Response:
        operational_node_id = node_id.lower()
        response = self.post(f"/v1/ui/nodes/{node_id}/schedule-delete")
        if response.status_code == 200 and operational_node_id in self.nodes_list:
            self.nodes_list.remove(operational_node_id)
        return response

    def _teardown(self):
        for node_id in list(self.nodes_list):  # Iterate over copy
            self.schedule_delete_node(node_id)

    @allure.step("Waiting {node_id} to be {expected_status}")
    def _wait_node_until_status(self, node_id: str, expected_status: NodeState, timeout: int = self.node_status_timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.get_node(node_id)
            if response.json()["status"] == expected_status:
                return
            time.sleep(self.sleep_period)
        raise Exception(f"Node {node_id} is not {expected_status} after {timeout} seconds")


class InternalAPIClient(APIClient):

    def __init__(self, settings: Settings):
        super().__init__(
            base_url=settings.cp_internal_api_url,
            api_key=settings.api_key
        )

    def register_worker(self, worker_id: str, worker_data: Dict[str, Any]) -> httpx.Response:
        return self.put(f"/internal/workers/{worker_id}", json=worker_data)

    def confirm_deletion(self, node_id: str) -> httpx.Response:
        return self.post(f"/internal/nodes/{node_id}/confirm-delete")


class AuthAPIClient(APIClient):

    def __init__(self, settings: Settings, token: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(
            base_url=settings.cp_nodes_api_url,
            token=token,
            refresh_token=refresh_token
        )

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> httpx.Response:        
        return self.post("/v1/auth/login", json={"username": username, "password": password})

    def post_refresh(self, refresh_token: str) -> httpx.Response:
        return self.post("/v1/auth/refresh", json={"refresh_token": refresh_token})

    def logout(self, refresh_token: Optional[str] = None) -> httpx.Response:
        payload = {"refresh_token": refresh_token} if refresh_token else {}
        return self.post("/v1/auth/logout", json=payload)

    def get_profile(self) -> httpx.Response:
        return self.get("/v1/auth/profile")

    def change_password(self, old_password: Optional[str] = None, new_password: Optional[str] = None) -> httpx.Response:
        return self.put("/v1/auth/password", json={"old_password": old_password, "new_password": new_password})

    def change_username(self, new_username: Optional[str] = None) -> httpx.Response:
        return self.put("/v1/auth/username", json={"new_username": new_username})

    def get_audit_log(self, page: Optional[int] = None, page_size: Optional[int] = None) -> httpx.Response:
        params = {"page": page, "page_size": page_size}
        return self.get("/v1/auth/audit-log", params=params)
