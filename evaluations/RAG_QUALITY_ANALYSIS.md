# CompanyAI RAG quality analysis

## Scope and evidence

Work is confined to the evaluation/security working copy. The original project
is untouched. The historical six-case report is preserved byte-for-byte as both
`results/ragas_eval_latest.json` and `results/ragas_eval_baseline.json` (SHA-256
`20b4886fe9699e144baf9bb50f720d8b8df3a757a4c149aa542f0084bce130ec`).
The six goldens and the handbook PDF are unchanged.

The historical report did **not** retain answers, contexts, queries, source
metadata, or judge verdicts. Its exact per-case failure causes cannot be
reconstructed. A fresh before-change diagnostic run collected those artifacts
using the same real ADK/router/MCP pipeline and RAGAS configuration:
`results/ragas_eval_diagnostic_baseline.json`. All six cases completed.
The reporter records the actual structured judge outputs without changing
prompts, metric inputs, verdicts, scores, or the number of judge calls.

All questions, references, generated answers, ranked context text, source/page
metadata, cosine scores, tool queries, and per-claim/per-context judge reasons
are available in that diagnostic report. `results/rag_corpus_before.json`
maps the original Qdrant point IDs to their full passage text and PDF pages.
Settings, package versions, and source hashes are recorded in
`results/rag_quality_baseline_manifest.json`.

| Metric | Historical baseline | Fresh unchanged-pipeline control |
| --- | ---: | ---: |
| Faithfulness | 0.8333 | 0.8333 |
| Context Precision | 0.7083 | 0.7639 |
| Context Recall | 1.0000 | 1.0000 |

The changed control scores occurred **before any production change**. Query
wording, answers, statement extraction, and verdicts are model-generated.
A historical-to-new score difference alone cannot establish a code improvement.

## Corpus audit

- The existing 14 Qdrant points exactly match the current chunker output.
  There is no stale-index mismatch and no exact duplicate passage.
- Chunks are formed from PDF **visual lines**, with 1,000-character packing and
  150-character overlap. A visual line is not a complete paragraph or rule.
- Point 2 ends with `2. Attendance and Working Hours` but contains no attendance
  policy. Point 3 mixes an employment fragment, attendance, and an unfinished
  leave entitlement. Point 4 mixes leave policy with a remote-work rule cut off
  at `unless their role is`; point 5 repeats that rule with its exception intact.
- Point 6 mixes remote-work process rules with internship reporting. Point 7
  starts `rt within 2 working days...` and mixes reporting with training.
  Several overlaps begin mid-word. These are real content-boundary defects.
- Source filenames and page numbers match the PDF. All six reference policies
  are present and unambiguous. No reference, filter, embedding-model, or RBAC
  correction is justified by this evidence.
- Context Recall is 1.0 for every control case. Missing reference facts are
  not demonstrated; mixed-topic passages and misranking are demonstrated.

## Individual case analysis before optimization

Triples below are Faithfulness / Context Precision / Context Recall. Historical
answers were not saved; quoted answers and rankings are from the fresh control.

### 1. Intern monthly deadline

**Question:** When must interns submit their monthly progress report?

**Reference:** Last working day of each month; if the last calendar date is a
weekend or company holiday, use the preceding working day.

**Actual answer:** “Interns must submit their monthly progress report by the last
working day of each month. If the final calendar date is a weekend or company
holiday, the deadline is the preceding working day.” Citation: handbook page 3.

**Scores:** historical 1.0 / 0.5 / 1.0; control 1.0 / 0.5 / 1.0.

**Problem:** The correct initial-report deadline is outranked by a revision chunk.

**Evidence:** Rank 1 is point 7, page 3, cosine 0.7960; rank 2 is point 6,
page 3, cosine 0.7741. Precision verdicts are [0, 1, 0, 0, 0]. The judge states
that rank 1 discusses revisions but does not give the monthly submission
deadline. Other returned passages cover remote work, payroll, and contents.
Both answer claims are supported according to the actual NLI verdicts.

**Root cause:** Reporting is split between two mixed-topic chunks. The revision
fragment embeds closer to the question than the chunk holding the deadline.

**Proposed fix:** Keep the reporting section together and separate other topics.

**Expected impact:** Retrieve the complete deadline and exception together at a
better rank; reduce fragmented context without changing an already correct answer.

