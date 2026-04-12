param(
    [int]$PgPort = 55432
)

$ErrorActionPreference = "SilentlyContinue"
$projectRoot = $PSScriptRoot
Set-Location $projectRoot

$pgCtl = Join-Path $projectRoot ".local-postgres\pgsql\pgsql\bin\pg_ctl.exe"
$pgData = Join-Path $projectRoot ".local-postgres\data"

Get-CimInstance Win32_Process |
    Where-Object {
        ($_.Name -ieq "python.exe" -or $_.Name -ieq "pythonw.exe") -and
        $_.CommandLine -match "uvicorn" -and
        $_.CommandLine -match "backend\.app:app"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Get-CimInstance Win32_Process |
    Where-Object {
        ($_.Name -ieq "node.exe" -or $_.Name -ieq "cmd.exe") -and
        $_.CommandLine -match "next" -and
        $_.CommandLine -match "dev"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

if (Test-Path $pgCtl) {
    & $pgCtl -D $pgData -m fast stop | Out-Null
}

Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -ieq "postgres.exe" -and
        $_.CommandLine -match "\\.local-postgres\\data"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Write-Output "Servicios detenidos: backend, frontend y PostgreSQL (si estaban activos)."
