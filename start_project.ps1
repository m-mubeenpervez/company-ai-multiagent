param(
    [int]$Port = 8000,
    [switch]$Check
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$VenvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvActivate)) {
    throw "Virtual environment not found. Run setup_windows.ps1 first."
}

& $VenvActivate
$env:PYTHONPATH = $PSScriptRoot
# ADK currently pins an OpenTelemetry version with a tracestate parsing advisory.
# Exclude the vulnerable tracecontext propagator for this local launcher.
$env:OTEL_PROPAGATORS = "baggage"
$env:OTEL_SDK_DISABLED = "true"
$env:OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT = "false"

Write-Host ""
Write-Host "======================================="
Write-Host " CompanyAI Gemini + MCP Environment"
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
python -c "from company_system.config import GEMINI_LLM_MODEL, GEMINI_EMBED_MODEL; print('Gemini LLM:', GEMINI_LLM_MODEL); print('Gemini embeddings:', GEMINI_EMBED_MODEL)"
Write-Host ""
Write-Host "Environment ready. No LM Studio server is required."
if ($LASTEXITCODE -ne 0) { throw "CompanyAI configuration check failed." }
if ($Check) {
    & (Join-Path $PSScriptRoot ".venv\Scripts\python.exe") -c "from company_system.agent import root_agent; print('Root agent:', root_agent.name); print('Agents:', len(root_agent.sub_agents))"
    if ($LASTEXITCODE -ne 0) { throw "CompanyAI root-agent check failed." }
}
else {
    & (Join-Path $PSScriptRoot ".venv\Scripts\python.exe") -m company_system.local_web --port $Port
    if ($LASTEXITCODE -ne 0) { throw "CompanyAI ADK web exited with an error." }
}
Write-Host ""
