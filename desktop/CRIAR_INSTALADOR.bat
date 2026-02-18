@echo off
chcp 65001 >nul
echo ============================================================
echo   DONA GUEDES - Criador de Instalador
echo ============================================================
echo.
echo Este script vai criar o arquivo DonaGuedes.exe
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante a instalacao, marque a opcao
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.
echo Instalando dependencias necessarias...
pip install pyinstaller fastapi uvicorn pydantic --quiet

echo.
echo Criando executavel... (pode demorar alguns minutos)
echo.

python build_installer.py

echo.
pause
