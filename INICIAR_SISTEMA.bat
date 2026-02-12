@echo off
echo ============================================
echo   Sistema Dona Guedes
echo   Japao Informatica - (19) 99813-2220
echo ============================================
echo.

echo Verificando instalacao...
if not exist "%~dp0backend\venv" (
    echo ERRO: Execute INSTALAR.bat primeiro!
    pause
    exit /b 1
)

echo Iniciando Backend...
start "BACKEND" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8001"

echo Aguardando backend...
timeout /t 5 /nobreak >nul

echo Iniciando Frontend...
start "FRONTEND" cmd /k "cd /d %~dp0frontend && set REACT_APP_BACKEND_URL=http://localhost:8001 && npm start"

echo.
echo ============================================
echo   Aguarde o navegador abrir...
echo   Se nao abrir, acesse: http://localhost:3000
echo.
echo   Login Admin: admin / admin123
echo ============================================

timeout /t 15 /nobreak >nul
start http://localhost:3000

pause
