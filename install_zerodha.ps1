# Quick Installation Script for Zerodha Integration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NIFTY 50 Trading Bot - Installation  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Install kiteconnect
Write-Host "Installing Zerodha Kite Connect library..." -ForegroundColor Yellow
pip install kiteconnect

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
}
else {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please edit it with your Zerodha credentials." -ForegroundColor Green
    Write-Host ""
    Write-Host "Edit .env and add:" -ForegroundColor Cyan
    Write-Host "  ZERODHA_API_KEY=your_key" -ForegroundColor White
    Write-Host "  ZERODHA_API_SECRET=your_secret" -ForegroundColor White
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Get Zerodha API credentials:" -ForegroundColor Yellow
Write-Host "   https://developers.kite.trade/" -ForegroundColor White
Write-Host ""
Write-Host "2. Edit .env file with your credentials:" -ForegroundColor Yellow
Write-Host "   notepad .env" -ForegroundColor White
Write-Host ""
Write-Host "3. Generate access token:" -ForegroundColor Yellow
Write-Host "   python zerodha_login.py" -ForegroundColor White
Write-Host ""
Write-Host "4. Test in paper mode:" -ForegroundColor Yellow
Write-Host "   python main.py --mode paper" -ForegroundColor White
Write-Host ""
Write-Host "5. View dashboard:" -ForegroundColor Yellow
Write-Host "   streamlit run dashboard/app.py" -ForegroundColor White
Write-Host ""
Write-Host "📖 Read ZERODHA_SETUP.md for complete guide!" -ForegroundColor Cyan
Write-Host ""
