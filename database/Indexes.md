# TreeFlow AI - Database Index Strategy

## Purpose

Indexes improve database performance by reducing query execution time.

They are used for:

- Fast Login
- Fast Search
- Fast Filtering
- Fast Sorting
- Reporting
- Analytics
- Dashboard Loading

---

# Primary Key Indexes

Every table uses UUID Primary Key.

- companies.id
- departments.id
- users.id
- roles.id
- user_roles.id
- projects.id
- tree_nodes.id
- tasks.id
- task_assignments.id
- task_dependencies.id
- task_attachments.id
- comments.id
- files.id
- file_versions.id
- notifications.id
- activity_logs.id
- ai_history.id
- reports.id

---

# UNIQUE Indexes

## Users

UNIQUE(users.email)

Purpose

- Fast Login
- Prevent Duplicate Emails

---

## Companies

UNIQUE(companies.email)

UNIQUE(companies.domain)

Purpose

- Prevent Duplicate Companies

---

## Roles

UNIQUE(roles.name)

Purpose

- Prevent Duplicate Roles

---

# Foreign Key Indexes

## Departments

INDEX(company_id)

---

## Users

INDEX(company_id)

---

## User Roles

INDEX(user_id)

INDEX(role_id)

---

## Projects

INDEX(department_id)

INDEX(created_by)

---

## Tree Nodes

INDEX(project_id)

INDEX(parent_id)

INDEX(type)

---

## Tasks

INDEX(project_id)

INDEX(node_id)

INDEX(created_by)

INDEX(status)

INDEX(priority)

INDEX(due_date)

---

## Task Assignments

INDEX(task_id)

INDEX(user_id)

INDEX(status)

---

## Task Dependencies

INDEX(task_id)

INDEX(depends_on_task_id)

---

## Task Attachments

INDEX(task_id)

INDEX(uploaded_by)

---

## Comments

INDEX(task_id)

INDEX(user_id)

---

## Files

INDEX(task_id)

INDEX(uploaded_by)

---

## File Versions

INDEX(file_id)

INDEX(created_by)

---

## Notifications

INDEX(user_id)

INDEX(is_read)

INDEX(created_at)

---

## Activity Logs

INDEX(user_id)

INDEX(module)

INDEX(created_at)

---

## AI History

INDEX(user_id)

INDEX(created_at)

---

## Reports

INDEX(user_id)

INDEX(type)

---

# Composite Indexes

## Users

(company_id, email)

Purpose

Fast Company User Search

---

## Projects

(department_id, status)

Purpose

Department Wise Project List

---

## Tree Nodes

(project_id, parent_id)

Purpose

Fast Tree Traversal

---

## Tasks

(project_id, status)

(node_id, status)

(priority, due_date)

Purpose

Fast Task Filtering

---

## Task Assignments

(user_id, status)

Purpose

Assigned Active Tasks

---

## Notifications

(user_id, is_read)

Purpose

Unread Notifications

---

## Activity Logs

(user_id, created_at)

Purpose

Latest Activity Timeline

---

# Search Indexes

Users

- email
- name

Companies

- name
- domain

Departments

- name

Projects

- name

Tasks

- title
- description

Reports

- name

---

# JSONB Indexes

Activity Logs

GIN(old_values)

GIN(new_values)

Reports

GIN(filters)

GIN(data)

Purpose

Fast JSON Search

---

# Performance Strategy

- Index every Foreign Key.
- Use Composite Indexes for reporting.
- Use UNIQUE indexes where required.
- Avoid unnecessary indexes.
- Review indexes regularly.
- Optimize slow queries.

---

# Future Indexes

- Full Text Search
- Trigram Search
- pgvector Index
- Redis Cache
- Materialized Views

---

# Index Review

✔ Primary Key Indexes Verified

✔ Unique Indexes Verified

✔ Foreign Key Indexes Verified

✔ Composite Indexes Verified

✔ Search Indexes Verified

✔ JSONB Indexes Planned

✔ Performance Strategy Reviewed

✔ Ready For Migration