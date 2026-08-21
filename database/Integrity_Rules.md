# TreeFlow AI - Data Integrity Rules

## Purpose

Data Integrity ensures that all information stored in the database is accurate, valid, consistent, and secure.

---

# 1. Entity Integrity

- Every table must have a UUID Primary Key.
- Primary Key values must be unique.
- Primary Key cannot be NULL.

Example:

companies.id

users.id

projects.id

tasks.id

---

# 2. Referential Integrity

Every Foreign Key must reference an existing record.

Examples

departments.company_id → companies.id

users.company_id → companies.id

projects.department_id → departments.id

tree_nodes.project_id → projects.id

tasks.node_id → tree_nodes.id

comments.task_id → tasks.id

comments.user_id → users.id

files.task_id → tasks.id

notifications.user_id → users.id

activity_logs.user_id → users.id

reports.user_id → users.id

---

# 3. Domain Integrity

Only valid values are allowed.

Task Status

- Todo
- In Progress
- Review
- Testing
- Completed
- Cancelled

Priority

- Low
- Medium
- High

Company Status

- Active
- Inactive

User Status

- Active
- Blocked

---

# 4. Unique Integrity

The following values must always remain unique.

users.email

companies.email

companies.domain

roles.name

---

# 5. NOT NULL Rules

These fields cannot be empty.

name

email

password_hash

company_id

project_id

node_id

created_at

---

# 6. Default Values

created_at = CURRENT_TIMESTAMP

updated_at = CURRENT_TIMESTAMP

status = Active

priority = Medium

is_deleted = FALSE

---

# 7. Soft Delete Rule

Records are never permanently deleted.

Instead:

is_deleted = TRUE

deleted_at = CURRENT_TIMESTAMP

---

# 8. Timestamp Rules

Every table should contain:

created_at

updated_at

created_by

updated_by

---

# 9. Data Validation Rules

Email must be valid.

Password must be hashed.

UUID must be generated automatically.

Date fields must store valid dates.

Budget cannot be negative.

Estimated time cannot be negative.

---

# 10. Relationship Integrity

A Project cannot exist without a Department.

A Department cannot exist without a Company.

A Task cannot exist without a Tree Node.

A Comment cannot exist without a Task.

A File cannot exist without a Task.

---

# 11. Cascade Rules

Deleting a Company deletes all Departments.

Deleting a Department deletes all Projects.

Deleting a Project deletes all Tree Nodes.

Deleting a Tree Node deletes all Tasks.

Deleting a Task deletes Comments and Files.

---

# 12. Audit Rules

Every important action must be stored in Activity Logs.

Store:

- User
- Action
- Module
- Timestamp
- Old Values
- New Values
- IP Address

---

# 13. Security Rules

Passwords are stored only as hashes.

JWT Authentication will be used.

Role Based Access Control (RBAC).

HTTPS required in production.

SQL Injection protection.

XSS protection.

CSRF protection.

---

# Summary

✔ Entity Integrity

✔ Referential Integrity

✔ Domain Integrity

✔ Unique Constraints

✔ NOT NULL Validation

✔ Default Values

✔ Soft Delete

✔ Relationship Integrity

✔ Cascade Rules

✔ Audit Rules

✔ Security Rules