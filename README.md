# CompanyAI — Complete Local Multi-Agent Company Management System

CompanyAI is a learning-oriented but realistic local company management system built with Google ADK, local LLMs, structured company tools, SQLite, Qdrant, and PDF-based RAG.

The project demonstrates:

- Multi-agent architecture
- Deterministic request routing
- Tool calling
- Local LLM deployment
- Retrieval-Augmented Generation (RAG)
- Vector search
- Relational database access
- Authentication and authorization
- Role-based company workflows
- Audit logging

---

## Tech Stack

- **Agent Framework:** Google ADK
- **LLM Adapter:** LiteLLM
- **Local Inference Server:** LM Studio
- **Main LLM:** `qwen2.5-7b-instruct-1m`
- **Embedding Model:** `text-embedding-nomic-embed-text-v1.5`
- **Vector Database:** Qdrant
- **Relational Database:** SQLite
- **RAG Source:** `company_handbook.pdf`

No Gemini API key, OpenRouter API key, or Ollama installation is required for the current setup.

---

## High-Level Architecture

```text
User
  ↓
Google ADK
  ↓
CompanyAI Supervisor
  ↓
Deterministic Router
  ↓
Specialist Agent
  ↓
Domain Tool
  ↓
SQLite / Qdrant
```

The root supervisor does not depend on the LLM to decide which specialist should receive a request. Routing is performed by deterministic Python rules so that agent selection remains predictable and testable.

---

## Local Model Flow

```text
Specialist Agent
  ↓
LiteLLM
  ↓
LM Studio OpenAI-Compatible API
  ↓
Qwen2.5-7B-Instruct
```

The local LLM is mainly used for:

- Understanding the specialist task
- Tool selection inside the selected specialist
- Formatting grounded tool results
- Producing user-facing responses

Top-level routing is handled separately in Python.

---

## RAG Flow

```text
company_handbook.pdf
  ↓
PDF Text Extraction
  ↓
Cleaning + Chunking
  ↓
Nomic Embed Text v1.5
  ↓
Qdrant
  ↓
Similarity Search
  ↓
Relevant Policy Chunks
  ↓
Policy Agent
  ↓
Grounded Answer
```

Official company-policy questions are answered through the Policy Agent using retrieved handbook content.

---

## Structured Company Data Flow

```text
Specialist Agent
  ↓
Domain Tool
  ↓
Authorization Check
  ↓
SQLite
  ↓
Structured Company Record
```

SQLite stores company data such as employees, interns, attendance, leave, recruitment, performance, training, projects, payroll, expenses, IT assets, documents, notifications, and audit logs.

---

## Agents

The root agent is:

```text
company_ai_supervisor
```

It has 18 registered sub-agents:

1. Authentication Agent
2. HR Agent
3. Employee Records Agent
4. Intern Management Agent
5. Attendance Agent
6. Leave Agent
7. Policy RAG Agent
8. Recruitment Agent
9. Performance Agent
10. Training Agent
11. Project Agent
12. Payroll Agent
13. Finance Agent
14. IT Asset Agent
15. Document Agent
16. Analytics Agent
17. Notification Agent
18. Audit Agent

Specialist-to-specialist peer transfer is disabled.

Preferred flow:

```text
User
  ↓
Supervisor
  ↓
Correct Specialist
```

If the user's domain changes, control returns through the supervisor instead of transferring directly from one specialist to another.

---

## Deterministic Routing

CompanyAI uses a deterministic router instead of relying on the LLM for top-level routing.

Examples:

```text
"Show my leave balance"
→ leave_agent
```

```text
"Show my training assignments"
→ training_agent
```

```text
"What is the internship report deadline?"
→ policy_agent
```

```text
"Show company headcount summary"
→ analytics_agent
```

Benefits:

- Predictable routing
- Easier regression testing
- Lower local-model prompt overhead
- Reduced routing hallucinations
- Clear separation between orchestration and generation

---

## Local Models

### Main LLM

```text
qwen2.5-7b-instruct-1m
```

The model runs locally through LM Studio. It is used by specialist agents for tool use and response generation.

