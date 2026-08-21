# TreeFlow AI - Database Migration Plan

## Overview

TreeFlow AI uses Alembic with SQLAlchemy to manage database schema changes.

Database: PostgreSQL

ORM: SQLAlchemy

Migration Tool: Alembic

---

# Migration Workflow

## Step 1

Install Required Packages

- SQLAlchemy
- Alembic
- psycopg2-binary

Status: Planned

---

## Step 2

Initialize Alembic

Command

alembic init migrations

Status: Planned

---

## Step 3

Configure Alembic

Update alembic.ini

Set PostgreSQL Database URL

Status: Planned

---

## Step 4

Create SQLAlchemy Models

Create all database models:

- Company
- Department
- User
- Role
- UserRole
- Project
- TreeNode
- Task
- TaskAssignment
- TaskDependency
- TaskAttachment
- Comment
- File
- FileVersion
- Notification
- ActivityLog
- AIHistory
- Report

Status: Planned

---

## Step 5

Generate Initial Migration

Command

alembic revision --autogenerate -m "Initial database schema"

Status: Planned

---

## Step 6

Review Migration File

Verify:

- Tables
- Columns
- Constraints
- Foreign Keys
- Indexes

Status: Planned

---

## Step 7

Apply Migration

Command

alembic upgrade head

Status: Planned

---

## Step 8

Verify Database

Check that all tables are created successfully in PostgreSQL.

Status: Planned

---

## Step 9

Seed Initial Data

Insert default records.

Default Company

Demo Company

Default Roles

- Admin
- Manager
- Team Lead
- Employee
- Client

Default Department

Development

Status: Planned

---

## Step 10

Rollback Migration

Command

alembic downgrade -1

Purpose

Rollback the last migration if required.

Status: Planned

---

# Migration Best Practices

- Always review generated migration files.
- Keep one migration for one feature.
- Never edit old production migrations.
- Test migrations before deployment.
- Backup database before production migration.
- Maintain migration history in Git.

---

# Deployment Workflow

Development

↓

Generate Migration

↓

Review

↓

Upgrade Database

↓

Testing

↓

Production Deployment

---

# Current Status

Migration Planning Completed

Implementation Starts in Backend Development Phase.