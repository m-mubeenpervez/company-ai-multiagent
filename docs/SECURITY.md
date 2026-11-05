# CompanyAI security boundary

Updated 2026-11-04 (Asia/Karachi). Local development candidate; unresolved
advisories and incomplete live acceptance prevent production-security claims.
The earlier report is preserved in docs/archive/FINAL_RELEASE_REPORT_20261103.md.

## Trusted authentication and credential handling

Use start_project.ps1 or `python -m company_system.local_web --port 8000`.
The existing ADK Runner, Gemini semantic router, 18 agents and 39 MCP wire tools
remain. The thin local UI has separate sign-in and HR credential forms.

- Login JSON goes directly to trusted Python password verification, before any
  ADK conversation exists. Passwords do not enter Runner, MCP or model requests.
- A successful login creates a host-held MCP token and a separate opaque browser
  session cookie. Only non-secret identity enters ADK state. Cookie flags are
  HttpOnly/SameSite=Strict; host expiry is one hour. Every authenticated request
  revalidates the authoritative MCP account, role and employee binding.
- Chat accepts only message text. It cannot supply roles, state, tokens, user IDs
  or ADK session IDs. Each browser session owns a distinct host-created session.
- Known credentials, labeled secrets and credential-bearing chat are rejected
  before history creation. A second callback checks final model payloads. No text
  filter can identify every unlabelled arbitrary secret; use the forms and never
  paste other secrets into chat.
- Model declarations omit bearer parameters. The bridge injects the host token
  into a private wire-argument copy, preserving token-free ADK events. Secret
  fields are removed even from JSON nested inside MCP text responses.
- Login/create/update/delete credential tools are withheld from models. HR uses
  /api/credentials, existing Python authorization and credential lifecycle logic.
  The original 39 public MCP schemas remain unchanged for trusted native clients.
- The root refuses model execution without a trusted host token context. Login
  is not delegated to an LLM. Logout/identity still use authorized MCP tools.

The bounded redaction registry holds known secret values in host process memory
only, never ADK or disk. Protect the process itself. Unknown/disabled accounts
perform the same password derivation; failures are generic and existing per-user
lockout remains. This reduces account enumeration, not a claim of constant-time
HTTP behavior or comprehensive distributed throttling.

## Web exposure, telemetry and history

The supported server binds only 127.0.0.1. It rejects non-loopback clients, requires
the exact numeric Host/port and exact same Origin for JSON POSTs, and grants no
cross-origin CORS access. Bodies are capped at 16 KiB. Validation and exception
responses omit submitted input and tracebacks. Output uses textContent; CSP blocks
external scripts/framing. Responses use no-store/no-referrer. Access logging is off.

Stock ADK dev-ui, list-apps, session administration, trace, OpenAPI and docs endpoints
are not mounted. Anonymous identity/chat calls are denied. Telemetry SDK export and
GenAI content capture are disabled before framework imports; tracecontext is not
propagated. Log records redact known values and labeled secret fields; exception
logging omits sensitive exception repr/locals. Offline tests force native ADK spans
into an in-memory exporter to inspect attributes as an additional defense check.

Do not use stock `adk web` for real credentials. Manually launching that separate
upstream debug server can create raw transcripts before callbacks. The supported
launcher never starts it. Historical transcripts were preserved, not erased or
certified secret-free. Keep them private.

Loopback HTTP is not TLS. Cookies intentionally lack Secure on this HTTP-only local
interface. Another local process can imitate Origin/Host headers: these checks
protect browser CSRF/rebinding, not OS process identity. Stolen cookies, debuggers,
a compromised workstation, public demo passwords or writable private files remain
risks. No public deployment, enterprise identity gateway, MFA, comprehensive ACL
review, distributed throttling or production monitoring was implemented. Local
anonymous denial of service is not ruled out. Never expose UI or MCP to a network.

## Authorization and data

MCP stores token hashes, applies expiry/revocation and rechecks authoritative account
bindings on every protected call. Python roles and record ownership grant access;
model instructions/routing do not. PBKDF2-HMAC-SHA256 salts and constant-time digest
comparison remain. Credential changes revoke sessions; disabling referenced accounts
prevents foreign-key errors and token resurrection. Finance/leave input checks,
self-decision denial and atomic/idempotent leave balances remain.

SQL stays parameterized; tools do not accept arbitrary SQL, shells or file reads.
Retrieved/tool text and identity values are untrusted data. Domain tool allowlists
and application authorization supplement instructions. Offline safeguards do not
prove live adversarial resistance: direct/indirect model tests remain quota-blocked.

Business-operation/audit writes are not universally one transaction. Sparse legacy
constraints and HR exception/reconciliation rules need separate reviewed design.
No schema migration or historical balance reconciliation was performed.

## Dependency status and evidence

Audit status remains FAIL. The full per-advisory severity/range/path/reachability,
patch constraints and decisions are in evaluations/DEPENDENCY_SECURITY_REPORT.md.
Compatible installer patches were applied; framework versions were preserved. ADK
excludes patched OpenTelemetry versions; LiteLLM excludes the patched filelock
family. Diskcache/RAGAS have no advertised patched release in checked metadata.
Configured text evaluation does not enable disk caching or multimodal metrics.
Private-cache/disabled-path controls do not remove installed-package advisories.

Exact commands, interpreters, local/UTC dates, exits and counts are recorded in
`evaluations/results/remediation_test_runs.json` and dependency scan ledgers.
Dummy-secret tests inspect actual ADK payloads/history, a real MCP identity call,
wire arguments, nested tool output, logs, forced offline traces and HTTP denials.
Model test doubles are expressly offline verification, not live Gemini results.
D:/CompanyAI remains uncreated and final copying remains unauthorized.


## Master finalization refresh ? 2026-11-04

The connectivity verifier now honors the shared quota circuit, disables automatic
SDK retries and records provider quota errors without echoing raw exceptions.
Setup now refuses missing company SQLite/Qdrant data instead of initializing or
ingesting it. Injection acceptance additionally includes malicious free text appended
to a real MCP identity response; this is an isolated adversarial fixture, not a
production tool change or fabricated model response. See current final report for
actual live outcomes. Supported local-HTTP and OS-process limitations above remain.


### Final frozen-code verification

Runtime database connections now use SQLite URI mode=rw, so missing files cannot
silently become empty company databases. Only the explicit initializer creates a
database. Runtime policy clients require persisted Qdrant metadata; missing indexes
return not_ready without creating files or calling embeddings. Explicit ingestion
retains its separate creation path, and was not run on active company data.
Provider Retry-After supports HTTP dates and numeric delays. Checkpoints now include
runtime-isolator/requirements/lock hashes, full installed versions and an account
fingerprint; source/stage account differences cannot silently reuse completions.
Focused tests cover these guards and honest resume accounting; a positive agent
case cannot pass merely because an auth_required tool was called.

Current final evidence uses *_master_final.json. Earlier *_master_verified.json
measurements precede these final data/provenance guards and remain historical.
The finite tests do not remove the local HTTP, OS-process, historical-transcript,
privileged-HR-administration or business/audit transaction limitations above.