### 2. Remote-work approval

**Question:** What approval is required before an intern works remotely?

**Reference:** Written manager approval unless an approved remote-work
arrangement covers the role; remote work is not automatic.

**Actual answer:** “Employees and interns require written manager approval before
working remotely, unless their role is covered by an approved remote-work
arrangement.” Citation: handbook page 2.

**Scores:** historical 0.5 / 0.5 / 1.0; control 1.0 / 0.5833 / 1.0.

**Problem:** Mixed-topic and incomplete approval passages dilute retrieval.
The historical Faithfulness penalty does not reproduce in this control.

**Evidence:** Actual query: `intern remote work approval policy`. Rank 1 is
point 6, page 3, cosine 0.8080, mixing remote-work process separation with intern
reporting; it does not state the written-approval requirement. The complete rule
is point 5, page 2, rank 2, cosine 0.7856. Point 4, rank 3, cosine 0.7648,
ends before the approved-arrangement exception. Precision verdicts [0,1,1,0,0]
allow a partially useful chunk; they do not certify that every condition is present.
Both generated policy claims receive NLI verdict 1 in the control.

**Root cause:** Section mixing boosts an incomplete topical match, while overlap
duplicates only part of the approval rule. No observed generation hallucination
justifies a prompt change; the historical 0.5 cannot be diagnosed retrospectively.

**Proposed fix:** Preserve the complete remote-work approval section, separately
from reporting and leave. Retain the agent's exception and source citation.

**Expected impact:** Better ranking and fewer incomplete/duplicated policy fragments.
Do not attribute the pre-change Faithfulness recovery to an optimization.

### 3. Leave entitlements

**Question:** What annual, sick, and casual leave entitlements do permanent
employees receive?

**Reference and actual answer:** 20 annual, 10 sick, 7 casual days per leave
year unless a signed contract specifies otherwise. Citation: handbook page 2.

**Scores:** historical and control both 1.0 / 1.0 / 1.0.

**Problem:** No answer or recall failure is demonstrated. The context includes
redundant, partly cut-off entitlement text and unrelated trailing passages.

**Evidence:** Point 4 is rank 1 (page 2, 0.7080), with the complete rule. Point 3
is rank 2 (page 2, 0.6973), but its entitlement text ends at `per leave`.
Precision verdicts [1,1,0,0,0]; all three answer claims receive NLI verdict 1.

**Root cause:** Overlap across section boundaries creates partial redundancy.
Context Precision is average precision over relevant ranks; a score of 1.0
does not mean all five passages are useful.

**Proposed fix:** Apply the same section-boundary correction; preserve the full
entitlement rule and contract exception. Do not change correct instructions.

**Expected impact:** Cleaner evidence, with no justified expectation of an already
perfect metric increasing. Preserve answer correctness and recall.

### 4. Late arrival

**Question:** At what time is an employee considered late under the handbook?

**Reference and actual answer:** “Arrival after 9:15 AM is treated as late unless
approved by a manager or covered by an official flexible schedule.”
Citation: handbook page 2.

**Scores:** historical 1.0 / 0.25 / 1.0; control 0.5 / 0.5 / 1.0.

**Problem:** The attendance heading is detached from its rule. Separately, a valid
citation is penalized by a judge that receives only passage bodies.

**Evidence:** Query: `late employee attendance working hours handbook`. Point 2
is rank 1 (page 2, 0.7324); it ends with the attendance heading but lacks the
rule. Point 3 is rank 2 (page 2, 0.7180) and contains the complete rule.
Precision verdicts [0,1,0,0,0]. The policy claim gets NLI verdict 1. A second
extracted claim, “The source of this information is company_handbook.pdf on
page 2,” gets verdict 0 because “The context does not mention” that source.
The separately recorded source metadata does confirm the filename and page.

**Root cause:** Retrieval: line packing strands a heading in the preceding
section. Evaluation: citation claims are inconsistently extracted and judged
against body-only contexts, which omit real source metadata.

**Proposed fix:** Keep heading and policy together. Preserve citations and raw
metric inputs; document the evaluation limitation instead of overriding verdicts.

**Expected impact:** Better attendance ranking. Faithfulness may still fluctuate
because the evaluation artifact is deliberately not changed in this comparison.

### 5. Report revision

