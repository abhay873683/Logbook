# Tasks Table

## Purpose

Stores all tasks and work items assigned within projects.

---

## Table Name

tasks

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Task ID |
| node_id | UUID | FK | Related Tree Node |
| title | VARCHAR(255) | - | Task Title |
| description | TEXT | - | Task Description |
| priority | VARCHAR(20) | - | Low / Medium / High / Critical |
| status | VARCHAR(20) | - | Todo / In Progress / Review / Completed |
| start_date | DATE | - | Task Start Date |
| due_date | DATE | - | Task Due Date |
| estimate_time | INTEGER | - | Estimated Hours |
| actual_time | INTEGER | - | Actual Hours Spent |
| progress | INTEGER | - | Completion Percentage |
| created_by | UUID | FK | User who created task |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |
| is_deleted | BOOLEAN | - | Soft Delete Flag |

---

## Relationships

- One Tree Node can have multiple Tasks.
- One User can create multiple Tasks.
- One Task can have multiple Assignments.
- One Task can have multiple Comments.
- One Task can have multiple Files.

---

## Constraints

- id is Primary Key.
- node_id is Foreign Key.
- created_by is Foreign Key.
- progress must be between 0 and 100.
- is_deleted defaults to False.