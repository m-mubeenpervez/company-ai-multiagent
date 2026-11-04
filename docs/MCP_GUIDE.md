# CompanyAI MCP guide

The server exposes 39 tools: ping, three authentication tools, and 35 domain
tools. All 37 protected tools validate a server-issued bearer token. Ping and
login are public. Every specialist uses an explicit domain allowlist.

From the project root, using the application environment:

```powershell
# STDIO: the default used by ADK; stdout belongs to the MCP protocol.
.\.venv\Scripts\python.exe mcp_server\server.py

# Loopback streamable HTTP; endpoint http://127.0.0.1:8001/mcp
.\.venv\Scripts\python.exe mcp_server\server.py --transport streamable-http --port 8001

# Standalone STDIO demonstration using seeded LOCAL DEMO credentials
.\.venv\Scripts\python.exe -m mcp_client.client
```

The standalone client accepts both SDK structured responses and JSON text
responses. Do not print or persist returned bearer tokens. The ADK bridge injects
tokens from trusted host state and replaces any token supplied by the model.
Successful login replaces the previous session; logout revokes the token.

Resources and prompts are intentionally empty. The server does not offer raw SQL,
arbitrary file reads, or shell execution. Document tools return metadata, not file
contents. HTTP is bound to `127.0.0.1`; this is not an internet-facing OAuth/TLS
deployment. Keep both transports local unless a separately reviewed secure
deployment is provided.

The complete transport test copies company data, runs all 39 tools (including
mutations on those copies), checks discovery, and stops its own child server:

```powershell
.\.venv-eval\Scripts\python.exe evaluations\verify_mcp_release.py --transport stdio
.\.venv-eval\Scripts\python.exe evaluations\verify_mcp_release.py --transport streamable-http
```

Policy search makes a real Gemini embedding request. Run one live evaluation at a
time. Reports are `evaluations/results/remediation_mcp_<transport>.json`.

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
