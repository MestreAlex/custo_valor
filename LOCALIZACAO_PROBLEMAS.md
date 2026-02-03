# 🗂️ LOCALIZAÇÃO DOS PROBLEMAS NO CÓDIGO

## Referência Rápida para Desenvolvedores

---

## PROBLEMA #1: Cálculo de xGH e xGA

### Próxima Rodada ❌ (MÉTODO 1)

**Arquivo:** `analisar_proxima_rodada.py`
**Linhas:** 348-358
**Função:** (Bloco de cálculo principal no loop de fixtures)

```python
# Linhas 348-358
if mcgh is not None and mcga is not None and mvga is not None:
    try:
        # xGH = (1 + MCGA * MVGA * oddH * oddA) / (2 * MCGH * oddH)
        xgh = (1 + mcga * mvga * odd_h * odd_a) / (2 * mcgh * odd_h)
        df_fixtures.at[idx, 'xGH'] = xgh
    except:
        pass

if mcga is not None and mcgh is not None and mvgh is not None:
    try:
        # xGA = (1 + MCGH * MVGH * oddH * oddA) / (2 * MCGA * oddA)
        xga = (1 + mcgh * mvgh * odd_h * odd_a) / (2 * mcga * odd_a)
        df_fixtures.at[idx, 'xGA'] = xga
    except:
        pass
```

**Também precisa verificar:**
- Linhas 300-320: Cálculo de MCGH, MVGH, MCGA, MVGA
- Linhas 330-341: Cálculo de CFxGH e CFxGA (coeficiente de confiança)

**Problema:** Fórmula muito complexa, usa odds de mercado multiplicativamente

---

### Backtest ✅ (MÉTODO 2)

**Arquivo:** `backtest_engine.py`
**Linhas:** 366-410
**Função:** `calcular_xg_e_odds(self, home_team, away_team)`

```python
# Linhas 372-391: Extração de dados
jogos_home = self.df_treino[self.df_treino[self.coluna_home] == home_team].copy()
jogos_away = self.df_treino[self.df_treino[self.coluna_away] == away_team].copy()

n_jogos = 10

if len(jogos_home) >= n_jogos:
    jogos_home_recent = jogos_home.tail(n_jogos)
else:
    jogos_home_recent = jogos_home
    
if len(jogos_away) >= n_jogos:
    jogos_away_recent = jogos_away.tail(n_jogos)
else:
    jogos_away_recent = jogos_away

# Linhas 392-410: Cálculo de xG
if len(jogos_home_recent) > 0:
    home_gols_feitos = jogos_home_recent[self.coluna_gols_home].mean()
    home_gols_sofridos = jogos_home_recent[self.coluna_gols_away].mean()
else:
    home_gols_feitos = 1.5
    home_gols_sofridos = 1.5
    
if len(jogos_away_recent) > 0:
    away_gols_feitos = jogos_away_recent[self.coluna_gols_away].mean()
    away_gols_sofridos = jogos_away_recent[self.coluna_gols_home].mean()
else:
    away_gols_feitos = 1.0
    away_gols_sofridos = 1.5

# Calcular xG esperado
xgh = (home_gols_feitos + away_gols_sofridos) / 2
xga = (away_gols_feitos + home_gols_sofridos) / 2
```

**Também precisa verificar:**
- Linhas 414-419: Cálculo de DxG e classificação

**Vantagem:** Fórmula simples, baseada em dados reais

---

## PROBLEMA #2: Cálculo de Odds

### Próxima Rodada ❌ (MÉTODO 1)

**Arquivo:** `salvar_jogo.py`
**Linhas:** 1278-1285
**Função:** (Bloco de cálculo em `analisar_padroes_jogos_ia` ou similar)

```python
# Linhas 1278-1285
if 'ODD_H_CALC' not in jogo_normalizado and 'xGH' in jogo_normalizado:
    xgh_val = float(jogo_normalizado.get('xGH', 1))
    xga_val = float(jogo_normalizado.get('xGA', 1))
    # Fórmula simplificada: odd_casa = 1 / (xGH / (xGH + xGA))
    if (xgh_val + xga_val) > 0:
        prob_casa = xgh_val / (xgh_val + xga_val)
        jogo_normalizado['ODD_H_CALC'] = 1 / prob_casa if prob_casa > 0 else 2.0
        jogo_normalizado['ODD_A_CALC'] = 1 / (1 - prob_casa) if (1 - prob_casa) > 0 else 2.0
```

**Problema:** Simplificado demais, não considera distribuição real de gols

---

### Backtest ✅ (MÉTODO 2)

**Arquivo:** `backtest_engine.py`
**Linhas:** 422-448
**Função:** `calcular_xg_e_odds(self, home_team, away_team)` (continuação)

```python
# Linhas 422-448
# Calcular odds esperadas usando distribuição de Poisson
from scipy.stats import poisson

# Probabilidade de vitória da casa
prob_home = 0
for h in range(0, 6):
    for a in range(0, 6):
        if h > a:
            prob_home += poisson.pmf(h, xgh) * poisson.pmf(a, xga)

# Probabilidade de vitória visitante
prob_away = 0
for h in range(0, 6):
    for a in range(0, 6):
        if a > h:
            prob_away += poisson.pmf(h, xgh) * poisson.pmf(a, xga)

# Probabilidade de empate
prob_draw = 1 - prob_home - prob_away

# Converter para odds (com margem de segurança)
odd_home_calc = 1 / prob_home if prob_home > 0.05 else 20
odd_away_calc = 1 / prob_away if prob_away > 0.05 else 20
```

