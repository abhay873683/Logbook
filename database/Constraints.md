# TreeFlow AI - Database Constraints

## Primary Key Constraints

- All tables use UUID as Primary Key.
- Primary Keys are UNIQUE.
- Primary Keys are NOT NULL.

---

## Foreign Key Constraints

- departments.company_id → companies.id
- users.company_id → companies.id
- user_roles.user_id → users.id
- user_roles.role_id → roles.id
- projects.department_id → departments.id
- projects.created_by → users.id
- tree_nodes.project_id → projects.id
- tree_nodes.parent_id → tree_nodes.id
- tasks.node_id → tree_nodes.id
- tasks.project_id → projects.id
- tasks.created_by → users.id
- task_assignments.task_id → tasks.id
- task_assignments.user_id → users.id
- task_dependencies.task_id → tasks.id
- task_dependencies.depends_on_task_id → tasks.id
- task_attachments.task_id → tasks.id
- task_attachments.uploaded_by → users.id
- comments.task_id → tasks.id
- comments.user_id → users.id
- files.task_id → tasks.id
- files.uploaded_by → users.id
- file_versions.file_id → files.id
- file_versions.created_by → users.id
- notifications.user_id → users.id
- activity_logs.user_id → users.id
- ai_history.user_id → users.id
- reports.user_id → users.id

---

## UNIQUE Constraints

- users.email
- companies.email
- companies.domain
- roles.name

---

## NOT NULL Constraints

Required Fields

- company_id
- department_id
- project_id
- node_id
- user_id
- task_id
- role_id
- name
- email
- password_hash
- created_at

---

## CHECK Constraints

### Status

- active
- inactive
- archived

### Task Status

- todo
- in_progress
- review
- testing
- completed
- cancelled

### Priority

- low
- medium
- high
- urgent

### Plan Type

- free
- pro
- enterprise

### Node Type

- root
- module
- task
- subtask

---

## DEFAULT Values

created_at = CURRENT_TIMESTAMP

updated_at = CURRENT_TIMESTAMP

status = 'active'

priority = 'medium'

is_deleted = FALSE

---

## ON DELETE Rules

Company → Departments : CASCADE

Department → Users : CASCADE

Department → Projects : CASCADE

Project → Tree Nodes : CASCADE

Project → Tasks : CASCADE

Tree Node → Tasks : CASCADE

Task → Task Assignments : CASCADE

Task → Task Dependencies : CASCADE

Task → Task Attachments : CASCADE

Task → Comments : CASCADE

Task → Files : CASCADE

Files → File Versions : CASCADE

Users → Notifications : CASCADE

Users → Activity Logs : CASCADE

Users → AI History : CASCADE

Users → Reports : CASCADE

---

## ON UPDATE Rules

All Foreign Keys use

ON UPDATE CASCADE

---

## Soft Delete

Instead of permanently deleting data

- is_deleted = TRUE
- deleted_at = CURRENT_TIMESTAMP

---

## Audit Fields

Every table contains

- created_at
- updated_at
- created_by
- updated_by

---

## Security Constraints

- Passwords stored using BCrypt hash.
- JWT Authentication supported.
- UUID used for all Primary Keys.
- Foreign Key Integrity enforced.
- Duplicate emails not allowed.
- Duplicate domains not allowed.
- Role Based Access Control (RBAC).

---

## Data Integrity Rules

- No orphan records allowed.
- Every Foreign Key must reference a valid record.
- Every table must have a Primary Key.
- Required fields cannot be NULL.
- Enum values validated using CHECK constraints.
- Soft Delete used where applicable.

---

## Constraint Review

✔ Primary Keys Verified

✔ Foreign Keys Verified

✔ Unique Constraints Verified

✔ NOT NULL Constraints Verified

✔ CHECK Constraints Verified

✔ Default Values Verified

✔ ON DELETE Rules Verified

✔ ON UPDATE Rules Verified

✔ Soft Delete Strategy Verified

✔ Security Constraints Verified

✔ Data Integrity Verified

✔ Ready For Migration