Local performance depends on CPU, GPU, RAM, VRAM, context size, prompt size, and the number of LLM calls.

A practical LM Studio context size for this project is:

```text
8192
```

A larger context such as `16384` may be used when needed.

### Embedding Model

```text
text-embedding-nomic-embed-text-v1.5
```

Current embedding vector size:

```text
768
```

Embedding flow:

```text
Text
  ↓
Embedding Vector
  ↓
Qdrant
  ↓
Similarity Search
```

If the embedding model changes, rebuild the Qdrant collection because vectors from different embedding spaces should not be mixed.

```powershell
python ingest_documents.py --reset
```

---

## LM Studio

The project connects to:

```text
http://localhost:1234/v1
```

Before running CompanyAI:

1. Open LM Studio.
2. Make sure the main LLM is available.
3. Make sure the embedding model is available.
4. Start the local API server.
5. Confirm that port `1234` is active.

Verify the configuration with:

```powershell
python verify_lmstudio.py
```

Expected result:

```text
LM Studio server: OK
Configured LLM: qwen2.5-7b-instruct-1m
Configured embedding model: text-embedding-nomic-embed-text-v1.5
LM Studio configuration: PASS
```

---

## Environment Configuration

Example `.env` values:

```text
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_LLM_MODEL=qwen2.5-7b-instruct-1m
LM_STUDIO_EMBED_MODEL=text-embedding-nomic-embed-text-v1.5
RAG_COLLECTION=company_policies
RAG_TOP_K=5
RAG_MIN_SCORE=0.45
```

---

## First-Time Setup

```powershell
cd D:\company_ai_multiagent
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
```

Make sure LM Studio is running before setup steps that require the local model server.

---

## Starting the Project

For normal development:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
```

The current startup script prepares the local environment, activates `.venv`, sets `PYTHONPATH`, confirms Python, and reminds you to keep LM Studio running.

Then start ADK Web:

```powershell
adk web
```

---

## Demo Accounts

See:

```text
DEMO_CREDENTIALS.md
```

Example intern account:

```text
Username: intern.mubeen
Password: Intern#2026
```

Example HR account:

```text
Username: hr.admin
Password: HrAdmin#2026
```

These credentials are for local educational/demo use only. Passwords are stored as salted hashes rather than plain text.

---

## Authentication and Session State

Successful login stores values in ADK session state:

```text
auth_user_id
auth_username
auth_role
auth_employee_id
auth_full_name
```

Sensitive tools read this state before accessing protected resources.

```text
Agent
  ↓
Tool
  ↓
require_auth()
  ↓
Role / Employee Permission Check
  ↓
SQLite
```

The LLM is not the security boundary. Authorization is enforced in Python tools.

After logout, authentication state is cleared and protected tools return an authentication-required response.

---

## Role-Based Authorization

Examples:

- Employees can access their own allowed records.
- Managers can access permitted records for direct reports.
- HR and Admin can access broader employee information.
- Finance can access permitted payroll and finance operations.
- IT can access IT-specific asset operations.
- HR-only credential administration is enforced inside tools.
- Audit-log access is restricted to authorized roles.

Permission failures return statuses such as `forbidden` or `auth_required`.

---

## HR Credential Administration

Credential creation, update, and deletion are restricted to HR.

Example:

```text
Create login credentials for employee 3.
```

Authorization is checked in the tool itself. An unauthorized role cannot bypass this by changing prompt wording.

---

## Policy RAG

Main policy source:

```text
company_system/documents/company_handbook.pdf
```

Example question:

```text
What is the deadline for submitting a monthly internship report?
```

Expected flow:

```text
User
  ↓
Supervisor
  ↓
policy_agent
  ↓
Query Embedding
  ↓
Qdrant
  ↓
Relevant Handbook Chunk
  ↓
Grounded Answer + Source
```

Validated answer:

```text
Interns submit their monthly progress report by the last working day
of each month. If the final calendar date is a weekend or company
holiday, the deadline is the preceding working day.

Source: company_handbook.pdf, page 3
```

---

## RAG Ingestion

The ingestion pipeline performs:

```text
PDF
  ↓
