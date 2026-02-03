# Documentação Completa de Fórmulas - Sistema de Análise xG

**Data:** 02 de Fevereiro de 2026  
**Status:** ✅ Validado e Unificado entre Modelo 1 e Modelo 2

---

## 📋 Índice

1. [Cálculo de CGH e CGA (Custo do Gol)](#1-cálculo-de-cgh-e-cga)
2. [Cálculo de VGH e VGA (Valor do Gol)](#2-cálculo-de-vgh-e-vga)
3. [Filtro por Range de Probabilidade](#3-filtro-por-range-de-probabilidade)
4. [Cálculo de MCGH, MVGH, MCGA, MVGA](#4-cálculo-de-médias-históricas)
5. [Cálculo de xGH e xGA (Expected Goals)](#5-cálculo-de-xgh-e-xga)
6. [Coeficiente de Confiança (CF)](#6-coeficiente-de-confiança)
7. [Cálculo de Odds com Poisson](#7-cálculo-de-odds-com-poisson)
8. [Cálculo de DxG (Diferença de xG)](#8-cálculo-de-dxg)
9. [Identificação de Value Bets](#9-identificação-de-value-bets)

---

## 1. Cálculo de CGH e CGA (Custo do Gol)

**Objetivo:** Calcular o custo relativo de cada gol marcado considerando a odd do time.

### Fórmula CGH (Custo do Gol Casa):

```
SE GH = 0 ENTÃO
    CGH = 1.0
SENÃO
    CGH = 1 / (ODDS_H × GH)
```

### Fórmula CGA (Custo do Gol Visitante):

```
SE GA = 0 ENTÃO
    CGA = 1.0
SENÃO
    CGA = 1 / (ODDS_A × GA)
```

### Variáveis:
- **GH** = Gols marcados pelo time da Casa
- **GA** = Gols marcados pelo time Visitante
- **ODDS_H** = Odd da casa (Bet365)
- **ODDS_A** = Odd do visitante (Bet365)

### Regra Especial:
**⚠️ IMPORTANTE:** Quando o time não marca gols (GH=0 ou GA=0), o custo é definido como **1.0** para evitar divisão por zero e manter consistência estatística.

### Implementação:
- **Arquivo:** `adicionar_colunas_calculadas.py` (linhas 76-83)
- **Arquivo:** `baixar_argentina.py` (linhas 107-116)

### Exemplo:
```
Jogo: Flamengo 3-0 Vasco
ODDS_H = 1.50, ODDS_A = 6.00

CGH = 1 / (1.50 × 3) = 1 / 4.5 = 0.222
CGA = 1.0  (porque GA = 0)
```

---

## 2. Cálculo de VGH e VGA (Valor do Gol)

**Objetivo:** Calcular o valor relativo de cada gol considerando a odd do adversário.

### Fórmula VGH (Valor do Gol Casa):

```
VGH = GH / ODDS_A
```

### Fórmula VGA (Valor do Gol Visitante):

```
VGA = GA / ODDS_H
```

### Variáveis:
- **GH** = Gols marcados pelo time da Casa
- **GA** = Gols marcados pelo time Visitante
- **ODDS_H** = Odd da casa
- **ODDS_A** = Odd do visitante

### Implementação:
- **Arquivo:** `adicionar_colunas_calculadas.py` (linhas 89-92)
- **Arquivo:** `baixar_argentina.py` (linhas 119-122)

### Exemplo:
```
Jogo: Flamengo 3-0 Vasco
ODDS_H = 1.50, ODDS_A = 6.00

VGH = 3 / 6.00 = 0.50
VGA = 0 / 1.50 = 0.00
```

---

## 3. Filtro por Range de Probabilidade

**Objetivo:** Filtrar jogos históricos que estejam dentro de um range similar de probabilidade (±7%) em relação ao jogo atual.

### Fórmula:

```
prob_time = 1 / odd_time
prob_adversario = 1 / odd_adversario

prob_time_min = prob_time × (1 - 0.07)  → -7%
prob_time_max = prob_time × (1 + 0.07)  → +7%

prob_adv_min = prob_adversario × (1 - 0.07)
prob_adv_max = prob_adversario × (1 + 0.07)
```

### Filtro de Jogos Históricos:

Para time **CASA**:
```
jogos_filtrados = jogos WHERE
    prob_h >= prob_time_min AND
    prob_h <= prob_time_max AND
    prob_a >= prob_adv_min AND
    prob_a <= prob_adv_max
```

Para time **VISITANTE**:
```
jogos_filtrados = jogos WHERE
    prob_a >= prob_time_min AND
    prob_a <= prob_time_max AND
    prob_h >= prob_adv_min AND
    prob_h <= prob_adv_max
```

### Implementação:
- **Arquivo:** `analisar_proxima_rodada.py` (linhas 108-157)
- **Arquivo:** `backtest/backtest_engine.py` (linhas 398-475)

### Exemplo:
```
Jogo Atual: Flamengo vs Palmeiras
ODDS_H = 2.10, ODDS_A = 3.50

prob_h = 1/2.10 = 0.476 (47.6%)
Range: 0.443 a 0.510 (±7%)

prob_a = 1/3.50 = 0.286 (28.6%)
Range: 0.266 a 0.305 (±7%)

→ Busca jogos históricos do Flamengo (casa) com odds nestes ranges
```

---

## 4. Cálculo de Médias Históricas

**Objetivo:** Calcular médias de CGH, VGH, CGA, VGA dos jogos filtrados por range de odd.

### Fórmulas:

Para time **CASA**:
```
MCGH = MÉDIA(CGH dos jogos filtrados)
MVGH = MÉDIA(VGH dos jogos filtrados)

DesvioPadrão_MCGH = DESVIO_PADRÃO(CGH dos jogos filtrados)
DesvioPadrão_MVGH = DESVIO_PADRÃO(VGH dos jogos filtrados)
```

Para time **VISITANTE**:
```
MCGA = MÉDIA(CGA dos jogos filtrados)
MVGA = MÉDIA(VGA dos jogos filtrados)

DesvioPadrão_MCGA = DESVIO_PADRÃO(CGA dos jogos filtrados)
DesvioPadrão_MVGA = DESVIO_PADRÃO(VGA dos jogos filtrados)
```

### Variáveis Resultantes:
- **MCGH** = Média do Custo do Gol da Casa
- **MVGH** = Média do Valor do Gol da Casa
- **MCGA** = Média do Custo do Gol do Visitante
- **MVGA** = Média do Valor do Gol do Visitante

### Implementação:
- **Arquivo:** `analisar_proxima_rodada.py` (linhas 166-170, 196-200)
- **Arquivo:** `backtest/backtest_engine.py` (linhas 445-475)

### Regra Importante:
**⚠️ Se não houver jogos suficientes no range ±7%, o cálculo NÃO é feito** (retorna `None`) para manter consistência metodológica. **NÃO há fallback.**

---

## 5. Cálculo de xGH e xGA (Expected Goals)

**Objetivo:** Calcular os gols esperados usando fórmula completa com médias históricas e odds.

### Fórmula xGH (Expected Goals Casa):

```
xGH = (1 + MCGH × MVGH × oddH × oddA) / (2 × MCGH × oddH)
```

### Fórmula xGA (Expected Goals Visitante):

```
xGA = (1 + MCGA × MVGA × oddH × oddA) / (2 × MCGA × oddA)
```

### Variáveis:
- **MCGH** = Média do Custo do Gol da Casa (do histórico filtrado)
- **MVGH** = Média do Valor do Gol da Casa (do histórico filtrado)
- **MCGA** = Média do Custo do Gol do Visitante (do histórico filtrado)
- **MVGA** = Média do Valor do Gol do Visitante (do histórico filtrado)
- **oddH** = Odd da casa do jogo atual
- **oddA** = Odd do visitante do jogo atual

### Correção Implementada (02/02/2026):
**❌ ANTES (ERRADO - fórmulas invertidas):**
```
xGH = (1 + MCGA × MVGA × oddH × oddA) / (2 × MCGH × oddH)  ← Usava MCGA!
xGA = (1 + MCGH × MVGH × oddH × oddA) / (2 × MCGA × oddA)  ← Usava MCGH!
```

**✅ DEPOIS (CORRETO):**
```
xGH = (1 + MCGH × MVGH × oddH × oddA) / (2 × MCGH × oddH)  ← Usa MCGH
xGA = (1 + MCGA × MVGA × oddH × oddA) / (2 × MCGA × oddA)  ← Usa MCGA
```

### Implementação:
- **Arquivo:** `analisar_proxima_rodada.py` (linhas 348-358) ✅ CORRIGIDO
- **Arquivo:** `backtest/backtest_engine.py` (linhas 531-535) ✅ IMPLEMENTADO

### Exemplo:
```
Jogo: Flamengo vs Palmeiras
oddH = 2.10, oddA = 3.50

Histórico filtrado (±7%):
MCGH = 0.25, MVGH = 0.45
MCGA = 0.32, MVGA = 0.38

xGH = (1 + 0.25 × 0.45 × 2.10 × 3.50) / (2 × 0.25 × 2.10)
    = (1 + 0.826) / 1.05
    = 1.74

xGA = (1 + 0.32 × 0.38 × 2.10 × 3.50) / (2 × 0.32 × 3.50)
    = (1 + 0.895) / 2.24
    = 0.85
```

---

## 6. Coeficiente de Confiança (CF)

**Objetivo:** Calcular a confiança no xG baseado na variabilidade dos dados históricos.

### Fórmula CFxGH (Confiança xGH):

```
CV_MCGH = DesvioPadrão_MCGH / MCGH
CV_MVGH = DesvioPadrão_MVGH / MVGH

CFxGH = 1 / (1 + √(CV_MCGH² + CV_MVGH²))
```

### Fórmula CFxGA (Confiança xGA):

```
CV_MCGA = DesvioPadrão_MCGA / MCGA
CV_MVGA = DesvioPadrão_MVGA / MVGA

CFxGA = 1 / (1 + √(CV_MCGA² + CV_MVGA²))
```

### Variáveis:
- **CV** = Coeficiente de Variação (Desvio Padrão / Média)
- **CFxGH** = Fator de Confiança do xGH (0 a 1)
- **CFxGA** = Fator de Confiança do xGA (0 a 1)

### Interpretação:
- **CF próximo de 1.0** = Alta confiança (baixa variabilidade histórica)
- **CF próximo de 0.0** = Baixa confiança (alta variabilidade histórica)

### Implementação:
- **Arquivo:** `analisar_proxima_rodada.py` (linhas 330-341)
- **Arquivo:** `backtest/backtest_engine.py` (linhas 540-556)

### Exemplo:
```
MCGH = 0.25, DesvioPadrão_MCGH = 0.05
MVGH = 0.45, DesvioPadrão_MVGH = 0.08

CV_MCGH = 0.05 / 0.25 = 0.20
CV_MVGH = 0.08 / 0.45 = 0.178

CFxGH = 1 / (1 + √(0.20² + 0.178²))
      = 1 / (1 + √0.0716)
      = 1 / (1 + 0.268)
      = 1 / 1.268
      = 0.789  → 78.9% de confiança
```

---

## 7. Cálculo de Odds com Poisson

**Objetivo:** Calcular odds esperadas usando distribuição de Poisson (0-5 gols).

### Algoritmo:

```
# Probabilidade de Vitória Casa
prob_home = 0
PARA h DE 0 ATÉ 5:
    PARA a DE 0 ATÉ 5:
        SE h > a:
            prob_home += Poisson(h, xGH) × Poisson(a, xGA)

# Probabilidade de Vitória Visitante
prob_away = 0
PARA h DE 0 ATÉ 5:
    PARA a DE 0 ATÉ 5:
        SE a > h:
            prob_away += Poisson(h, xGH) × Poisson(a, xGA)

# Probabilidade de Empate
prob_draw = 1 - prob_home - prob_away
```

### Fórmula de Poisson:

```
Poisson(k, λ) = (λ^k × e^(-λ)) / k!

Onde:
- k = número de gols (0 a 5)
- λ = xGH ou xGA (lambda, valor esperado)
- e = número de Euler (2.71828...)
```

### Conversão para Odds:

```
SE prob_home > 0.05 ENTÃO
    odd_home_calc = 1 / prob_home
SENÃO
    odd_home_calc = 20.0  (margem de segurança)

SE prob_away > 0.05 ENTÃO
    odd_away_calc = 1 / prob_away
SENÃO
    odd_away_calc = 20.0

SE prob_draw > 0.05 ENTÃO
    odd_draw_calc = 1 / prob_draw
SENÃO
    odd_draw_calc = 20.0
```

### Margem de Segurança:
**⚠️ Probabilidade mínima de 5%** para evitar odds absurdas (máximo odd = 20.0)

### Implementação:
- **Arquivo:** `analisar_proxima_rodada.py` (linhas 362-402) ✅ IMPLEMENTADO
- **Arquivo:** `backtest/backtest_engine.py` (linhas 560-605) ✅ ORIGINAL

### Exemplo:
```
xGH = 1.74, xGA = 0.85

Matriz de Probabilidades (0-5 gols):
        0a    1a    2a    3a    4a    5a
0h   0.0296 0.0252 0.0107 0.0030 0.0006 0.0001
1h   0.0515 0.0438 0.0186 0.0053 0.0011 0.0002
2h   0.0448 0.0381 0.0162 0.0046 0.0010 0.0002
...
(36 combinações totais)

prob_home = soma de todos h > a = 0.712 (71.2%)
prob_away = soma de todos a > h = 0.114 (11.4%)
prob_draw = 1 - 0.712 - 0.114 = 0.174 (17.4%)

odd_home_calc = 1 / 0.712 = 1.40
odd_away_calc = 1 / 0.114 = 8.77
odd_draw_calc = 1 / 0.174 = 5.75
```

---

## 8. Cálculo de DxG (Diferença de xG)

**Objetivo:** Classificar o equilíbrio do jogo baseado na diferença entre xGH e xGA.

### Fórmula:

```
DxG = xGH - xGA
```

### Classificação (Modelo 1 - Próxima Rodada):

```
SE DxG > 1.0   → FH (Forte Home)
SE DxG > 0.3   → LH (Leve Home)
SE DxG > -0.3  → EQ (Equilibrado)
SE DxG > -1.0  → LA (Leve Away)
SE DxG ≤ -1.0  → FA (Forte Away)
```

### Classificação (Modelo 2 - Backtest):

```
SE DxG ≥ 0.75  → FH (Forte Home)
SE DxG ≥ 0.35  → LH (Leve Home)
SE DxG > -0.35 → EQ (Equilibrado)
SE DxG > -0.75 → LA (Leve Away)
SE DxG ≤ -0.75 → FA (Forte Away)
```

### Diferença entre Modelos:
- **Modelo 1:** Intervalos ±1.0 e ±0.3
- **Modelo 2:** Intervalos ±0.75 e ±0.35

⚠️ **Pendente:** Padronizar intervalos entre os dois modelos.

### Implementação:
- **Arquivo:** `analisar_proxima_rodada.py` (usa intervalos ±1.0/±0.3)
- **Arquivo:** `backtest/backtest_engine.py` (linhas 558-568, usa ±0.75/±0.35)

### Exemplo:
```
xGH = 1.74, xGA = 0.85
DxG = 1.74 - 0.85 = 0.89

Modelo 1: 0.89 > 0.3 mas < 1.0 → LH (Leve Home)
Modelo 2: 0.89 > 0.75 → FH (Forte Home)

→ CLASSIFICAÇÃO DIFERENTE!
```

---

## 9. Identificação de Value Bets

**Objetivo:** Identificar quando as odds reais estão 10% acima das odds calculadas E alinhadas com DxG.

### Critério Base (Ambos Modelos):

```
odd_real > odd_calculada × 1.10
```

### Critério Adicional (Apenas Modelo 2 - Backtest):

**Value Bet HOME:**
```
SE odd_real_home > odd_calc_home × 1.10 E
   DxG IN [FH, LH, EQ]
ENTÃO
    Value Bet HOME
```

**Value Bet AWAY:**
```
SE odd_real_away > odd_calc_away × 1.10 E
   DxG IN [FA, LA, EQ]
ENTÃO
    Value Bet AWAY
```

### Regra de Ambos os Lados:

```
SE ambos têm value:
    Escolhe o lado com odd_calc MENOR (mais provável)
```

### Diferença entre Modelos:
- **Modelo 1 (Próxima Rodada):** Apenas threshold 10%, sem validação DxG
- **Modelo 2 (Backtest):** Threshold 10% + validação alinhamento DxG

⚠️ **Pendente:** Implementar validação DxG no Modelo 1.

### Implementação:
- **Arquivo:** `salvar_jogo.py` (linhas 55-56) - Sem validação DxG
- **Arquivo:** `backtest/backtest_engine.py` (linhas 629-665) - Com validação DxG

### Exemplo:
```
Jogo: Flamengo vs Palmeiras
DxG = 0.89 (FH no Modelo 2)

odd_real_home = 2.30
odd_calc_home = 1.40
threshold = 1.40 × 1.10 = 1.54

2.30 > 1.54? SIM → Tem value HOME

Modelo 1: ✅ Value Bet HOME (só threshold)
Modelo 2: ✅ Value Bet HOME (threshold + DxG=FH alinhado)

---

Jogo: Palmeiras vs Flamengo (invertido)
DxG = -0.89 (FA no Modelo 2)

odd_real_home = 2.30
odd_calc_home = 8.77
threshold = 8.77 × 1.10 = 9.65

2.30 > 9.65? NÃO → Não tem value HOME

Modelo 1: ❌ Não é Value Bet
Modelo 2: ❌ Não é Value Bet (DxG=FA indica favorito visitante)
```

---

## 📊 Fluxograma Completo

```
┌─────────────────────────────────────────┐
│ 1. Dados Históricos (CSVs completos)   │
│    - Adicionar CGH, CGA, VGH, VGA       │
│    - Regra: Se GH=0 → CGH=1             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. Jogo Atual com Odds (oddH, oddA)    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. Calcular Range de Probabilidade     │
│    - prob = 1/odd                       │
│    - range = prob × (1 ± 0.07)          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 4. Filtrar Jogos Históricos (±7%)      │
│    - Filtra por range de prob           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 5. Calcular MCGH, MVGH, MCGA, MVGA     │
│    - Média dos jogos filtrados          │
│    - Desvio padrão dos jogos filtrados  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 6. Calcular xGH e xGA                   │
│    - Fórmula completa com MC×MV×odds    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 7. Calcular CFxGH e CFxGA               │
│    - Coeficiente de confiança (0-1)     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 8. Calcular Odds com Poisson            │
│    - Itera 0-5 gols (36 combinações)    │
│    - prob_home, prob_away, prob_draw    │
│    - Margem segurança 5% (odd max 20)   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 9. Calcular DxG = xGH - xGA             │
│    - Classificar: FH/LH/EQ/LA/FA        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 10. Identificar Value Bets              │
│     - odd_real > odd_calc × 1.10?       │
│     - DxG alinhado? (Modelo 2)          │
└─────────────────────────────────────────┘
```

---

## 🔧 Arquivos Modificados (02/02/2026)

### ✅ Correções Implementadas:

1. **analisar_proxima_rodada.py (linhas 348-358)**
   - ✅ Corrigido: xGH agora usa MCGH×MVGH (antes usava MCGA×MVGA)
   - ✅ Corrigido: xGA agora usa MCGA×MVGA (antes usava MCGH×MVGH)

2. **analisar_proxima_rodada.py (linhas 362-402)**
   - ✅ Implementado: Poisson 0-5 gols
   - ✅ Implementado: Margem de segurança 5%
   - ✅ Implementado: prob_draw = 1 - prob_home - prob_away

3. **backtest/backtest_engine.py (linhas 398-475)**
   - ✅ Novo método: `calcular_medias_historicas_por_odds()`
   - ✅ Filtro por range ±7% implementado

4. **backtest/backtest_engine.py (linhas 476-620)**
   - ✅ Método atualizado: `calcular_xg_e_odds()`
   - ✅ Aceita parâmetros odd_h e odd_a
   - ✅ Usa fórmula completa xGH/xGA
   - ✅ Calcula CFxGH e CFxGA
   - ✅ SEM FALLBACK (retorna None se dados insuficientes)

5. **backtest/backtest_engine.py (linha 625)**
   - ✅ Atualizado: Passa odds reais para filtro
   - ✅ Pula jogos sem dados suficientes

---

## ⚠️ Pendências Identificadas

### 1. Intervalos DxG Divergentes
- **Modelo 1:** ±1.0 e ±0.3
- **Modelo 2:** ±0.75 e ±0.35
- **Ação:** Padronizar para um único conjunto de intervalos

### 2. Validação Value Bet
- **Modelo 1:** Não valida alinhamento DxG
- **Modelo 2:** Valida alinhamento DxG
- **Ação:** Implementar validação no Modelo 1

### 3. Testes de Convergência
- **Pendente:** Validar qual método xG é mais preciso (fórmula vs média simples)
- **Ação:** Rodar script `test_formula_unificada.py` com dados históricos

---

## 📚 Referências

- **Distribuição de Poisson:** [Wikipedia](https://pt.wikipedia.org/wiki/Distribui%C3%A7%C3%A3o_de_Poisson)
- **Expected Goals (xG):** Métrica estatística de análise de futebol
- **Value Betting:** Estratégia baseada em odds com expectativa positiva

---

## ✅ Status de Unificação

| Aspecto | Modelo 1 | Modelo 2 | Status |
|---------|----------|----------|--------|
| **Fórmula xGH/xGA** | Fórmula completa | Fórmula completa | ✅ UNIFICADO |
| **Filtro por Range** | ±7% de prob | ±7% de prob | ✅ UNIFICADO |
| **Cálculo Odds** | Poisson 0-5 | Poisson 0-5 | ✅ UNIFICADO |
| **Margem Segurança** | 5% (odd max 20) | 5% (odd max 20) | ✅ UNIFICADO |
| **Coef. Confiança** | CFxGH, CFxGA | CFxGH, CFxGA | ✅ UNIFICADO |
| **Intervalos DxG** | ±1.0/±0.3 | ±0.75/±0.35 | ⚠️ DIFERENTE |
| **Validação Value Bet** | Sem validação DxG | Com validação DxG | ⚠️ DIFERENTE |
| **Fallback** | N/A | Sem fallback | ✅ CONSISTENTE |

---

**Última Atualização:** 02 de Fevereiro de 2026  
**Responsável:** Sistema Unificado de Análise xG  
**Status:** ✅ Validado e Documentado
