# Requirements Document: Authentication Microservice

---

## 1. Executive Summary
**Purpose:** To provide a centralized, secure, and scalable authentication and authorization service for all internal applications and microservices.
**Version:** 1.0
**Status:** Draft

## 2. Scope
This microservice will handle user identity management, login flows, token issuance, and permission validation. It will not handle user profile data (e.g., avatars, bios) beyond credentials and basic contact info; that is delegated to a separate User Profile Service.

---

---
## 3. Functional Requirements

### 3.1. User Registration
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system shall accept email, password, and required metadata to create a new user account. | High |
| FR-02 | The system shall enforce password complexity rules (min 8 chars, mix of cases, numbers, special characters). | High |
| FR-03 | The system shall hash passwords before storage. | Critical |
| FR-04 | The system shall send a verification email with a one-time token to verify the user's email address. | High |
| FR-05 | The system shall prevent duplicate email registrations. | High |

### 3.2. Authentication (Login)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-06 | The system shall authenticate users using Email/Password and return an ID Token and Access Token (JWT). | High |
| FR-07 | The system shall support "Remember Me" functionality, issuing refresh tokens with longer expiration (30 days) vs. short-lived access tokens (15 minutes). | High |
| FR-08 | The system shall lock an account after 5 failed login attempts for 15 minutes to prevent brute force attacks. | High |

### 3.3. Authorization
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-09 | The system shall issue signed JWTs using RS256 (private/public key pair). | Critical |
| FR-10 | The system shall support Role-Based Access Control (RBAC) (e.g., Admin, User, Viewer). | High |

---

---
## 4. API Contracts (High-Level)

### 4.1. Public API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user. |
| `/api/v1/auth/login` | POST | Authenticate and return tokens. |
| `/api/v1/auth/logout` | POST | Revoke current token/session. |
| `/api/v1/auth/refresh` | POST | Rotate refresh token. |
| `/api/v1/auth/verify` | GET | Verify email with OTP. |

### 4.2. Internal API
| Endpoint | Method | Description | Consumers |
|----------|--------|-------------|-----------|
| `/internal/v1/users/{id}/permissions` | GET | Fetch permissions for a user. | Authorization Service |

---
---

## 5. Data Model (Simplified)

### `users` (PostgreSQL/MySQL/SQLite)
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `email` | VARCHAR(255) | Unique, indexed |
| `password_hash` | VARCHAR(255) | Nullable for SSO users |
| `is_verified` | BOOLEAN | Email verification status |
| `role` | VARCHAR(50) | User role (admin, user, viewer) |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

---

