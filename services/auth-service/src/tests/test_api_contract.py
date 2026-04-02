import pytest
import requests

BASE_URL = "http://localhost:8080" 

# ==========================================
# 1. POST /api/v1/auth/register
# ==========================================
def test_register_user():
    url = f"{BASE_URL}/api/v1/auth/register"
    payload = {
        "email": "testuser@example.com",
        "password": "SecurePassword123",
        "username": "testuser"
    }
    
    response = requests.post(url, json=payload)
    
    # Check standard HTTP status codes for creation
    assert response.status_code in [200, 201]
    
    # Check expected JSON contract
    data = response.json()
    assert "email" in data
    assert data["email"] == payload["email"]

# ==========================================
# 2. POST /api/v1/auth/login
# ==========================================
def test_login_user():
    url = f"{BASE_URL}/api/v1/auth/login"
    payload = {
        "email": "testuser@example.com",
        "password": "SecurePassword123"
    }
    
    response = requests.post(url, json=payload)
    
    assert response.status_code == 200
    
    # Verify token payload shape
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert type(data["access_token"]) is str

# ==========================================
# 3. POST /api/v1/auth/logout
# ==========================================
def test_logout_user():
    url = f"{BASE_URL}/api/v1/auth/logout"
    # Provide a mock or valid bearer token for the auth header
    headers = {"Authorization": "Bearer mock_or_real_access_token"}
    
    response = requests.post(url, headers=headers)
    
    # Check that the server acknowledges the logout
    assert response.status_code in [200, 204] 

# ==========================================
# 4. GET /api/v1/auth/verify
# ==========================================
def test_verify_email():
    url = f"{BASE_URL}/api/v1/auth/verify"
    params = {
        "email": "testuser@example.com",
        "otp": "123456"
    }
    
    response = requests.get(url, params=params)
    
    assert response.status_code == 200
    
    data = response.json()
    # Contract assertion: ensure standard messaging or status
    assert data.get("status") in ["success", "verified"] or "message" in data

# ==========================================
# 5. GET /internal/v1/users/{id}/permissions
# ==========================================
def test_get_user_permissions():
    user_id = "12345"
    url = f"{BASE_URL}/internal/v1/users/{user_id}/permissions"
    
    # Internal endpoints usually require a specific API key or network header
    headers = {"X-Internal-Secret": "your_internal_test_key"}
    
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    
    data = response.json()
    # Contract assertion: ensure permissions are returned as a list
    assert "permissions" in data
    assert isinstance(data["permissions"], list)
