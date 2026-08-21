# Task Assignments Table

## Purpose

Stores information about which users are assigned to which tasks.

---

## Table Name

task_assignments

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Assignment ID |
| task_id | UUID | FK | Assigned Task ID |
| user_id | UUID | FK | Assigned User ID |
| assigned_by | UUID | FK | User who assigned the task |
| role | VARCHAR(50) | - | Assignee Role |
| assigned_at | TIMESTAMP | - | Assignment Date & Time |
| status | VARCHAR(20) | - | Active / Completed / Removed |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |

---

## Relationships

- One Task can have multiple Assignments.
- One User can receive multiple Task Assignments.
- One User can assign tasks to other users.

---

## Constraints

- id is Primary Key.
- task_id is Foreign Key.
- user_id is Foreign Key.
- assigned_by is Foreign Key.
- status defaults to Active.