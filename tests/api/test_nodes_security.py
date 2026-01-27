import pytest
import allure


@allure.feature("Nodes")
@allure.story("Security Headers")
@pytest.mark.api
class TestNodesSecurityHeaders:

    @allure.title("List nodes endpoint has security headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_nodes_security_headers(self, authenticated_nodes_client):
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 200
        self._verify_security_headers(response)

    @allure.title("Get node endpoint has security headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_node_security_headers(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.get_node(existing_node_id)
        
        assert response.status_code == 200
        self._verify_security_headers(response)

    @allure.title("Create node endpoint has security headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_node_security_headers(self, authenticated_nodes_client, valid_eth_preset_instance_id):
        response = authenticated_nodes_client.create_node(
            preset_instance_id=valid_eth_preset_instance_id
        )
        
        assert response.status_code == 201
        self._verify_security_headers(response)

    @allure.title("Delete node endpoint has security headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_node_security_headers(self, authenticated_nodes_client, existing_node_id):
        response = authenticated_nodes_client.schedule_delete_node(existing_node_id)
        
        self._verify_security_headers(response)

    @allure.title("Error responses have security headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_error_response_security_headers(self, authenticated_nodes_client):
        response = authenticated_nodes_client.get_node("00000000-0000-0000-0000-000000000000")
        
        self._verify_security_headers(response)

    @allure.title("Unauthorized responses have security headers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_unauthorized_response_security_headers(self, authenticated_nodes_client):
        token = authenticated_nodes_client.token
        authenticated_nodes_client.token = None
        
        response = authenticated_nodes_client.list_nodes()
        
        assert response.status_code == 401
        self._verify_security_headers(response)
        authenticated_nodes_client.token = token

    def _verify_security_headers(self, response):
        headers = response.headers
        
        # X-Content-Type-Options
        assert "X-Content-Type-Options" in headers, \
            "Missing X-Content-Type-Options header"
        assert headers["X-Content-Type-Options"] == "nosniff", \
            f"Expected 'nosniff', got '{headers['X-Content-Type-Options']}'"
        
        # X-Frame-Options
        assert "X-Frame-Options" in headers, \
            "Missing X-Frame-Options header"
        assert headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"], \
            f"Invalid X-Frame-Options: {headers['X-Frame-Options']}"
        
        # Strict-Transport-Security (HSTS)
        assert "Strict-Transport-Security" in headers, \
            "Missing Strict-Transport-Security header"
        
        # X-XSS-Protection (optional but good to have)
        if "X-XSS-Protection" in headers:
            assert "1" in headers["X-XSS-Protection"], \
                "X-XSS-Protection should be enabled"
