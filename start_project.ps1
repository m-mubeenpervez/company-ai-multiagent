$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$VenvActivate = Join-Path `
    $PSScriptRoot `
    ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $VenvActivate)) {
    throw "Virtual environment not found. Run setup_windows.ps1 first."
}

& $VenvActivate

$env:PYTHONPATH = $PSScriptRoot

Write-Host ""
Write-Host "======================================="
Write-Host " CompanyAI Development Environment"
Write-Host "======================================="
Write-Host ""
Write-Host "Project:"
Write-Host "  $PSScriptRoot"
Write-Host ""
Write-Host "PYTHONPATH:"
Write-Host "  $env:PYTHONPATH"
Write-Host ""
Write-Host "Python:"
python --version
Write-Host ""
Write-Host "Environment ready."
Write-Host ""
Write-Host "Make sure LM Studio server is running."
Write-Host ""