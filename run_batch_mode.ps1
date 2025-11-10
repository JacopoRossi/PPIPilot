# PPIPilot - Batch Execution Mode Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PPIPilot - Batch Execution Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Streamlit interface..." -ForegroundColor Yellow
Write-Host ""

# Check if streamlit is installed
if (Get-Command streamlit -ErrorAction SilentlyContinue) {
    streamlit run interface_batch.py
} else {
    Write-Host "ERROR: Streamlit is not installed!" -ForegroundColor Red
    Write-Host "Please install it with: pip install streamlit" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
