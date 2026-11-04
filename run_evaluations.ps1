param(
    [ValidateSet("offline", "routing", "ragas", "deepeval", "security", "prompt-injection", "all")]
    [string]$Mode = "offline"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$EvalPython = Join-Path $PSScriptRoot ".venv-eval\Scripts\python.exe"
if (-not (Test-Path $EvalPython)) {
    throw "Evaluation environment not found. Run setup_evaluation.ps1 first."
}

$env:PYTHONPATH = $PSScriptRoot

function Invoke-EvalScript([string]$Script, [string[]]$Arguments = @()) {
    Write-Host ""
    Write-Host "RUN | $Script"
    & $EvalPython $Script @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Evaluation failed: $Script"
    }
}

switch ($Mode) {
    "offline" {
        Invoke-EvalScript ".\scripts\run_isolated_regressions.py"
        Invoke-EvalScript ".\security\run_security_regression.py"
    }
    "routing" {
        Invoke-EvalScript ".\evaluations\run_routing_eval.py"
    }
    "ragas" {
        Invoke-EvalScript ".\evaluations\run_ragas_eval.py"
    }
    "deepeval" {
        Invoke-EvalScript ".\evaluations\run_deepeval_eval.py"
    }
    "security" {
        Invoke-EvalScript ".\security\run_security_regression.py"
    }
    "prompt-injection" {
        Invoke-EvalScript ".\security\run_prompt_injection_eval.py"
    }
    "all" {
        Invoke-EvalScript ".\scripts\run_isolated_regressions.py"
        Invoke-EvalScript ".\security\run_security_regression.py"
        Invoke-EvalScript ".\evaluations\run_routing_eval.py"
        Invoke-EvalScript ".\evaluations\run_ragas_eval.py"
        Invoke-EvalScript ".\evaluations\run_deepeval_eval.py"
        Invoke-EvalScript ".\security\run_prompt_injection_eval.py"
    }
}

Write-Host ""
Write-Host "Requested CompanyAI evaluation mode completed."
