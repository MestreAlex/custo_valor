@echo off
REM Script para executar backtest automático
REM Este script iniciará o Python venv e executará o script de backtest

setlocal enabledelayedexpansion

REM Definir cores (Windows 10+)
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

cd /d "%~dp0"

echo.
echo ================================================================================
echo          SISTEMA DE BACKTEST AUTOMATICO - TODAS AS LIGAS E TEMPORADAS
echo ================================================================================
echo.
echo Este script processará:
echo   - 31 ligas
echo   - 7 anos (2020-2026)
echo   - Múltiplos formatos de temporada
echo.
echo Os resultados serão salvos automaticamente.
echo.

REM Verificar se Python está disponível
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Python não encontrado! Verifique sua instalação.
    pause
    exit /b 1
)

REM Executar script
echo Iniciando script de backtest automático...
echo.

".venv\Scripts\python.exe" executar_backtest_automatico.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar script
    pause
    exit /b 1
)

echo.
echo ✅ Backtest automático concluído!
echo.
echo Para monitorar o progresso, execute:
echo   python monitor_backtest.py
echo.

pause
