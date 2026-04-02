import pytest
import requests
import uuid

# Base URL of the running Safety Analysis Microservice
BASE_URL = "http://localhost:8080"

# Generate consistent mock IDs
TEST_USER_ID = str(uuid.uuid4())

# Helper function to generate a base payload
def get_base_health_payload():
    return {
        "target_medicine": {
            "name": "Amoxicillin",
            "dosage": "500mg",
            "frequency": "Twice a day"
        },
        "user_context": {
            "weight_kg": 70,
            "age": 35,
            "illness_symptoms": ["Bacterial throat infection"]
        },
        "history": {
            "allergies": ["None"],
            "current_medications": ["Vitamin C"]
        }
    }

# ==========================================
# 1. POST /analyze/safety
# ==========================================
def test_analyze_safety_clear():
    """
    Tests a standard, safe medication addition with no known interactions.
    """
    url = f"{BASE_URL}/analyze/safety"
    payload = get_base_health_payload()
    
    # Increase timeout as LLM processing can be slow (as noted in section 6.2)
    response = requests.post(url, json=payload, timeout=30.0)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify the LLM returned the expected structured JSON contract
    assert "status" in data
    assert "message" in data
    assert data["status"] in ["clear", "warning", "danger"]

def test_analyze_safety_critical_allergy():
    """
    Tests the Allergy Alert logic by explicitly triggering a known allergy.
    """
    url = f"{BASE_URL}/analyze/safety"
    payload = get_base_health_payload()
    
    # Modify payload to trigger a direct allergy conflict
    payload["target_medicine"]["name"] = "Penicillin"
    payload["history"]["allergies"] = ["Penicillin"]
    
    response = requests.post(url, json=payload, timeout=30.0)
    
    assert response.status_code == 200
    data = response.json()
    
    # We expect the AI to flag this as a critical danger based on section 3.3
    assert data["status"] == "danger"
    assert len(data["message"]) > 0

def test_analyze_safety_missing_data():
    """
    Tests that the endpoint requires the full aggregated payload to make a safe decision.
    """
    url = f"{BASE_URL}/analyze/safety"
    payload = {
        "target_medicine": {"name": "Ibuprofen", "dosage": "400mg"}
        # Missing user_context and history completely
    }
    
    response = requests.post(url, json=payload, timeout=5.0)
    
    # Should be rejected before hitting the LLM to save compute/costs
    assert response.status_code in [400, 422]

# ==========================================
# 2. GET /analysis/history/{userId}
# ==========================================
def test_get_analysis_history():
    """
    Tests retrieving the audit log of past safety checks.
    """
    url = f"{BASE_URL}/analysis/history/{TEST_USER_ID}"
    
    response = requests.get(url)
    
    assert response.status_code == 200
    
    data = response.json()
    # Expecting an array of past reports
    assert isinstance(data, list)
    
    if len(data) > 0:
        report = data[0]
        assert "target_medicine" in report
        assert "status" in report
        assert "message" in report
        assert "timestamp" in report