**Question:** How long does an intern have to revise a monthly report after
changes are requested?

**Reference and actual answer:** Submit the revised report within 1 working day
of receiving feedback if changes are requested. Citation: handbook page 3.

**Scores:** historical and control both 1.0 / 1.0 / 1.0.

**Problem:** No answer failure; supporting revision text is repeated across
mixed reporting/training and remote-work/reporting chunks.

**Evidence:** Points 7 and 6 rank first and second, page 3, cosine 0.7818 and
0.7207. Precision verdicts [1,1,0,0,0]. The extracted policy claim is supported.

**Root cause:** Arbitrary overlap duplicates the revision rule and surrounding
fragments, despite successful retrieval for this particular question.

**Proposed fix:** Preserve the reporting section as one complete topical unit.

**Expected impact:** Less fragmented evidence while retaining the same deadline.

### 6. Leave approval

**Question:** When is a leave request considered approved?

**Reference:** An authorized manager or HR representative must approve it;
pending requests must not be described as approved.

**Actual answer:** “A leave request is not considered approved until an authorized
manager or HR representative approves it.” Citation: handbook page 2.

**Scores:** historical and control both 0.5 / 1.0 / 1.0.

**Problem:** The measured Faithfulness penalty is a citation-evaluation artifact
in the control, not an unsupported approval policy.

**Evidence:** Point 4, page 2, is rank 1 (0.7022); precision verdicts [1,0,0,0,0].
The NLI judge accepts the approval rule (1) and rejects “The source of this
information is company_handbook.pdf on page 2” (0), saying the context does
not state that source. The tool metadata does state it. Recall verdicts accept
both the approval authority and pending-request prohibition.

**Root cause:** Same body-only-context/citation mismatch as late arrival.
The original historical verdict is unavailable, so its identical numeric score
alone cannot prove it had this same cause.

**Proposed fix:** Do not remove legitimate citations, hardcode an answer, or
weaken policy instructions. Clean the mixed leave/remote-work chunk with the
shared boundary fix. Consider metadata-aware judging only as a separate future
evaluation change applied to both frozen before and after samples.

**Expected impact:** Cleaner policy evidence; no claimed generation repair or
guaranteed Faithfulness increase from changing the chunker.

## Selected change and integrity constraints

Implement section-aware, whole-sentence chunking in the existing chunker and
re-embed/reindex the unchanged handbook with the existing Gemini embedding
model, 768 dimensions, collection, and Qdrant directory. Keep page/source
metadata. Use whole-sentence overlap only when a section exceeds the chunk
budget; allow an individual overlong sentence to exceed the soft limit rather
than truncating a policy condition. Keep page boundaries explicit.

Do not change the router, agent prompts, tool definitions/schemas, retrieval
algorithm, top-K (5), similarity threshold (0.45), references, scoring logic,
or judge configuration. No hybrid retriever, reranker, source filter, or new
dependency is justified yet. Backups of changed files and the entire old Qdrant
index are in `.evaluation_runtime/rag_quality_backups_20261103_203432/`.

The analysis above was completed before the production change. Final executed results follow.

## Implemented changes

- `company_system/rag/chunker.py`: numbered section boundaries, normalized visual wrapping, whole-sentence packing and overlap; original source/page values retained. Page-opening titles and continued section headings are handled without mixing different documents.
- Rebuilt the backed-up working-copy `company_policies` collection from the unchanged six-page PDF using the existing ingestion path. Actual Gemini embedding generation returned 17 vectors of 768 dimensions; maximum new chunk length is 949 characters. The old index has 14 points.
- `evaluations/run_ragas_eval.py`: save actual answers, queries, ranked passage bodies and source metadata, and observe the exact structured outputs used by the existing metrics. Added `--output`; the default writes `results/ragas_eval_improved.json` to preserve the historical latest report. Metric prompts, judge settings and score calculations remain unchanged. The reporter passes actual retrieved passage bodies and generated answers through without augmentation; passage content changes only because the corpus was rebuilt.
- `evaluations/test_ragas_eval.py`: adapt reporting fixtures and verify preservation of historical reports and faithful capture of actual judge outputs.
- `evaluations/compare_rag_retrieval.py`: reproducible controlled retrieval comparison with the same six captured tool queries and the same cached query vectors against both indexes. No reference answers are used for retrieval, filtering, or ranking.
- `tests/test_rag_chunker_quality.py`: six offline content-preservation and boundary regressions; registered in `scripts/run_isolated_regressions.py`. Its standalone runner uses stdout so PowerShell does not render successful unittest progress as an error.
- No dependency changes. No changes to the retriever, embedding implementation, agent prompts, routing, MCP definitions, SQLite implementation, authentication, sessions, or RBAC. Protected source hashes were checked against the before manifest.

