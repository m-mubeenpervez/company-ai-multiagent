# CompanyAI MCP Architecture

CompanyAI uses a local MCP server over STDIO as the tool transport for all 18 registered agents.

## Request flow

```text
User
  -> Gemini semantic router
  -> specialist agent
  -> filtered ADK McpToolset
  -> local STDIO MCP server
  -> MCP session validation
  -> CompanyAI business/security tool
  -> SQLite or Qdrant RAG
  -> MCP result
  -> specialist response
```

## Tool coverage

The MCP server exposes 39 tools across authentication, HR, employee records, interns, attendance, leave, policy/RAG, recruitment, performance, training, projects/tasks, payroll, finance/expenses, IT/assets, documents, analytics, notifications, and audit. `ping_companyai` is a health-check tool.

## Authentication and security boundary

- Login verifies the user's password against the salted PBKDF2 hash.
- The MCP server creates a random opaque token and stores only its SHA-256 hash.
- The ADK host stores the token in session state.
- The `before_tool_callback` overwrites any model-supplied token with the trusted ADK session token.
- The MCP server checks token validity, expiry, revocation, and current account/role state on every protected call.
- The original CompanyAI Python tools enforce role and record-level permissions.

The LLM is not a security boundary. Tool authorization remains server-side.

## Local transport

ADK starts the MCP server as a child process using STDIO through `McpToolset`. Do not manually run `mcp_server/server.py` during normal `adk web` usage.

## Evaluation safety

Evaluation and regression scripts run against copied SQLite and Qdrant stores. They must not delete active sessions or rebuild the live project's Qdrant collection.

See `EVALUATION_SECURITY_IMPLEMENTATION.md` for setup and commands.
