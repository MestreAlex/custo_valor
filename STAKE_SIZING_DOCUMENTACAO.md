# Stake Sizing para Value Betting

## 🎯 Objetivo

Calcular o tamanho ideal de cada aposta baseado em:
- **ROI médio do modelo**: 18%
- **Odd da entrada**: Odds maiores = menor stake (mais risco)
- **Confiança do modelo**: Coeficientes CF (confianças altas = maior stake)
- **Gestão de risco**: Preservar bankroll e máximizar crescimento

---

## 📊 Fórmulas Principais

### 1. **Probabilidade Implícita**

A probabilidade implícita na odd é:

$$P_{implícita} = \frac{1}{Odd}$$

**Exemplos:**
- Odd 2.00 → 50% probabilidade
- Odd 3.00 → 33.3% probabilidade
- Odd 1.50 → 66.7% probabilidade

### 2. **Edge da Aposta**

O edge real da aposta é o ROI vezes a probabilidade de ganho:

$$Edge = ROI_{médio} \times P_{implícita} = 0.18 \times \frac{1}{Odd}$$

**Exemplos:**
- Odd 1.50: Edge = 0.18 × 0.667 = **12%**
- Odd 2.00: Edge = 0.18 × 0.5 = **9%**
- Odd 3.00: Edge = 0.18 × 0.333 = **6%**

Odds maiores = edge menor = risco maior

### 3. **Kelly Criterion (Clássico)**

Fórmula que maximiza crescimento geométrico do bankroll:

$$f^* = \frac{b \times p - q}{b}$$

Onde:
- $b$ = odds - 1 (payoff)
- $p$ = probabilidade de vitória
- $q$ = 1 - p (probabilidade de derrota)

**Exemplo com odd 2.50:**
- $b = 1.50$
- $p = 0.55$ (55% chance)
- $q = 0.45$ (45% chance)
- $f^* = \frac{1.50 \times 0.55 - 0.45}{1.50} = \frac{0.825 - 0.45}{1.50} = 0.25 = 25\%$

### 4. **Probabilidade Ajustada**

A probabilidade é ajustada pela confiança do modelo:

$$P_{ajustada} = P_{implícita} + (CF_{média} - 0.5) \times 0.1$$

Onde $CF_{média} = \sqrt{CF_{xgh} \times CF_{xga}}$ (média geométrica)

**Lógica:**
- Se CF = 0.5 (baixa confiança) → não ajusta
- Se CF = 0.85 (alta confiança) → aumenta 3.5% na probabilidade
- Se CF = 0.25 (muito baixa) → reduz 2.5% na probabilidade

### 5. **Fractional Kelly (Segurança)**

Para evitar volatilidade extrema, usamos fração do Kelly:

$$f_{fracionado} = f^* \times \frac{1}{n}$$

**Recomendações:**
- **1/2 Kelly**: Crescimento moderado, menos volatilidade (recomendado iniciantes)
- **1/4 Kelly**: Crescimento conservador, mínima volatilidade (recomendado para volume alto)
- **Kelly Completo**: Máximo crescimento, alta volatilidade (apenas com muita confiança)

### 6. **Stake Final**

$$Stake = f_{fracionado} \times Bankroll$$

Com limites mín/máx:
- **Mínimo**: 1% do bankroll
- **Máximo**: 5% do bankroll

---

## 🎲 Método Simplificado: Stakes por Faixa de Odd

Para facilitar a execução, usamos uma tabela simplificada:

| Faixa de Odd | Stake % | Razão |
|---|---|---|
| < 1.50 | 5% | Odds baixas = menor risco |
| 1.50 - 1.75 | 4% |  |
| 1.75 - 2.00 | 3.5% |  |
| 2.00 - 2.50 | 3% | Ponto ideal (melhor razão risco/retorno) |
| 2.50 - 3.00 | 2.5% |  |
| 3.00 - 3.50 | 2% |  |
| 3.50 - 4.00 | 1.5% |  |
| > 4.00 | 1% | Odds altas = maior risco |

**Ajuste pela Confiança:**
$$Stake_{final} = Stake\% \times Bankroll \times (0.7 + CF \times 0.6)$$

Isso cria um multiplicador entre 0.7 e 1.3:
- CF = 0.5 (média) → multiplicador 1.0
- CF = 0.85 (alta) → multiplicador 1.21
- CF = 0.3 (baixa) → multiplicador 0.88

