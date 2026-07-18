# Windows PowerShell Environment Setup Script
Write-Host "Initializing Drawffyfish Virtual Environment Deployment Script..." -ForegroundColor Cyan

# Create localized python deployment sandboxes
if (-not (Test-Path ".\.venv")) {
    python -m venv .venv
    Write-Host "Created isolated virtual environment inside .\.venv" -ForegroundColor Green
}

# Target and activate project execution layers
& ".\.venv\Scripts\Activate.ps1"

# Elevate asset installation channels
Write-Host "Upgrading foundational package management channels..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install project dependency frameworks
if (Test-Path ".\requirements.txt") {
    Write-Host "Installing dependencies mapped from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "Creating default dependency manifest..." -ForegroundColor Cyan
    @"
python-chess>=2.1.1
requests>=2.31.0
pyyaml>=6.0.1
"@ | Out-File -FilePath ".\requirements.txt" -Encoding utf8
    pip install -r requirements.txt
}

Write-Host "Setup Completed Successfully! Run win_launch.bat to boot up your Lichess Draw bot." -ForegroundColor Green