## Before-and-after RAGAS comparison

These are the actual report values; differences are subtraction of reported averages, not independently calculated metric scores. The first complete after-change run is retained without selecting a more favorable rerun.

| Metric | Baseline | Improved | Difference |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.8333 | 0.8333 | +0.0000 |
| Context Precision | 0.7083 | 1.0000 | +0.2917 |
| Context Recall | 1.0000 | 1.0000 | +0.0000 |

The fresh unchanged-pipeline control is an additional fair comparison:

| Metric | Fresh control | Improved | Difference |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.8333 | 0.8333 | +0.0000 |
| Context Precision | 0.7639 | 1.0000 | +0.2361 |
| Context Recall | 1.0000 | 1.0000 | +0.0000 |

### Individual case scores

Triples are Faithfulness / Context Precision / Context Recall, displayed to four decimals. Raw values remain in the reports.

| Case | Historical baseline | Fresh control | Improved |
| --- | --- | --- | --- |
| Monthly deadline | 1.0000 / 0.5000 / 1.0000 | 1.0000 / 0.5000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Remote work | 0.5000 / 0.5000 / 1.0000 | 1.0000 / 0.5833 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Leave entitlements | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Late arrival | 1.0000 / 0.2500 / 1.0000 | 0.5000 / 0.5000 / 1.0000 | 0.5000 / 1.0000 / 1.0000 |
| Report revision | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Leave approval | 0.5000 / 1.0000 / 1.0000 | 0.5000 / 1.0000 / 1.0000 | 0.5000 / 1.0000 / 1.0000 |

### Generated answers before and after

All answers below were generated by the real Policy Agent. Source citations are retained. The reporting and approval exceptions were checked against the original handbook and references.

| Case | Fresh control answer | After-change answer |
| --- | --- | --- |
| Monthly deadline | Interns must submit their monthly progress report by the last working day of each month. If the final calendar date is a weekend or company holiday, the deadline is the preceding working day.<br><br>Source: company_handbook.pdf, page 3 | Interns must submit their monthly progress report by the last working day of each month. If the final calendar date is a weekend or company holiday, the deadline is the preceding working day.<br><br>Source: company_handbook.pdf, page 3 |
| Remote work | Employees and interns require written manager approval before working remotely, unless their role is covered by an approved remote-work arrangement.<br><br>Source: company_handbook.pdf, page 2 | Employees and interns require written manager approval before working remotely, unless their role is covered by an approved remote-work arrangement. Remote work is not automatic.<br><br>Source: company_handbook.pdf, page 2 |
| Leave entitlements | Permanent employees receive 20 annual leave days, 10 sick leave days, and 7 casual leave days per leave year unless a signed contract specifies otherwise.<br><br>Source: company_handbook.pdf, page 2 | Permanent employees receive 20 annual leave days, 10 sick leave days, and 7 casual leave days per leave year unless a signed contract specifies otherwise.<br><br>Source: company_handbook.pdf, page 2 |
| Late arrival | Arrival after 9:15 AM is treated as late unless approved by a manager or covered by an official flexible schedule.<br><br>Source: company_handbook.pdf, page 2 | Arrival after 9:15 AM is treated as late unless approved by a manager or covered by an official flexible schedule.<br><br>Source: company_handbook.pdf, page 2 |
| Report revision | If changes are requested, an intern must submit the revised monthly report within 1 working day of receiving feedback.<br><br>Source: company_handbook.pdf, page 3 | If changes are requested, an intern must submit the revised report within 1 working day of receiving feedback.<br><br>Source: company_handbook.pdf, page 3 |
| Leave approval | A leave request is not considered approved until an authorized manager or HR representative approves it.<br><br>Source: company_handbook.pdf, page 2 | A leave request is not considered approved until an authorized manager or HR representative approves it.<br><br>Source: company_handbook.pdf, page 2 |

