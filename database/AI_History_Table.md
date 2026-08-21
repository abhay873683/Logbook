# AI History Table

## Purpose

Stores all AI interactions, prompts, responses, and usage history for analysis and auditing.

---

## Table Name

ai_history

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique AI History ID |
| user_id | UUID | FK | User who interacted with AI |
| prompt | TEXT | - | User Input |
| response | TEXT | - | AI Response |
| model | VARCHAR(100) | - | AI Model Name |
| tokens_used | INTEGER | - | Total Tokens Consumed |
| response_time | FLOAT | - | Response Time (Seconds) |
| created_at | TIMESTAMP | - | Interaction Time |

---

## Relationships

- One User can have multiple AI History records.

---

## Constraints

- id is Primary Key.
- user_id is Foreign Key.
- created_at is automatically generated.