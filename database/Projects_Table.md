# Projects Table

## Purpose

Stores project information for each department within a company.

---

## Table Name

projects

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Project ID |
| company_id | UUID | FK | Company ID |
| department_id | UUID | FK | Department ID |
| created_by | UUID | FK | User who created the project |
| name | VARCHAR(255) | - | Project Name |
| description | TEXT | - | Project Description |
| start_date | DATE | - | Project Start Date |
| end_date | DATE | - | Project End Date |
| budget | DECIMAL(12,2) | - | Project Budget |
| priority | VARCHAR(20) | - | Low / Medium / High / Critical |
| status | VARCHAR(20) | - | Planning / Active / Completed / Cancelled |
| progress | INTEGER | - | Completion Percentage (0–100) |
| is_deleted | BOOLEAN | - | Soft Delete Flag |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |

---

## Relationships

- One Company can have multiple Projects.
- One Department can have multiple Projects.
- One User can create multiple Projects.
- One Project can contain multiple Tree Nodes.
- One Project can contain multiple Tasks.

---

## Constraints

- id is Primary Key.
- company_id is Foreign Key.
- department_id is Foreign Key.
- created_by is Foreign Key.
- progress must be between 0 and 100.
- is_deleted defaults to False.