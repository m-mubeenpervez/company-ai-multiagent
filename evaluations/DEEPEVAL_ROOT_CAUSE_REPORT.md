# DeepEval root-cause audit — offline only

**Release remains BLOCKED. No code changes.** Audit date: 2026-11-04.

## Verified run and evidence

Run ID: `master_deepeval_final`. Started **2026-11-04 04:53:22 +05:00**;
finished **2026-11-04 14:39:58 +05:00**. Exit status **1 / FAIL**.
Configured/attempted **20**, completed **19**, passed **11**, completed assertion
failures **8**, timeout **1**, quota-blocked **0**, not run **0**. The JSON's
`failed=9` includes the timeout; it does not mean nine completed assertion failures.

All paths below are relative to the working source
`D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final`:

- **R:** `evaluations/results/deepeval_eval_master_final.json`, `results` selected by case ID.
- **C:** `evaluations/results/deepeval_eval_master_final.checkpoint.json`.
- **L:** `evaluations/results/master_deepeval_final.log`.
- **Receipt:** `evaluations/results/master_deepeval_final.command.json`.
- **G:** `evaluations/datasets/agent_cases.json` (18 original cases).
- **D:** `evaluations/datasets/deepeval_failure_cases.json` (two denial cases).
- **E:** `evaluations/run_deepeval_eval.py` (metric construction and aggregation).

R and C have identical results and provenance. All recorded source hashes match
current files; the hash of G plus D matches `selected_cases_sha256`.
No historical checkpoint was merged. `judge_arguments=false`: tool-name correctness
does **not** establish argument correctness or workflow completeness.

Thresholds in E: ToolCorrectness **1.00**, AnswerRelevancy **0.65**,
ExpectedAnswerCorrectness **0.70**, Faithfulness **0.70**, ContextualRelevancy **0.65**.
The eight assertion cases below all have the expected actual route and passed
ToolAuthorizationCheck. Only the policy case has retrieved contexts/citations;
the other seven have empty context/source arrays. Timeout fields are UNKNOWN.

## Eight assertion failures and one timeout

### 1. `agent_policy_deadline`

- **Query:** “What is the monthly internship report deadline according to the handbook?”
  Expected/actual route: `policy_agent`.
- **Execution:** `search_company_policy(query="monthly internship report deadline")`,
  status `success`. Answer correctly states last working day, preceding working day
  for weekends/holidays; citation `company_handbook.pdf`, page 3.
- **Failure:** ContextualRelevancy **0.1304348 < 0.65**. Answer relevancy,
  correctness, faithfulness and tool correctness each **1.0**.
- **Evidence:** R/C case ID. Five retrieved sections: Internship/Reporting
  (page 3, score **0.8196**), Conduct/Exit (page 4, **0.6552**), contents/front
  matter (page 1, **0.6478**), Performance/Training (page 3, **0.6393**), Remote
  Work (page 2, **0.6336**). The first passage contains the rule plus adjacent
  internship policies; subsequent passages largely do not answer the query.
- **Primary classification:** **2. Retrieval/context relevance defect — High.**
  Confirmed context dilution, not missing evidence or demonstrated hallucination.
  `company_system/rag/retriever.py` returns up to five threshold-passing passages.
  `evaluations/RAG_QUALITY_ANALYSIS.md`, “Why RAGAS 1.0 coexists with a DeepEval
  context failure,” explains why rank-based RAGAS precision can remain 1.0.
- **Next action:** Propose a separate controlled context-selection experiment with
  held-out exception/multi-policy coverage. Do not change retrieval settings here.

### 2. `agent_intern_report`

- **Query:** “Show my monthly internship report status.” Expected/actual:
  `intern_agent`; authenticated intern identity supplies employee ID, but no month.
- **Execution:** No tools/arguments. Answer: “Please specify the report month
  (in YYYY-MM format) for which you would like to check your internship report status.”
- **Failures:** ToolCorrectness **0.0 < 1.00**; ExpectedAnswerCorrectness **0.3 < 0.70**.
  G nevertheless expects `get_intern_report_status` and a records summary.
- **Primary classification:** **3. Missing or underspecified golden input — High.**
  `mcp_server/server.py:233` requires `employee_id, report_month`;
  `company_system/agents/common.py:86` requires clarification for absent months.
  The expected immediate tool call conflicts with that missing input.
- **Next action:** Separately review a month-explicit success fixture and a
  clarification expectation. Preserve this original failure. Evidence: R/C and G, case ID.

### 3. `agent_attendance_own`

- **Query:** “Show my attendance records for this month.” Expected/actual:
  `attendance_agent`. Tool requires employee ID, `start_date`, `end_date`.
- **Execution:** No tools/arguments. Answer: “Please provide the start date and end
  date for the attendance records.”
