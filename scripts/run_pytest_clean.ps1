param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("bulgaria-property-alert-tests-" + [guid]::NewGuid().ToString("N"))
$tempDbPath = Join-Path $tempRoot "test.db"
$tempPreviewDir = Join-Path $tempRoot "email-previews"

New-Item -ItemType Directory -Path $tempPreviewDir -Force | Out-Null

$previousDatabaseUrl = $env:DATABASE_URL
$previousEmailPreviewDir = $env:EMAIL_PREVIEW_DIR
$previousSchedulerEnabled = $env:SCHEDULER_ENABLED
$previousImotLiveEnabled = $env:IMOT_LIVE_ENABLED
$previousSmtpPassword = $env:SMTP_PASSWORD

$env:DATABASE_URL = "sqlite:///$($tempDbPath -replace '\\', '/')"
$env:EMAIL_PREVIEW_DIR = $tempPreviewDir
$env:SCHEDULER_ENABLED = "false"
$env:IMOT_LIVE_ENABLED = "false"
$env:SMTP_PASSWORD = ""

Push-Location $repoRoot
try {
    & ".\.venv\Scripts\python" -m pytest @PytestArgs
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location

    if ($null -ne $previousDatabaseUrl) { $env:DATABASE_URL = $previousDatabaseUrl } else { Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue }
    if ($null -ne $previousEmailPreviewDir) { $env:EMAIL_PREVIEW_DIR = $previousEmailPreviewDir } else { Remove-Item Env:EMAIL_PREVIEW_DIR -ErrorAction SilentlyContinue }
    if ($null -ne $previousSchedulerEnabled) { $env:SCHEDULER_ENABLED = $previousSchedulerEnabled } else { Remove-Item Env:SCHEDULER_ENABLED -ErrorAction SilentlyContinue }
    if ($null -ne $previousImotLiveEnabled) { $env:IMOT_LIVE_ENABLED = $previousImotLiveEnabled } else { Remove-Item Env:IMOT_LIVE_ENABLED -ErrorAction SilentlyContinue }
    if ($null -ne $previousSmtpPassword) { $env:SMTP_PASSWORD = $previousSmtpPassword } else { Remove-Item Env:SMTP_PASSWORD -ErrorAction SilentlyContinue }

    Remove-Item $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

exit $exitCode
