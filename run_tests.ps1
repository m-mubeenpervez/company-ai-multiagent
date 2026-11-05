param(
    [switch]$Live
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment not found. Run setup_windows.ps1 first."
}

$env:PYTHONPATH = $PSScriptRoot

Write-Host ""
Write-Host "======================================="
Write-Host " CompanyAI Isolated Regression Suite"
Write-Host "======================================="
Write-Host ""
Write-Host "Tests run against copied SQLite and Qdrant data."
Write-Host "The active project data will not be modified."
Write-Host "Stop 'adk web' first so Qdrant is not being written during the copy."
Write-Host ""

if ($Live) {
    & $VenvPython .\scripts\run_isolated_regressions.py --live
}
else {
    & $VenvPython .\scripts\run_isolated_regressions.py
}

if ($LASTEXITCODE -ne 0) {
    throw "CompanyAI regression suite failed."
}

Write-Host ""
Write-Host "Regression suite completed successfully."