Monthly deadline, leave entitlements, late arrival, and leave approval retain the same policy answer and citation. The revision answer retains the same one-working-day rule. The remote-work answer retains the approved-arrangement exception and additionally states that remote work is not automatic. No unsupported policy claim was identified by the after-run NLI verdicts; its only rejected statements are the citation declarations listed below.

### Controlled retrieval and context comparison

The query vectors are identical on both sides. Before scores reproduce the actual control retrieval to four decimals. Complete-policy ranks are evidence annotations from the retrieved passage text, not replacement RAGAS scores. Cosines are Qdrant similarities, not calibrated quality probabilities. All six retain top-K 5, minimum similarity 0.45, Gemini Embedding 2, and 768 dimensions.

| Case | Complete policy rank before -> after | Supporting page | Cosine before -> after | Context characters before -> after |
| --- | --- | --- | --- | --- |
| Monthly deadline | 2 -> 1 | 3 -> 3 | 0.7741 -> 0.8376 | 2989 -> 2757 |
| Remote work | 2 -> 1 | 2 -> 2 | 0.7856 -> 0.8168 | 4045 -> 2999 |
| Leave entitlements | 1 -> 1 | 2 -> 2 | 0.7080 -> 0.7536 | 4588 -> 3199 |
| Late arrival | 2 -> 1 | 2 -> 2 | 0.7180 -> 0.7766 | 4003 -> 2896 |
| Report revision | 1 -> 1 | 3 -> 3 | 0.7818 -> 0.7765 | 3310 -> 3066 |
| Leave approval | 1 -> 1 | 2 -> 2 | 0.7022 -> 0.7603 | 4523 -> 2373 |

All full before/after passage bodies and metadata are retained in `results/rag_retrieval_comparison.json`. The actual end-to-end before/after contexts, which can also vary with generated tool queries, are retained in the two diagnostic RAGAS reports and `results/rag_quality_comparison.json`.

The complete deadline, remote-approval, and attendance rules move from rank 2 to rank 1 under identical queries/vectors. The other three correct passages stay first. Context size decreases for every frozen query, while complete rules and exceptions remain available. This is demonstrated retrieval improvement rather than a top-K reduction, a reference injection, or a score override.

### Apparent regressions and Faithfulness limitation

Historical late-arrival Faithfulness falls from 1.0 to 0.5, but its fresh control was already 0.5 before any optimization. The policy answer before/after is identical and gets an accepted NLI verdict. The rejected statement is its correct citation, whose filename/page are absent from the body-only metric contexts. Conversely, historical remote-work Faithfulness rises from 0.5 to 1.0, but it was already 1.0 in the fresh control. Neither change establishes a generation repair or a policy-answer regression caused by the chunker.

After-change rejected claims (actual judge output, not overridden):

- **Late arrival**: The source of this rule is company_handbook.pdf on page 2. Judge reason: The context does not mention that the source of the rule is company_handbook.pdf on page 2. Tool metadata confirms `company_handbook.pdf`, page 2.
- **Leave approval**: The source of the information is company_handbook.pdf on page 2. Judge reason: The context does not state that the source of the information is company_handbook.pdf on page 2. Tool metadata confirms `company_handbook.pdf`, page 2.

Average Faithfulness is unchanged at 0.8333. All observed policy claims are accepted; source-citation declarations account for the two remaining 0.5 cases. Citation statements are inconsistently included by statement extraction. This evaluation limitation is documented rather than hidden by removing citations or adding reference text to contexts.

Previously perfect raw Context Precision values may decrease by about 5e-11 when two overlapping useful fragments become one complete passage. RAGAS 0.4.3 divides by the count of useful verdicts plus 1e-10. This denominator epsilon explains the tiny change; both values display as 1.0000. All raw scores are preserved. Average Context Precision genuinely increases and Recall does not decline.

## Executed tests and architecture checks