**Vantagem:** Poisson é estatisticamente correto, considera empates, margem de segurança

---

## PROBLEMA #3: Intervalo DxG

### Próxima Rodada

**Arquivo:** `salvar_jogo.py`
**Linhas:** 110-130
**Função:** `_calcular_dxg(xgh, xga)`

```python
# Linhas 110-130
def _calcular_dxg(xgh, xga):
    """Calcula a classificação DxG baseada na diferença entre xGH e xGA"""
    try:
        gh = float(xgh) if xgh is not None else 0
        ga = float(xga) if xga is not None else 0
        diff = gh - ga
        
        if diff < -1.0:
            return 'FA'  # Forte Away
        elif -1.0 <= diff < -0.3:
            return 'LA'  # Leve Away
        elif -0.3 <= diff <= 0.3:
            return 'EQ'  # Equilibrado
        elif 0.3 < diff <= 1.0:
            return 'LH'  # Leve Home
        else:  # diff > 1.0
            return 'FH'  # Forte Home
    except Exception:
        return '-'
```

**Intervalos:**
- FA: DxG < -1.0
- LA: -1.0 ≤ DxG < -0.3
- EQ: -0.3 ≤ DxG ≤ 0.3
- LH: 0.3 < DxG ≤ 1.0
- FH: DxG > 1.0

---

### Backtest

**Arquivo:** `backtest_engine.py`
**Linhas:** 414-419
**Função:** (Continuação de `calcular_xg_e_odds`)

```python
# Linhas 414-419
# Calcular DxG
diff = xgh - xga
if diff >= 0.75:
    dxg = 'FH'
elif diff >= 0.35:
    dxg = 'LH'
elif diff > -0.35:
    dxg = 'EQ'
elif diff > -0.75:
    dxg = 'LA'
else:
    dxg = 'FA'
```

**Intervalos:**
- FH: DxG >= 0.75
- LH: 0.35 ≤ DxG < 0.75
- EQ: -0.35 < DxG < 0.35
- LA: -0.75 < DxG ≤ -0.35
- FA: DxG <= -0.75

**NOTA:** Backtest usa **0.75** e **0.35**, enquanto Próxima Rodada usa **1.0** e **0.3**
→ Pode gerar classificações diferentes em zonas limítrofes!

---

## CRITÉRIO DE VALUE BET

### Próxima Rodada

**Arquivo:** `salvar_jogo.py`
**Linhas:** 55-56
**Função:** `_calcular_lp()`

```python
# Linhas 55-56
# Verificar value bets (10% de margem)
value_home = b365h > (odd_h_calc * 1.1)
value_away = b365a > (odd_a_calc * 1.1)
```

**Simples:** Apenas 10% acima das odds calculadas

---

### Backtest

**Arquivo:** `backtest_engine.py`
**Linhas:** 461-488
**Função:** `identificar_value_bets()`

```python
# Linhas 461-488
def identificar_value_bets(self, rodada_jogos):
    """
    Identifica value bets na rodada
    Value bet: odd da casa > odd calculada * 1.1
    A entrada deve estar alinhada com o DxG
    """
    value_bets = []
    
    for jogo in rodada_jogos:
        # ... [extração de dados]
        
        # Verificar se cada lado tem value (10% ou mais)
        has_value_home = b365h > calc['odd_home_calc'] * 1.1
        has_value_away = b365a > calc['odd_away_calc'] * 1.1
        
        entrada = None
        
        # Se ambos os lados têm value, escolhe o mais provável (odd menor)
        if has_value_home and has_value_away:
            if calc['odd_home_calc'] < calc['odd_away_calc']:
                entrada = 'HOME'
            else:
                entrada = 'AWAY'
        # Se só HOME tem value, verifica se está alinhado com DxG
        elif has_value_home:
            if dxg in ['FH', 'LH', 'EQ']:
                entrada = 'HOME'
        # Se só AWAY tem value, verifica se está alinhado com DxG
        elif has_value_away:
            if dxg in ['FA', 'LA', 'EQ']:
                entrada = 'AWAY'
```

**Mais sofisticado:**
- 10% acima das odds calculadas
- MAIS: Validação contra DxG
- Apenas HOME pode entrar se DxG favorece HOME
- Apenas AWAY pode entrar se DxG favorece AWAY

---

## RESUMO PARA AÇÃO

### Se Quiser Corrigir Próxima Rodada

```bash
# Arquivo 1: Atualizar xGH/xGA
vim analisar_proxima_rodada.py  # Linhas 348-358

# Arquivo 2: Atualizar Odds
vim salvar_jogo.py  # Linhas 1278-1285

# Arquivo 3: Verificar DxG
vim salvar_jogo.py  # Linhas 110-130 (considerar atualizar para 0.75)

# Arquivo 4: Adicionar validação de Value Bet com DxG
vim salvar_jogo.py  # Após linha 56
```

### Se Quiser Usar Backtest em Próxima Rodada

```bash
# Solução 1: Copiar função
cp backtest_engine.py:366-448 → novo_arquivo.py

# Solução 2: Importar diretamente
# Em analisar_proxima_rodada.py, adicionar:
from backtest.backtest_engine import BacktestEngine
engine = BacktestEngine()
xgh, xga = engine.calcular_xg_e_odds(home_team, away_team)
```

---

**Referência de Código | 02 de Fevereiro de 2026**
