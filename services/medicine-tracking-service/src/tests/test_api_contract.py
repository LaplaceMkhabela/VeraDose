import pytest
import requests
import uuid
from datetime import datetime, timezone, timedelta

# Base URL of the running Medicine Tracking Microservice
BASE_URL = "http://localhost:8080"

# Generate some consistent mock IDs for the test suite
TEST_USER_ID = str(uuid.uuid4())
TEST_LOG_ID = str(uuid.uuid4())
TODAY_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ==========================================
# 1. POST /logs
# ==========================================
def test_create_daily_log_success():
    url = f"{BASE_URL}/logs"
    payload = {
        "user_id": TEST_USER_ID,
        "date": TODAY_DATE,
        "medication_name": "Lisinopril",
        "dose": "20mg",                  # <-- NEW FIELD
        "scheduled_time": "08:00",       # <-- NEW FIELD
        "status": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    response = requests.post(url, json=payload)
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert "log_id" in data

def test_create_daily_log_duplicate_prevention():
    url = f"{BASE_URL}/logs"
    payload = {
        "user_id": TEST_USER_ID,
        "date": TODAY_DATE,
        "medication_name": "Lisinopril", 
        "dose": "20mg",                  # <-- NEW FIELD
        "scheduled_time": "08:00",       # <-- NEW FIELD
        "status": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Send it twice
    requests.post(url, json=payload)
    response = requests.post(url, json=payload)
    
    # Prevent duplicate logs for the same medication/dose/time on the same date
    assert response.status_code in [400, 409]

# ==========================================
# 2. GET /history/{userId}
# ==========================================
def test_get_history_with_date_range():
    url = f"{BASE_URL}/history/{TEST_USER_ID}"
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = TODAY_DATE
    
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = requests.get(url, params=params)
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    if len(data) > 0:
        log = data[0]
        assert "log_id" in log
        assert "date" in log
        assert "medication_name" in log
        assert "status" in log
        assert type(log["status"]) is bool
        # Assert the new fields are returned in the history payload
        assert "dose" in log             # <-- NEW ASSERTION
        assert "scheduled_time" in log   # <-- NEW ASSERTION

# ==========================================
# 3. GET /stats/{userId}
# ==========================================
def test_get_user_stats():
    # Note: Stats likely calculates based on boolean "status" over time, 
    # but the test contract remains the same regardless of dose/time additions.
    url = f"{BASE_URL}/stats/{TEST_USER_ID}"
    
    response = requests.get(url)
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert "adherence_score" in data
    assert 0 <= data["adherence_score"] <= 100 
    
    assert "monthly_streak" in data
    assert type(data["monthly_streak"]) is int
    
    assert "missed_days" in data
    assert isinstance(data["missed_days"], list)

# ==========================================
# 4. DELETE /logs/{logId}
# ==========================================
def test_delete_log_success():
    create_url = f"{BASE_URL}/logs"
    payload = {
        "user_id": TEST_USER_ID,
        "date": TODAY_DATE,
        "medication_name": "AccidentalMed",
        "dose": "1 puff",                # <-- NEW FIELD
        "scheduled_time": "14:00",       # <-- NEW FIELD
        "status": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    create_response = requests.post(create_url, json=payload)
    
    # Safely get the log_id if creation was successful, otherwise fallback to mock for the test to fail logically
    log_id_to_delete = create_response.json().get("log_id") if create_response.status_code in [200, 201] else TEST_LOG_ID
    
    delete_url = f"{BASE_URL}/logs/{log_id_to_delete}"
    response = requests.delete(delete_url)
    
    assert response.status_code in [200, 204]

def test_delete_log_not_found():
    fake_log_id = str(uuid.uuid4())
    delete_url = f"{BASE_URL}/logs/{fake_log_id}"
    
    response = requests.delete(delete_url)
    
    assert response.status_code == 404
