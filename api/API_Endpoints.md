# TreeFlow AI - API Endpoints

## Overview

Base URL

/api

---

Authentication

JWT Bearer Token

---

Response Format

JSON

---

Content Type

application/json

---

## Authentication APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login user |
| POST | /api/auth/refresh | Refresh access token |
| POST | /api/auth/logout | Logout current user |
| POST | /api/auth/forgot-password | Forgot password |
| POST | /api/auth/reset-password | Reset password |
| GET | /api/auth/me | Current user profile |

---

## Company APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/companies | Get all companies |
| GET | /api/companies/{id} | Get company by ID |
| POST | /api/companies | Create company |
| PUT | /api/companies/{id} | Update company |
| DELETE | /api/companies/{id} | Delete company |

---

## Department APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/departments | Get departments |
| GET | /api/departments/{id} | Get department |
| POST | /api/departments | Create department |
| PUT | /api/departments/{id} | Update department |
| DELETE | /api/departments/{id} | Delete department |

---

## User APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/users | Get users |
| GET | /api/users/{id} | Get user |
| POST | /api/users | Create user |
| PUT | /api/users/{id} | Update user |
| DELETE | /api/users/{id} | Delete user |

---

## Role APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/roles | Get roles |
| POST | /api/roles | Create role |
| PUT | /api/roles/{id} | Update role |
| DELETE | /api/roles/{id} | Delete role |

---

## Project APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/projects | Get projects |
| GET | /api/projects/{id} | Get project |
| POST | /api/projects | Create project |
| PUT | /api/projects/{id} | Update project |
| DELETE | /api/projects/{id} | Delete project |

---

## Tree APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/trees | Get trees |
| GET | /api/trees/{id} | Get tree |
| POST | /api/trees | Create tree |
| PUT | /api/trees/{id} | Update tree |
| DELETE | /api/trees/{id} | Delete tree |
| POST | /api/trees/{id}/nodes | Add node |
| PUT | /api/trees/nodes/{id} | Update node |
| DELETE | /api/trees/nodes/{id} | Delete node |

---

## Task APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/tasks | Get tasks |
| GET | /api/tasks/{id} | Get task |
| POST | /api/tasks | Create task |
| PUT | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| POST | /api/tasks/{id}/assign | Assign task |
| PUT | /api/tasks/{id}/status | Update task status |

---

## Comment APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/comments | Get comments |
| POST | /api/comments | Add comment |
| PUT | /api/comments/{id} | Update comment |
| DELETE | /api/comments/{id} | Delete comment |

---

## File APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /api/files/upload | Upload file |
| GET | /api/files/{id} | Download file |
| DELETE | /api/files/{id} | Delete file |
| GET | /api/files/list/{module} | List module files |

---

## Notification APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/notifications | Get notifications |
| PUT | /api/notifications/{id}/read | Mark as read |
| DELETE | /api/notifications/{id} | Delete notification |

---

## Report APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/reports | Get reports |
| GET | /api/reports/{id} | Get report |
| POST | /api/reports/generate | Generate report |
| DELETE | /api/reports/{id} | Delete report |

---

## AI APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /api/ai/analyze | Analyze data |
| POST | /api/ai/chat | AI Chat |
| GET | /api/ai/history | AI History |
| DELETE | /api/ai/history/{id} | Delete history |

---

## Activity Log APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/activity-logs | Get logs |
| GET | /api/activity-logs/{id} | Get log details |

---

## HTTP Status Codes

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

## Security

- JWT Authentication
- Bearer Token
- HTTPS Only
- Role Based Access Control (RBAC)
- Input Validation
- Rate Limiting
- Request Logging

---

## API Version

v1.0

---

## Status

✅ Authentication APIs Planned

✅ Company APIs Planned

✅ Department APIs Planned

✅ User APIs Planned

✅ Project APIs Planned

✅ Tree APIs Planned

✅ Task APIs Planned

✅ File APIs Planned

✅ Report APIs Planned

✅ AI APIs Planned

✅ Ready for FastAPI Development (Day 12)