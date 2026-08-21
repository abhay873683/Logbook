# TreeFlow AI - Role Based Access Control (RBAC)

## Purpose

Role Based Access Control (RBAC) is used to manage user permissions based on their assigned role. Every authenticated user can access only the resources allowed for their role.

---

# Roles

## 1. Super Admin

Description:

- Full system access
- Manage all companies
- Manage all departments
- Manage all users
- Manage all projects
- Manage all tasks
- Manage reports
- Manage system settings

Permissions:

- Create
- Read
- Update
- Delete
- Export
- Import
- Manage Roles

---

## 2. Company Admin

Description:

Manages a single company.

Permissions:

- Manage company profile
- Manage departments
- Manage employees
- Manage projects
- Manage tasks
- View reports
- Invite users

Restrictions:

- Cannot access other companies.

---

## 3. Department Manager

Description:

Manages one department.

Permissions:

- Create projects
- Assign tasks
- Manage employees
- View reports
- Update department information

Restrictions:

- Cannot delete company.
- Cannot manage other departments.

---

## 4. Tree Manager

Description:

Responsible for Tree Structure.

Permissions:

- Create Tree
- Update Tree
- Delete Tree
- Manage Tree Nodes

Restrictions:

- Cannot manage users.

---

## 5. Team Member

Description:

Works on assigned tasks.

Permissions:

- View assigned tasks
- Update task progress
- Upload files
- Add comments
- View notifications

Restrictions:

- Cannot create projects.
- Cannot delete tasks.

---

## 6. Viewer

Description:

Read-only access.

Permissions:

- View Projects
- View Reports
- View Trees
- View Tasks

Restrictions:

- No Create
- No Update
- No Delete

---

# Permission Matrix

| Module | Super Admin | Company Admin | Department Manager | Tree Manager | Team Member | Viewer |
|---------|-------------|---------------|--------------------|--------------|-------------|--------|
| Companies | CRUD | CRUD | Read | No | No | Read |
| Departments | CRUD | CRUD | CRUD | Read | Read | Read |
| Users | CRUD | CRUD | Read | No | No | No |
| Roles | CRUD | Read | No | No | No | No |
| Projects | CRUD | CRUD | CRUD | Read | Read | Read |
| Trees | CRUD | Read | Read | CRUD | Read | Read |
| Tasks | CRUD | CRUD | CRUD | Read | Update Assigned | Read |
| Files | CRUD | CRUD | CRUD | CRUD | Upload/View | Read |
| Comments | CRUD | CRUD | CRUD | CRUD | CRUD | Read |
| Reports | CRUD | Read | Read | Read | Read | Read |
| Notifications | CRUD | CRUD | CRUD | Read | Read | Read |

---

# JWT Authentication

Every protected API requires:

Authorization

Bearer <JWT_TOKEN>

---

# Authorization Rules

- Every request must contain a valid JWT token.
- Expired tokens are rejected.
- Disabled users cannot access APIs.
- Deleted users cannot login.
- Users can access only their company data.
- Department Managers can access only their department.
- Team Members can update only assigned tasks.
- Viewers have read-only access.

---

# Role Hierarchy

Super Admin

↓

Company Admin

↓

Department Manager

↓

Tree Manager

↓

Team Member

↓

Viewer

---

# Security Rules

- Password stored using BCrypt hashing.
- JWT Authentication.
- Role validation on every request.
- Company level isolation.
- Department level restrictions.
- API permission validation.
- Secure HTTPS communication.

---

# Future Enhancements

- Dynamic Permission System
- Permission Groups
- Custom Roles
- API Level Permission Control
- Feature Flags
- Audit Permission Logs

---

# Status

✅ RBAC Designed

✅ Roles Defined

✅ Permission Matrix Completed

✅ Authorization Rules Completed

✅ Ready for FastAPI Implementation (Day 12)