# Roles Table

## Purpose

Stores all user roles and permission levels in TreeFlow AI.

---

## Table Name

roles

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Role ID |
| name | VARCHAR(100) | UNIQUE | Role Name |
| description | TEXT | - | Role Description |
| level | INTEGER | - | Permission Level |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |

---

## Default Roles

- Super Admin
- Company Admin
- Manager
- Team Lead
- Employee
- Client

---

## Relationships

- One Role can be assigned to multiple Users.
- Roles are linked through the user_roles table.

---

## Constraints

- id is Primary Key.
- name must be unique.
- level must be greater than 0.