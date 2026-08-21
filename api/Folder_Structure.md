# TreeFlow AI - Backend Folder Structure

## Overview

TreeFlow AI follows a modular and scalable folder structure based on FastAPI best practices.

---

# Project Structure

```
TreeFlow-AI/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   ├── dependencies.py
│   │   │   └── routes.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── settings.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   │
│   │   ├── models/
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── services/
│   │   │
│   │   ├── repositories/
│   │   │
│   │   ├── middleware/
│   │   │
│   │   ├── utils/
│   │   │
│   │   ├── exceptions/
│   │   │
│   │   ├── tests/
│   │   │
│   │   └── main.py
│   │
│   ├── alembic/
│   │
│   ├── requirements.txt
│   │
│   ├── .env
│   │
│   ├── .gitignore
│   │
│   └── README.md
│
├── frontend/
│
├── database/
│
├── api/
│
├── docs/
│
├── assets/
│
├── ui-design/
│
└── README.md
```

---

# Folder Description

## app/

Main FastAPI application.

---

## api/

Contains all API routes.

Example

- Authentication
- Users
- Companies
- Projects
- Tasks

---

## core/

Application configuration.

Contains

- Config
- JWT
- Security
- Settings

---

## database/

Database connection.

Contains

- SQLAlchemy Engine
- Session
- Base Model

---

## models/

SQLAlchemy Models

Example

- User
- Company
- Task
- Project

---

## schemas/

Pydantic Schemas

Used for

- Request Validation
- Response Validation

---

## services/

Business Logic

Example

- Authentication Service
- Task Service
- Report Service

---

## repositories/

Database Queries

Responsible for

- CRUD Operations
- Query Optimization

---

## middleware/

Application