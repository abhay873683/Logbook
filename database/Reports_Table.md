# Reports Table

## Purpose

Stores generated reports for projects, teams, employees, and AI analytics.

---

## Table Name

reports

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Report ID |
| company_id | UUID | FK | Company ID |
| generated_by | UUID | FK | User who generated the report |
| report_name | VARCHAR(255) | - | Report Name |
| report_type | VARCHAR(100) | - | Project / Team / Employee / AI |
| file_path | TEXT | - | Report File Location |
| generated_at | TIMESTAMP | - | Report Generation Time |
| status | VARCHAR(20) | - | Processing / Completed / Failed |
| created_at | TIMESTAMP | - | Record Creation Time |

---

## Relationships

- One Company can have multiple Reports.
- One User can generate multiple Reports.

---

## Constraints

- id is Primary Key.
- company_id is Foreign Key.
- generated_by is Foreign Key.
- status defaults to Processing.