| Test | Status | Evidence |
| --- | --- | --- |
| Full fresh before-change RAGAS | PASSED | 6 completed, 0 failed; `ragas_eval_diagnostic_baseline.json` |
| Requested full after-change RAGAS command | PASSED | 6 completed, 0 failed, exit 0; `ragas_eval_improved.json` |
| Frozen-query retrieval comparison | PASSED | 6 queries, same query vectors and settings; complete supporting passages first afterward |
| `run_evaluations.ps1 -Mode offline` | PASSED | 9 regression scripts including all 6 new chunking tests, plus 13/13 additional security checks; exit 0 |
| `python -m unittest evaluations.test_ragas_eval -v` | PASSED | 4/4 tests, exit 0 |
| Existing `tests/test_rag_live.py` | PASSED | Live Gemini embedding -> Qdrant retrieval, 5 passages, exit 0 |
| `python -m pip check` | PASSED | No broken requirements |
| Integrity checks | PASSED | Original report bytes unchanged; dataset/PDF/router/agent/retriever/MCP-server/dependency hashes unchanged; actual after contexts match newly indexed chunks |

All evaluation commands used `.venv-eval`. No required check is FAILED, NOT RUN, or BLOCKED. The offline log confirms 18 agents, the Gemini semantic router, 39 MCP tools, database sanity, authentication/session-token behavior, RBAC, Gemini embedding configuration, and the PDF/Qdrant integration checks.

Logs: `results/rag_quality_offline_regression.log`. An initial offline pass also returned exit 0 but PowerShell rendered unittest stderr progress as a red NativeCommandError; that log is retained as `rag_quality_offline_initial_stderr.log`. The new test runner now writes stdout and the complete offline command passed again without that artifact. A manual early smoke command lacked PYTHONPATH; the existing wrapper environment and subsequent smoke/live checks passed. The evaluator unit run still emits an upstream RAGAS analytics ResourceWarning for its UUID file; its four tests pass, and third-party packages were not patched.

## Remaining weaknesses and recommendations

1. **Citation judging:** the primary benchmark still gives body-only contexts to Faithfulness. Propose a separately versioned metadata-aware evaluation protocol, applied to both frozen before/after samples with actual source metadata. Do not remove legitimate citations or replace these historical/raw scores.
2. **Trailing irrelevant retrieval:** top-K remains five, so several unrelated sections or the contents page still appear after the supporting section. Context Precision here measures average precision of useful ranks; 1.0 does not mean five useful chunks. Evaluate any future adaptive context selection against a separate held-out set with multi-policy and exception questions before changing thresholds or top-K.
3. **Cross-page prose:** page boundaries remain explicit to preserve existing source/page metadata. The payroll sentence spanning pages 3-4 still spans separate passages; its continuation is now labeled with the correct section, but document-wide paragraph joining would need page-span metadata and dedicated coverage. This six-case benchmark does not test that behavior, so no universal chunking claim is made.
4. **Coverage and variance:** six cases and one before/after generation pass do not estimate broad quality or confidence intervals. Add separate held-out paraphrases, policy exceptions, cross-page policies, and remote-work-versus-leave distinctions; keep the original six unchanged. Repeated paired evaluations are needed before claiming a general Faithfulness improvement.

## Conclusion

The pipeline genuinely improves retrieval on the demonstrated weaknesses: complete policy sections replace cut-off mixed-topic fragments; three previously outranked answer passages become first under the same queries/vectors; all six contexts are smaller in that controlled comparison; and end-to-end Context Precision rises while Recall and answer correctness are preserved. No generation prompt change was justified, and no Faithfulness improvement is claimed. Authentication, routing, the 18-agent/39-tool architecture, SQLite, and Qdrant remain intact.

Machine-readable comparison: `results/rag_quality_comparison.json`. Final settings and integrity manifest: `results/rag_quality_improved_manifest.json`. Backups include all modified pre-existing files and the entire original vector index in `.evaluation_runtime/rag_quality_backups_20261103_203432/`.


## End-to-end release audit follow-up (2026-11-03)

The improved chunker, six RAG goldens, handbook and historical baseline/latest/
improved reports remain byte-for-byte unchanged. The release work does not alter
top-K, similarity threshold, vector model, ranking, contexts or golden references.
The original-company SQLite file is also unchanged; all mutation tests use copies.

A paced full run before the final shared session-context provider was added
completed 6/6 cases, zero errors. Its real async evaluator remains
`ragas.llms.litellm_llm.LiteLLMStructuredLLM`, `is_async=True`.
The report is `results/ragas_eval_release_pre_context.json`.

