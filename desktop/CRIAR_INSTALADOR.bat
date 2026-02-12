@echo off
echo ============================================
echo   DONA GUEDES - Instalador Offline
echo   Japao Informatica - (19) 99813-2220
echo ============================================
echo.
echo Este script vai criar o DonaGuedes.exe
echo.
echo Requisitos:
echo   - Python 3.11+ instalado
echo   - Node.js 18+ instalado
echo.
pause

echo.
echo [1/4] Instalando dependencias Python...
pip install pyinstaller fastapi uvicorn pydantic

echo.
echo [2/4] Instalando dependencias Frontend...
cd /d %~dp0..\frontend
call npm install --legacy-peer-deps

echo.
echo [3/4] Compilando Frontend...
call npm run build

echo.
echo [4/4] Criando executavel...
cd /d %~dp0
if exist static rmdir /s /q static
xcopy /E /I /Y ..\frontend\build static
pyinstaller --onefile --noconsole --name=DonaGuedes --add-data "static;static" --add-data "dona_guedes.db;." server_offline.py

echo.
echo ============================================
echo   PRONTO!
echo.
echo   O arquivo DonaGuedes.exe esta em:
echo   %~dp0dist\DonaGuedes.exe
echo.
echo   Copie este arquivo para qualquer PC
echo   e execute com duplo clique!
echo ============================================
pause
