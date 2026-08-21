# TreeFlow AI - Database Overview

## Database Name

treeflow_ai

---

## Database Type

PostgreSQL

---

## ORM

SQLAlchemy

---

## Migration Tool

Alembic

---

## Database Design

Third Normal Form (3NF)

---

## Character Set

UTF-8

---

## Time Zone

UTC

---

## Primary Key Strategy

UUID for all tables

---

## Total Core Tables

17

- companies
- departments
- users
- roles
- user_roles
- projects
- tree_nodes
- tasks
- task_assignments
- task_dependencies
- task_attachments
- comments
- files
- file_versions
- notifications
- activity_logs
- ai_history
- reports

---

## Architecture

- Modular
- Scalable
- Secure
- Multi Tenant
- High Performance

---

## Audit Fields

Every table contains:

- created_at
- updated_at
- created_by
- updated_by

---

## Soft Delete

Instead of deleting records permanently:

- is_deleted BOOLEAN
- deleted_at TIMESTAMP

---

## Security Features

- UUID Primary Keys
- JWT Authentication
- BCrypt Password Hashing
- Role Based Access Control (RBAC)
- HTTPS Communication
- Foreign Key Integrity

---

## Performance Features

- Foreign Key Indexes
- Composite Indexes
- Unique Indexes
- JSONB Support
- Optimized Queries

---

## Database Goals

- High Performance
- High Availability
- Easy Maintenance
- Horizontal Scalability
- Secure Data Storage
- Fast Query Execution

---

## Backup Strategy

- Daily Backup
- Weekly Full Backup
- Point-in-Time Recovery

---

## Future Enhancements

- Database Replication
- Read Replicas
- Table Partitioning
- Redis Cache
- Full Text Search
- Vector Search (pgvector)

---

## Status

✅ Database Overview Completed

✅ ER Diagram Completed

✅ Database Schema Completed

✅ Constraints Completed

✅ Index Strategy Completed

✅ Ready for SQLAlchemy Models (Day 11)