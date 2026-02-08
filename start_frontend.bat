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

echo Instalando/Atualizando dependencias...
call yarn install

echo.
echo Iniciando frontend na porta 3000...
echo Aguarde o navegador abrir automaticamente...
echo.

set REACT_APP_BACKEND_URL=http://localhost:8001
call yarn start

pause
