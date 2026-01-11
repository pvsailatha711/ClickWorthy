# ClickWorthy - One-Click Startup Script
# This script starts all services in the background

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting ClickWorthy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker not found. Please install Docker Desktop." -ForegroundColor Red
    pause
    exit 1
}

# Check Python
try {
    python --version | Out-Null
    Write-Host "[OK] Python found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+." -ForegroundColor Red
    pause
    exit 1
}

# Check Java
try {
    java -version 2>&1 | Out-Null
    Write-Host "[OK] Java found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Java not found. Please install Java 17+." -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# Setup Python venv if needed
$venvPath = Join-Path $scriptDir "clickworthy-nlp-analyzer\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Setting up Python environment (first time only)..." -ForegroundColor Yellow
    Set-Location (Join-Path $scriptDir "clickworthy-nlp-analyzer")
    python -m venv venv
    & "venv\Scripts\activate.ps1"
    pip install -r requirements.txt
    Set-Location $scriptDir
    Write-Host "[OK] Python environment ready" -ForegroundColor Green
    Write-Host ""
}

# Start Kafka
Write-Host "[1/3] Starting Kafka..." -ForegroundColor Cyan
Set-Location (Join-Path $scriptDir "clickWorthy-kafkaSetup")
Start-Process powershell -ArgumentList "-NoExit", "-Command", "docker-compose up" -WindowStyle Normal
Set-Location $scriptDir
Write-Host "Waiting 30 seconds for Kafka to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Start Python Analyzer
Write-Host "[2/3] Starting Python NLP Analyzer..." -ForegroundColor Cyan
Set-Location (Join-Path $scriptDir "clickworthy-nlp-analyzer")
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& venv\Scripts\activate.ps1; python kafka_consumer.py" -WindowStyle Normal
Set-Location $scriptDir
Start-Sleep -Seconds 5

# Start Spring Boot Backend
Write-Host "[3/3] Starting Spring Boot Backend..." -ForegroundColor Cyan
Set-Location (Join-Path $scriptDir "clickworthy-backend")
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\mvnw.cmd spring-boot:run" -WindowStyle Normal
Set-Location $scriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ClickWorthy Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Three windows opened:" -ForegroundColor White
Write-Host "  1. Kafka (Docker)" -ForegroundColor White
Write-Host "  2. Python Analyzer" -ForegroundColor White
Write-Host "  3. Spring Boot Backend" -ForegroundColor White
Write-Host ""
Write-Host "Wait for 'Started ClickworthyBackendApplication' in window 3" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Install browser extension:" -ForegroundColor White
Write-Host "     - Go to chrome://extensions/" -ForegroundColor Gray
Write-Host "     - Enable 'Developer mode'" -ForegroundColor Gray
Write-Host "     - Click 'Load unpacked'" -ForegroundColor Gray
Write-Host "     - Select: clickworthy-extension folder" -ForegroundColor Gray
Write-Host "  2. Visit YouTube and hover over videos!" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close all 3 windows or run stop.ps1" -ForegroundColor Yellow
Write-Host ""
pause
