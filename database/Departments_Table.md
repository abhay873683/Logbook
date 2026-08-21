# Departments Table

## Purpose

Stores department information for each company.

---

## Table Name

departments

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Department ID |
| company_id | UUID | FK | Company ID |
| name | VARCHAR(255) | - | Department Name |
| description | TEXT | - | Department Description |
| manager_id | UUID | FK | Department Manager (User ID) |
| status | VARCHAR(20) | - | Active / Inactive |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |

---

## Relationships

- One Company can have multiple Departments.
- One Department belongs to one Company.
- One Department can have multiple Projects.
- One Department has one Manager.

---

## Constraints

- id is Primary Key.
- company_id is Foreign Key.
- manager_id references users.id.
- Department name should not be empty.