| Measurement | Faithfulness | Context Precision | Context Recall |
|---|---:|---:|---:|
| Historical improved chunking | 0.8333 | 1.0000 | 1.0000 |
| Release run before final shared-context change | 0.9167 | 1.0000 | 1.0000 |
| Final candidate rerun | BLOCKED | BLOCKED | BLOCKED |

| Case | Historical improved F/P/R | Pre-context release F/P/R |
|---|---|---|
| rag_intern_monthly_deadline | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| rag_remote_work_approval | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| rag_leave_entitlements | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| rag_late_arrival | 0.5000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| rag_report_revision | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| rag_leave_approval | 0.5000 / 1.0000 / 1.0000 | 0.5000 / 1.0000 / 1.0000 |

The late-arrival answer remains policy-grounded and cited to page 2. Its faithfulness
changed from 0.5 to 1.0 without a retrieval or policy-generation repair. This is
consistent with the previously demonstrated citation/judge-scope instability, not
proof of generation improvement. Leave approval still receives 0.5 in this run.
No reference text or source metadata was injected into the judge's passage bodies.

The final shared instruction provider supplies only authenticated identity and
current date to specialists. It addresses missing self-service tool context, not
policy facts. Policy executed with a grounded monthly-deadline answer in the
subsequent DeepEval run, but judging then hit the actual 500/day Gemini generation
limit. Full final-candidate RAGAS was actually invoked again and returned nonzero:
0 completed, six BLOCKED (one attempted; five not executed after confirmed daily
quota exhaustion). Its null scores are not successful measurements. See
`results/ragas_eval_final_candidate.json` and the release report.

The same-vector retrieval experiment was rerun offline after relocating its
historical index/vectors to `evaluations/provenance` so it is portable. Results are
`results/release_frozen_retrieval_comparison.json`; the original comparison report
is preserved. The source/page/text chunks and their rankings remain unchanged.

Remaining issues remain trailing irrelevant passages, body-only citation scoring,
and the page 3?4 payroll sentence boundary. There is no measured evidence here for
another global retrieval or chunking change. A full post-context model evaluation
must be rerun when Gemini quota is available before calling this candidate FINAL.


## 2026-11-04 security remediation follow-up

No further chunking, embeddings, top-K, threshold, handbook, golden-reference or
active-index change was justified or made. Credential/transport boundaries changed,
so historical quality scores are not presented as final candidate acceptance.
The actual final entry point confirms LiteLLMStructuredLLM, AsyncInstructor and
async=True; all six cases are BLOCKED with null final aggregate scores. The shared
provider deadline prevented additional HTTP generation requests. Full source,
dataset, database and index fingerprints accompany the report.

Historical comparisons remain: original0.8333/0.7083/1, improved0.8333/1/1,
pre-final-context release0.9167/1/1. The latter citation/judge variation is not proof
of a generation improvement. Leave-approval faithfulness0.5, body-only citation
scope, trailing unrelated chunks and cross-page payroll remain as documented above.
A separate reviewed citation-aware evaluation could assess attribution explicitly;
it must not silently add source labels to comparable passage bodies or rewrite
references. Cross-page chunk changes need a separate measured retrieval experiment
and isolated index, not a reset of company data. No new quality improvement is
claimed without a comparable live run.


## Intermediate master finalization run, before final data guards (HISTORICAL)

`results/ragas_eval_master_verified.json`: six completed, zero errors, zero blocked.
The actual LiteLLMStructuredLLM/AsyncInstructor async evaluator and all three
awaited metrics ran against real Policy Agent answers and retrieved contexts.
A preceding live failure exposed host/MCP database isolation selected too late;
that entry-point defect was fixed and fresh-process regression-tested before this run.

| Case | Faithfulness | Context Precision | Context Recall |
|---|---:|---:|---:|
| rag_intern_monthly_deadline | 1.0000 | 1.0000 | 1.0000 |
| rag_remote_work_approval | 1.0000 | 1.0000 | 1.0000 |
| rag_leave_entitlements | 1.0000 | 1.0000 | 1.0000 |
| rag_late_arrival | 1.0000 | 1.0000 | 1.0000 |
| rag_report_revision | 1.0000 | 1.0000 | 1.0000 |
| rag_leave_approval | 1.0000 | 1.0000 | 1.0000 |

