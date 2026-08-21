# Companies Table

## Purpose

Stores company or organization information for the multi-tenant TreeFlow AI platform.

---

## Table Name

companies

---

# Companies Table

| Column | Data Type | Constraint | Default | Description |
|---------|-----------|------------|----------|-------------|
| id | UUID | PK | gen_random_uuid() | Company ID |
| name | VARCHAR(255) | NOT NULL | - | Company Name |
| email | VARCHAR(255) | UNIQUE | - | Company Email |
| phone | VARCHAR(20) | NULL | - | Phone Number |
| domain | VARCHAR(255) | UNIQUE | - | Company Domain |
| plan_type | VARCHAR(20) | NOT NULL | free | Subscription Plan |
| status | VARCHAR(20) | NOT NULL | active | Company Status |
| created_at | TIMESTAMP | NOT NULL | now() | Created Time |
| updated_at | TIMESTAMP | NOT NULL | now() | Updated Time |

---

## Relationships

- One Company can have multiple Users.
- One Company can have multiple Departments.
- One Company can have multiple Projects.

---

## Constraints

- id is Primary Key.
- email must be unique.
- status defaults to Active.