@echo off
title Dona Guedes - Backend
echo ==========================================
echo   Sistema Dona Guedes - Backend
echo   Japao Informatica - (19) 99813-2220
echo ==========================================
echo.

cd /d "%~dp0backend"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Verificando ambiente virtual...
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando/Atualizando dependencias...
pip install -r requirements.txt --quiet

echo.
echo Iniciando backend na porta 8001...
echo.
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

pause
