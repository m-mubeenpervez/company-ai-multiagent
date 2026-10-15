# CompanyAI Demo Credentials

> These are local demo accounts only. Do not reuse these passwords in a real system.

| Level / role | Name | Username | Password | Employee ID | Typical access |
|---|---|---|---|---:|---|
| HR | Saqib Khan | `hr.admin` | `HrAdmin#2026` | 1 | Employee lifecycle + **credential create/update/delete** |
| Manager | Asim Raza | `manager.asim` | `Manager#2026` | 2 | Direct reports, attendance, leave approval, projects |
| Permanent Employee | Ali Hassan | `employee.ali` | `Employee#2026` | 3 | Own profile/leave/payroll/tasks/expenses |
| Permanent Employee | Sara Ahmed | `employee.sara` | `Employee#2026` | 4 | Own profile/leave/payroll/tasks/expenses |
| Intern | Mubeen Pervez | `intern.mubeen` | `Intern#2026` | 5 | Own intern profile/reports/training/leave/tasks |
| Intern | Ahmad Javaid | `intern.ahmad` | `Intern#2026` | 6 | Own intern profile/reports/training/leave/tasks |
| Recruiter | Noor Fatima | `recruiter.noor` | `Recruit#2026` | 7 | Candidate/interview pipeline |
| Finance | Hina Malik | `finance.hina` | `Finance#2026` | 8 | Payroll/expense finance access |
| IT | Usman Tariq | `it.usman` | `ItSupport#2026` | 9 | IT asset operations |
| System/Audit Admin | Adeel Shah | `admin.auditor` | `Audit#2026` | 10 | Audit + permitted operational views |

## Credential administration rule

This project intentionally implements the user's requested rule:

**Only the `hr` role can create, update, or delete CompanyAI login credentials.**

The restriction exists in two places:

1. The HR Agent is the only specialist that receives credential-management tools.
2. The credential tools themselves call `require_roles(..., {"hr"})`.

So even if another agent/model attempts to invoke credential logic indirectly, the tool rejects it.

The `admin` role does **not** receive credential CRUD permission in this demo because the project requirement explicitly reserves that capability for HR.

## Login examples in ADK Web

- `Log in with username hr.admin and password HrAdmin#2026`
- `Log in with username intern.mubeen and password Intern#2026`
- `Who am I?`

After login, the identity and role are stored in ADK session state for that conversation.
