# Script para agendar execução automática do buscar_proxima_rodada.py
# Executa nas terças e sextas-feiras às 08:00

$scriptPath = "c:\Users\Alex Menezes\projetos\custo_valor\buscar_proxima_rodada.py"
$pythonPath = "python"
$taskName = "FootballData_ProximaRodada"

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "AGENDADOR DE TAREFAS - PRÓXIMA RODADA" -ForegroundColor Cyan
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se a tarefa já existe
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Tarefa '$taskName' já existe." -ForegroundColor Yellow
    $response = Read-Host "Deseja remover e recriar? (S/N)"
    
    if ($response -eq "S" -or $response -eq "s") {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "✓ Tarefa removida" -ForegroundColor Green
    } else {
        Write-Host "Operação cancelada" -ForegroundColor Yellow
        exit
    }
}

# Criar ação da tarefa
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory (Split-Path $scriptPath)

# Criar gatilhos (Terça e Sexta às 08:00)
$triggerTerca = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Tuesday -At "08:00"
$triggerSexta = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At "08:00"

# Configurações adicionais
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Criar a tarefa
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Write-Host "Criando tarefa agendada..." -ForegroundColor Yellow

try {
    Register-ScheduledTask -TaskName $taskName `
                          -Action $action `
                          -Trigger $triggerTerca,$triggerSexta `
                          -Settings $settings `
                          -Principal $principal `
                          -Description "Baixa automaticamente os jogos da próxima rodada às terças e sextas-feiras" | Out-Null
    
    Write-Host ""
    Write-Host "================================================================================================" -ForegroundColor Green
    Write-Host "✓ TAREFA CRIADA COM SUCESSO!" -ForegroundColor Green
    Write-Host "================================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nome da tarefa: $taskName" -ForegroundColor White
    Write-Host "Script: $scriptPath" -ForegroundColor White
    Write-Host "Frequência: Toda terça e sexta-feira às 08:00" -ForegroundColor White
    Write-Host ""
    Write-Host "Para gerenciar esta tarefa:" -ForegroundColor Cyan
    Write-Host "  - Abra o 'Agendador de Tarefas' do Windows" -ForegroundColor Gray
    Write-Host "  - Procure por '$taskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Comandos úteis:" -ForegroundColor Cyan
    Write-Host "  - Executar agora: " -ForegroundColor Gray -NoNewline
    Write-Host "Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "  - Desabilitar: " -ForegroundColor Gray -NoNewline
    Write-Host "Disable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "  - Habilitar: " -ForegroundColor Gray -NoNewline
    Write-Host "Enable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "  - Remover: " -ForegroundColor Gray -NoNewline
    Write-Host "Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host ""
    
    # Perguntar se deseja executar agora
    $runNow = Read-Host "Deseja executar a tarefa agora para testar? (S/N)"
    
    if ($runNow -eq "S" -or $runNow -eq "s") {
        Write-Host ""
        Write-Host "Executando tarefa..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $taskName
        Write-Host "✓ Tarefa iniciada! Verifique o diretório 'fixtures' para os resultados." -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ ERRO ao criar tarefa: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "  1. Execute o PowerShell como Administrador" -ForegroundColor Gray
    Write-Host "  2. Verifique se o Python está no PATH" -ForegroundColor Gray
    Write-Host "  3. Verifique o caminho do script: $scriptPath" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Pressione Enter para sair..."
Read-Host
