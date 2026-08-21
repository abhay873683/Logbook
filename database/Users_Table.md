# Users Table

## Purpose

Stores all user accounts for the TreeFlow AI platform.

---

## Table Name

users

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique User ID |
| company_id | UUID | FK | Company ID |
| name | VARCHAR(255) | - | Full Name |
| email | VARCHAR(255) | UNIQUE | User Email |
| password_hash | TEXT | - | Encrypted Password |
| phone | VARCHAR(20) | - | Phone Number |
| avatar | TEXT | - | Profile Image URL |
| status | VARCHAR(20) | - | Active / Inactive |
| last_login_at | TIMESTAMP | - | Last Login Time |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |
| is_deleted | BOOLEAN | - | Soft Delete Flag |

---

## Relationships

- One User belongs to one Company.
- One User can have multiple Roles.
- One User can create Projects.
- One User can create Tasks.
- One User can write Comments.
- One User can upload Files.

---

## Constraints

- id is Primary Key.
- company_id is Foreign Key.
- email must be unique.
- Password must be stored in hashed format.
- status defaults to Active.
- is_deleted defaults to False.