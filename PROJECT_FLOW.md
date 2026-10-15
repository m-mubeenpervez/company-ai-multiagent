# CompanyAI Multi-Agent System — Complete Project Flow

## 1. Core Architecture

```text
Company User
    |
    v
ADK Web
    |
    v
CompanyAI Supervisor
    |
    v
Deterministic Router
    |
    +--> Authentication Agent
    +--> HR Agent
    +--> Employee Records Agent
    +--> Intern Management Agent
    +--> Attendance Agent
    +--> Leave Agent
    +--> Policy RAG Agent
    +--> Recruitment Agent
    +--> Performance Agent
    +--> Training Agent
    +--> Project Agent
    +--> Payroll Agent
    +--> Finance Agent
    +--> IT Asset Agent
    +--> Document Agent
    +--> Analytics Agent
    +--> Notification Agent
    +--> Audit Agent
```

The root agent is:

```text
company_ai_supervisor
```

It has 18 registered sub-agents.

The supervisor is the central orchestration point, but top-level routing is not decided by the LLM. A deterministic Python router selects the correct specialist from the user's request.

This makes routing predictable, testable, and less dependent on local-model behavior.

---

## 2. Deterministic Routing Flow

```text
User Request
    |
    v
CompanyAI Supervisor
    |
    v
route_request()
    |
    v
DeterministicRouterAgent
    |
    v
Selected Specialist Agent
```

Examples:

```text
"Show my leave balance."
    -> leave_agent
```

```text
"Show my projects."
    -> project_agent
```

```text
"What is the internship report deadline?"
    -> policy_agent
```

```text
"Show company headcount summary."
    -> analytics_agent
```

Top-level routing is therefore separated from LLM generation.

---

## 3. Why Deterministic Routing Is Used

The earlier LLM-based supervisor could sometimes:

- Return an agent name instead of transferring correctly
- Select an incorrect specialist
- Increase prompt size
- Produce inconsistent routing with a local 7B model

The deterministic router solves this by using explicit Python rules.

Benefits:

- Predictable agent selection
- Easier regression testing
- Lower prompt overhead
- Reduced routing hallucination
- Better local-model reliability

---

## 4. Specialist Transfer Design

Specialist-to-specialist peer transfer is disabled.

Preferred architecture:

```text
User
    |
    v
Supervisor
    |
    v
Correct Specialist
```

For each new user request, the supervisor/router evaluates the request again and dispatches it to the appropriate specialist.

This avoids direct flows such as:

```text
Intern Agent -> Leave Agent
```

and keeps orchestration centralized.

---

## 5. Local LLM Flow

```text
Specialist Agent
    |
    v
Google ADK
    |
    v
LiteLLM
    |
    v
LM Studio OpenAI-Compatible API
    |
    v
qwen2.5-7b-instruct-1m
```

LM Studio API base:

```text
http://localhost:1234/v1
```

Main LLM:

```text
qwen2.5-7b-instruct-1m
```

The local LLM is used mainly for:

- Understanding requests inside the selected specialist
- Tool selection
- Function calling
- Formatting grounded tool results
- User-facing responses

Top-level specialist routing is handled by deterministic Python logic rather than the LLM.

---

## 6. Identity and Authentication Flow

```text
User enters username/password
        |
        v
Supervisor
        |
        v
Authentication Agent
        |
        v
login()
        |
        v
SQLite users table
        |
        v
PBKDF2 password verification
        |
        v
ADK session state
```

Successful login stores:

```text
auth_user_id
auth_username
auth_role
auth_employee_id
auth_full_name
```

These values are later read by protected tools.

---

## 7. Authorization Flow

The model knowing a user's role is not considered security.

Actual authorization is enforced in Python.

```text
User Request
    |
    v
Specialist Agent
    |
    v
Domain Tool
    |
    v
require_auth()
    |
    v
Role / Employee Permission Check
    |
    v
SQLite
```

Important helpers include:

```text
current_session_user()
require_auth()
require_roles()
can_view_employee()
is_manager_of()
```

If authorization fails, tools return statuses such as:

```text
auth_required
```

or:

```text
forbidden
```

The LLM cannot override these Python-level checks.

---

## 8. Logout and Session Flow

```text
Authenticated User
    |
    v
Authentication Agent
    |
    v
logout()
    |
    v
Authentication state cleared
```

After logout, protected operations require login again.

Validated behavior:

```text
Login
  -> success

View own employee profile
  -> success

Logout
  -> success

View employee profile again
  -> auth_required
```

---

## 9. HR-Only Credential Lifecycle

