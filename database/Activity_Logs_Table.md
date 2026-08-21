# Activity Logs Table

## Purpose

Stores all user activities performed within the TreeFlow AI platform for auditing and tracking.

---

## Table Name

activity_logs

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Activity Log ID |
| user_id | UUID | FK | User who performed the action |
| action | VARCHAR(255) | - | Activity Name |
| module | VARCHAR(100) | - | Module Name |
| description | TEXT | - | Activity Details |
| ip_address | VARCHAR(45) | - | User IP Address |
| device_info | TEXT | - | Browser / Device Information |
| created_at | TIMESTAMP | - | Activity Time |

---

## Relationships

- One User can have multiple Activity Logs.

---

## Constraints

- id is Primary Key.
- user_id is Foreign Key.
- created_at is automatically generated.