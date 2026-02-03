# Sistema de Análise de Jogos de Futebol

Sistema completo para análise e acompanhamento de apostas esportivas com base em dados históricos e cálculos estatísticos.

## 📁 Estrutura do Projeto

```
custo_valor/
├── buscar_proxima_rodada.py    # Script principal - busca e analisa próximos jogos
├── analisar_proxima_rodada.py  # Engine de análise histórica e Poisson
├── salvar_jogo.py              # Gerenciamento de jogos salvos
├── servidor_api.py             # Servidor Flask para API
├── adicionar_colunas_calculadas.py  # Processamento de dados históricos
├── dados_ligas/                # Dados históricos (14 temporadas)
├── dados_ligas_new/            # Dados consolidados por liga
└── fixtures/                   # Próximos jogos e análises
    ├── proxima_rodada.html     # Página de próximos jogos
    ├── jogos_salvos.html       # Página de jogos acompanhados
    └── jogos_salvos.json       # Banco de dados dos jogos salvos
```

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install pandas numpy requests scipy flask flask-cors
```

### 2. Buscar Próximos Jogos

```bash
python buscar_proxima_rodada.py
```

Este comando:
- Baixa os fixtures de 2 fontes
- Filtra para 30 ligas com dados históricos
- Calcula métricas usando histórico com range ±7%
- Gera expected goals (xGH, xGA)
- Aplica distribuição de Poisson
- Cria HTML com color-coding de value bets

### 3. Iniciar Servidor API

```bash
python servidor_api.py
```

O servidor fica disponível em `http://localhost:5000` e permite:
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
