@echo off
echo ===================================================
echo   Starting Document Summary Assistant (Local)
echo ===================================================

:: Start backend in a separate terminal window
echo [1/2] Starting Backend (FastAPI on Port 8000)...
start "Backend Server (FastAPI)" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Start frontend in this terminal window
echo [2/2] Starting Frontend (React + Vite)...
cd /d %~dp0frontend
npm run dev

pause
