@echo off
chcp 65001 >nul
title Dona Guedes - Sistema
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     Sistema Dona Guedes - Japao Informatica                  ║
echo ║     Contato: (19) 99813-2220                                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Verificar se foi instalado
if not exist "%~dp0backend\venv" (
    echo ERRO: Sistema nao instalado!
    echo Execute primeiro: INSTALAR.bat
    pause
    exit /b 1
)

if not exist "%~dp0frontend\node_modules" (
    echo ERRO: Sistema nao instalado!
    echo Execute primeiro: INSTALAR.bat
    pause
    exit /b 1
)

echo [1/3] Iniciando Backend...
start "Dona Guedes - Backend" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate && python -m uvicorn server:app --host 0.0.0.0 --port 8001"

echo       Aguardando backend iniciar...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Iniciando Frontend...
start "Dona Guedes - Frontend" cmd /k "cd /d "%~dp0frontend" && set REACT_APP_BACKEND_URL=http://localhost:8001 && npm start"

echo       Aguardando frontend iniciar...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Abrindo navegador...
start http://localhost:3000

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     SISTEMA INICIADO!                                        ║
echo ║                                                              ║
echo ║     Acesse: http://localhost:3000                            ║
echo ║                                                              ║
echo ║     Login Admin: admin / admin123                            ║
echo ║     Login Funcionario: usar codigo cadastrado                ║
echo ║                                                              ║
echo ║     NAO FECHE ESTA JANELA!                                   ║
echo ║     Para parar: feche as janelas Backend e Frontend          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

pause
