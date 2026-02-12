@echo off
echo Iniciando Sistema Dona Guedes...

start "BACKEND" cmd /c "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8001"

timeout /t 3 /nobreak >nul

start "FRONTEND" cmd /c "cd /d %~dp0frontend && set REACT_APP_BACKEND_URL=http://localhost:8001 && npm start"

timeout /t 10 /nobreak >nul

start http://localhost:3000

echo.
echo Sistema iniciado! Acesse: http://localhost:3000
echo Admin: admin / admin123
pause
