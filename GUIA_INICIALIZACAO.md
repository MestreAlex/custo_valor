# 🚀 Sistema de Análise de Futebol - Guia de Inicialização

## 📋 Descrição

Sistema completo de análise de dados de futebol com:
- Análise de próximas rodadas (odds, xG, DxG)
- Backtest de estratégias
- Validação de entradas qualificadas
- Dashboard interativo

## 🖥️ Servidores Disponíveis

### Porta 8000 - servidor_api.py
Páginas de análise da próxima rodada:

1. **Próxima Rodada** - http://localhost:8000/proxima_rodada.html
   - Análise de jogos futuros
   - Cálculo de odds teóricas
   - Validação de entradas qualificadas
   - Coluna VALIDADA para conferir se a entrada está qualificada

2. **Jogos Salvos** - http://localhost:8000/jogos_salvos.html
   - Histórico de jogos salvos
   - Resultados e análise

3. **Análise Salvos** - http://localhost:8000/analise_salvos.html
   - Análise AI dos jogos salvos

### Porta 5001 - servidor_analise_backtest.py
Páginas de análise de backtest:

1. **Backtest** - http://localhost:5001/backtest.html
   - Dashboard de backtests

2. **Backtests Salvos** - http://localhost:5001/backtest_salvos.html
   - Histórico de backtests salvos

3. **Resumo de Entradas** - http://localhost:5001/backtest_resumo_entradas.html
   - Análise detalhada de entradas por liga, tipo e DxG
   - Filtros: entradas >= 30, ROI >= 5%, lucro >= 5.0

## 🚀 Como Iniciar

### Opção 1: Python (Linux/Mac/Windows)

```bash
cd custo_valor
python iniciar_todos_servidores.py
```

### Opção 2: PowerShell (Windows)

```powershell
cd custo_valor
.\iniciar_todos_servidores.ps1
```

### Opção 3: Batch (Windows Legacy)

```batch
cd custo_valor
iniciar_servidores.bat
```

## 📊 Estrutura de Diretórios

```
custo_valor/
├── fixtures/                          # Dados HTML e CSV das próximas rodadas
│   ├── proxima_rodada.html           # Página de próxima rodada
│   ├── jogos_salvos.html             # Página de jogos salvos
│   ├── analise_salvos.html           # Página de análise
│   └── backtest_acumulado.json       # Dados de backtest acumulados
├── backtest/                          # Dados e páginas de backtest
│   ├── backtest.html
│   ├── backtest_salvos.html
│   ├── backtest_resumo_entradas.html
│   └── *.csv                          # Dados brutos por liga
├── servidor_api.py                    # Servidor principal (8000)
├── servidor_analise_backtest.py       # Servidor backtest (5001)
├── buscar_proxima_rodada.py          # Gera proxima_rodada.html
├── salvar_jogo.py                    # Gera jogos_salvos.html e analise_salvos.html
└── DOCUMENTACAO_FORMATACAO_PAGINAS.md # Documentação de CSS/formatação
```

## 🎨 Formatação das Páginas

### Tema Visual
- **Gradiente de Fundo:** `linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)`
- **Cor Primária:** `#00d4ff` (cyan)
- **Texto:** `#ecf0f1` (branco)

### Coluna VALIDADA
- **Verde (SIM):** Entrada qualificada de acordo com os critérios
- **Vermelho (NÃO):** Entrada não qualificada

Critérios de Qualificação:
- Entradas >= 30
- ROI >= 5%
- Lucro >= 5.0

### Coluna ODD H CALC / ODD D CALC / ODD A CALC
- **Verde com ✓:** Value Bet (SIM) - Melhor oportunidade
- **Vermelho com ✗:** Bad Bet (NÃO) - Evitar
- **Laranja com ◆:** Neutral Bet (ACEITÁVEL) - Mediocre

## 📈 Como Usar

### 1. Validar Próximas Rodadas
1. Acesse: http://localhost:8000/proxima_rodada.html
2. Veja a coluna VALIDADA:
   - **SIM** = Entrada qualificada, pode entrar no mercado
   - **NÃO** = Entrada não qualificada, evitar
3. Combine com análise visual (xG, DxG, CFG)
4. Clique "Salvar" para registrar a aposta

### 2. Acompanhar Apostas Salvas
1. Acesse: http://localhost:8000/jogos_salvos.html
2. Veja resultados de apostas anteriores
3. Analise o desempenho

### 3. Analisar Backtest
1. Acesse: http://localhost:5001/backtest_resumo_entradas.html
2. Filtre por liga
3. Veja estatísticas de cada tipo de entrada
4. Use para confirmar critérios de entrada

## 🔧 Requisitos

- Python 3.8+
- Flask
- Pandas
- Requests

### Instalar dependências
```bash
pip install -r requirements.txt
```

## 📝 Arquivos de Configuração

### DOCUMENTACAO_FORMATACAO_PAGINAS.md
Documentação completa sobre:
- CSS das 6 páginas
- Localização exata de cada formatação
- Como fazer alterações futuras
- Mapeamento de cores e ícones

### RELATORIO_ENTRADAS_QUALIFICADAS.txt
Relatório das 40 entradas que atendem aos critérios:
- Liga
- Tipo (HOME/AWAY)
- DxG (FH, LH, EQ, LA, FA)
- Estatísticas (ROI, Lucro, Winrate)

## 🐛 Troubleshooting

### Porta 8000 ou 5001 em uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Arquivos HTML não atualizando
1. Pressione Ctrl+Shift+R no navegador (hard refresh)
2. Ou delete o cache do navegador

### Servidor não inicia
1. Verifique se Python está instalado: `python --version`
2. Verifique dependências: `pip list | grep flask`
3. Verifique se arquivo JSON existe: `ls fixtures/backtest_acumulado.json`

## 📊 Relatório de Entradas

Para gerar um novo relatório:
```bash
python gerar_relatorio_entradas.py
```

Saída: `RELATORIO_ENTRADAS_QUALIFICADAS.txt`

## 📖 Documentação Adicional

- [DOCUMENTACAO_FORMATACAO_PAGINAS.md](DOCUMENTACAO_FORMATACAO_PAGINAS.md) - CSS e formatação visual
- [README.md](README.md) - Documentação geral do projeto

## 🚀 Próximas Melhorias

- [ ] Dashboard consolidado
- [ ] Alertas de novas entradas qualificadas
- [ ] Histórico de performance por critério
- [ ] API de dados em tempo real

## 📞 Suporte

Para questões sobre:
- **Formatação visual:** Ver DOCUMENTACAO_FORMATACAO_PAGINAS.md
- **Dados de backtest:** Ver RELATORIO_ENTRADAS_QUALIFICADAS.txt
- **Estrutura geral:** Ver README.md

---

**Versão:** 1.0  
**Data:** 3 de fevereiro de 2026  
**Status:** ✅ Operacional
