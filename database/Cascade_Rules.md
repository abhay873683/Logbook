# TreeFlow AI - Cascade Rules

## Purpose

Cascade Rules define what happens to related records when a parent record is updated or deleted.

---

# ON DELETE CASCADE

Deleting a parent record automatically deletes all related child records.

companies
    ↓
departments
    ↓
projects
    ↓
tree_nodes
    ↓
tasks
    ↓
comments

tasks
    ↓
files

users
    ↓
notifications

users
    ↓
activity_logs

files
    ↓
file_versions

---

# ON UPDATE CASCADE

If a Primary Key changes, all related Foreign Keys update automatically.

Examples

companies.id → departments.company_id

departments.id → projects.department_id

projects.id → tree_nodes.project_id

tree_nodes.id → tasks.node_id

tasks.id → comments.task_id

tasks.id → files.task_id

users.id → reports.user_id

users.id → ai_history.user_id

---

# ON DELETE SET NULL

Some relationships should not delete child records.

Examples

departments.manager_id

projects.created_by

files.uploaded_by

If parent record is removed:

manager_id = NULL

created_by = NULL

uploaded_by = NULL

---

# ON DELETE RESTRICT

Prevent deleting parent if child records exist.

roles

↓

user_roles

Cannot delete Role if assigned to users.

---

# NO ACTION

Database checks integrity before deletion.

If related data exists,
operation will fail.

---

# Cascade Flow

Company

↓

Departments

↓

Projects

↓

Tree Nodes

↓

Tasks

↓

Comments

↓

Files

↓

File Versions

---

# Best Practices

✔ Use CASCADE only where necessary.

✔ Use SET NULL for optional relationships.

✔ Use RESTRICT for critical master tables.

✔ Never allow orphan records.

✔ Always maintain Referential Integrity.

---

# Summary

ON DELETE CASCADE

ON UPDATE CASCADE

ON DELETE SET NULL

ON DELETE RESTRICT

NO ACTION

Database Integrity Maintained