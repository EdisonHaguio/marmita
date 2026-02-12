@echo off
echo ============================================
echo   CRIANDO INSTALADOR - Dona Guedes
echo   Japao Informatica
echo ============================================
echo.

echo [1/5] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Instale Python primeiro!
    pause
    exit /b 1
)

echo [2/5] Instalando dependencias Python...
pip install pyinstaller fastapi uvicorn pydantic --quiet

echo [3/5] Compilando Frontend...
cd /d %~dp0..\frontend
call npm run build

echo [4/5] Copiando arquivos...
cd /d %~dp0
if exist static rmdir /s /q static
xcopy /E /I /Y ..\frontend\build static

echo [5/5] Criando executavel...
pyinstaller --onefile --name=DonaGuedes --add-data "static;static" server_offline.py

echo.
echo ============================================
echo   PRONTO!
echo   Arquivo: dist\DonaGuedes.exe
echo ============================================
pause
