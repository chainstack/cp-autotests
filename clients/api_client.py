import httpx
import allure
from typing import Optional, Dict, Any
from config.settings import Settings


class APIClient:

    def __init__(self, base_url: str, token: Optional[str] = None, refresh_token: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.refresh_token = refresh_token
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers

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
        
        return response

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
        
        return response

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
        
        return response

    @allure.step("DELETE {endpoint}")
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(headers)
        
        with allure.step(f"Request: DELETE {url}"):
            response = self.client.delete(url, headers=request_headers)
            allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        
        return response

    @allure.step("Custom Request {method} {endpoint}")
    def send_custom_request(self, method: str, endpoint: str, 
                           json: Optional[Dict[str, Any]] = None,
                           params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        if method.upper() == "GET":
            return self.get(endpoint, params=params)
        elif method.upper() == "POST":
            return self.post(endpoint, json=json)
        elif method.upper() == "PUT":
            return self.put(endpoint, json=json)
        elif method.upper == "PATCH":
            return self.patch(endpoint, json=json)
        elif method.upper() == "DELETE":
            return self.delete(endpoint)
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
    def __init__(self, settings: Settings):
        super().__init__(
            base_url=settings.cp_nodes_api_url,
            token=settings.api_token
        )

    def create_node(self, node_data: Dict[str, Any]) -> httpx.Response:
        return self.post("/ui/nodes", json=node_data)

    def get_nodes(self, filters: Optional[Dict[str, Any]] = None) -> httpx.Response:
        return self.get("/ui/nodes", params=filters)

    def get_node(self, node_id: str) -> httpx.Response:
        return self.get(f"/ui/nodes/{node_id}")

    def update_node(self, node_id: str, update_data: Dict[str, Any]) -> httpx.Response:
        return self.put(f"/ui/nodes/{node_id}", json=update_data)

    def delete_node(self, node_id: str) -> httpx.Response:
        return self.delete(f"/ui/nodes/{node_id}")


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

    def login(self, username: any = None, password: any = None) -> httpx.Response:        
        return self.post("/v1/auth/login", json={"username": username, "password": password})

    def refresh_token(self, refresh_token: str) -> httpx.Response:
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
        params = {"page": page, "page_size": page_size} if page and page_size else None
        return self.get("/v1/auth/audit-log", params=params)
