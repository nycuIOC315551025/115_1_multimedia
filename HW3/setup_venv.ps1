$ErrorActionPreference = 'Stop'
$venvPath = Join-Path $PSScriptRoot '.venv'
$venvPython = Join-Path $venvPath 'Scripts\python.exe'
$requirements = Join-Path $PSScriptRoot 'requirements.txt'

if (-not (Test-Path -LiteralPath $venvPython)) {
    if (Test-Path -LiteralPath $venvPath) {
        throw 'The .venv directory exists but has no Scripts\python.exe. Repair or remove it before continuing.'
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv $venvPath
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv $venvPath
    } else {
        throw 'Python 3 was not found. Install Python 3 and make py or python available on PATH.'
    }
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create the virtual environment.' }
} else {
    Write-Host 'Using the existing .venv.'
}

& $venvPython -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) { throw 'Failed to install requirements.' }
Write-Host 'Environment ready. Run: .\.venv\Scripts\python.exe main_algorithm.py'
