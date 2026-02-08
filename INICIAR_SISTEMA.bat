@echo off
color 0A
title Sistema Dona Guedes - Inicializacao Completa

echo.
echo  =====================================================
echo        SISTEMA DONA GUEDES - Japao Informatica
echo        Contato: (19) 99813-2220
echo  =====================================================
echo.

echo [1/4] Verificando MongoDB...
sc query MongoDB | find "RUNNING" >nul
if errorlevel 1 (
    echo MongoDB nao esta rodando. Tentando iniciar...
    net start MongoDB >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ATENCAO: MongoDB nao encontrado ou nao iniciou!
        echo.
        echo Opcoes:
        echo 1. Instalar MongoDB: https://www.mongodb.com/try/download/community
        echo 2. Ou usar Docker Desktop (recomendado)
        echo.
        pause
        exit /b 1
    )
    echo MongoDB iniciado com sucesso!
) else (
    echo MongoDB ja esta rodando!
)

echo.
echo [2/4] Iniciando Backend (porta 8001)...
start "Dona Guedes - Backend" /MIN cmd /k "%~dp0start_backend.bat"
timeout /t 8 /nobreak >nul

echo [3/4] Testando Backend...
curl -s http://localhost:8001/api/ >nul 2>&1
if errorlevel 1 (
    echo AVISO: Backend ainda nao respondeu. Aguardando...
    timeout /t 5 /nobreak >nul
)
echo Backend OK!

echo.
echo [4/4] Iniciando Frontend (porta 3000)...
start "Dona Guedes - Frontend" /MIN cmd /k "%~dp0start_frontend.bat"

echo.
echo =====================================================
echo   SISTEMA INICIADO COM SUCESSO!
echo =====================================================
echo.
echo   Acesse: http://localhost:3000
echo.
echo   Login Admin: admin / admin123
echo   Login Funcionario: usar codigo cadastrado
echo.
echo   Feche esta janela para manter o sistema rodando.
echo   Para parar: feche as janelas Backend e Frontend.
echo =====================================================
echo.

timeout /t 15 >nul
start http://localhost:3000

:loop
timeout /t 60 >nul
goto loop
