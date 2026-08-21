# Comments Table

## Purpose

Stores comments made by users on tasks.

---

## Table Name

comments

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Comment ID |
| task_id | UUID | FK | Related Task ID |
| user_id | UUID | FK | User who wrote the comment |
| comment | TEXT | - | Comment Text |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |
| is_deleted | BOOLEAN | - | Soft Delete Flag |

---

## Relationships

- One Task can have multiple Comments.
- One User can write multiple Comments.

---

## Constraints

- id is Primary Key.
- task_id is Foreign Key.
- user_id is Foreign Key.
- is_deleted defaults to False.