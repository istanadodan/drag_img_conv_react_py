# HEIC to JPG Converter - Full Stack Application Launcher
# Runs FastAPI backend and React frontend simultaneously

param(
    [switch]$NoFrontend = $false,
    [switch]$NoBackend = $false,
    [switch]$All = $false,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

# UTF-8 인코딩 설정 (한글 깨짐 해결)
cmd /c chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Color output for better visibility
function Write-Status { Write-Host "[INFO]" -ForegroundColor Green -NoNewline; Write-Host " $($args -join ' ')" }
function Write-Error-Custom { Write-Host "[ERROR]" -ForegroundColor Red -NoNewline; Write-Host " $($args -join ' ')" }

# Check if running from correct directory
if (-not (Test-Path "app\main.py") -or -not (Test-Path "ui\package.json")) {
    Write-Error-Custom "Must run from project root directory"
    exit 1
}

# Activate Python virtual environment
Write-Status "Activating Python virtual environment..."
. ".\app\.venv\Scripts\Activate.ps1"

$projectRoot = (Get-Location).Path
$jobs = @()

# Start Backend (FastAPI)
if (-not $NoBackend) {
    Write-Status "Starting FastAPI backend on http://localhost:$BackendPort..."
    $backendJob = Start-Job -ScriptBlock {
        param($Root, $Port)
        Set-Location $Root
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONPATH = "$Root\app"
        & python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $Port
    } -ArgumentList $projectRoot, $BackendPort -Name "Backend-$BackendPort"

    $jobs += $backendJob
    Start-Sleep -Seconds 2
    Write-Status "Backend started (Job ID: $($backendJob.Id))"
}

# Start Frontend (Vite + React)
if (-not $NoFrontend) {
    Write-Status "Starting Vite frontend dev server on http://localhost:$FrontendPort..."
    $frontendJob = Start-Job -ScriptBlock {
        param($Root, $Port)
        Set-Location "$Root\ui"
        $env:LANG = "en_US.UTF-8"
        $env:LC_ALL = "en_US.UTF-8"
        $env:VITE_PORT = $Port
        npm run dev
    } -ArgumentList $projectRoot, $FrontendPort -Name "Frontend-$FrontendPort"

    $jobs += $frontendJob
    Start-Sleep -Seconds 3
    Write-Status "Frontend started (Job ID: $($frontendJob.Id))"
}

Write-Status "=========================================="
Write-Status "Backend:  http://localhost:$BackendPort"
Write-Status "Frontend: http://localhost:$FrontendPort"
Write-Status "=========================================="
Write-Status "Services running. Press Ctrl+C to stop."
Write-Status "=========================================="

# Keep script alive and handle Ctrl+C
if (-not $All) {
    Write-Status "Running in All mode - Both backend and frontend will start automatically"
    exit 1
}
try {
    $iteration = 0
    $host.UI.RawUI.ForegroundColor = "Yellow"
    while ($true) {
        $iteration++
        Write-Host "----------------------------------------------------------------------"
        Write-Status "[$iteration] Job Status (Every 60s):"
        Get-Job | Format-Table -AutoSize

        # Check for job errors and logs (both running and stopped jobs)
        Get-Job | ForEach-Object {
            # Always check for any pending output/errors regardless of state
            if ($_.HasMoreData) {
                Write-Status "Logs from $($_.Name) (State: $($_.State)):"
                $_ | Receive-Job -Keep
            }
        }

        Write-Status "[$iteration] Services are running. Press Ctrl+C to stop all services."
        Start-Sleep -Seconds 60
    }
}
catch {
    Write-Status "Shutting down services..."
}
finally {
    Write-Status "Stopping all background jobs..."
    Get-Job | Stop-Job -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Get-Job | Remove-Job -ErrorAction SilentlyContinue
    Write-Status "All services stopped and cleaned up"
}
