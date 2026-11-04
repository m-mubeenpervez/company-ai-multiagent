# CompanyAI agents

There are 18 registered domain/auth agents under one semantic supervisor:

| Agent | Responsibility | MCP tool domain |
|---|---|---|
| auth_agent | Trusted sign-in guidance, logout, current identity | auth |
| hr_agent | Employee lifecycle and trusted credential-form guidance | hr |
| employee_agent | Profiles and permitted name lookup | employee |
| intern_agent | Intern profiles and monthly report records | intern |
| attendance_agent | Date-range records and attendance summary | attendance |
| leave_agent | Balances, requests and authorized decisions | leave |
| policy_agent | Handbook-grounded policy answers | policy |
| recruitment_agent | Candidates and interview records | recruitment |
| performance_agent | Performance review records | performance |
| training_agent | Training assignments | training |
| project_agent | Memberships and assigned tasks | project |
| payroll_agent | Authorized payslip lookup | payroll |
| finance_agent | Claims, submission and Finance review | finance |
| it_agent | Assigned/available assets | it |
| document_agent | Visible document metadata | document |
| analytics_agent | Authorized company aggregate summaries | analytics |
| notification_agent | Own notifications and permitted sending | notification |
| audit_agent | Authorized audit-log reads | audit |

The actual allowlists live in `company_system/mcp/client.py:DOMAIN_TOOLS`.
Business permissions live in the tools and server, not in the model's route.
Seventeen business specialists plus Authentication make the total of 18; there
are not 18 business specialists plus a nineteenth auth agent.

The supervisor retains the strict route schema, confidence threshold, bounded
second pass and configured Gemini fallback. Specialists cannot transfer directly
to peers. They receive non-secret session identity; the bearer token is omitted
from ADK state, instructions, history and model tool arguments. Login is a trusted
host operation; models cannot call credential tools. Missing required inputs should lead to clarification, not fabricated IDs,
months, dates or records.

Run live coverage with the evaluation interpreter:

```powershell
.\.venv-eval\Scripts\python.exe evaluations\run_deepeval_eval.py --full
.\.venv-eval\Scripts\python.exe evaluations\run_routing_eval.py --full
```

Imports and tool registration checks alone are not execution evidence. Consult
`FINAL_RELEASE_REPORT.md` and the machine-readable reports for actual executed
routes, tool calls, denials, judge failures and any incomplete coverage.

## 2026-11-04 credential boundary update

The supported entry point is now the authenticated loopback interface in
`company_system/local_web.py`, launched by `start_project.ps1`. It uses the existing
ADK Runner/supervisor and all 18 agents. Login and HR credential administration
run in trusted host code before conversation creation, with a separate HTTP form.
Bearer tokens live only in host memory/context, not ADK session state or model
arguments. The model-facing tool wrapper injects tokens only at the MCP transport
boundary and removes secret response fields. Login/create/update/delete credential
tools are withheld from models; all 39 MCP wire schemas remain available unchanged
to trusted clients. Stock ADK development/debug/session APIs are not mounted.
See `docs/SECURITY.md` (or `SECURITY.md` from this directory) for boundaries and limits.
