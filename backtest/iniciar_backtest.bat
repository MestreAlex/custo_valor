@echo off
REM Script para iniciar o Backtest no Windows
REM Inicia tanto a API quanto o Servidor HTTP

cd /d "%~dp0"

echo.
echo ============================================================
echo 🚀 Iniciando Backtest - API e Servidor HTTP
echo ============================================================
echo.
echo 📡 Iniciando API Backtest (porta 5001)...
start "API Backtest - 5001" python api_backtest.py

echo 🌐 Iniciando Servidor HTTP (porta 8001)...
timeout /t 2 /nobreak
start "Servidor HTTP - 8001" python -m http.server 8001

echo.
echo ============================================================
echo ✅ Servidores iniciados com sucesso!
echo ============================================================
echo.
echo 📍 Acesse: http://localhost:8001/backtest.html
echo.
echo ⚠️  Duas janelas foram abertas:
echo   - API Backtest (porta 5001)
echo   - Servidor HTTP (porta 8001)
echo.
echo Para parar: feche ambas as janelas
echo ============================================================
echo.
pause
