This requirements document outlines the functional and technical specifications for the **User Profile Microservice**. This service acts as the source of truth for user personal information and medical safety data within the ecosystem.

---

## 1. Overview
The User Profile Microservice is responsible for managing core identity and health-related data. It must provide a secure, authenticated interface for users to manage their profiles and for other internal services to retrieve necessary contact or medical information.

---

## 2. Data Model
Each profile record will consist of the following fields:

| Field | Type | Constraints |
| :--- | :--- | :--- |
| **User ID** | UUID | Primary Key, Unique, Auto-generated |
| **Name** | String | Required, Max 100 chars |
| **Age** | Integer | Required, Range: 0–120 |
| **Phone** | String | Required, E.164 format |
| **Email** | String | Required, Unique, Valid format |
| **Emergency Contact** | Object | Required (Name: String, Phone: String) |
| **Medications** | Array | List of Strings (Optional) |
| **Created/Updated At** | Timestamp | ISO 8601 |

---

## 3. Functional Requirements (CRUD)

### 3.1 Create Profile
* **Action:** `POST /profiles`
* **Description:** Creates a new user profile.
* **Validation:** Must verify that the email is not already in use. Age must be a positive integer.

### 3.2 Read Profile
* **Action:** `GET /profiles/{userId}`
* **Description:** Retrieves the full details of a specific profile.
* **Alternative:** `GET /profiles` (Admin only) to list all users with pagination.

### 3.3 Update Profile
* **Action:** `PUT /profiles/{userId}` or `PATCH /profiles/{userId}`
* **Description:** Updates existing information.
* **Validation:** Partial updates (PATCH) should be supported for the medications list or phone number without requiring the full object.

### 3.4 Delete Profile
* **Action:** `DELETE /profiles/{userId}`
* **Description:** Deletes the user profile.
* **Constraint:** Implement **Soft Delete** (mark as `is_deleted: true`) initially to prevent accidental loss of medical history.

---

## 4. Technical Constraints & Architecture

### 4.1 Technology Stack
* **Runtime:** Node.js (Express), Python (FastAPI), or Go.
* **Database:** PostgreSQL (for relational integrity) or MongoDB (for flexibility with the medications list).
* **Containerization:** Dockerized with a multi-stage `Dockerfile`.

### 4.2 Security
* **PII Protection:** Email, phone, and emergency contacts are Personally Identifiable Information (PII). Data must be encrypted at rest.
* **Authentication:** All endpoints must require a valid JWT (JSON Web Token).
* **Authorization:** Users can only CRUD their own profiles (`owner-only` access), while an `admin` role can access all.

---

## 5. Dockerization Strategy
The service will include:
1.  **`.dockerignore`**: To exclude `node_modules` or `.env`.
2.  **Environment Variables**: Database credentials and secrets must be injected at runtime, never hardcoded in the image.
