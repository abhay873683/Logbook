# TreeFlow AI - ER Diagram

Entities

1. Companies
2. Departments
3. Users
4. Roles
5. User Roles
6. Projects
7. Tree Nodes
8. Tasks
9. Task Assignments
10. Comments
11. Files
12. Notifications
13. Activity Logs
14. AI History
15. Reports

Primary Relationships

Company -> Department
Company -> User
Department -> Project
Project -> Tree Node
Tree Node -> Task
Task -> Comments
Task -> Files
Task -> Task Assignments
User -> Notifications
User -> Activity Logs
User -> Reports
User -> AI History