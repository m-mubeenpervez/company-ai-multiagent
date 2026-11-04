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
# Gemini API
# ---------------------------------------------------------

Write-Host ""
Write-Host "Checking Gemini generation, semantic-router, and embedding APIs..."
& $VenvPython verify_gemini.py
if ($LASTEXITCODE -ne 0) {
    throw "Gemini API verification failed. Check GEMINI_API_KEY and quota/access."
}

# ---------------------------------------------------------
# SQLite Database
# ---------------------------------------------------------

$DatabasePath = Join-Path $PSScriptRoot "company_system\database\company.db"

if (-not (Test-Path $DatabasePath)) {
    throw "Existing company database is required. Restore approved data; setup will not create/reset it."
}

Write-Host "Verifying existing Qdrant collection without ingestion..."
& $VenvPython -c "from company_system.rag.vector_store import get_client, COLLECTION, QDRANT_PATH; assert QDRANT_PATH.is_dir(), 'Existing Qdrant directory required'; c=get_client(); exists=c.collection_exists(COLLECTION); c.close(); assert exists, 'Existing policy collection required; setup does not ingest data.'"
if ($LASTEXITCODE -ne 0) { throw "Existing policy data is required; restore approved Qdrant data separately." }

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
