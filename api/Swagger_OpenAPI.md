# TreeFlow AI - Swagger & OpenAPI Documentation

## Overview

TreeFlow AI uses OpenAPI 3.0 specification with Swagger UI for interactive API documentation.

Swagger automatically documents every API endpoint, request body, response model, authentication method, and error response.

---

# API Documentation

Documentation Tool

- Swagger UI
- OpenAPI 3.0

---

# API Information

Title

TreeFlow AI API

Version

v1.0.0

Description

REST API for TreeFlow AI Project Management Platform.

License

MIT License

Contact

Developer Team

Email

support@treeflow.ai

---

# Base URL

Development

http://localhost:8000

Production

https://api.treeflow.ai

---

# API Prefix

/api/v1

---

# Authentication

Authentication Type

JWT Bearer Token

Authorization Header

Authorization: Bearer <access_token>

Protected APIs require a valid JWT token.

---

# Swagger URL

Development

/docs

Example

http://localhost:8000/docs

---

# ReDoc URL

/redoc

Example

http://localhost:8000/redoc

---

# OpenAPI JSON

/openapi.json

Example

http://localhost:8000/openapi.json

---

# API Tags

## Authentication

- Login
- Register
- Logout
- Refresh Token

---

## Companies

- Create Company
- Update Company
- Delete Company
- Get Companies

---

## Departments

- Create Department
- Update Department
- Delete Department
- Get Departments

---

## Users

- Create User
- Update User
- Delete User
- Get Users

---

## Roles

- Create Role
- Assign Role
- Remove Role

---

## Projects

- Create Project
- Update Project
- Delete Project
- Get Projects

---

## Tree Management

- Create Tree
- Update Tree
- Delete Tree
- Manage Nodes

---

## Tasks

- Create Task
- Assign Task
- Update Task
- Delete Task
- Change Status

---

## Comments

- Add Comment
- Update Comment
- Delete Comment

---

## Files

- Upload File
- Download File
- Delete File

---

## Notifications

- Get Notifications
- Mark As Read

---

## Reports

- Generate Report
- Export Report
- Download Report

---

## AI Module

- AI Chat
- AI Suggestions
- AI History

---

# Request Format

Content Type

application/json

Supported Methods

- GET
- POST
- PUT
- PATCH
- DELETE

---

# Response Format

All responses return JSON.

Example

```json
{
    "status": "success",
    "message": "Operation completed successfully.",
    "data": {}
}
```

---

# HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# API Versioning

Current Version

v1

Future Versions

- v2
- v3

Version Format

/api/v1

---

# Security Schemes

JWT Authentication

Bearer Token

HTTPS

Role Based Access Control (RBAC)

Input Validation

Rate Limiting

---

# Documentation Features

- Interactive API Testing
- Request Examples
- Response Examples
- Authentication Support
- Error Documentation
- Model Schemas
- Validation Rules

---

# Development Workflow

Design API

↓

Implement FastAPI

↓

Generate OpenAPI

↓

Swagger Documentation

↓

Testing

↓