# CPR Assistant Environment Activation Script
Write-Host "🏥 Activating CPR Assistant Python 3.9 Environment..." -ForegroundColor Green
& ".\cpr_env_39\Scripts\Activate.ps1"
Write-Host "✅ Environment activated! You can now run:" -ForegroundColor Green
Write-Host "   python simple_cpr_assistant.py" -ForegroundColor Yellow
Write-Host "   python enhanced_cpr_assistant.py" -ForegroundColor Yellow
Write-Host "   python cpr_assistant.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To deactivate, type: deactivate" -ForegroundColor Cyan
