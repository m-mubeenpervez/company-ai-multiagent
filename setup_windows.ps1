$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================="
Write-Host " CompanyAI Multi-Agent Setup"
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

    python -m venv .venv
}


$VenvPython = Join-Path `
    $PSScriptRoot `
    ".venv\Scripts\python.exe"

$VenvPip = Join-Path `
    $PSScriptRoot `
    ".venv\Scripts\pip.exe"


if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python was not created."
}


# ---------------------------------------------------------
# Dependencies
# ---------------------------------------------------------

Write-Host ""
Write-Host "Updating pip..."

& $VenvPython -m pip install --upgrade pip


Write-Host ""
Write-Host "Installing Python dependencies..."

& $VenvPython -m pip install `
    -r requirements.txt `
    --default-timeout=120 `
    --retries=10


Write-Host ""
Write-Host "Checking Python dependencies..."

& $VenvPython -m pip check


# ---------------------------------------------------------
# LM Studio
# ---------------------------------------------------------

Write-Host ""
Write-Host "Checking LM Studio..."

& $VenvPython verify_lmstudio.py


# ---------------------------------------------------------
# SQLite Database
# ---------------------------------------------------------

$DatabasePath = Join-Path `
    $PSScriptRoot `
    "company_system\database\company.db"


if (-not (Test-Path $DatabasePath)) {

    Write-Host ""
    Write-Host "Initializing SQLite company database..."

    & $VenvPython initialize_database.py --reset
}
else {

    Write-Host ""
    Write-Host "SQLite database already exists."
    Write-Host "Skipping database reset to protect existing data."
}


# ---------------------------------------------------------
# RAG / Qdrant
# ---------------------------------------------------------

Write-Host ""
Write-Host "Building company policy vector database..."

& $VenvPython ingest_documents.py --reset


# ---------------------------------------------------------
# Smoke Tests
# ---------------------------------------------------------

Write-Host ""
Write-Host "Running smoke tests..."

& $VenvPython tests\test_database.py
& $VenvPython tests\test_permissions.py
& $VenvPython tests\test_rag.py


# ---------------------------------------------------------
# Root Agent
# ---------------------------------------------------------

Write-Host ""
Write-Host "Checking root agent..."

& $VenvPython -c `
    "from company_system.agent import root_agent; print('Root agent:', root_agent.name)"


Write-Host ""
Write-Host "======================================="
Write-Host " Setup completed successfully"
Write-Host "======================================="
Write-Host ""
Write-Host "Start development environment with:"
Write-Host ""
Write-Host "powershell -ExecutionPolicy Bypass -File .\start_project.ps1"
Write-Host ""
Write-Host "Then run:"
Write-Host ""
Write-Host "adk web"
Write-Host ""