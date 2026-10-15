# Role Permission Matrix

| Capability | HR | Manager | Employee | Intern | Recruiter | Finance | IT | Admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Login / own identity | Y | Y | Y | Y | Y | Y | Y | Y |
| Create / update / delete login credentials | **Y** | N | N | N | N | N | N | N |
| Create employee record | **Y** | N | N | N | N | N | N | N |
| View employee records | All | Team | Own | Own | Own | Own | Own | All |
| View intern reports | All | Team | N | Own | N | N | N | All |
| View attendance | All | Team | Own | Own | Own | Own | Own | All |
| Request own leave | Y | Y | Y | Y | Y | Y | Y | Y |
| Approve leave | Y | Team | N | N | N | N | N | N |
| Search company policy RAG | Y | Y | Y | Y | Y | Y | Y | Y |
| Recruitment pipeline | Y | N | N | N | Y | N | N | N |
| Performance reviews | All | Team | Own | Own | Own | Own | Own | All |
| Training assignments | All | Team | Own | Own | Own | Own | Own | All |
| Project / task records | All | Team | Own | Own | Own | Own | Own | All |
| Payroll | All | Own | Own | Own | Own | All | Own | Own |
| Expense claims | All / View | Own | Own | Own | Own | All + Review | Own | Own |
| View assigned assets | All | Team | Own | Own | Own | Own | All | All |
| View available assets | N | N | N | N | N | N | Y | N |
| Audit logs | Y | N | N | N | N | N | N | Y |

## Notes

- **All** means the role may access the permitted records across the company where the corresponding tool allows it.
- **Team** means a manager can access direct-report records when the tool authorizes it.
- **Own** means the user can access only their own permitted records.
- HR-only credential CRUD is enforced inside Python tools with `require_roles(..., {"hr"})`.
- Available-asset listing is restricted to IT.
- Audit-log access is restricted to HR and Admin.
- The LLM is not treated as the security boundary; authorization is enforced in Python tools.

This matrix is a learning/demo policy. Production systems should use a dedicated identity provider and a formal RBAC/ABAC authorization layer.