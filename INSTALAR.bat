@echo off
title Dona Guedes - INSTALADOR

echo.
echo ============================================================
echo     INSTALADOR - Sistema Dona Guedes
echo     Japao Informatica - (19) 99813-2220
echo ============================================================
echo.

echo [1/6] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo       Python OK!

echo.
echo [2/6] Verificando Node.js...
node --version
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    echo Baixe em: https://nodejs.org/
    pause
    exit /b 1
)
echo       Node.js OK!

echo.
echo [3/6] Instalando Backend...
cd /d %~dp0backend

if exist venv (
    echo       Removendo ambiente antigo...
    rmdir /s /q venv
)

echo       Criando ambiente virtual...
python -m venv venv

echo       Ativando ambiente...
call venv\Scripts\activate.bat

echo       Atualizando pip...
python -m pip install --upgrade pip

echo       Instalando dependencias do backend...
pip install fastapi uvicorn pymongo pydantic python-jose passlib python-multipart requests bcrypt cryptography

echo       Backend instalado!

echo.
echo [4/6] Instalando Frontend...
cd /d %~dp0frontend

if exist node_modules (
    echo       Removendo node_modules antigo...
    rmdir /s /q node_modules
)

if exist package-lock.json (
    del package-lock.json
)

echo       Instalando dependencias (pode demorar alguns minutos)...
call npm install --legacy-peer-deps

echo       Frontend instalado!

echo.
echo [5/6] Criando arquivo de configuracao...
echo REACT_APP_BACKEND_URL=http://localhost:8001> .env

echo.
echo [6/6] Instalacao concluida!
echo.
echo ============================================================
echo     INSTALACAO CONCLUIDA COM SUCESSO!
echo.
echo     Para iniciar o sistema, execute: INICIAR_SISTEMA.bat
echo ============================================================
echo.

pause
