# Script para iniciar os 3 servidores do sistema
# Uso: .\iniciar_servidores.ps1

$ErrorActionPreference = "Stop"

# Caminho do projeto
$projectPath = "c:\Users\Alex Menezes\projetos\custo_valor"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  INICIANDO SISTEMA DE ANÁLISE DE JOGOS" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Parar processos Python existentes
Write-Host "[1/4] Parando servidores anteriores..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "      ✓ Servidores anteriores finalizados" -ForegroundColor Green
Write-Host ""

# Servidor 1: API Principal (porta 8000)
Write-Host "[2/4] Iniciando Servidor API Principal (porta 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; Write-Host 'SERVIDOR API PRINCIPAL - PORTA 8000' -ForegroundColor Cyan; python servidor_api.py"
Start-Sleep -Seconds 3
Write-Host "      ✓ Servidor API iniciado" -ForegroundColor Green
Write-Host ""

# Servidor 2: Análise de Jogos (porta 9000)
Write-Host "[3/4] Iniciando Servidor Análise de Jogos (porta 9000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; Write-Host 'SERVIDOR ANÁLISE DE JOGOS - PORTA 9000' -ForegroundColor Cyan; python servidor_analise_jogos.py"
Start-Sleep -Seconds 3
Write-Host "      ✓ Servidor Análise de Jogos iniciado" -ForegroundColor Green
Write-Host ""

# Servidor 3: Análise de Backtest (porta 5001)
Write-Host "[4/4] Iniciando Servidor Análise de Backtest (porta 5001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; Write-Host 'SERVIDOR ANÁLISE DE BACKTEST - PORTA 5001' -ForegroundColor Cyan; python servidor_analise_backtest.py"
Start-Sleep -Seconds 3
Write-Host "      ✓ Servidor Análise de Backtest iniciado" -ForegroundColor Green
Write-Host ""

Write-Host "==================================================" -ForegroundColor Green
Write-Host "  ✓ TODOS OS SERVIDORES INICIADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs disponíveis:" -ForegroundColor Cyan
Write-Host "  • Servidor Principal:      http://localhost:8000" -ForegroundColor White
Write-Host "  • Análise de Jogos:        http://localhost:9000" -ForegroundColor White
Write-Host "  • Análise de Backtest:     http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "Pressione qualquer tecla para fechar esta janela..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
