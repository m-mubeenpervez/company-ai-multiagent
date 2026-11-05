# CompanyAI setup

Use Windows PowerShell and Python 3.14 for the application runtime. The separate evaluation environment uses Python 3.12. Work from an approved source/staging copy;
D:\CompanyAI remains unauthorized. Preserve private `.env`, company SQLite and
Qdrant data. Setup does not restore missing company data automatically.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-bootstrap.txt
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-runtime-lock.txt
.\.venv\Scripts\python.exe -m pip check
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Check
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
```

The bootstrap pins pip 26.3. Install dependencies only into the new environment;
do not copy another virtual environment. Configure `.env` privately only if absent,
using `.env.example`; never overwrite an existing configuration. Restore approved
SQLite/Qdrant/handbook data separately if missing. Do not reset or re-ingest it.
Open http://127.0.0.1:8000 and use the separate sign-in form. Stock `adk web` is not
the supported authenticated launcher. Stop with Ctrl+C.

For evaluations, `setup_evaluation.ps1` creates `.venv-eval`, installs bootstrap,
runtime plus evaluation requirements with `requirements-evaluation-lock.txt`, runs
pip check and the offline security suite. `setup_windows.ps1` additionally performs
live Gemini verification (honoring the quota circuit), validates existing data and
runs regressions. Its full completion requires current provider access.

Fresh staged Python 3.12 installation evidence is retained in
`evaluations/results/remediation_stage_install_app.log` and
`remediation_stage_install_eval.log`. Dependency declarations are unchanged since
those installs; vulnerability findings are reported separately and remain unresolved.
See [release report](../FINAL_RELEASE_REPORT.md) for current executed test scopes.
