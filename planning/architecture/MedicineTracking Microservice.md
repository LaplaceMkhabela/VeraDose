This requirements document outlines the **Medicine Tracking Microservice**. This service handles the logic for daily logs, historical data, and performance metrics based on the medication list managed by the User Profile service.

---

## 1. Overview
The Medicine Tracking Microservice is a high-write service designed to log daily compliance. It calculates behavioral metrics like "streaks" and "adherence" to help users visualize their consistency.

---

## 2. Data Model
This service uses a **Time-Series** approach to track daily actions.

| Field | Type | Constraints |
| :--- | :--- | :--- |
| **Log ID** | UUID | Primary Key |
| **User ID** | UUID | Foreign Key (Reference to Profile Service) |
| **Date** | Date | Index for fast lookups |
| **Medication Name** | String | Sourced from Profile Service |
| **Status** | Boolean | `True` (Taken), `False` (Missed) |
| **Timestamp** | DateTime | When the log was recorded |

---

## 3. Functional Requirements

### 3.1 Daily Logging (CRUD)
* **Action:** `POST /logs`
* **Description:** Records the status of a specific medication for the current day.
* **Validation:** Prevent duplicate logs for the same medication on the same date.

### 3.2 Automated Score Computation
The service must calculate the following metrics on demand:

* **Adherence Score:**
    $$\text{Score} = \left( \frac{\text{Total Days Taken}}{\text{Total Days Tracked}} \right) \times 100$$
* **Monthly Streak:** The number of consecutive days where **all** medications were marked "Taken" within the current calendar month.
* **Missed Days:** A list of dates where at least one medication was marked "Missed" or had no entry.

### 3.3 Profile Integration
* **Mechanism:** Upon a `GET /summary` request, this service queries the **User Profile Microservice** (via internal REST or gRPC) to get the current `list_of_medications`.
* **Sync Logic:** If a user adds a new medication today, the tracker should immediately include it in the "To-Be-Taken" list.

---

## 4. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/logs` | Log a medication as taken/missed. |
| **GET** | `/history/{userId}` | Get logs for a specific date range. |
| **GET** | `/stats/{userId}` | Get Adherence, Streaks, and Missed Days. |
| **DELETE** | `/logs/{logId}` | Correct an accidental entry. |

---

## 5. Technical Architecture & Dockerization

### 5.1 Communication Pattern
Since this service depends on the Profile service, you should implement a **Circuit Breaker** pattern. If the Profile service is down, the Tracking service should cache the last known medication list to allow the user to continue logging.



### 5.2 Docker Orchestration
In your root `docker-compose.yml`, this service will require:
* **Environment Variables:** `PROFILE_SERVICE_URL` to allow internal communication.
* **Database:** A separate volume from the Profile service to ensure data isolation (Database-per-service pattern).

### 5.3 Performance Requirement
The "Streak" calculation can be computationally expensive if calculated from scratch every time.
* **Strategy:** Implement a small Redis cache to store the "Current Streak" value, updating it only when a new `POST /logs` occurs.

---

## 6. Logic for Edge Cases
* **Timezone Handling:** Logs must be stored in UTC but displayed based on the user's local timezone to ensure a "day" is defined correctly.
* **Medication Removal:** If a medication is removed from the Profile Service, historical logs for that medication should remain but it should stop appearing in "today's" requirements.
