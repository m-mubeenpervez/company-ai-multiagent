# Recovery status - RELEASE BLOCKED

Updated 2026-11-04T10:06:21.200325+00:00. This current recovery status supersedes acceptance claims in the historical text below. Final-copy authorization remains **false**; `D:\CompanyAI` is absent.

RAGAS: **PASS execution**, six completed, scores **0.8889 / 1.0 / 1.0**. DeepEval: **FAIL**, 20 attempted, 19 completed, 11 passed, eight assertion failures plus one timeout. Routing: **PASS 36/36**. Agent acceptance: **BLOCKED/incomplete**, 13 recorded passes of 24; 11 unknown outcomes, exact interrupted attempt count unavailable. Injection: **NOT RUN 0/3**. Dependency audit: **FAIL**, 16 unresolved IDs.

Original 103 fingerprints, rollback 481 files, and 16 protected assets: **PASS**. SQLite source/stage/rollback integrity and foreign keys: **PASS**. Qdrant copied-index structure: **PASS**, 17 points, 768 dimensions. Existing source/stage/fresh offline receipts reused; four new renderer tests **PASS**. No live evaluations launched or packages installed during recovery; the pre-existing job was stopped.

Renderer classification/missing-status/dependency filtering defects corrected, but full renderer execution is **BLOCKED** by missing required evidence. No source/staging synchronization was performed. Full 15-file status, per-suite accounting, limitations and evidence paths: [recovery audit](../docs/RECOVERY_AUDIT.md).

---

## HISTORICAL - preserved previous report, superseded by recovery audit above

# Agent acceptance coverage

2026-11-04 (Asia/Karachi). Registration/instructions/tool surfaces inspected; live model behavior remains BLOCKED. Positive tool-transport checks do not prove agent execution.

| Agent | Registration | Model execution/current candidate | Instruction/tool/input evidence |
|---|---|---|---|
| auth_agent | PASS | BLOCKED | company_system/agents/auth_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| hr_agent | PASS | BLOCKED | company_system/agents/hr_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| employee_agent | PASS | BLOCKED | company_system/agents/employee_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| intern_agent | PASS | BLOCKED | company_system/agents/intern_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| attendance_agent | PASS | BLOCKED | company_system/agents/attendance_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| leave_agent | PASS | BLOCKED | company_system/agents/leave_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| policy_agent | PASS | BLOCKED | company_system/agents/policy_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| recruitment_agent | PASS | BLOCKED | company_system/agents/recruitment_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| performance_agent | PASS | BLOCKED | company_system/agents/performance_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| training_agent | PASS | BLOCKED | company_system/agents/training_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| project_agent | PASS | BLOCKED | company_system/agents/project_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| payroll_agent | PASS | BLOCKED | company_system/agents/payroll_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| finance_agent | PASS | BLOCKED | company_system/agents/finance_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| it_agent | PASS | BLOCKED | company_system/agents/it_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| document_agent | PASS | BLOCKED | company_system/agents/document_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| analytics_agent | PASS | BLOCKED | company_system/agents/analytics_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| notification_agent | PASS | BLOCKED | company_system/agents/notification_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |
| audit_agent | PASS | BLOCKED | company_system/agents/audit_agent.py; detailed required fields/model tools in agent_acceptance_remediation_final.json |

The 24 separate acceptance cases cover18 explicit-input read workflows,4 missing-input requests and2 authorization denials. All24 are blocked by the current quota circuit, not failed model decisions. Exact questions/accounts/expected tools are in datasets/agent_acceptance_cases.json; the original 18 agent goldens remain byte-identical. No native model output is fabricated.

Original underspecified cases: intern report lacks a month; payroll asks latest although the tool requires pay_month; recruitment omits stage; finance reviewing responsibility does not identify a target employee; audit omits a required limit. Attendance uses a relative month and must be resolved consistently or clarified. These are documented for review, not silently repaired in the original dataset. Separate fixtures provide explicit inputs; missing-input cases expect clarification without tool execution.

Instructions retain role/record-denial preservation, factual output grounding and untrusted tool/document rules. There is no universal structured JSON answer contract. The host identity provider supplies only non-secret identity/date. Tool names, required inputs, instruction fingerprints, responsibility, response/error boundaries and per-case statuses are recorded in results/agent_acceptance_remediation_final.json. Credential operations use trusted forms rather than model tools. All writes in deterministic security/transport tests use disposable data; no historical policy/balance reconciliation is performed.


## Master finalization status (live execution in progress)

The tables above describe the previous remediation snapshot, whose live runs were
blocked. New frozen-code evidence uses `results/*_master_final.json`; registration
alone is not counted as model execution. DeepEval original-golden failures caused
by omitted month/stage/date/target/limit inputs remain distinct from explicit-input
agent smoke cases and the four deliberate missing-input cases. Positive smoke now
requires real success tool results; auth_required cannot pass merely by tool name.
Final per-agent results will replace this current-state table after the sequential
acceptance run completes. All original datasets remain unchanged.