```text
HR User
    |
    v
Supervisor
    |
    v
HR Agent
    |
    +--> create_user_credentials()
    +--> update_user_credentials()
    +--> delete_user_credentials()
    |
    v
require_roles({"hr"})
    |
    v
users table
    |
    v
audit log
```

Unauthorized roles receive:

```text
forbidden
```

Credential security is enforced by the tool, not by prompt instructions alone.

---

## 10. Structured Company Data Flow

Structured records are stored in SQLite.

```text
Specialist Agent
    |
    v
Domain Tool
    |
    v
Authorization Check
    |
    v
SQLite Query
    |
    v
Grounded Structured Result
    |
    v
LLM Formats Response
```

Examples of structured data include:

- Users
- Employees
- Departments
- Intern profiles
- Internship reports
- Attendance
- Leave balances
- Leave requests
- Recruitment candidates
- Interviews
- Offers
- Performance reviews
- Training courses
- Training assignments
- Projects
- Project members
- Tasks
- Payroll
- Expense claims
- Assets
- Asset assignments
- Document metadata
- Notifications
- Audit logs

---

## 11. Example: Leave Balance Flow

User asks:

```text
Show my leave balance.
```

Flow:

```text
User
    |
    v
Supervisor
    |
    v
Deterministic Router
    |
    v
Leave Agent
    |
    v
get_leave_balance()
    |
    v
Authorization Check
    |
    v
SQLite leave_balances
    |
    v
Confirmed Result
    |
    v
Readable Answer
```

The LLM does not invent the leave balance.

---

## 12. Example: Payroll Flow

```text
User
    |
    v
Supervisor
    |
    v
Payroll Agent
    |
    v
get_payroll()
    |
    v
Authorization Check
    |
    v
SQLite payroll table
    |
    v
Net Pay Calculation in Tool
    |
    v
Grounded Response
```

Access rules are enforced inside the payroll tool.

Representative validated behavior:

```text
employee.ali -> payroll for employee 5
    -> forbidden

finance.hina -> payroll for employee 5
    -> success
```

---

## 13. RAG Source Document

Main policy source:

```text
company_system/documents/company_handbook.pdf
```

The system starts from a real PDF file rather than treating manually prepared chunks as the original source.

---

## 14. RAG Ingestion Flow

```text
company_handbook.pdf
    |
    v
PDF Text Extraction by Page
    |
    v
Text Cleaning
    |
    v
Chunking
    |
    v
LM Studio Embeddings API
    |
    v
text-embedding-nomic-embed-text-v1.5
    |
    v
768-Dimensional Vectors
    |
    v
Qdrant Local Storage
```

Current validated ingestion:

```text
PDF pages: 6
Chunks: 14
Embedding dimensions: 768
```

Qdrant payload contains information used to trace retrieved content back to its source, such as page/source information and text.

---

## 15. Policy RAG Query Flow

Example:

```text
What is the deadline for submitting a monthly internship report?
```

Flow:

```text
User
    |
    v
Supervisor
    |
    v
Deterministic Router
    |
    v
Policy Agent
    |
    v
search_company_policy()
    |
    v
Query Embedding
    |
    v
Nomic Embed Text v1.5
    |
    v
Qdrant Similarity Search
    |
    v
Top Relevant Policy Chunks
    |
    v
Policy Agent
    |
    v
Grounded Answer + Source
```

Validated response:

```text
Interns submit their monthly progress report by the last working day
of each month. If the final calendar date is a weekend or company
holiday, the deadline is the preceding working day.

Source: company_handbook.pdf, page 3
```

The Policy Agent should not invent official company-policy facts from general model knowledge.

---

## 16. Important RAG Embedding Rule

If the embedding model changes:

```text
Old Model
    -> Old Vector Space

New Model
    -> Different Vector Space
```

The existing collection should be rebuilt.

Run:

```powershell
python ingest_documents.py --reset
```

Current embedding model:

```text
text-embedding-nomic-embed-text-v1.5
```

---

## 17. Intern Same-Session Flow

A validated same-session test used:

```text
Login as intern.mubeen
    |
    v
Intern Profile
    |
    v
Training Assignments
    |
    v
Projects
    |
    v
Assigned Tasks
    |
    v
Notifications
    |
    v
Leave Balance
    |
    v
Internship Report Policy
```

Actual routing:

```text
Intern profile
    -> intern_agent

Training
    -> training_agent

Projects
    -> project_agent

Tasks
    -> project_agent

Notifications
    -> notification_agent

Leave
    -> leave_agent

Policy question
    -> policy_agent
```

