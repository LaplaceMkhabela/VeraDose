import pytest
import requests
import uuid

# Base URL of the running User Profile Microservice
BASE_URL = "http://localhost:8080"

# Generate some consistent mock IDs and Auth Headers for the test suite
TEST_USER_ID = str(uuid.uuid4())

# Since Section 4.2 requires a valid JWT for all endpoints
AUTH_HEADERS = {
    "Authorization": "Bearer mock_valid_jwt_token_for_test_user",
    "Content-Type": "application/json"
}

ADMIN_HEADERS = {
    "Authorization": "Bearer mock_valid_jwt_token_for_admin_user",
    "Content-Type": "application/json"
}

# Helper function to generate a valid profile payload
def get_valid_profile_payload(email_suffix="test.com"):
    return {
        "name": "Jane Doe",
        "age": 30,
        "phone": "+12345678900",  # E.164 format
        "email": f"jane.doe.{uuid.uuid4().hex[:6]}@{email_suffix}", # Ensure unique
        "emergency_contact": {
            "name": "John Doe",
            "phone": "+19876543210"
        },
        "medications": ["Lisinopril", "Metformin"]
    }

# ==========================================
# 1. POST /profiles
# ==========================================
def test_create_profile_success():
    url = f"{BASE_URL}/profiles"
    payload = get_valid_profile_payload()
    
    response = requests.post(url, json=payload, headers=AUTH_HEADERS)
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert "user_id" in data # Expecting the DB-generated UUID

def test_create_profile_invalid_age():
    url = f"{BASE_URL}/profiles"
    payload = get_valid_profile_payload()
    # Age constraint: Range 0-120
    payload["age"] = -5 
    
    response = requests.post(url, json=payload, headers=AUTH_HEADERS)
    
    assert response.status_code in [400, 422]

def test_create_profile_duplicate_email():
    url = f"{BASE_URL}/profiles"
    payload = get_valid_profile_payload(email_suffix="duplicate.com")
    payload["email"] = "static.duplicate@example.com"
    
    # First creation
    requests.post(url, json=payload, headers=AUTH_HEADERS)
    
    # Second creation attempt with the exact same email
    response = requests.post(url, json=payload, headers=AUTH_HEADERS)
    
    assert response.status_code in [400, 409]

# ==========================================
# 2. GET /profiles/{userId} & /profiles
# ==========================================
def test_get_profile_by_id_success():
    # First, create a user to fetch
    create_url = f"{BASE_URL}/profiles"
    payload = get_valid_profile_payload()
    create_response = requests.post(create_url, json=payload, headers=AUTH_HEADERS)
    
    # Safely extract the ID or fallback so the test fails logically if creation failed
    user_id = create_response.json().get("user_id", TEST_USER_ID) if create_response.status_code in [200, 201] else TEST_USER_ID
    
    get_url = f"{BASE_URL}/profiles/{user_id}"
    response = requests.get(get_url, headers=AUTH_HEADERS)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify the full data model is returned
    assert data["name"] == payload["name"]
    assert data["age"] == payload["age"]
    assert "emergency_contact" in data
    assert isinstance(data["medications"], list)

def test_get_all_profiles_admin_only():
    url = f"{BASE_URL}/profiles"
    
    # 1. Test with standard user headers (should be denied)
    user_response = requests.get(url, headers=AUTH_HEADERS)
    assert user_response.status_code in [401, 403]
    
    # 2. Test with Admin headers (should succeed)
    admin_response = requests.get(url, headers=ADMIN_HEADERS)
    assert admin_response.status_code == 200
    assert isinstance(admin_response.json(), list) or "data" in admin_response.json()

# ==========================================
# 3. PATCH /profiles/{userId}
# ==========================================
def test_update_profile_partial():
    # Create a base user
    create_url = f"{BASE_URL}/profiles"
    payload = get_valid_profile_payload()
    create_response = requests.post(create_url, json=payload, headers=AUTH_HEADERS)
    user_id = create_response.json().get("user_id", TEST_USER_ID) if create_response.status_code in [200, 201] else TEST_USER_ID
    
    update_url = f"{BASE_URL}/profiles/{user_id}"
    
    # Send a partial update (PATCH) as specified in Section 3.3
    update_payload = {
        "medications": ["Lisinopril", "Metformin", "Aspirin"],
        "phone": "+19998887777"
    }
    
    response = requests.patch(update_url, json=update_payload, headers=AUTH_HEADERS)
    
    assert response.status_code == 200
    data = response.json()
    
    # Depending on whether the API returns the updated object or just a success message,
    # we might need to fetch it again to verify. Let's assume it returns the updated object.
    updated_profile = data if "medications" in data else requests.get(update_url, headers=AUTH_HEADERS).json()
    
    assert "Aspirin" in updated_profile["medications"]
    assert updated_profile["phone"] == "+19998887777"
    # Ensure other fields weren't wiped out
    assert updated_profile["name"] == payload["name"]

# ==========================================
# 4. DELETE /profiles/{userId}
# ==========================================
def test_delete_profile_soft_delete():
    # Create a user to delete
    create_url = f"{BASE_URL}/profiles"
    create_response = requests.post(create_url, json=get_valid_profile_payload(), headers=AUTH_HEADERS)
    user_id = create_response.json().get("user_id", TEST_USER_ID) if create_response.status_code in [200, 201] else TEST_USER_ID
    
    delete_url = f"{BASE_URL}/profiles/{user_id}"
    
    # Perform the deletion
    response = requests.delete(delete_url, headers=AUTH_HEADERS)
    assert response.status_code in [200, 204]
    
    # Try to fetch the deleted user
    get_response = requests.get(delete_url, headers=AUTH_HEADERS)
    
    # Because it is a soft delete, the API might return 404, or it might return 200 with 'is_deleted: true'
    # Typically, a standard user query should return 404 for soft-deleted records.
    assert get_response.status_code == 404 or get_response.json().get("is_deleted") is True
