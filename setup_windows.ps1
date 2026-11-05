$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================="
Write-Host " CompanyAI Gemini + MCP Setup"
Write-Host "======================================="
Write-Host ""

Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot

# ---------------------------------------------------------
# .env
# ---------------------------------------------------------

if (-not (Test-Path ".env")) {
    if (-not (Test-Path ".env.example")) {
        throw ".env.example file not found."
    }
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
    Write-Host ""
    Write-Host "IMPORTANT: Open .env, paste your Google AI Studio GEMINI_API_KEY,"
    Write-Host "then run setup_windows.ps1 again."
    throw "Gemini API key configuration is required before setup can continue."
}
else {
    Write-Host ".env already exists."
}

# ---------------------------------------------------------
# Virtual Environment
# ---------------------------------------------------------

if (-not (Test-Path ".venv")) {
    Write-Host ""
    Write-Host "Creating virtual environment..."
    py -3.14 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Python 3.14 is required. Install it with the Windows Python launcher." }
}

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python was not created."
}

# ---------------------------------------------------------
# Dependencies
# ---------------------------------------------------------

Write-Host ""
& $VenvPython -m pip --version
& $VenvPython -m pip install -r requirements-bootstrap.txt --default-timeout=120 --retries=3
if ($LASTEXITCODE -ne 0) { throw "Patched pip bootstrap installation failed." }

Write-Host "Installing Python dependencies..."
& $VenvPython -m pip install `
    -r requirements.txt `
    -c requirements-runtime-lock.txt `
    --default-timeout=120 `
    --retries=10
if ($LASTEXITCODE -ne 0) {
    throw "Python dependency installation failed."
}

Write-Host ""
Write-Host "Checking Python dependencies..."
& $VenvPython -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "Python dependency consistency check failed."
}

# ---------------------------------------------------------
# Local runtime data
# ---------------------------------------------------------

Write-Host ""
Write-Host "Resolving configured local data paths..."
& $VenvPython -c "from company_system.database.db import DB_PATH; from company_system.rag.vector_store import QDRANT_PATH; print('SQLite:', DB_PATH); print('Qdrant:', QDRANT_PATH)"
if ($LASTEXITCODE -ne 0) { throw "Configured data paths could not be resolved." }

Write-Host "Initializing the configured SQLite path if it is absent..."
& $VenvPython initialize_database.py --synthetic
if ($LASTEXITCODE -ne 0) { throw "Synthetic SQLite initialization failed." }

& $VenvPython -c "from company_system.database.db import get_connection; c=get_connection(); assert c.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'; assert not c.execute('PRAGMA foreign_key_check').fetchall(); assert c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='mcp_sessions'\").fetchone(); c.close()"
if ($LASTEXITCODE -ne 0) { throw "Configured SQLite verification failed." }

# ---------------------------------------------------------
# Gemini API and handbook ingestion
# ---------------------------------------------------------

Write-Host ""
Write-Host "Checking Gemini generation, semantic-router, and embedding APIs..."
& $VenvPython verify_gemini.py
if ($LASTEXITCODE -ne 0) {
    throw "Gemini API verification failed. Check GEMINI_API_KEY and quota/access."
}

Write-Host "Creating the configured handbook index if it is absent..."
& $VenvPython ingest_documents.py
if ($LASTEXITCODE -ne 0) { throw "Handbook ingestion failed." }

Write-Host "Verifying the configured Qdrant collection..."
& $VenvPython -c "from company_system.rag.vector_store import get_client, COLLECTION, QDRANT_PATH; assert QDRANT_PATH.is_dir(), 'Existing Qdrant directory required'; c=get_client(); exists=c.collection_exists(COLLECTION); c.close(); assert exists, 'Existing policy collection required; setup does not ingest data.'"
if ($LASTEXITCODE -ne 0) { throw "Configured policy index verification failed." }

# ---------------------------------------------------------
# Full Regression Suite
# ---------------------------------------------------------

Write-Host ""
Write-Host "Running full regression suite..."
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1
if ($LASTEXITCODE -ne 0) {
    throw "Regression suite failed."
}

# ---------------------------------------------------------
# Root Agent
# ---------------------------------------------------------

Write-Host ""
Write-Host "Checking root agent..."
& $VenvPython -c "from company_system.agent import root_agent; print('Root agent:', root_agent.name); print('Registered agents:', len(root_agent.sub_agents))"
if ($LASTEXITCODE -ne 0) { throw "Root agent import failed." }

Write-Host ""
Write-Host "======================================="
Write-Host " Setup completed successfully"
Write-Host "======================================="
Write-Host ""
Write-Host "Start development environment with:"
Write-Host ""
Write-Host "powershell -ExecutionPolicy Bypass -File .\start_project.ps1"
Write-Host ""
