@echo off
chcp 65001 > nul
echo ==================================================
echo   INICIANDO SISTEMA DE ANÁLISE DE JOGOS
echo ==================================================
echo.

echo [1/4] Parando servidores anteriores...
taskkill /F /IM python.exe > nul 2>&1
timeout /t 2 /nobreak > nul
echo       ✓ Servidores anteriores finalizados
echo.

echo [2/4] Iniciando Servidor API Principal (porta 8000)...
start "SERVIDOR API - PORTA 8000" cmd /k "cd /d "%~dp0" && python servidor_api.py"
timeout /t 3 /nobreak > nul
echo       ✓ Servidor API iniciado
echo.

echo [3/4] Iniciando Servidor Análise de Jogos (porta 9000)...
start "SERVIDOR JOGOS - PORTA 9000" cmd /k "cd /d "%~dp0" && python servidor_analise_jogos.py"
timeout /t 3 /nobreak > nul
echo       ✓ Servidor Análise de Jogos iniciado
echo.

echo [4/4] Iniciando Servidor Backtest API (porta 5001)...
start "SERVIDOR BACKTEST API - PORTA 5001" cmd /k "cd /d "%~dp0backtest" && python api_backtest.py"
timeout /t 3 /nobreak > nul
echo       ✓ Servidor Backtest API iniciado
echo.

echo ==================================================
echo   ✓ TODOS OS SERVIDORES INICIADOS COM SUCESSO!
echo ==================================================
echo.
echo URLs disponíveis:
echo   • Servidor Principal:      http://localhost:8000
echo   • Análise de Jogos:        http://localhost:9000
echo   • Análise de Backtest:     http://localhost:5001
echo.
pause
