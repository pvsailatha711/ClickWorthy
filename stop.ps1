# ClickWorthy - Stop Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Stopping ClickWorthy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Stop Kafka
Write-Host "Stopping Kafka..." -ForegroundColor Yellow
Set-Location (Join-Path $scriptDir "clickWorthy-kafkaSetup")
docker-compose down
Set-Location $scriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Kafka Stopped" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Please close the other windows:" -ForegroundColor Yellow
Write-Host "  - Python Analyzer (Ctrl+C or close window)" -ForegroundColor White
Write-Host "  - Spring Boot (Ctrl+C or close window)" -ForegroundColor White
Write-Host ""
pause