---

## 💡 Exemplo Prático

**Cenário:**
- Bankroll: R$ 10.000
- Odd encontrada: 2.80
- CF xGH: 0.82
- CF xGA: 0.75

**Cálculo Kelly Completo:**

1. **Probabilidade Implícita**: 1 / 2.80 = 35.7%

2. **Confiança Média**: √(0.82 × 0.75) = 0.785 ≈ 78.5%

3. **Probabilidade Ajustada**: 0.357 + (0.785 - 0.5) × 0.1 = 0.357 + 0.0285 = **38.55%**

4. **Kelly Puro**:
   - b = 1.80
   - f* = (1.80 × 0.3855 - 0.6145) / 1.80 = (0.6939 - 0.6145) / 1.80 = **4.4%**

5. **Kelly 1/4**: 4.4% × 0.25 = **1.1%**

6. **Stake Final**: 10.000 × 1.1% = **R$ 110**

---

## 📈 Gestão de Risco

### Cenário: 20 Apostas em um Mês

**Com Stakes de 2.5% em média:**
- Total apostado: R$ 5.000
- ROI esperado (18%): **R$ 900**
- Crescimento bankroll: **9%**

**Pior caso (se ganhar apenas 5%):**
- Ganho mínimo: R$ 250
- Drawdown possível: 20-30%

**Recomendações:**
1. ✅ Nunca apostar mais de 5% do bankroll em uma única aposta
2. ✅ Usar 1/4 Kelly como padrão (muito mais seguro)
3. ✅ Monitorar drawdown máximo (limite 30%)
4. ✅ Aumentar stakes apenas após comprovar ROI positivo
5. ✅ Manter log detalhado de todas as apostas

---

## 🔄 Integração com o Seu Sistema

Seu sistema já calcula:
- **MCGH/MVGH/MCGA/MVGA**: Métricas de valor
- **CF**: Coeficiente de confiança
- **Odds**: De entrada

**Próximo passo:** Adicionar coluna de stake sizing em `analisar_proxima_rodada.py`:

```python
from stake_sizing import StakeSizer

sizer = StakeSizer(bankroll=10000, roi_medio=0.18, kelly_fraction=0.25)

# Para cada jogo:
stake_info = sizer.stake_sizing_adaptativo(
    odd=odd_entrada,
    cfxgh=cfxgh,
    cfxga=cfxga,
    bankroll_atual=bankroll_atual
)

print(f"Aposta sugerida: R$ {stake_info['stake']:.2f}")
```

---

## ⚖️ Comparação: Métodos de Stake Sizing

| Método | Complexidade | Risco | Retorno | Quando Usar |
|---|---|---|---|---|
| **Fixed 1%** | ⭐ Mínima | ⭐ Mínimo | ⭐ Lento | Testando novo modelo |
| **Por Faixa Odd** | ⭐⭐ Simples | ⭐⭐ Baixo | ⭐⭐ Moderado | Produção (RECOMENDADO) |
| **Kelly 1/4** | ⭐⭐ Simples | ⭐⭐ Baixo-Médio | ⭐⭐⭐ Bom | Muitas apostas/mês |
| **Kelly Completo** | ⭐⭐⭐ Complexo | ⭐⭐⭐ Alto | ⭐⭐⭐⭐ Muito bom | Confiança 90%+ |

---

## 🎓 Referências Teóricas

1. **Kelly Criterion**: Maximiza crescimento logarítmico do capital
2. **Fractional Kelly**: Reduz volatilidade mantendo crescimento
3. **Edge Theory**: Edge = (Odd - 1) × Probabilidade - (1 - Probabilidade)

---

## ⚡ Resumo da Implementação

| Passo | Ferramenta | Resultado |
|---|---|---|
| 1 | Executar `stake_sizing.py` | Ver exemplos de stakes para diferentes odds |
| 2 | Integrar em `analisar_proxima_rodada.py` | Adicionar coluna de stake sugerido |
| 3 | Usar no site de apostas | Apenas apostar valores sugeridos pelo sistema |
| 4 | Logar resultados | Rastrear ROI real vs esperado |
| 5 | Ajustar parâmetros | Se ROI real ≠ esperado após 50+ apostas |

**Fórmula de Ouro:** Stake = f* × Bankroll, onde f* é a fração Kelly ajustada
