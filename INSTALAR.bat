@echo off
echo ============================================
echo   INSTALADOR - Sistema Dona Guedes
echo   Japao Informatica - (19) 99813-2220
echo ============================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo.
    echo ERRO: Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    echo IMPORTANTE: Marque "Add Python to PATH"
    pause
    exit /b 1
)

echo Verificando Node.js...
node --version
if errorlevel 1 (
    echo.
    echo ERRO: Node.js nao encontrado!
    echo Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo ============================================
echo   INSTALANDO BACKEND
echo ============================================
cd /d %~dp0backend

echo Removendo ambiente antigo...
if exist venv rmdir /s /q venv

echo Criando ambiente virtual...
python -m venv venv

echo Ativando ambiente...
call venv\Scripts\activate.bat

echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando dependencias...
pip install fastapi==0.115.0 uvicorn==0.30.6 pymongo==4.8.0 pydantic==2.9.1 python-jose==3.3.0 passlib==1.7.4 python-multipart==0.0.9 requests==2.32.3 bcrypt cryptography

echo.
echo ============================================
echo   INSTALANDO FRONTEND
echo ============================================
cd /d %~dp0frontend

echo Removendo node_modules antigo...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

echo Instalando dependencias (aguarde alguns minutos)...
call npm install --legacy-peer-deps

echo.
echo ============================================
echo   INSTALACAO CONCLUIDA!
echo   Execute: INICIAR_SISTEMA.bat
echo ============================================
pause
