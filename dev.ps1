# Development startup script for Windows - builds frontend and starts server on single port
# Run with: .\dev.ps1

$ErrorActionPreference = "Stop"

# Get project directory
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_DIR

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Meeting Assistant - Development Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if config.yaml exists
if (-not (Test-Path "config.yaml")) {
    Write-Host "Error: config.yaml not found!" -ForegroundColor Red
    Write-Host "Please copy config.example.yaml to config.yaml and fill in your credentials."
    exit 1
}

# Check if frontend dependencies are installed
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Build frontend
Write-Host ""
Write-Host "Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run build
Set-Location ..
Write-Host "Frontend built successfully!" -ForegroundColor Green

# Start server
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting server on port 5173..." -ForegroundColor Green
Write-Host ""
Write-Host "  Open: http://localhost:5173"
Write-Host "  API Docs: http://localhost:5173/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop"
Write-Host "==========================================" -ForegroundColor Cyan

uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 5173
