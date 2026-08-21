# User Roles Table

## Purpose

Stores the relationship between users and their assigned roles.

---

## Table Name

user_roles

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Record ID |
| user_id | UUID | FK | User ID |
| role_id | UUID | FK | Role ID |
| assigned_by | UUID | FK | User who assigned the role |
| assigned_at | TIMESTAMP | - | Role Assignment Time |
| status | VARCHAR(20) | - | Active / Inactive |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |

---

## Relationships

- One User can have multiple Roles.
- One Role can be assigned to multiple Users.
- user_id references users.id.
- role_id references roles.id.

---

## Constraints

- id is Primary Key.
- user_id is Foreign Key.
- role_id is Foreign Key.
- assigned_by is Foreign Key.
- status defaults to Active.