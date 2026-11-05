# CompanyAI Security Assessment Matrix

| Threat area | Coverage added | Enforcement / expected behavior | Test |
|---|---|---|---|
| Direct prompt injection | Yes | Router treats request as untrusted; tool authorization remains server-side | `run_prompt_injection_eval.py` |
| Indirect RAG prompt injection | Yes | Retrieved passages are untrusted evidence; embedded instructions must be ignored | `run_prompt_injection_eval.py` |
| Tool-output injection | Defense-in-depth | Policy Agent must not follow commands in returned passage content | Golden security dataset + live RAG test |
| Cross-employee profile access | Existing RBAC + regression | `can_view_employee` denies non-permitted targets | Existing MCP security regression |
| Cross-employee payroll access | Existing RBAC + regression | Payroll tool returns `forbidden` | Existing MCP security regression + live injection test |
| Unauthorized credential management | Existing HR-only tool checks | Credential tools enforce HR role | Existing security regression |
| Forged MCP token | Yes | Unknown token returns `auth_required` | `run_security_regression.py` |
| Token replay after logout | Existing + new regression | Revoked token returns `auth_required` | MCP security regression |
| Expired MCP token | Yes | Expired token is revoked and rejected | `run_security_regression.py` |
| Stale role / disabled account | Yes | Current user record is checked on every MCP request; stale token is revoked | `run_security_regression.py` |
| Login brute-force attempts | Yes, basic local throttle | Five failures in 15 minutes trigger 15-minute lockout | `run_security_regression.py` |
| Secret/token exposure in reports | Yes | Evaluation reports omit bearer tokens, passwords, and raw payroll outputs | Evaluation harness/report design |
| MCP tool catalog drift | Existing + regression | Expected and actual MCP tool names must match | `tests/test_mcp_catalog.py` |
| Agent routing errors | Yes | Golden route dataset covers all 18 routes | `run_routing_eval.py` |
| RAG grounding/retrieval quality | Yes | RAGAS scores faithfulness, context precision, and context recall | `run_ragas_eval.py` |
| Agent answer/tool quality | Yes | DeepEval evaluates answer relevancy, faithfulness, tool correctness, tool permission | `run_deepeval_eval.py` |

## Important limitations

- Prompt-injection resistance cannot be guaranteed by prompt wording alone.
- Tool-level authorization is the actual security boundary.
- The login throttle is local per-username protection; it is not a distributed IP/device rate limiter.
- Destructive/write operations still rely on the existing role and record checks; a production system should add explicit confirmation/approval gates for high-impact actions such as credential changes, leave approvals, expense reviews, and employee-status changes.
- An authorized user's allowed tool can still be misused if the model misunderstands intent. Tool permission checks alone do not prove that the user explicitly intended a particular write operation.
- The current app uses demo accounts and local SQLite/STDIO. Production use requires a managed identity system, secure deployment, monitoring, backups, and independent review.
