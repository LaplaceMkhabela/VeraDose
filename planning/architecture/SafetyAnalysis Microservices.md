This final service, the **Safety Analysis Microservice**, acts as the "expert" layer of your application. It processes sensitive medical data to provide a safety gate before the Reminder or Tracking services take over.

---

## 1. Overview
The Safety Analysis Microservice is a stateless, computation-heavy service. It takes a proposed medication and cross-references it against the user's existing profile and health data using a Large Language Model (LLM) to identify potential contraindications.

---

## 2. Input Data Requirements
To perform an accurate check, the service requires a combined payload (often aggregated by an API Gateway or a specialized "Orchestrator"):

* **Target Medicine:** Name, Dosage (e.g., 500mg), Frequency.
* **User Context:** Weight, Age, and reported Illness/Symptoms.
* **History (from Profile Service):** Known Allergies and current Medication List.

---

## 3. Functional Requirements (The Triple-Check)

### 3.1 Dosage & Indication Verification
* **Logic:** The LLM checks if the medicine is typically prescribed for the stated illness and if the dose is appropriate for the user's weight/age.
* **Output:** `SAFE`, `CAUTION` (High Dose), or `INVALID` (Wrong Medication for Condition).

### 3.2 Drug-Drug Interaction (DDI)
* **Logic:** The LLM compares the **Target Medicine** against the **Users Medicine List**.
* **Output:** Identification of synergistic or antagonistic effects (e.g., "Drug A increases the toxicity of Drug B").

### 3.3 Allergy Alert
* **Logic:** The LLM scans the ingredients of the Target Medicine against the **User Allergies**.
* **Output:** Immediate `CRITICAL` alert if a match is found.

---

## 4. Technical Architecture

### 4.1 Prompt Engineering & Structure
The core of this service is the "System Prompt." It must instruct the LLM to act as a clinical pharmacist and return **Structured JSON** for easy parsing by your frontend.

**Example Internal Prompt Structure:**
> "You are a clinical safety AI. Analyze the following: [Medicine Name] for [Illness] at [Dose]. User weighs [Weight] and takes [Med List]. User is allergic to [Allergies]. Return JSON: {status: 'clear'|'warning'|'danger', message: 'string'}"

### 4.2 Security & Privacy
Since this service handles PII (Personally Identifiable Information) and health data:
* **Data Masking:** Before sending data to an external LLM API (like Gemini or OpenAI), remove names and specific IDs. Only send the medical facts.
* **Audit Logging:** Every "Safety Check" must be logged (anonymously) for medical-legal liability.

---

## 5. API Definition

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/analyze/safety` | Receives the full health payload and returns the LLM analysis. |
| **GET** | `/analysis/history/{userId}` | Retrieves past safety reports. |

---

## 6. Dockerization & Integration

### 6.1 The "Orchestrator" Pattern
In a dockerized environment, the **Safety Microservice** should not talk to the database directly. 
1.  **API Gateway** receives a request to "Add Medicine."
2.  **Gateway** fetches data from the **Profile Service**.
3.  **Gateway** sends the compiled data to the **Safety Service**.
4.  If **Safety Service** returns `clear`, the Gateway then tells the **Profile Service** to save the new medicine.

### 6.2 Docker Compose Specifics
* **Secrets Management:** Use Docker Secrets or an `.env` file to store your LLM API Keys. **Never** bake these into the image.
* **Resource Limits:** LLM processing can be slow. Set a higher `timeout` in your Nginx/Gateway config for this specific route (e.g., 30 seconds) to allow the LLM time to respond.

---

## 7. Summary of your 4-Service App
1.  **User Profile:** Stores PII, Allergies, and Med List.
2.  **Medicine Tracking:** Logs daily "Taken/Missed" status and scores.
3.  **Reminder:** Proactively alerts users based on the schedule.
4.  **Safety Analysis:** Uses AI to verify safety before a med is added to the profile.
