@echo off
REM Script para iniciar o sistema de análise de jogos

echo ================================================================================
echo Sistema de Análise de Jogos de Futebol
echo ================================================================================
echo.

:menu
echo.
echo [1] Buscar próximos jogos e gerar análise
echo [2] Iniciar servidor API (necessário para salvar jogos)
echo [3] Iniciar servidor HTTP para visualizar páginas
echo [4] Gerar página de jogos salvos
echo [5] Abrir página de próximos jogos no navegador
echo [6] Abrir página de jogos salvos no navegador
echo [7] Iniciar tudo (API + HTTP + abrir páginas)
echo [0] Sair
echo.

set /p opcao="Escolha uma opção: "

if "%opcao%"=="1" goto buscar
if "%opcao%"=="2" goto api
if "%opcao%"=="3" goto http
if "%opcao%"=="4" goto gerar
if "%opcao%"=="5" goto abrir_proximos
if "%opcao%"=="6" goto abrir_salvos
if "%opcao%"=="7" goto iniciar_tudo
if "%opcao%"=="0" goto sair
goto menu

:buscar
echo.
echo Buscando próximos jogos e gerando análise...
python buscar_proxima_rodada.py
pause
goto menu

:api
echo.
echo Iniciando servidor API em http://localhost:5000...
echo Pressione Ctrl+C para parar o servidor
start cmd /k python servidor_api.py
timeout /t 2
goto menu

:http
echo.
echo Iniciando servidor HTTP em http://localhost:8000...
echo Pressione Ctrl+C para parar o servidor
start cmd /k "cd fixtures && python -m http.server 8000"
timeout /t 2
goto menu

:gerar
echo.
echo Gerando página de jogos salvos...
python salvar_jogo.py gerar
pause
goto menu

:abrir_proximos
echo.
echo Abrindo página de próximos jogos...
start http://localhost:8000/proxima_rodada.html
timeout /t 2
goto menu

:abrir_salvos
echo.
echo Abrindo página de jogos salvos...
start http://localhost:8000/jogos_salvos.html
timeout /t 2
goto menu

:iniciar_tudo
echo.
echo Iniciando servidor API...
start cmd /k python servidor_api.py
timeout /t 3

echo Iniciando servidor HTTP...
start cmd /k "cd fixtures && python -m http.server 8000"
timeout /t 3

echo Abrindo páginas no navegador...
start http://localhost:8000/proxima_rodada.html
timeout /t 2
start http://localhost:8000/jogos_salvos.html

echo.
echo ================================================================================
echo Sistema iniciado com sucesso!
echo.
echo Servidor API: http://localhost:5000
echo Servidor HTTP: http://localhost:8000
echo.
echo Páginas abertas no navegador.
echo Feche as janelas do terminal para parar os servidores.
echo ================================================================================
pause
goto menu

:sair
echo.
echo Saindo...
exit
