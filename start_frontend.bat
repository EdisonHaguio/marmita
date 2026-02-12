@echo off
title Dona Guedes - Frontend
echo ==========================================
echo   Sistema Dona Guedes - Frontend
echo   Japao Informatica - (19) 99813-2220
echo ==========================================
echo.

cd /d "%~dp0frontend"

echo Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    echo Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js encontrado!
echo.

if not exist "node_modules" (
    echo Instalando dependencias pela primeira vez...
    echo Isso pode demorar alguns minutos...
    echo.
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo.
        echo Tentando instalacao alternativa...
        call npm install --force
    )
) else (
    echo Dependencias ja instaladas!
)

echo.
echo Iniciando frontend na porta 3000...
echo Aguarde o navegador abrir automaticamente...
echo.

set REACT_APP_BACKEND_URL=http://localhost:8001
call npm start

pause
