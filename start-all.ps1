param(
    [int]$PgPort = 55432,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
Set-Location $projectRoot

function Test-HttpOk {
    param(
        [Parameter(Mandatory = $true)][string]$Url
    )

    try {
        $null = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
        return $true
    }
    catch {
        return $false
    }
}

$pgBase = Join-Path $projectRoot ".local-postgres"
$pgBin = Join-Path $pgBase "pgsql\pgsql\bin"
$pgCtl = Join-Path $pgBin "pg_ctl.exe"
$pgReady = Join-Path $pgBin "pg_isready.exe"
$pgData = Join-Path $pgBase "data"
$pgLog = Join-Path $pgBase "postgres.log"

if (-not (Test-Path $pgCtl)) {
    throw "No se encontro PostgreSQL portable en .local-postgres."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "No se encontro .venv\\Scripts\\python.exe."
}

$npmCmd = "C:\Program Files\nodejs\npm.cmd"
if (-not (Test-Path $npmCmd)) {
    throw "No se encontro npm en C:\Program Files\nodejs\npm.cmd."
}

if (-not (Test-Path ".env")) {
    @(
        "DATABASE_URL=postgresql://menuuser:password@127.0.0.1:$PgPort/menuai_db"
        "OPENAI_API_KEY="
        "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:$BackendPort"
    ) | Set-Content -Path ".env" -Encoding ASCII
}

& $pgReady -h 127.0.0.1 -p $PgPort -U postgres *> $null
if ($LASTEXITCODE -ne 0) {
    Start-Process -FilePath $pgCtl `
        -ArgumentList "-D", "$pgData", "-l", "$pgLog", "-o", "-p $PgPort -h 127.0.0.1", "start" `
        -WindowStyle Minimized | Out-Null
}

Start-Process -FilePath ".\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $projectRoot `
    -WindowStyle Minimized | Out-Null

if (-not (Test-Path "frontend\node_modules")) {
    $env:Path = "C:\Program Files\nodejs;$env:Path"
    & $npmCmd --prefix frontend install | Out-Null
}

$env:Path = "C:\Program Files\nodejs;$env:Path"
Start-Process -FilePath $npmCmd `
    -ArgumentList "--prefix", "frontend", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", "$FrontendPort" `
    -WorkingDirectory $projectRoot `
    -WindowStyle Minimized | Out-Null

Write-Output "POSTGRES: http://127.0.0.1:$PgPort"
Write-Output "BACKEND_DOCS: http://127.0.0.1:$BackendPort/docs"
Write-Output "FRONTEND: http://127.0.0.1:$FrontendPort"
Write-Output "STARTUP_DONE: true"
Write-Output "NOTA: si necesitas recrear datos, ejecuta: .\\.venv\\Scripts\\python.exe -m backend.seed"
