@echo off
chcp 65001 >nul
echo ============================================================
echo   DONA GUEDES - Sistema de Marmitaria
echo ============================================================
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
echo Instalando dependencias...
pip install fastapi uvicorn pydantic --quiet

echo.
echo ============================================================
echo   SISTEMA INICIANDO...
echo   Acesse: http://localhost:8000
echo   Login: admin / admin123
echo   
echo   Para FECHAR, pressione Ctrl+C nesta janela
echo ============================================================
echo.

python server_offline.py
pause