This test confirmed that the authentication session remained active while different requests were routed to different specialists.

---

## 18. Recruitment Flow

```text
Recruiter / HR
    |
    v
Supervisor
    |
    v
Recruitment Agent
    |
    +--> list_candidates()
    |
    +--> get_interview_status()
    |
    v
Authorization Check
    |
    v
SQLite
```

Validated examples include:

- Listing candidates in interview stages
- Retrieving interview history

---

## 19. Performance Flow

```text
User
    |
    v
Performance Agent
    |
    v
get_performance_reviews()
    |
    v
can_view_employee()
    |
    v
SQLite performance_reviews
```

Users may access only records permitted by the authorization rules.

---

## 20. Training Flow

```text
User
    |
    v
Training Agent
    |
    v
get_training_assignments()
    |
    v
can_view_employee()
    |
    v
SQLite
```

Validated intern training records include compliance, Python/AI, and Generative AI assignments.

---

## 21. Project and Task Flow

```text
User
    |
    v
Project Agent
    |
    +--> get_employee_projects()
    |
    +--> get_employee_tasks()
    |
    v
Authorization Check
    |
    v
SQLite
```

The tool returns current structured project and task information.

---

## 22. Finance and Expense Flow

```text
User
    |
    v
Finance Agent
    |
    +--> get_expense_claims()
    +--> submit_expense()
    +--> review_expense()
    |
    v
Authorization Check
    |
    v
SQLite expense_claims
```

Only permitted roles can review claims.

Unauthorized review attempts return:

```text
forbidden
```

---

## 23. IT Asset Flow

```text
User
    |
    v
IT Agent
    |
    +--> get_assigned_assets()
    +--> list_available_assets()
    |
    v
Authorization Check
    |
    v
SQLite
```

Available-asset listing is restricted to IT.

---

## 24. Document Flow

```text
User
    |
    v
Document Agent
    |
    v
list_documents()
    |
    v
Authorization Check
    |
    v
SQLite document_records
```

Visibility rules are enforced in the tool.

---

## 25. Analytics Flow

```text
HR / Manager / Admin
    |
    v
Analytics Agent
    |
    +--> company_people_summary()
    |
    +--> company_operational_summary()
    |
    v
Authorization Check
    |
    v
SQLite Aggregation
```

Validated analytics include:

- Headcount by employment type
- Headcount by department
- Pending leave count
- Overdue tasks
- Missing intern reports

---

## 26. Notification Flow

```text
User
    |
    v
Notification Agent
    |
    +--> get_my_notifications()
    +--> send_notification()
    |
    v
Authorization Check
    |
    v
SQLite notifications
```

Users can view their own notifications.

Sending notifications is restricted to authorized roles.

---

## 27. Audit Flow

```text
HR / Admin
    |
    v
Audit Agent
    |
    v
get_recent_audit_logs()
    |
    v
Authorization Check
    |
    v
SQLite audit_logs
```

Unauthorized users receive:

```text
forbidden
```

Audit logs record selected security and administrative actions.

---

## 28. Company Facts and LLM Responsibility

The LLM may reformat confirmed data.

Example:

```text
2026-08-01
```

may become:

```text
August 1, 2026
```

Likewise:

```text
under_review
```

may be displayed as:

```text
Under Review
```

This is presentation, not invention.

The model must not add unsupported company facts.

For example, if a tool returns no currency, the response should not invent a currency symbol.

---

## 29. Data Security Design

- Passwords are stored as salted PBKDF2 hashes.
- Authentication information is stored in ADK session state.
- Sensitive tools call authorization helpers.
- HR-only credential CRUD is enforced in Python.
- Managers are limited to permitted direct-report access.
- Payroll and finance access is role-controlled.
- Audit logs are restricted.
- Policy vectors contain handbook content, not employee credentials.
- Private structured records remain in SQLite.
- The LLM is not treated as the security boundary.

---

## 30. Local / Free AI Stack

```text
Google ADK
    |
    v
LiteLLM
    |
    v
LM Studio
    |
    v
qwen2.5-7b-instruct-1m
```

Embeddings:

```text
Text
    |
    v
LM Studio /v1/embeddings
    |
    v
text-embedding-nomic-embed-text-v1.5
    |
    v
768-dimensional vector
```

Storage:

```text
Structured Data -> SQLite
Policy Vectors   -> Qdrant
```

No Gemini API key is required.

No OpenRouter API key is required.

Ollama is not required by the current project.

---

## 31. LM Studio Configuration

API base:

```text
http://localhost:1234/v1
```

Main LLM:

