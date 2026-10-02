@echo off
setlocal
echo ==========================================================
echo  Starting SuperIndia.ai Decision Intelligence Engine 
echo ==========================================================

set "PATH=C:\Users\DRONA\nodejs;%PATH%"

echo Starting Backend API on http://127.0.0.1:8000 ...
start "SuperIndia Backend" cmd /k "python backend\run.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend on http://localhost:5173 ...
cd frontend
start "SuperIndia Frontend" cmd /k "set PATH=C:\Users\DRONA\nodejs;%%PATH%% && npm run dev"

echo.
echo ==========================================================
echo  SuperIndia.ai is RUNNING!
echo  Frontend: http://localhost:5173
echo  Backend:  http://127.0.0.1:8000
echo ==========================================================
pause
