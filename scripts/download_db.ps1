$remoteHost = "lean@178.128.29.29"
$remoteDb = "/home/lean/phytolean/db.sqlite3"
$remoteBak = "/tmp/db_backup.sqlite3"
$localPath = Join-Path $PSScriptRoot ".." "db.sqlite3"

# Use sqlite3 .backup for a safe, consistent copy
Write-Host "Creating safe backup on remote server..."
ssh $remoteHost "sqlite3 $remoteDb '.backup $remoteBak' && gzip -f $remoteBak"

Write-Host "Downloading db_backup.sqlite3.gz..."
scp "$remoteHost`:${remoteBak}.gz" "$localPath.gz"

# Move existing local db to a timestamped backup
if (Test-Path $localPath) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = "$localPath.$timestamp.bak"
    Write-Host "Moving existing local db to $backupPath"
    Move-Item -Path $localPath -Destination $backupPath
}

Write-Host "Decompressing..."
$gzFile = "$localPath.gz"
$bytes = [System.IO.File]::ReadAllBytes($gzFile)
$ms = New-Object System.IO.MemoryStream(,$bytes)
$gz = New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
$fs = [System.IO.File]::Create($localPath)
$gz.CopyTo($fs)
$fs.Close()
$gz.Close()
$ms.Close()
Remove-Item $gzFile

Write-Host "Done. Database saved to $localPath"
