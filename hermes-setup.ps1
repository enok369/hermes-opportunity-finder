# Hermes Opportunity Finder - Windows PowerShell Setup
# Usage: .\hermes-setup.ps1 [init|start|stop|logs|status]

param([string]$Command = "start")

$HERMES_HOME = "$env:USERPROFILE\.hermes"
$OPPORTUNITIES_DIR = "$env:USERPROFILE\opportunities"
$SCRIPT_DIR = (Get-Item $PSScriptRoot).FullName

function Initialize-Setup {
    Write-Host "Initializing Hermes Opportunity Finder..." -ForegroundColor Cyan
    
    # Create directory structure
    Write-Host "Creating directories..." -ForegroundColor Cyan
    $dirs = @(
        "$HERMES_HOME\config",
        "$HERMES_HOME\skills",
        "$HERMES_HOME\memory",
        "$HERMES_HOME\logs",
        "$OPPORTUNITIES_DIR\proposals",
        "$OPPORTUNITIES_DIR\feedback",
        "$OPPORTUNITIES_DIR\archive",
        "$OPPORTUNITIES_DIR\reports"
    )
    
    foreach ($dir in $dirs) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
    
    Write-Host "OK - Directories created" -ForegroundColor Green
    
    # Copy config files
    Write-Host "Copying configuration files..." -ForegroundColor Cyan
    Copy-Item -Path "$SCRIPT_DIR\hermes-config.yaml" -Destination "$HERMES_HOME\config.yaml" -Force
    Copy-Item -Path "$SCRIPT_DIR\hermes-crontab.yaml" -Destination "$HERMES_HOME\crontab.yaml" -Force
    Copy-Item -Path "$SCRIPT_DIR\hermes-skills\*" -Destination "$HERMES_HOME\skills\" -Force -Recurse
    
    Write-Host "OK - Configuration files copied" -ForegroundColor Green
    Write-Host ""
    Write-Host "Hermes Home: $HERMES_HOME" -ForegroundColor Cyan
    Write-Host "Opportunities: $OPPORTUNITIES_DIR" -ForegroundColor Cyan
}

function Start-Stack {
    Initialize-Setup
    
    Write-Host ""
    Write-Host "Starting Docker services..." -ForegroundColor Cyan
    
    if (-not (Test-Path "$SCRIPT_DIR\docker-compose.yml")) {
        Write-Host "ERROR: docker-compose.yml not found" -ForegroundColor Red
        exit 1
    }
    
    Push-Location $SCRIPT_DIR
    docker compose up -d
    Pop-Location
    
    Write-Host "Waiting for services (20 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
    
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host "Hermes Opportunity Finder is Running!" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Hermes Backend:  http://localhost:9119" -ForegroundColor Cyan
    Write-Host "Model Runner:    http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Hermes Home:     $HERMES_HOME" -ForegroundColor Cyan
    Write-Host "Opportunities:   $OPPORTUNITIES_DIR" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next: Open new terminal and run:" -ForegroundColor Yellow
    Write-Host "  hermes desktop" -ForegroundColor White
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  docker compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop:" -ForegroundColor Yellow
    Write-Host "  docker compose down" -ForegroundColor White
    Write-Host ""
}

function Stop-Stack {
    Write-Host "Stopping Docker services..." -ForegroundColor Yellow
    Push-Location $SCRIPT_DIR
    docker compose down
    Pop-Location
    Write-Host "OK - Services stopped" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "Following Docker logs (Ctrl+C to exit)..." -ForegroundColor Yellow
    Push-Location $SCRIPT_DIR
    docker compose logs -f
    Pop-Location
}

function Show-Status {
    Push-Location $SCRIPT_DIR
    docker compose ps
    Pop-Location
}

function Show-Help {
    Write-Host "Hermes Opportunity Finder Setup" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\hermes-setup.ps1 [command]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  init       Initialize directories and config"
    Write-Host "  start      Initialize and start services (default)"
    Write-Host "  stop       Stop Docker services"
    Write-Host "  status     Show service status"
    Write-Host "  logs       Follow Docker logs"
    Write-Host ""
}

# Main
switch ($Command.ToLower()) {
    "init" {
        Initialize-Setup
    }
    "start" {
        Start-Stack
    }
    "stop" {
        Stop-Stack
    }
    "logs" {
        Show-Logs
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
    default {
        if ($Command -eq "") {
            Start-Stack
        } else {
            Write-Host "Unknown command: $Command" -ForegroundColor Red
            Show-Help
            exit 1
        }
    }
}
