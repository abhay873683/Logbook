# TreeFlow AI - API Response Format

## Overview

All APIs in TreeFlow AI return responses in JSON format.

Every response follows a consistent structure for success and error handling.

---

# Response Structure

Every API response contains:

- status
- message
- data
- errors (if any)
- timestamp

---

# Success Response

HTTP Status Code

200 OK

```json
{
    "status": "success",
    "message": "Request completed successfully.",
    "data": {},
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Resource Created

HTTP Status Code

201 Created

```json
{
    "status": "success",
    "message": "Resource created successfully.",
    "data": {
        "id": "uuid"
    },
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# No Content

HTTP Status Code

204 No Content

Description

The request completed successfully, but no response body is returned.

---

# Validation Error

HTTP Status Code

422 Unprocessable Entity

```json
{
    "status": "error",
    "message": "Validation failed.",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email address."
        }
    ],
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Bad Request

HTTP Status Code

400 Bad Request

```json
{
    "status": "error",
    "message": "Invalid request.",
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Unauthorized

HTTP Status Code

401 Unauthorized

```json
{
    "status": "error",
    "message": "Authentication required.",
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Forbidden

HTTP Status Code

403 Forbidden

```json
{
    "status": "error",
    "message": "Access denied.",
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Not Found

HTTP Status Code

404 Not Found

```json
{
    "status": "error",
    "message": "Requested resource not found.",
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Conflict

HTTP Status Code

409 Conflict

```json
{
    "status": "error",
    "message": "Resource already exists.",
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Internal Server Error

HTTP Status Code

500 Internal Server Error

```json
{
    "status": "error",
    "message": "Internal server error.",
    "timestamp": "2026-07-11T10:30:00Z"
}
```

---

# Pagination