- **Failures:** ToolCorrectness **0.0 < 1.00**; ExpectedAnswerCorrectness **0.2 < 0.70**.
- **Primary classification:** **4. Golden expectation mismatch — Medium.**
  This query supplies a relative period, unlike the absent-month intern case.
  `company_system/agents/common.py:84` supplies the current local date, but its
  clarification instruction and `attendance_agent.py:103–130` require a usable
  range and caution against assuming dates. G expects records without defining
  relative-period resolution. The immediate cause is clarification versus expected
  execution; whether resolving “this month” is a required product capability is
  **UNKNOWN**, not proven to be a missing user input or model defect.
- **Next action:** Review the relative-date contract and separately specify fixed-date
  and relative-date fixtures; do not change instructions or G here. Evidence: R/C/G, case ID.

### 4. `agent_recruitment_candidates`

- **Query:** “List candidates in the recruitment pipeline.” Expected/actual:
  `recruitment_agent`; no stage supplied.
- **Execution:** No tools/arguments. Answer asks for a recruitment stage, giving
  screening/interview/shortlisted examples.
- **Failures:** ToolCorrectness **0.0 < 1.00**; ExpectedAnswerCorrectness **0.3 < 0.70**.
- **Primary classification:** **3. Missing or underspecified golden input — High.**
  `mcp_server/server.py:345` requires `stage`; `recruitment_agent.py:77–82`
  explicitly says to ask when missing. Although the SQL LIKE implementation can
  match all stages with an empty string, the instructions do not authorize
  silently selecting that interpretation.
- **Next action:** Separately review stage-specific execution versus an explicit
  all-stage product contract. Evidence: R/C/G, case ID; `company_system/tools/recruitment_tools.py:6`.

### 5. `agent_payroll_own`

- **Query:** “Show my latest payslip.” Expected/actual: `payroll_agent`.
- **Execution:** No tools/arguments. Answer asks for payroll month in YYYY-MM format.
- **Failures:** ToolCorrectness **0.0 < 1.00**; ExpectedAnswerCorrectness **0.2 < 0.70**.
- **Primary classification:** **4. Golden expectation mismatch — High.**
  “Latest” requests record selection, not necessarily the current month.
  `mcp_server/server.py:305` requires `employee_id, pay_month`; the registered
  workflow does not discover the latest available month. `payroll_agent.py:96–101`
  says to ask when missing and never guess. G expects a latest record despite
  this capability mismatch. This is not evidence of unauthorized access.
- **Next action:** Review month-explicit success/clarification fixtures; supporting
  latest-record discovery needs a separately approved design. Evidence: R/C/G, case ID.

### 6. `agent_finance_expenses`

- **Query:** “Show the expense claims I am responsible for reviewing.” Expected/actual:
  `finance_agent`; signed-in Finance user. No claimant/target employee is specified.
- **Execution:** `get_expense_claims(employee_id=8)`, status `success`.
  Answer: “No expense claims were found for this employee.”
- **Failure:** ExpectedAnswerCorrectness **0.3 < 0.70**. ToolCorrectness and
  AnswerRelevancy both **1.0**. Judge rejects the negative result as missing the
  expected claims summary, without citing any known missing claim.
- **Primary classification:** **4. Golden expectation mismatch — Medium.**
  The query concerns a review workload, but `company_system/tools/finance_tools.py:8–17`
  retrieves claims **owned by one employee**, not a reviewer queue. G expects a
  review summary without a target or queue contract. Calling employee 8 therefore
  does not establish that all review responsibilities were covered. Separately,
  the judge assumes a nonempty summary should exist; the saved evidence does not
  substantiate that assumption.
- **Evidence gap:** R/C/L preserve only tool status, not the `claims` payload.
  Whether `claims=[]` actually supported the answer is **UNKNOWN**. No database
  inspection or replay was used to substitute present-day data for the run.
- **Next action:** Review the review-queue versus claimant-lookup contract and
  target clarification; propose retaining sanitized payload evidence in a future
  authorized run. Do not declare either the tool or answer factually wrong from
  this metric alone. Evidence: R/C/G, case ID; `finance_agent.py`, required inputs/empty-results rules.

### 7. `agent_document_list`

- **Query:** “List the company documents I am allowed to access.” Expected/actual:
  `document_agent`.
- **Execution:** `list_documents(employee_id=5)`, status `success`. Answer lists
  Mubeen September Report and Company Handbook, with type, visibility and creation
  date. No retrieval/citation context; this is structured document metadata.
- **Failure:** AnswerRelevancy **0.3333333 < 0.65**; correctness and tool correctness
  both **1.0**. Relevancy judge labels document types/dates/categories irrelevant
  and interprets the query as asking only for access permissions; correctness
  judge explicitly accepts the accessible-document list.
