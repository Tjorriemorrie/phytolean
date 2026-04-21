param(
    [string]$User = "lean",
    [string]$RemoteHost = "178.128.29.29",
    [string]$RemoteDir = "~/phytolean",
    [string]$LocalPath = ".\db.sqlite3"
)

$ErrorActionPreference = "Stop"

$localGz    = "$LocalPath.gz"
$localBck   = "$LocalPath.bck"
$remoteFile = "db.sqlite3"
$remoteGz   = "db.sqlite3.gz"

# 1) Compress remotely. Use pv for progress if available, otherwise plain gzip.
#    set -o pipefail so a mid-pipeline failure (e.g. missing pv) actually errors
#    instead of silently producing an empty .gz.
Write-Host "Compressing remote DB..."
$remoteCmd = "set -o pipefail; cd $RemoteDir && if command -v pv >/dev/null 2>&1; then pv $remoteFile | gzip > $remoteGz; else gzip -c $remoteFile > $remoteGz; fi && ls -l $remoteGz"
ssh "$User@$RemoteHost" "bash -c '$remoteCmd'"
if ($LASTEXITCODE -ne 0) { throw "Remote compression failed." }

# 2) Download compressed file with scp (shows progress locally)
Write-Host "Downloading compressed DB (progress shown locally)..."
scp "${User}@${RemoteHost}:$RemoteDir/$remoteGz" $localGz
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $localGz)) { throw "Download failed." }

$gzSize = (Get-Item $localGz).Length
Write-Host "Downloaded $localGz ($gzSize bytes)"
if ($gzSize -lt 1024) { throw "Downloaded gz is suspiciously small ($gzSize bytes) — remote compression likely failed." }

# 3) Backup local DB
if (Test-Path $LocalPath) {
    Write-Host "Backing up local DB to $localBck..."
    Copy-Item $LocalPath $localBck -Force
}

# 4) Decompress. 7z 'e' on db.sqlite3.gz outputs db.sqlite3 into the output dir,
#    overwriting the existing local file. Quote the -o switch so PowerShell
#    passes it through intact (bare '-o.' is parsed as too-short).
Write-Host "Decompressing..."
$sevenZip = Get-Command 7z -ErrorAction SilentlyContinue
if (-not $sevenZip) { throw "7-Zip not installed. Install it or switch to gzip -d." }

$outDir = (Resolve-Path ".").Path
& 7z e $localGz "-o$outDir" -y | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Decompression failed via 7z" }

if (-not (Test-Path $LocalPath)) { throw "Expected $LocalPath after decompression, not found." }

# 5) Clean up
Write-Host "Cleaning up..."
Remove-Item $localGz -Force
ssh "$User@$RemoteHost" "rm -f $RemoteDir/$remoteGz"

Write-Host "Sync complete."
