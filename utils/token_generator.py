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
        
        # SQL injection attempts in token
        "'; DROP TABLE users; --"
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
        
        # Note: Unicode/emoji tokens cause httpx UnicodeEncodeError (HTTP headers are ASCII-only)
        # To test these, use raw sockets instead
        # "тест.refresh.токен",
        # "🔄.🔐.🔒",
        
        # Very long token
        "r" * 10000,
        
        # SQL injection attempts
        "'; DROP TABLE refresh_tokens; --",
        
        # Note: Null bytes cause httpx.LocalProtocolError client-side, not server-side rejection
        # If you need to test null bytes, handle them separately with error catching
        # "refresh\x00.token\x00.signature\x00",
    ]


def generate_expired_token(
    sub: str = "4fa033a0-8aae-4a2d-a216-30228f6f6320",
    email: str = "admin@example.com",
    username: str = "admin",
    tenant_id: str = "550e8400-e29b-41d4-a716-446655440000",
    tenant_role: str = "admin",
    expired_seconds_ago: int = 3600
) -> str:
    """
    Generate a JWT token that has already expired.
    
    Note: This token will have a valid JWT structure but an invalid signature
    (since we don't have the private key). The API should reject it either
    because of the invalid signature OR the expired claim - both scenarios
    correctly test the "unauthorized" path.
    
    Args:
        sub: Subject (user ID)
        email: User email
        username: Username
        tenant_id: Tenant ID
        tenant_role: Role within tenant
        expired_seconds_ago: How many seconds in the past the token expired
        
    Returns:
        str: An expired JWT token string
    """
    now = int(time.time())
    exp = now - expired_seconds_ago  # Token expired in the past
    iat = exp - 300  # Issued 5 minutes before expiration
    nbf = iat
    
    header = {
        "alg": "RS256",  # Match the real token's algorithm
        "typ": "JWT"
    }
    
    payload = {
        "sub": sub,
        "email": email,
        "username": username,
        "tenant_id": tenant_id,
        "tenant_role": tenant_role,
        "iss": "cp-auth",
        "exp": exp,
        "nbf": nbf,
        "iat": iat
    }
    
    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip('=')
    
    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip('=')
    
    # Generate a fake signature (won't be valid, but structurally correct)
    fake_signature = ''.join(random.choices(
        string.ascii_letters + string.digits + '-_', k=86
    ))
    
    return f"{header_encoded}.{payload_encoded}.{fake_signature}"


def generate_expired_refresh_token(
    sub: str = "4fa033a0-8aae-4a2d-a216-30228f6f6320",
    expired_seconds_ago: int = 3600
) -> str:
    """
    Generate an expired refresh token for testing.
    
    Args:
        sub: Subject (user ID)
        expired_seconds_ago: How many seconds in the past the token expired
        
    Returns:
        str: An expired refresh token string
    """
    return generate_expired_token(
        sub=sub,
        expired_seconds_ago=expired_seconds_ago
    )