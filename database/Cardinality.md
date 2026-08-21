# TreeFlow AI - Cardinality

companies (1) ------ (N) departments

companies (1) ------ (N) users

departments (1) ------ (N) projects

projects (1) ------ (N) tree_nodes

tree_nodes (1) ------ (N) tasks

tasks (1) ------ (N) comments

tasks (1) ------ (N) files

tasks (1) ------ (N) task_assignments

users (1) ------ (N) task_assignments

users (N) ------ (N) roles
(via user_roles)

tree_nodes (1) ------ (N) tree_nodes

files (1) ------ (N) file_versions