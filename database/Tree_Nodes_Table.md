# Tree Nodes Table

## Purpose

Stores the hierarchical tree structure of projects, modules, tasks, and subtasks in TreeFlow AI.

---

## Table Name

tree_nodes

---

## Columns

| Field | Data Type | Key | Description |
|---------|-----------|-----|-------------|
| id | UUID | PK | Unique Node ID |
| project_id | UUID | FK | Project ID |
| parent_id | UUID | FK | Parent Node ID (NULL for root node) |
| type | VARCHAR(50) | - | Project / Module / Task / Subtask |
| title | VARCHAR(255) | - | Node Title |
| description | TEXT | - | Node Description |
| order_index | INTEGER | - | Display Order |
| level | INTEGER | - | Tree Level |
| status | VARCHAR(20) | - | Active / Completed / Archived |
| created_by | UUID | FK | User who created the node |
| created_at | TIMESTAMP | - | Record Creation Time |
| updated_at | TIMESTAMP | - | Last Updated Time |
| is_deleted | BOOLEAN | - | Soft Delete Flag |

---

## Relationships

- One Project can have many Tree Nodes.
- One Tree Node can have many Child Nodes.
- One Tree Node belongs to one Parent Node.
- One User can create many Tree Nodes.

---

## Constraints

- id is Primary Key.
- project_id is Foreign Key.
- parent_id references tree_nodes.id.
- created_by references users.id.
- level must be 0 or greater.
- is_deleted defaults to False.