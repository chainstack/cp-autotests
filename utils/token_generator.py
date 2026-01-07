import base64
import json
from faker import Faker
import random
import string
import time


def generate_invalid_bearer_tokens():
    """
    Generate various types of invalid bearer tokens for testing.
    
    Returns:
        list: List of invalid token strings for testing
    """

    faker = Faker()
    valid_header = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).decode().rstrip('=')
    
    valid_payload = base64.urlsafe_b64encode(
        json.dumps({"sub": "1234567890", "name": str(faker.name()), "iat": int(time.time())}).encode()
    ).decode().rstrip('=')
    
    valid_signature = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=43))
    
    return [
        # Completely invalid strings
        "invalid_token",
        "not.a.jwt",
        "12345",
        "",
        
        # Missing parts
        f"{valid_header}",
        f"{valid_header}.{valid_payload}",
        f".{valid_payload}.{valid_signature}",
        f"{valid_header}..{valid_signature}",
        
        # Too many parts
        f"{valid_header}.{valid_payload}.{valid_signature}.extra",
        f"{valid_header}.{valid_payload}.{valid_signature}.extra.parts",
        
        # Invalid base64 encoding
        f"{valid_header}.invalid_base64.{valid_signature}",
        f"invalid_base64.{valid_payload}.{valid_signature}",
        f"{valid_header}.{valid_payload}.invalid_base64",
        
        # Malformed structure
        f"...",
        f"....",
        f"{valid_header}...{valid_signature}",
        
        # Invalid JSON in parts
        "bm90X2pzb24.bm90X2pzb24.signature",  # "not_json" base64 encoded
        
        # Tampered signature
        f"{valid_header}.{valid_payload}.tampered_signature",
        f"{valid_header}.{valid_payload}.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        
        # Special characters
        f"{valid_header}.{valid_payload}.sig@#$%",
        f"header!@#.payload$%^.signature&*()",
        
        # Expired/invalid timestamps (will be caught by signature validation)
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid",
        
        # Wrong algorithm in header
        "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature",
        
        # Unicode/special encoding
        "тест.токен.подпись",
        "🔑.🔐.🔒",
        
        # Very long token
        "a" * 10000,
        
        # SQL injection attempts in token
        "'; DROP TABLE users; --",
        
        # Null bytes
        "header\x00.payload\x00.signature\x00",
    ]

def generate_invalid_refresh_tokens():
    """
    Generate various types of invalid refresh tokens for testing.
    Refresh tokens are JWTs similar to access tokens but typically have longer expiration.
    
    Returns:
        list: List of invalid refresh token strings for testing
    """
    faker = Faker()
    valid_header = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).decode().rstrip('=')
    
    valid_payload = base64.urlsafe_b64encode(
        json.dumps({
            "sub": faker.uuid4(),
            "type": "refresh",
            "iat": int(time.time()),
            "exp": int(time.time()) + 2592000  # 30 days
        }).encode()
    ).decode().rstrip('=')
    
    valid_signature = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=43))
    
    wrong_type_token = (
        base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip('=') + "." +
        base64.urlsafe_b64encode(json.dumps({
            "sub": faker.uuid4(),
            "type": "access",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }).encode()).decode().rstrip('=') + "." + valid_signature
    )
    
    return [
        # Completely invalid strings
        "invalid_refresh_token",
        "not.a.refresh.token",
        "refresh123",
        "",
        
        # Missing parts
        f"{valid_header}",
        f"{valid_header}.{valid_payload}",
        f".{valid_payload}.{valid_signature}",
        f"{valid_header}..{valid_signature}",
        
        # Too many parts
        f"{valid_header}.{valid_payload}.{valid_signature}.extra",
        
        # Invalid base64 encoding
        f"{valid_header}.invalid_base64.{valid_signature}",
        f"invalid_base64.{valid_payload}.{valid_signature}",
        f"{valid_header}.{valid_payload}.invalid_base64",
        
        # Malformed structure
        "...",
        "....",
        
        # Tampered signature
        f"{valid_header}.{valid_payload}.tampered_signature",
        f"{valid_header}.{valid_payload}.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        
        # Special characters
        f"{valid_header}.{valid_payload}.sig@#$%",
        
        # Wrong token type (access token instead of refresh)
        wrong_type_token,
        
        # Unicode/special encoding
        "тест.refresh.токен",
        "🔄.🔐.🔒",
        
        # Very long token
        "r" * 10000,
        
        # SQL injection attempts
        "'; DROP TABLE refresh_tokens; --",
        
        # Null bytes
        "refresh\x00.token\x00.signature\x00",
    ]