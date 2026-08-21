# Notifications Table

## Purpose

Stores all notifications sent to users.

---

## Table Name

notifications

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Notification ID |
| user_id | UUID | FK | Recipient User ID |
| title | VARCHAR(255) | - | Notification Title |
| message | TEXT | - | Notification Message |
| type | VARCHAR(50) | - | Task, Project, System, Reminder |
| is_read | BOOLEAN | - | Read Status |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |

---

## Relationships

- One User can receive multiple Notifications.

---

## Constraints

- id is Primary Key.
- user_id is Foreign Key.
- is_read defaults to False.