| Metric | Original baseline | Historical improved | Current run |
|---|---:|---:|---:|
| Faithfulness |0.8333|0.8333|1.0000|
| Context Precision |0.7083|1.0000|1.0000|
| Context Recall |1.0000|1.0000|1.0000|

These observations do not establish a new retrieval or prompt optimization: no
chunking, embeddings, top-K, threshold, handbook, golden or metric prompts changed.
The previous pre-context release run scored 0.9167/1/1; shorter answers and stochastic
statement/judge decomposition can change Faithfulness. The current leave-approval
answer states the authorized-approval requirement in one sentence and scored 1.0;
its full answer, context and judge trace are retained. Missing pending wording is
not manually scored or reference-adjusted. Trailing passages, body-only citation
scope and cross-page payroll remain possible weaknesses beyond this six-case sample.
A real execution/isolation defect was fixed; broader quality improvement is not claimed.


### Why RAGAS 1.0 coexists with a DeepEval context failure

Current deadline RAGAS judge traces give context-usefulness verdicts `[1, 0, 0, 0, 0]`.
RAGAS 0.4.3 ContextPrecision uses average precision over relevant ranks
(`ContextPrecision._calculate_average_precision`), so a relevant first passage and
irrelevant trailing passages still yield approximately 1.0. It is not the fraction
of the five retrieved chunks that are relevant. No scoring implementation was changed.

The pre-final-data-guard DeepEval deadline case scored ContextualRelevancyMetric
0.1363636364, below the unchanged 0.65 threshold. Its judge cites unrelated training,
supervisor and workplace-conduct statements. Answer relevancy, expected-answer
correctness and faithfulness were all 1.0. Evidence is the actual metric reason,
contexts and per-case checkpoint/report in `results/deepeval_eval_master_verified*`.

Problem: relevant policy evidence is ranked first, but the assembled context is
heavily diluted. Root cause: retrieving up to five threshold-passing chunks includes
trailing unrelated material and some multi-policy content inside chunks; this is
context efficiency/relevance, not demonstrated answer hallucination or absent recall.
A safe next experiment should compare question-focused context assembly against
these fixed six cases plus separately added cross-page/exception coverage before
altering retrieval behavior. No global top-K/threshold/chunking change was made to
force this test to pass. The quality failure remains visible in release acceptance.


## Final frozen-code RAGAS acceptance (2026-11-04)

`results/ragas_eval_master_final.json`: **6/6 completed, zero errors, zero blocked.**
Faithfulness **0.8889**, Context Precision **1.0000**, Context Recall **1.0000**.
The intermediate 1/1/1 run above is historical and is not the final score.

| Case | Faithfulness | Context Precision | Context Recall |
|---|---:|---:|---:|
| rag_intern_monthly_deadline | 1.0000 | 1.0000 | 1.0000 |
| rag_remote_work_approval | 1.0000 | 1.0000 | 1.0000 |
| rag_leave_entitlements | 1.0000 | 1.0000 | 1.0000 |
| rag_late_arrival | 0.3333 | 1.0000 | 1.0000 |
| rag_report_revision | 1.0000 | 1.0000 | 1.0000 |
| rag_leave_approval | 1.0000 | 1.0000 | 1.0000 |

Late-arrival analysis: the generated answer contains both manager-approval and
flexible-schedule exceptions in the same grounded sentence. The RAGAS statement
generator decomposed it into three statements, two mentioning only one exception.
Its faithfulness judge then rejected those two derived statements for omitting
the other exception, producing 1/3. This is demonstrated by the retained raw
StatementGenerator/NLI trace, not a manually substituted score. The full original
answer and retrieved policy support both exceptions. No prompt, reference, threshold
or scoring logic was changed to avoid the penalty, and no score-seeking rerun was made.

Versus the original baseline, measured aggregate differences are +0.0556 faithfulness,
+0.2917 context precision and 0 recall. Versus the historical pre-context release
0.9167/1/1, final faithfulness is lower by 0.0278. These observations do not demonstrate
a new retrieval optimization: the actual code changes protect missing data and
correct evaluation isolation/provenance. The existing section-aware chunker, active
vectors, top-K, threshold, source handbook and all original golden datasets remain.
Further retrieval-quality work requires a separately measured context-assembly
experiment with cross-page/exception coverage, not an artificial metric pass.
