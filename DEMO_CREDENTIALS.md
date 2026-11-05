# CompanyAI Demo Credentials

> These are local demo accounts only. Do not reuse these passwords in a real system.

| Level / role | Name | Username | Password | Employee ID | Typical access |
|---|---|---|---|---:|---|
| HR | Rowan Cedar | `demo.hr` | `DemoHr#2026` | 1 | Employee lifecycle + **credential create/update/delete** |
| Manager | Arden Vale | `demo.manager` | `DemoManager#2026` | 2 | Direct reports, attendance, leave approval, projects |
| Permanent Employee | Jules Ember | `demo.employee` | `DemoEmployee#2026` | 3 | Own profile, leave, payroll, tasks, expenses |
| Permanent Employee | Casey Harbor | `demo.employee2` | `DemoEmployee#2026` | 4 | Own profile, leave, payroll, tasks, expenses |
| Intern | Riley Quartz | `demo.intern` | `DemoIntern#2026` | 5 | Own intern profile, reports, training, leave, tasks |
| Intern | Morgan Pine | `demo.intern2` | `DemoIntern#2026` | 6 | Own intern profile, reports, training, leave, tasks |
| Recruiter | Taylor Nimbus | `demo.recruiter` | `DemoRecruit#2026` | 7 | Candidate and interview pipeline |
| Finance | Jordan Maple | `demo.finance` | `DemoFinance#2026` | 8 | Payroll and expense-finance access |
| IT | Quinn Solace | `demo.it` | `DemoSupport#2026` | 9 | IT asset operations |
| System / Audit Admin | Avery Lantern | `demo.admin` | `DemoAudit#2026` | 10 | Audit logs + permitted operational views |

## Credential Administration Rule

This project intentionally implements the requested rule:

**Only the `hr` role can create, update, or delete CompanyAI login credentials.**

The restriction exists in two places:

1. The HR Agent is the only specialist that receives credential-management tools.
2. The credential tools themselves call `require_roles(..., {"hr"})`.

So even if another agent or model attempts to invoke credential logic indirectly, the tool rejects it.

The `admin` role does **not** receive credential CRUD permission in this demo because the project requirement explicitly reserves that capability for HR.

## Login Examples in ADK Web

- `Log in with username demo.hr and password DemoHr#2026`
- `Log in with username demo.intern and password DemoIntern#2026`
- `Who am I?`

After login, identity and role values are stored in ADK session state for that conversation.

## Demo Security Note

- These accounts are for local educational/demo use only.
- Passwords in the SQLite database are stored as salted hashes rather than plain text.
- Real production credentials should never be committed to a repository.
- Production deployments should use a dedicated identity provider and proper secret management.