Page Extraction
  ↓
Text Cleaning
  ↓
Chunking
  ↓
Embedding
  ↓
Qdrant Storage
```

Rebuild the vector database with:

```powershell
python ingest_documents.py --reset
```

Current validated RAG setup:

```text
PDF pages: 6
Stored chunks: 14
Embedding size: 768
```

---

## SQLite Database

Database location:

```text
company_system/database/company.db
```

The project uses structured records for:

- Employees
- Users
- Intern profiles
- Internship reports
- Attendance
- Leave balances
- Leave requests
- Candidates
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
- Documents
- Notifications
- Audit logs

---

## Qdrant

Local storage:

```text
company_system/qdrant_storage/
```

Qdrant stores policy-document chunk embeddings and performs semantic similarity search.

---

## Response Grounding Rules

Company-specific facts should come from registered tools or retrieved RAG context.

The model may safely reformat confirmed values, for example `2026-08-01` → `August 1, 2026` or `under_review` → `Under Review`.

Unsupported facts must not be invented. For example, if a tool does not return a currency, the response should not add one.

---

## Automated Tests

### Routing Regression

```powershell
python tests/test_routing_regression.py
```

Validated result:

```text
Passed: 30
Failed: 0
Total: 30
```

### Security Regression

```powershell
python tests/test_security_regression.py
```

Validated result:

```text
Passed: 12
Failed: 0
Total: 12
```

### Database Sanity Test

```powershell
python tests/test_database_sanity.py
```

Validated result:

```text
Passed: 10
Failed: 0
Total: 10
```

---

## Validated Manual Integration Tests

The following behavior has been verified in ADK Web:

- Login
- Logout
- Post-logout access protection
- Cross-agent routing in the same session
- Intern profile retrieval
- Training retrieval
- Project retrieval
- Task retrieval
- Notification retrieval
- Leave balance retrieval
- Policy RAG grounding
- Handbook source citation

Example same-session flow:

```text
Login as intern.mubeen
  ↓
Intern Profile
  ↓
Training
  ↓
Projects
  ↓
Tasks
  ↓
Notifications
  ↓
Leave
  ↓
Policy RAG
```

All requests were routed to the expected specialist without stale data mixing.

---

## Test Data Cleanup

Known development test records can be removed with:

```powershell
python scripts/cleanup_test_data.py
```

The cleanup script should only target known development/test records.

---

## Important Files

```text
company_system/agent.py
```
Registers the root supervisor and sub-agents.

```text
company_system/routing/router.py
```
Contains deterministic routing rules.

```text
company_system/routing/deterministic_router_agent.py
```
Runs the selected specialist agent.

```text
company_system/agents/common.py
```
Contains shared grounding and response rules.

```text
company_system/security/authz.py
```
Contains authentication and authorization helpers.

```text
company_system/database/company.db
```
SQLite company database.

```text
company_system/documents/company_handbook.pdf
```
Main policy RAG source.

```text
company_system/qdrant_storage/
```
Local vector database storage.

```text
company_system/config.py
```
Model and RAG configuration.

```text
verify_lmstudio.py
```
Verifies LM Studio and configured models.

```text
start_project.ps1
```
Prepares the normal development environment.

```text
setup_windows.ps1
```
First-time setup script.

```text
tests/test_routing_regression.py
```
Deterministic routing regression tests.

```text
tests/test_security_regression.py
```
Role and permission regression tests.

```text
tests/test_database_sanity.py
```
Database baseline verification.

```text
scripts/cleanup_test_data.py
```
Removes known development test records.

---

## Final Verified Status

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

## Security Note

This is a local educational and learning-oriented project. It is not production identity infrastructure.

A production deployment should additionally use:

- External identity provider
- Secure secret management
- Formal RBAC or ABAC
- Encrypted transport
- Database backups
- Secret rotation
- Centralized logging
- Stronger audit controls
- Production-grade database infrastructure
- Secure deployment and monitoring

The current project demonstrates realistic implementation concepts for multi-agent systems, deterministic orchestration, tool calling, local LLMs, RAG, vector databases, relational databases, authentication, authorization, and company workflows.
