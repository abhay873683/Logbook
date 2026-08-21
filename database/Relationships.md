# TreeFlow AI - Database Relationships

## Overview

This document defines all relationships between the database tables used in the TreeFlow AI project.

---

# Company & Organization

Company (1) ------ (N) Departments

Company (1) ------ (N) Users

Department (1) ------ (N) Projects

---

# Project Management

Project (1) ------ (N) Tree Nodes

Tree Node (1) ------ (N) Child Tree Nodes (Self Reference)

Tree Node (1) ------ (N) Tasks

Task (1) ------ (N) Task Assignments

Task (1) ------ (N) Task Dependencies

Task (1) ------ (N) Task Attachments

Task (1) ------ (N) Comments

Task (1) ------ (N) Files

---

# User Management

User (1) ------ (N) Projects (created_by)

User (1) ------ (N) Task Assignments

User (1) ------ (N) Comments

User (1) ------ (N) Notifications

User (1) ------ (N) Activity Logs

User (1) ------ (N) AI History

User (1) ------ (N) Reports

User (1) ------ (N) Files (uploaded_by)

---

# Role Management

Role (1) ------ (N) User Roles

User (1) ------ (N) User Roles

Users (N) ------ (N) Roles (via user_roles)

---

# File Management

File (1) ------ (N) File Versions

Task (1) ------ (N) Task Attachments

User (1) ------ (N) Files

---

# AI Module

User (1) ------ (N) AI History

---

# Reports Module

User (1) ------ (N) Reports

---

# Relationship Types

## One-to-One

- User Avatar ↔ File (Optional)

---

## One-to-Many

- Company → Departments
- Company → Users
- Department → Projects
- Project → Tree Nodes
- Tree Node → Tasks
- Task → Comments
- Task → Files
- Task → Task Assignments
- Task → Task Dependencies
- Task → Task Attachments
- User → Notifications
- User → Activity Logs
- User → AI History
- User → Reports
- File → File Versions

---

## Many-to-Many

- Users ↔ Roles (user_roles)
- Users ↔ Tasks (task_assignments)

---

## Self Reference

- Tree Nodes → Parent Tree Nodes

---

# Referential Integrity Rules

- Every Foreign Key must reference an existing Primary Key.
- No orphan records are allowed.
- ON DELETE rules must be followed.
- ON UPDATE rules must be followed.
- Self-referencing nodes must maintain hierarchy integrity.

---

# Cardinality Summary

| Relationship | Cardinality |
|--------------|-------------|
| Company → Departments | 1 : N |
| Company → Users | 1 : N |
| Department → Projects | 1 : N |
| Project → Tree Nodes | 1 : N |
| Tree Node → Tasks | 1 : N |
| Task → Comments | 1 : N |
| Task → Files | 1 : N |
| Task → Assignments | 1 : N |
| Task → Dependencies | 1 : N |
| User → Notifications | 1 : N |
| User → Activity Logs | 1 : N |
| User → Reports | 1 : N |
| Users ↔ Roles | N : N |
| Users ↔ Tasks | N : N |
| Tree Nodes → Tree Nodes | 1 : N |

---

# Relationship Validation

✅ All One-to-One relationships verified

✅ All One-to-Many relationships verified

✅ All Many-to-Many relationships verified

✅ Self Reference verified

✅ Foreign Keys verified

✅ Referential Integrity verified

✅ Cardinality verified

✅ No orphan relationships found

---

# Final Status

✅ All Relationships Reviewed

✅ Relationship Design Completed

✅ Referential Integrity Completed

✅ Ready For SQLAlchemy Models

✅ Ready For Alembic Migration

✅ Day 10 Completed