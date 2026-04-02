This **Reminder Microservice** acts as the proactive engine of your application. Unlike the other services that wait for user input, this service must operate on a schedule to "watch" the state of both the Profile and Tracking services.

---

## 1. Overview
The Reminder Microservice is a background-worker-heavy service. It periodically reconciles the **expected** medications (from the Profile Service) with the **actual** logs (from the Medicine Tracking Service) and triggers notifications through an external provider (like Firebase Cloud Messaging or Twilio).

---

## 2. Functional Requirements

### 2.1 Scheduled Notification Logic
The service must run a "Check Loop" (Cron Job) to evaluate the following:

* **T-Minus 5 Minutes:** Identify medications scheduled for $T$. If no "Taken" log exists for today, send a "Pre-reminder."
* **On-Time ($T$):** If no "Taken" log exists at the exact scheduled time, send the primary "Take your medicine" alert.
* **Missed Alert:** At the end of the scheduled window (e.g., 30 minutes after $T$), if the status is still not "Taken," send a "Missed Medication" notification.

### 2.2 Integration Requirements
This service is the primary consumer of your other two microservices:
1.  **Fetch Schedule:** Query the `User Profile Microservice` to get medication names, dosage times, and the user’s phone/email.
2.  **Check Status:** Query the `Medicine Tracking Microservice` to see if a `POST /logs` entry exists for "today + medication_id."

---

## 3. Architecture & Components

### 3.1 The Scheduler (Task Queue)
Because you need precise timing (exactly 5 minutes before), a standard Cron job might be too "blunt." 
* **Recommendation:** Use a Distributed Task Queue like **Redis with Celery (Python)**, **BullMQ (Node.js)**, or **Sidekiq (Ruby)**.
* **Workflow:** When a user updates their profile, a task is scheduled for each medication time.

### 3.2 Data Model (Internal Cache)
To avoid hammering the other services every minute, this service should maintain a lightweight "Daily Schedule" cache.

| Field | Type | Description |
| :--- | :--- | :--- |
| **User ID** | UUID | To map notifications to the right device. |
| **Medication ID**| String | Reference to the medicine. |
| **Scheduled Time**| DateTime | The exact time it should be taken. |
| **Notification State**| Enum | `PENDING`, `SENT_5MIN`, `SENT_ON_TIME`, `MISSED_SENT`. |

---

## 4. API & Communication

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/trigger-test` | Manually trigger a notification (for debugging). |
| **PATCH** | `/preferences/{userId}` | Update notification preferences (e.g., "Mute 5-min reminders"). |

---

## 5. Dockerization & Deployment

### 5.1 Service Dependencies
In your `docker-compose.yml`, this service requires:
* **Redis Container:** Used as the message broker for the task queue.
* **Worker Container:** A second instance of your code running in "worker mode" to process the background tasks.



### 5.2 Reliability Patterns
* **Idempotency:** Ensure that if the service restarts, it doesn't accidentally send the same "5-minute reminder" three times.
* **Retry Logic:** If the Notification Provider (e.g., Firebase) is down, the service should retry with exponential backoff.

---

## 6. Logic Flow for Reminders

To determine if a notification is needed:

1.  **Poll** the Profile Service for all users.
2.  For each medication, **Compare** the current time ($T_{now}$) with the scheduled time ($T_{sch}$).
3.  **Check** Tracking Service: `IsMedicationTaken(userId, medId, today)`.
4.  **Execute:**
    * If $T_{now} = (T_{sch} - 5min)$ AND NOT Taken $\rightarrow$ **Notify**.
    * If $T_{now} = T_{sch}$ AND NOT Taken $\rightarrow$ **Notify**.
    * If $T_{now} > (T_{sch} + Window)$ AND NOT Taken $\rightarrow$ **Notify Missed**.