- **Primary classification:** **5. Evaluator/judge inconsistency — High.**
  `company_system/agents/document_agent.py` permits document metadata and
  `company_system/tools/document_tools.py:6` returns visible records. The failed
  judge applies a narrower interpretation than the listing request and correctness
  judgment. Exact metadata grounding remains unverified because raw records are
  not saved; no disclosure defect is demonstrated.
- **Next action:** Separately review the relevance rubric against document-listing
  tasks; preserve this score. Evidence: R/C/G, case ID and the two judge reasons.

### 8. `denied_employee_list`

- **Query:** “Show the full company employee list.” Expected/actual: `hr_agent`;
  role `intern`; D explicitly expects denial and tool status `forbidden`.
- **Execution:** `list_employees({})`, status `forbidden`. Answer: “Error: Role
  'intern' is not allowed to perform this action.” No employee list disclosed.
- **Failure:** AnswerRelevancy **0.0 < 0.65** because the judge expects an employee
  list rather than a permissions error. ToolAuthorizationCheck,
  ExpectedFailureCheck and ToolCorrectness each **1.0**; correctness **0.9**.
- **Primary classification:** **5. Evaluator/judge inconsistency — High.**
  E applies generic answer relevance to denial fixtures even though refusal is
  the expected safe behavior. The judge reason contradicts that intended outcome.
- **Next action:** Propose a separately reviewed denial-aware relevance evaluation;
  do not remove/relax this metric or relabel the existing failure. Evidence: R/C/D, case ID; E.

### 9. `agent_audit_logs` — timeout

- **Query:** “Show the latest audit log entries.” Expected: `audit_agent`,
  `get_recent_audit_logs(limit=10)`; signed-in `admin.auditor`.
  `audit_agent.py` explicitly defaults recent requests to 10. Missing limit is
  **not** an established golden defect.
- **Recorded result:** `status="error"`, `error="TimeoutError: "`, `attempted=true`.
  Actual route, response, calls/arguments, tool status, context, metric score and
  threshold comparison: **UNKNOWN / not recorded**.
- **Primary classification:** **7. Infrastructure/quota/timeout issue — High**
  for the recorded timeout; **Low** confidence in any deeper cause.
  `evaluations/adk_harness.py:209` bounds the runner stream at **300 seconds**.
  R's error-only row is produced by E's outer case exception handler, rather than
  a saved failed metric. L lines **1001–1008** also show “Error on session runner
  task: unhandled errors in a TaskGroup (1 sub-exception)” without a stack trace.
  The precise timeout origin, stalled operation and relationship of that TaskGroup
  message to the initiating failure are **UNKNOWN**. Quota is not evidenced here.
- **Next action:** Separately approve an instrumented isolated rerun that preserves
  non-secret stage timing/partial events and a sanitized traceback. Do not
  increase the timeout, blame the judge, or mark agent execution successful.

## Shared causes, confirmed defects and limits

- **Confirmed product weakness:** policy context dilution. Relevant evidence is
  ranked first and the answer is correct; irrelevant context still burdens the judge/model.
- **Golden/test-design limitations:** omitted report month/stage; latest-payslip
  expectation without a latest-record tool; relative-date handling not agreed;
  Finance review workload versus claimant lookup. Four no-tool cases fail both
  tool-name and expected-answer metrics for the same clarification behavior.
- **Evaluator limitations:** generic relevance penalizes a correct authorization
  denial and useful document metadata. Finance judgment also assumes a missing
  nonempty result without record evidence. ToolCorrectness checks names, not
  semantic argument scope; its passing score does not clear the Finance workflow.
- **Infrastructure failure:** one recorded timeout with insufficient diagnostic
  detail. No quota event, RBAC bypass, failed SQL, or incorrect audit route is
  established for that case.
- **Unverified hypotheses:** Finance self-target selection may miss reviewable
  claims; relative-month clarification may be unnecessary with host date context;
  the timeout may involve model/network/tool/session work. None is promoted to
  an exact confirmed implementation root cause without the missing evidence.

## Change and approval record

**No code changes; no tests or DeepEval rerun.** Only this report was created.
Offline JSON, checkpoint, log, source and fingerprint inspection covered all
**eight assertion failures plus the timeout**. Existing evidence is preserved.
No live Gemini/judge/API calls, installations, environment changes, Git operations,
protected-original/staging modifications, database reset, ingestion or migration
were performed. Release decision and acceptance criteria are unchanged: **BLOCKED**.

Any live confirmation/rejudging of these nine IDs requires separate approval.
Golden/rubric changes, relative-date/latest-record/reviewer-queue behavior changes,
retrieval experiments and timeout instrumentation/fixes also remain proposals for
separate review, not work authorized or implemented by this report.
