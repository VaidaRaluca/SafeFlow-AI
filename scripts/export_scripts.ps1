$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$dumpsDir = Join-Path $repoRoot "shared\dumps"

$versioned = Join-Path $dumpsDir "safeflow_db_full_$timestamp.sql"
$latest = Join-Path $dumpsDir "safeflow_db_full_latest.sql"

New-Item -ItemType Directory -Force -Path $dumpsDir | Out-Null

docker exec safeflow-db-dev pg_dump -U postgres -d safeflow_db --no-owner --no-privileges |
  Out-File -FilePath $versioned -Encoding utf8

Copy-Item $versioned $latest -Force

Write-Host "Dump exported:"
Write-Host $versioned
Write-Host $latest