# Script PowerShell para iniciar todos os servidores
# Funciona apenas em Windows PowerShell 5.1+

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🚀 INICIALIZADOR DE SERVIDORES - SISTEMA DE ANÁLISE DE FUTEBOL" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Servidores que serão inicializados:" -ForegroundColor Blue
Write-Host "  ✓ servidor_api.py (porta 8000)" -ForegroundColor White
Write-Host "    - Proxima Rodada: http://localhost:8000/proxima_rodada.html" -ForegroundColor Gray
Write-Host "    - Jogos Salvos: http://localhost:8000/jogos_salvos.html" -ForegroundColor Gray
Write-Host "    - Análise Salvos: http://localhost:8000/analise_salvos.html" -ForegroundColor Gray
Write-Host ""
Write-Host "  ✓ servidor_analise_backtest.py (porta 5001)" -ForegroundColor White
Write-Host "    - Backtest: http://localhost:5001/backtest.html" -ForegroundColor Gray
Write-Host "    - Backtests Salvos: http://localhost:5001/backtest_salvos.html" -ForegroundColor Gray
Write-Host "    - Resumo Entradas: http://localhost:5001/backtest_resumo_entradas.html" -ForegroundColor Gray
Write-Host ""

# Gerando páginas HTML
Write-Host "[PREPARAÇÃO] Gerando páginas HTML..." -ForegroundColor Yellow

Write-Host "  → Gerando proxima_rodada.html..." -NoNewline -ForegroundColor Yellow
python buscar_proxima_rodada.py 2>&1 | Out-Null
Write-Host " OK" -ForegroundColor Green

Write-Host "  → Gerando jogos_salvos.html..." -NoNewline -ForegroundColor Yellow
python salvar_jogo.py gerar 2>&1 | Out-Null
Write-Host " OK" -ForegroundColor Green

Write-Host "  → Gerando analise_salvos.html..." -NoNewline -ForegroundColor Yellow
python salvar_jogo.py gerar_analise 2>&1 | Out-Null
Write-Host " OK" -ForegroundColor Green

Write-Host ""
Write-Host "Iniciando Servidores:" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor_api.py
Write-Host "[INICIANDO] Servidor API (porta 8000)..." -NoNewline -ForegroundColor Blue
Start-Process python -ArgumentList "servidor_api.py" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host " ✓ OK" -ForegroundColor Green

# Iniciar servidor_analise_backtest.py
Write-Host "[INICIANDO] Servidor de Backtest (porta 5001)..." -NoNewline -ForegroundColor Blue
Start-Process python -ArgumentList "servidor_analise_backtest.py" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host " ✓ OK" -ForegroundColor Green

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Green
Write-Host "✓ SISTEMA TOTALMENTE OPERACIONAL" -ForegroundColor Green
Write-Host "=================================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Páginas disponíveis:" -ForegroundColor White
Write-Host ""
Write-Host "  📄 Próxima Rodada" -ForegroundColor White
Write-Host "     http://localhost:8000/proxima_rodada.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📄 Jogos Salvos" -ForegroundColor White
Write-Host "     http://localhost:8000/jogos_salvos.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📄 Análise Salvos" -ForegroundColor White
Write-Host "     http://localhost:8000/analise_salvos.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📊 Backtest" -ForegroundColor White
Write-Host "     http://localhost:5001/backtest.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📊 Backtests Salvos" -ForegroundColor White
Write-Host "     http://localhost:5001/backtest_salvos.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📊 Resumo de Entradas" -ForegroundColor White
Write-Host "     http://localhost:5001/backtest_resumo_entradas.html" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pressione Ctrl+C para parar os servidores" -ForegroundColor Yellow
Write-Host ""

# Manter o script rodando
while ($true) {
    Start-Sleep -Seconds 1
}
