$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "======================================="
Write-Host " CompanyAI Evaluation Environment Setup"
Write-Host "======================================="
Write-Host ""

if (-not (Test-Path ".env")) {
    throw ".env not found. Copy .env.example to .env and configure GEMINI_API_KEY first."
}

if (-not (Test-Path ".venv-eval")) {
    Write-Host "Creating isolated evaluation virtual environment..."
    py -3.12 -m venv .venv-eval
    if ($LASTEXITCODE -ne 0) { throw "Python 3.12 is required for the evaluation environment." }
}

$EvalPython = Join-Path $PSScriptRoot ".venv-eval\Scripts\python.exe"

& $EvalPython -m pip --version
& $EvalPython -m pip install -r requirements-bootstrap.txt --default-timeout=120 --retries=3
if ($LASTEXITCODE -ne 0) { throw "Patched pip bootstrap installation failed." }

Write-Host "Installing CompanyAI + evaluation dependencies..."
& $EvalPython -m pip install -r requirements.txt -r requirements-evaluation.txt -c requirements-evaluation-lock.txt --default-timeout=120 --retries=10
if ($LASTEXITCODE -ne 0) {
    throw "Evaluation dependency installation failed."
}

Write-Host "Checking dependency consistency..."
& $EvalPython -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "Evaluation dependency check failed."
}

Write-Host ""
Write-Host "Running offline security regression..."
$env:PYTHONPATH = $PSScriptRoot
& $EvalPython .\security\run_security_regression.py
if ($LASTEXITCODE -ne 0) {
    throw "Offline security regression failed."
}

Write-Host ""
Write-Host "======================================="
Write-Host " Evaluation environment is ready"
Write-Host "======================================="
Write-Host ""
Write-Host "Run: powershell -ExecutionPolicy Bypass -File .\run_evaluations.ps1 -Mode offline"
Write-Host "Live evals: use -Mode routing, ragas, deepeval, prompt-injection, or all"
Write-Host ""
