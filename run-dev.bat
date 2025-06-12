@echo off
echo Starting ChartGPT (Backend + Frontend)...

REM === Start Backend (FastAPI with Uvicorn) in a new terminal ===
start "ChartGPT Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

REM === Start Frontend (Vite) in a new terminal ===
start "ChartGPT Frontend" cmd /k "cd frontend && npm run dev"

echo Both services launched in separate windows.
