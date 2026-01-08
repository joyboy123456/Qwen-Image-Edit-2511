# PowerShell script to deploy with UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location "f:\1\comfyui"

Write-Host "============================================================"
Write-Host "Deploying ComfyUI service to Modal..."
Write-Host "============================================================"

# Run modal deploy
python -m modal deploy backend/comfyui_modal.py 2>&1 | Out-String -Stream | ForEach-Object {
    # Replace Unicode characters with ASCII equivalents
    $_ -replace '\u2713', '[OK]' -replace '\u2705', '[OK]' -replace '\u274c', '[X]'
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Deployment command completed"
Write-Host "Check Modal web console at: https://modal.com/apps"
Write-Host "============================================================"

Read-Host "Press Enter to continue"
