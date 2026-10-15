# Role Permission Matrix

| Capability | HR | Manager | Employee | Intern | Recruiter | Finance | IT | Admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Login / own identity | Y | Y | Y | Y | Y | Y | Y | Y |
| Create/update/delete login credentials | **Y** | N | N | N | N | N | N | N |
| Create employee record | **Y** | N | N | N | N | N | N | N |
| View all employee directory | Y | Team | Own | Own | Own | Own | Own | Y |
| View intern reports | Y | Team | N | Own | N | N | N | Y |
| View attendance | Y | Team | Own | Own | Own | Own | Own | Y |
| Request own leave | Y | Y | Y | Y | Y | Y | Y | Y |
| Approve leave | Y | Team | N | N | N | N | N | N |
| Search company policy RAG | Y | Y | Y | Y | Y | Y | Y | Y |
| Recruitment pipeline | Y | N | N | N | Y | N | N | N |
| Performance reviews | Y | Team | Own | Own | Own | Own | Own | Y |
| Training assignments | Y | Team | Own | Own | Own | Own | Own | Y |
| Project/task records | Y | Team | Own | Own | Own | Own | Own | Y |
| Payroll | Any | Own | Own | Own | Own | Any | Own | Own |
| Expense claims | Any | Own | Own | Own | Own | Any/review | Own | Own |
| IT asset assignment views | Y | Team | Own | Own | Own | Own | Any | Y |
| Audit logs | Y | N | N | N | N | N | N | Y |

"Team" means a manager can access direct-report records when the tool authorizes it.

This matrix is a learning/demo policy. Production systems should use a dedicated identity provider and a formal RBAC/ABAC authorization layer.
