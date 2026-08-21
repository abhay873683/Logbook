# TreeFlow AI - Authentication Flow

## Overview

TreeFlow AI uses JWT (JSON Web Token) based authentication for secure API access.

---

## Authentication Type

- JWT Authentication
- Access Token
- Refresh Token
- Bearer Token
- Role Based Access Control (RBAC)

---

## Authentication Flow

User
↓
Enter Email & Password
↓
POST /api/auth/login
↓
Validate Credentials
↓
Generate Access Token
↓
Generate Refresh Token
↓
Return Tokens
↓
Store Token (Client)
↓
Send Token in Authorization Header
↓
Backend Validates Token
↓
Check User Role & Permissions
↓
Grant or Deny Access

---

## Login Process

Step 1

User enters:

- Email
- Password

↓

Step 2

Backend validates:

- User Exists
- Password Correct
- User Active
- Company Active

↓

Step 3

Generate

- Access Token
- Refresh Token

↓

Step 4

Return Response

```json
{
    "status": "success",
    "message": "Login Successful",
    "data": {
        "access_token": "jwt_access_token",
        "refresh_token": "jwt_refresh_token",
        "token_type": "Bearer"
    }
}
```

---

## Authorization Header

Authorization: Bearer <access_token>

---

## Access Token

Purpose

- Access Protected APIs

Expiry

- 15 Minutes

---

## Refresh Token

Purpose

- Generate New Access Token

Expiry

- 7 Days

---

## JWT Payload

```json
{
    "user_id": "uuid",
    "company_id": "uuid",
    "role": "Company Admin",
    "email": "user@example.com",
    "exp": "expiration_time"
}
```

---

## Protected APIs

Requires JWT Token

- Company APIs
- Department APIs
- User APIs
- Project APIs
- Tree APIs
- Task APIs
- File APIs
- Report APIs
- Notification APIs

---

## Public APIs

No Authentication Required

- Login
- Register
- Forgot Password
- Reset Password
- Refresh Token

---

## Authentication Security

- BCrypt Password Hashing
- JWT Signature Verification
- Token Expiration
- HTTPS Required
- Role Verification
- Permission Verification
- Secure Password Policy
- Refresh Token Rotation

---

## Error Responses

### Invalid Credentials

```json
{
    "status": "error",
    "message": "Invalid Email or Password"
}
```

### Unauthorized

```json
{
    "status": "error",
    "message": "Unauthorized"
}
```

### Token Expired

```json
{
    "status": "error",
    "message": "Token Expired"
}
```

---

## Authentication Sequence

Client

↓

Login Request

↓

FastAPI

↓

Validate User

↓

PostgreSQL

↓

Password Verification

↓

JWT Token Generation

↓

Response

↓

Client Stores Token

↓

Protected API Request

↓

JWT Verification

↓

Role Verification

↓

Access Granted

---

## Technologies Used

- FastAPI
- JWT
- OAuth2 Password Bearer
- SQLAlchemy
- PostgreSQL
- BCrypt
- Pydantic

---

## Future Improvements

- Multi-Factor Authentication (MFA)
- Google Login
- GitHub Login
- Microsoft Login
- Session Management
- Device Tracking

---

## Status

✅ Authentication Flow Designed

✅ JWT Flow Completed

✅ Token Strategy Completed

✅ Authorization Planned

✅ Ready for Backend Implementation