```text
qwen2.5-7b-instruct-1m
```

Embedding model:

```text
text-embedding-nomic-embed-text-v1.5
```

Practical context size:

```text
8192
```

A larger value such as:

```text
16384
```

may be used if genuinely required.

---

## 32. Environment Configuration

Example `.env`:

```text
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_LLM_MODEL=qwen2.5-7b-instruct-1m
LM_STUDIO_EMBED_MODEL=text-embedding-nomic-embed-text-v1.5
RAG_COLLECTION=company_policies
RAG_TOP_K=5
RAG_MIN_SCORE=0.45
```

---

## 33. Development Startup Flow

```text
PowerShell
    |
    v
start_project.ps1
    |
    +--> Move to project root
    +--> Activate .venv
    +--> Set PYTHONPATH
    +--> Check Python
    |
    v
Development Environment Ready
```

The current script prepares the environment.

Then run:

```powershell
adk web
```

LM Studio should already be running.

---

## 34. First-Time Setup Flow

The project includes:

```text
setup_windows.ps1
```

Use it for first-time setup according to the steps implemented in that script.

Typical setup responsibilities include:

- Environment configuration
- Virtual environment creation
- Dependency installation
- Local model verification
- Database initialization
- RAG ingestion
- Project verification

If an important command fails, resolve the error before treating setup as complete.

---

## 35. Normal Run Sequence

```text
1. Open LM Studio
2. Start the LM Studio API server
3. Open PowerShell
4. Go to D:\company_ai_multiagent
5. Run start_project.ps1
6. Run adk web
7. Open the CompanyAI application
8. Log in using a demo account
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
```

Then:

```powershell
adk web
```

---

## 36. Important Storage and Code Locations

SQLite database:

```text
company_system/database/company.db
```

Policy document:

```text
company_system/documents/company_handbook.pdf
```

Qdrant storage:

```text
company_system/qdrant_storage/
```

Root agent:

```text
company_system/agent.py
```

Deterministic routing rules:

```text
company_system/routing/router.py
```

Deterministic router agent:

```text
company_system/routing/deterministic_router_agent.py
```

Shared specialist rules:

```text
company_system/agents/common.py
```

Authorization helpers:

```text
company_system/security/authz.py
```

Embedding integration:

```text
company_system/rag/embeddings.py
```

LM Studio verification:

```text
verify_lmstudio.py
```

Development startup:

```text
start_project.ps1
```

First-time setup:

```text
setup_windows.ps1
```

---

## 37. Automated Regression Testing

### Routing Regression

```powershell
python tests/test_routing_regression.py
```

Validated:

```text
Passed: 30
Failed: 0
Total: 30
```

### Security Regression

```powershell
python tests/test_security_regression.py
```

Validated:

```text
Passed: 12
Failed: 0
Total: 12
```

### Database Sanity

```powershell
python tests/test_database_sanity.py
```

Validated:

```text
Passed: 10
Failed: 0
Total: 10
```

---

## 38. Test Data Cleanup

Known temporary development records can be removed with:

```powershell
python scripts/cleanup_test_data.py
```

The cleanup process was followed by the database sanity test to confirm that baseline demo records remained intact.

---

## 39. Verified Project Status

```text
Registered sub-agents        18
Routing regression           30 / 30 PASS
Security regression          12 / 12 PASS
Database sanity              10 / 10 PASS
Cross-agent same-session     PASS
Authentication / logout      PASS
Post-logout protection       PASS
Policy RAG grounding         PASS
LM Studio verification       PASS
Root-agent loading           PASS
Startup environment          PASS
```

---

## 40. Final Architecture Summary

```text
                         USER
                           |
                           v
                 COMPANYAI SUPERVISOR
                           |
                           v
                 DETERMINISTIC ROUTER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Auth Agent       Leave Agent      Project Agent
          |                |                |
          v                v                v
       SQLite           SQLite           SQLite

                           |
                           +----------------------+
                           |
                           v
                      Policy Agent
                           |
                           v
                  LM Studio Embedding
                           |
                           v
                        Qdrant
                           |
                           v
                company_handbook.pdf
```

Local model path:

```text
Specialist Agent
    |
    v
Google ADK
    |
    v
LiteLLM
    |
    v
LM Studio
    |
    v
qwen2.5-7b-instruct-1m
```

This architecture keeps:

- Top-level routing deterministic
- Company facts grounded in tools
- Security enforced in Python
- Policies grounded in PDF RAG
- Structured records in SQLite
- Vector search in Qdrant
- LLM and embeddings local
- Regression behavior testable
- Cloud API quota dependency removed
