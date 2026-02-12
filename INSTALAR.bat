@echo off
echo ============================================
echo   INSTALADOR RAPIDO - Dona Guedes
echo ============================================

cd /d %~dp0backend
echo Instalando Backend...
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat
pip install fastapi uvicorn pymongo pydantic python-jose passlib python-multipart requests bcrypt cryptography --quiet

cd /d %~dp0frontend
echo Instalando Frontend...
if exist node_modules rmdir /s /q node_modules
call npm install --legacy-peer-deps --silent

echo ============================================
echo   PRONTO! Execute: INICIAR.bat
echo ============================================
pause
