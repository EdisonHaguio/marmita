@echo off
title Dona Guedes - Sistema

echo.
echo ============================================================
echo     Sistema Dona Guedes - Japao Informatica
echo     Contato: (19) 99813-2220
echo ============================================================
echo.

echo [1/3] Iniciando Backend...
cd /d %~dp0backend
start "Backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8001"

echo       Aguardando backend iniciar...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Iniciando Frontend...
cd /d %~dp0frontend
start "Frontend" cmd /k "set REACT_APP_BACKEND_URL=http://localhost:8001 && npm start"

echo       Aguardando frontend iniciar...
timeout /t 15 /nobreak >nul

echo.
echo [3/3] Abrindo navegador...
start http://localhost:3000

echo.
echo ============================================================
echo     SISTEMA INICIADO!
echo.
echo     Acesse: http://localhost:3000
echo.
echo     Login Admin: admin / admin123
echo     Login Funcionario: usar codigo cadastrado
echo.
echo     NAO FECHE ESTA JANELA!
echo ============================================================
echo.

pause
