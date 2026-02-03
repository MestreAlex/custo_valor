# 🏈 Sistema de Análise de Futebol - Validação de Entradas Qualificadas

Sistema completo para análise, validação e acompanhamento de apostas esportivas com base em backtest histórico e critérios de qualificação.

## ✨ Principais Características

✅ **6 Páginas Web Interativas**
- Análise de próxima rodada com validação de entradas
- Histórico de jogos salvos
- Análise AI de padrões
- Dashboard de backtest
- Resumo de entradas qualificadas

✅ **Validação Inteligente**
- 40 entradas qualificadas identificadas
- Filtros: Entradas >= 30, ROI >= 5%, Lucro >= 5.0
- Comparação automática Liga + Tipo + DxG

✅ **Formatação Visual Consistente**
- Tema escuro com cyan (#00d4ff)
- Value Bets destacadas em verde
- Bad Bets em vermelho
- Neutral Bets em laranja

## 🚀 Quick Start

### Opção 1: Script Automático (Recomendado)

**Python:**
```bash
python iniciar_todos_servidores.py
```

**PowerShell (Windows):**
```powershell
.\iniciar_todos_servidores.ps1
```

### Opção 2: Iniciar Manualmente

```bash
# Terminal 1
python servidor_api.py

# Terminal 2
python servidor_analise_backtest.py
```

## 📊 Acessar as Páginas

Após iniciar os servidores, acesse:

### Porto 8000 - Análise de Próxima Rodada

- 🌐 **Próxima Rodada** - http://localhost:8000/proxima_rodada.html
  - Análise de odds e xG
  - Coluna VALIDADA mostra SIM/NÃO para entradas qualificadas
  - Color-coding de value bets

- 💾 **Jogos Salvos** - http://localhost:8000/jogos_salvos.html
  - Histórico de apostas
  - Acompanhamento de resultados

- 📈 **Análise Salvos** - http://localhost:8000/analise_salvos.html
  - Análise AI de padrões
  - Estatísticas por liga

### Porto 5001 - Análise de Backtest

- 📊 **Backtest** - http://localhost:5001/backtest.html
  - Dashboard de backtests

- 💰 **Backtests Salvos** - http://localhost:5001/backtest_salvos.html
  - Histórico de backtests salvos

- 🎯 **Resumo de Entradas** - http://localhost:5001/backtest_resumo_entradas.html
  - **40 entradas qualificadas** por liga, tipo e DxG
  - Filtros: >= 30 entradas, ROI >= 5%, Lucro >= 5.0
  - Top ROI: N1|AWAY|LA (56.81%), E0|AWAY|LH (46.60%), POL|AWAY|FA (39.52%)

## 📁 Estrutura do Projeto

```
custo_valor/
├── 🎨 Formatação e Inicialização
│   ├── iniciar_todos_servidores.py         # Script principal (Python)
│   ├── iniciar_todos_servidores.ps1        # Script principal (PowerShell)
│   ├── DOCUMENTACAO_FORMATACAO_PAGINAS.md  # CSS e formatação visual
│   ├── GUIA_INICIALIZACAO.md               # Este guia
│   └── requirements.txt                    # Dependências Python
│
├── 🌐 Servidores
│   ├── servidor_api.py                     # API e páginas port 8000
│   └── servidor_analise_backtest.py        # Backtest API port 5001
│
├── 📊 Geradores de HTML
│   ├── buscar_proxima_rodada.py            # Gera proxima_rodada.html
│   └── salvar_jogo.py                      # Gera jogos/analise_salvos.html
│
├── 📈 Análise e Relatórios
│   ├── analisar_proxima_rodada.py          # Engine de análise
│   ├── gerar_relatorio_entradas.py         # Gera relatório qualificadas
│   └── RELATORIO_ENTRADAS_QUALIFICADAS.txt # 40 entradas qualificadas
│
├── 📁 Dados
│   ├── fixtures/                           # HTML e dados de próxima rodada
│   │   ├── proxima_rodada.html
│   │   ├── jogos_salvos.html
│   │   ├── analise_salvos.html
│   │   └── backtest_acumulado.json
│   ├── backtest/                           # Dados e páginas de backtest
│   │   ├── backtest.html
│   │   ├── backtest_salvos.html
│   │   └── backtest_resumo_entradas.html
│   ├── dados_ligas/                        # Dados históricos
│   └── dados_ligas_new/                    # Dados consolidados
│
└── 🔧 Testes e Utilitários
    └── test_*.py, debug_*.py               # Vários scripts de análise
```

## 🎯 Coluna VALIDADA Explicada

A página proxima_rodada.html mostra uma coluna **VALIDADA** com dois indicadores:

```
[HOME] [AWAY]
 SIM    NÃO
```

**Verde (SIM):** Entrada está qualificada  
**Vermelho (NÃO):** Entrada não está qualificada

### Critérios de Qualificação

Uma entrada é qualificada se:
- ✅ Liga (ARG, AUT, BRA, CHN, DNK, FIN, IRL, JPN, MEX, NOR, POL, ROU, RUS, SWE, SWZ, USA, E0, E1, D1, D2, I1, I2, F1, F2, SP1, SP2, P1, G1, T1, N1, B1)
- ✅ Tipo (HOME ou AWAY)
- ✅ DxG (FH = Forte Home, LH = Leve Home, EQ = Equilibrado, LA = Leve Away, FA = Forte Away)
- ✅ Entradas: >= 30
- ✅ ROI: >= 5%
- ✅ Lucro: >= 5.0

## 📋 Instalação de Dependências

```bash
pip install -r requirements.txt
```

Dependências:
- Flask 3.0.0
- pandas 2.0.0
- requests 2.31.0
- python-dateutil 2.8.2

## 📖 Documentação Completa

- **[GUIA_INICIALIZACAO.md](GUIA_INICIALIZACAO.md)** - Guia detalhado de inicialização
- **[DOCUMENTACAO_FORMATACAO_PAGINAS.md](DOCUMENTACAO_FORMATACAO_PAGINAS.md)** - CSS e formatação de todas as 6 páginas
- **[RELATORIO_ENTRADAS_QUALIFICADAS.txt](RELATORIO_ENTRADAS_QUALIFICADAS.txt)** - Lista das 40 entradas qualificadas

## 🔧 Troubleshooting

### Porta em Uso
```powershell
# Encontrar processo na porta
netstat -ano | findstr :8000

# Encerrar processo
taskkill /PID <PID> /F
```

### Cache de Página Não Atualiza
Pressione **Ctrl+Shift+R** no navegador para fazer hard refresh

### Servidor Não Inicia
1. Verifique Python: `python --version`
2. Verifique Flask: `pip list | findstr flask`
3. Verifique arquivo JSON: `ls fixtures/backtest_acumulado.json`

## 📊 Gerar Novo Relatório

Para gerar um novo relatório de entradas qualificadas:

```bash
python gerar_relatorio_entradas.py
```

Cria: `RELATORIO_ENTRADAS_QUALIFICADAS.txt`

## 🎨 Customizações Visuais

Todos os estilos CSS estão documentados em:
**[DOCUMENTACAO_FORMATACAO_PAGINAS.md](DOCUMENTACAO_FORMATACAO_PAGINAS.md)**

Inclui:
- Localização exata de cada elemento
- Cores e temas
- Como fazer alterações futuras
- Mapeamento de ícones (✓, ✗, ◆)

## 🚀 Deploy (GitHub)

### Para enviar para GitHub:

1. Criar novo repositório no GitHub (sem inicializar)
2. Executar:
   ```bash
   git remote add origin https://github.com/seu-usuario/seu-repositorio.git
   git branch -M main
   git push -u origin main
   ```

### Para clonar:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd custo_valor
   pip install -r requirements.txt
   python iniciar_todos_servidores.py
   ```

## 📈 Estatísticas de Entradas Qualificadas

Total de entradas qualificadas: **40**

### Distribuição por Tipo:
- AWAY: 22 entradas (55%)
- HOME: 18 entradas (45%)

### Distribuição por DxG:
- FA (Forte Away): 12 entradas
- FH (Forte Home): 10 entradas
- LH (Leve Home): 10 entradas
- LA (Leve Away): 5 entradas
- EQ (Equilibrado): 3 entradas

### Top 5 Melhor ROI:
1. N1 | AWAY | LA - 56.81%
2. E0 | AWAY | LH - 46.60%
3. POL | AWAY | FA - 39.52%
4. SWZ | AWAY | FA - 37.09%
5. FIN | AWAY | FA - 33.58%

## 🤝 Contribuindo

Para fazer alterações:
1. Fazer mudança no código
2. Regenerar HTML: `python buscar_proxima_rodada.py`
3. Testar em http://localhost:8000/proxima_rodada.html
4. Commit: `git add . && git commit -m "descrição"`
5. Push: `git push`

## 📝 Changelog

### v1.0 (3 de fevereiro de 2026)
- ✅ Sistema completo de 6 páginas
- ✅ Coluna VALIDADA com 40 entradas qualificadas
- ✅ Tema visual consistente (cyan dark)
- ✅ Scripts de inicialização automática
- ✅ Documentação completa
- ✅ Repositório Git inicializado

## 📞 Contato

Para dúvidas sobre o projeto, consulte:
- DOCUMENTACAO_FORMATACAO_PAGINAS.md (CSS/Formatação)
- GUIA_INICIALIZACAO.md (Uso)
- RELATORIO_ENTRADAS_QUALIFICADAS.txt (Dados)

---

**Status:** ✅ Operacional  
**Última Atualização:** 3 de fevereiro de 2026  
**Versão:** 1.0
- Salvar jogos para acompanhamento
- Atualizar resultados reais
- Gerar página de jogos salvos

### 4. Visualizar Análises

Abra no navegador:
- `fixtures/proxima_rodada.html` - Ver próximos jogos e análises
- `fixtures/jogos_salvos.html` - Acompanhar jogos salvos

## 📊 Metodologia

### Cálculo de Custo e Valor do Gol

- **CGH** (Custo Gol Home): `1 / (oddH × GH)`
- **CGA** (Custo Gol Away): `1 / (oddA × GA)`
- **VGH** (Valor Gol Home): `GH / oddA`
- **VGA** (Valor Gol Away): `GA / oddH`

### Expected Goals

```
xGH = (1 + MCGA × MVGA × oddH × oddA) / (2 × MCGH × oddH)
xGA = (1 + MCGH × MVGH × oddH × oddA) / (2 × MCGA × oddA)
```

Onde M* são médias históricas filtradas por probabilidade ±7%

### Distribuição de Poisson

Para cada combinação de gols (0-6 vs 0-6):
```
P(GH=gh, GA=ga) = Poisson(gh; λ=xGH) × Poisson(ga; λ=xGA)
```

Probabilidades:
- **Home Win**: Σ P(gh > ga)
- **Draw**: Σ P(gh = ga)
- **Away Win**: Σ P(gh < ga)

Odds calculadas: `ODD = 1 / Probabilidade`

### Color Coding

- 🟢 **Verde** (Value Bet): `B365 > ODD_CALC × 1.10`
- 🟡 **Amarelo** (Neutro): `ODD_CALC ≤ B365 ≤ ODD_CALC × 1.10`
- 🔴 **Vermelho** (Bad Bet): `B365 < ODD_CALC`

## 📋 Funcionalidades

### Página de Próximos Jogos

- ✅ 12 colunas de análise
- ✅ Busca e filtro em tempo real
- ✅ Color-coding de value bets
- ✅ Botão "Salvar" para acompanhamento
- ✅ Navegação entre páginas

### Página de Jogos Salvos

- ✅ Histórico persistente
- ✅ Campos editáveis para resultado real (GH, GA)
- ✅ Estatísticas de acompanhamento
- ✅ Comparação predição vs realidade

### API REST

**POST** `/api/salvar_jogo`
```json
{
  "index": 0
}
```

**POST** `/api/atualizar_resultado`
```json
{
  "id": "abc123",
  "gh": 2,
  "ga": 1
}
```

**POST** `/api/gerar_pagina_salvos`
```json
{}
```

## 🎯 Ligas Suportadas

30 ligas europeias e internacionais:
- **Inglaterra**: Premier League, Championship
- **Alemanha**: Bundesliga, 2. Bundesliga
- **Itália**: Serie A, Serie B
- **França**: Ligue 1, Ligue 2
- **Espanha**: La Liga, La Liga 2
- **Portugal**: Primeira Liga
- **E mais**: Áustria, Brasil, China, Dinamarca, Finlândia, Irlanda, Japão, México, Noruega, Polônia, Romênia, Rússia, Suécia, Suíça, Turquia, Holanda, Bélgica, Grécia, EUA

## 📈 Dados Históricos

- **117.947** jogos históricos
- **14 temporadas** (2012/13 até 2025/26)
- **Fonte**: football-data.co.uk
- **Bookmakers**: Bet365, Pinnacle, Marathonbet, etc.

## ⚙️ Automação

Configure o Task Scheduler do Windows para rodar automaticamente:

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "buscar_proxima_rodada.py" -WorkingDirectory "C:\Users\Alex Menezes\projetos\custo_valor"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Tuesday,Friday -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "BuscarProximaRodada"
```

## 🔧 Comandos Úteis

```bash
# Gerar página de jogos salvos manualmente
python salvar_jogo.py gerar

# Salvar jogo específico (índice da tabela)
python salvar_jogo.py salvar 0

# Atualizar resultado
python salvar_jogo.py atualizar <id> <gh> <ga>
```

## 📝 Notas

- Odds são de Bet365 (B365H, B365D, B365A)
- Análise histórica usa range de ±7% de probabilidade
- São Paulo odd 4.10 retorna NaN (nunca foi tão underdog em casa)
- Ligas sem histórico são automaticamente filtradas
- JSON usado para persistência simples (considerar DB para produção)

## 🐛 Troubleshooting

**"Erro: Arquivo de análise não encontrado"**
→ Execute `buscar_proxima_rodada.py` primeiro

**"Erro ao salvar o jogo"**
→ Verifique se o servidor API está rodando (`python servidor_api.py`)

**"CORS Error"**
→ Flask-CORS está instalado e configurado no servidor_api.py

**Página em branco**
→ Verifique se há jogos disponíveis nas ligas suportadas
