# Files Table

## Purpose

Stores all files and attachments uploaded to projects and tasks.

---

## Table Name

files

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique File ID |
| task_id | UUID | FK | Related Task ID |
| uploaded_by | UUID | FK | User who uploaded the file |
| file_name | VARCHAR(255) | - | Original File Name |
| file_path | TEXT | - | File Storage Path |
| file_type | VARCHAR(100) | - | File Type (PDF, JPG, PNG, DOCX, etc.) |
| file_size | BIGINT | - | File Size in Bytes |
| version | INTEGER | - | File Version Number |
| uploaded_at | TIMESTAMP | - | Upload Date & Time |
| updated_at | TIMESTAMP | - | Last Updated Time |
| is_deleted | BOOLEAN | - | Soft Delete Flag |

---

## Relationships

- One Task can have multiple Files.
- One User can upload multiple Files.

---

## Constraints

- id is Primary Key.
- task_id is Foreign Key.
- uploaded_by is Foreign Key.
- version starts from 1.
- is_deleted defaults to False.