@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo   SuperIndia.ai - Instant Public HTTPS Tunnel Launcher
echo   Hack in Hills Manali 2026 (AI Systems & National Infra Track)
echo ================================================================
echo.

set "PATH=C:\Users\DRONA\nodejs;%PATH%"

:: 1. Ensure Backend is running on port 8000
netstat -ano | findstr :8000 | findstr LISTENING >nul
if errorlevel 1 (
    echo [1/3] Starting FastAPI Backend on port 8000 in background...
    start "SuperIndia Backend (Port 8000)" cmd /k "set PATH=C:\Users\DRONA\nodejs;%%PATH%% && python backend\run.py"
    timeout /t 3 /nobreak >nul
) else (
    echo [1/3] FastAPI Backend is already running on port 8000.
)

:: 2. Ensure Frontend is running on port 5173
netstat -ano | findstr :5173 | findstr LISTENING >nul
if errorlevel 1 (
    echo [2/3] Starting Vite Frontend on port 5173 in background...
    cd frontend
    start "SuperIndia Frontend (Port 5173)" cmd /k "set PATH=C:\Users\DRONA\nodejs;%%PATH%% && npm run dev -- --host 127.0.0.1 --port 5173"
    cd ..
    timeout /t 3 /nobreak >nul
) else (
    echo [2/3] Vite Frontend is already running on port 5173.
)

:: 3. Launch Public HTTPS Tunnel
echo [3/3] Establishing instant public HTTPS tunnel...
echo ----------------------------------------------------------------

where cloudflared >nul 2>&1
if not errorlevel 1 (
    echo [Tunnel Provider] Using Cloudflare Quick Tunnel (cloudflared)...
    echo.
    echo ================================================================
    echo  Copy the generated https://*.trycloudflare.com URL below!
    echo ================================================================
    cloudflared tunnel --url http://127.0.0.1:5173 --http-host-header localhost:5173
) else (
    echo [Tunnel Provider] Using localtunnel (npx localtunnel)...
    echo.
    echo ================================================================
    echo  Copy the generated https://*.loca.lt URL below!
    echo ================================================================
    npx localtunnel --port 5173 --local-host 127.0.0.1
)

pause
