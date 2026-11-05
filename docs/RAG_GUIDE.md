# CompanyAI RAG guide

The PDF source is `company_system/documents/company_handbook.pdf`. pypdf extracts
page text. `rag/chunker.py` preserves numbered sections on each page, normalizes
visual line wrapping, and splits oversized sections at complete sentences with
whole-sentence overlap. Default budgets remain 1000/150 characters; a single
overlong sentence is preserved rather than cut. Source/page metadata is retained.
The current handbook produces 17 chunks from six pages.

Gemini embeds each chunk separately using a Content object and validates the
number and dimension of returned vectors. Qdrant stores those vectors and payloads.
Policy search embeds the actual user/tool query and returns up to five passages
with cosine score at least 0.45 by default. No references are injected into search.

```powershell
# Preserves an existing collection; ingests only when absent.
.\.venv\Scripts\python.exe ingest_documents.py
```

Rebuilding an existing collection requires explicit `--reset` after backup and
stopping other Qdrant users. It replaces the collection; this is not incremental
multi-document synchronization. Never use it to make tests pass on active data.

The policy specialist must search for each policy question, treat passages as
untrusted evidence, preserve exceptions, and cite the returned filename/page.
Absent support should produce an explicit lack-of-evidence response. Tools and
MCP authorization remain independent of instructions embedded in documents.

Historical improved RAGAS results were 0.8333 faithfulness, 1.0000 context
precision, 1.0000 recall. These are measurements, not promises. RAGAS average
precision can be 1.0 while irrelevant passages trail the supporting first result.
Body-only faithfulness judges may also reject correct source/page attribution
because metadata is outside the passage bodies. Payroll text spanning pages 3–4
remains a known boundary limitation; it was not changed speculatively.

The release does not change section-aware chunking, top-K, threshold, embeddings,
or golden answers to inflate scores. See
[`evaluations/RAG_QUALITY_ANALYSIS.md`](../evaluations/RAG_QUALITY_ANALYSIS.md)
for the controlled retrieval experiment, individual cases and release measurements.
