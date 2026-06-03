# scripts/check.ps1
# Equivalente Windows do scripts/check.sh
# Espelha o CI: ruff check -> ruff format --check -> mypy --strict -> pytest
# Uso: pwsh ./scripts/check.ps1

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Yellow
}

function Ok($msg) {
    Write-Host "OK $msg" -ForegroundColor Green
}

function Fail($msg) {
    Write-Host "FAIL $msg" -ForegroundColor Red
    exit 1
}

Step "1/4 ruff check ."
ruff check .
if ($LASTEXITCODE -ne 0) { Fail "ruff check falhou" }
Ok "ruff check"

Step "2/4 ruff format --check ."
ruff format --check .
if ($LASTEXITCODE -ne 0) { Fail "ruff format --check falhou (rode: ruff format .)" }
Ok "ruff format --check"

Step "3/4 mypy --strict src"
mypy --strict src
if ($LASTEXITCODE -ne 0) { Fail "mypy --strict falhou" }
Ok "mypy --strict"

Step "4/4 pytest"
pytest
if ($LASTEXITCODE -ne 0) { Fail "pytest falhou" }
Ok "pytest"

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host " Todos os checks passaram" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
