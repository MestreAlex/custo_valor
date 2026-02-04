# 🎯 Guia Prático: Stake Sizing para Seu Modelo

## 📋 Resumo das 3 Abordagens

### **Opção 1: Tabela Simplificada (RECOMENDADA para produção)**

Use a tabela de faixas de odd com ajuste pela confiança do modelo:

```
Odd       | Stake % Base | Com CF Alta (0.8) | Com CF Baixa (0.5)
----------|---|---|---|
1.50      | 5.0%        | 6.0%              | 3.5%
1.75      | 4.0%        | 4.8%              | 2.8%
2.00      | 3.5%        | 4.2%              | 2.5%
2.50      | 3.0%        | 3.6%              | 2.1%
3.00      | 2.5%        | 3.0%              | 1.75%
3.50      | 2.0%        | 2.4%              | 1.4%
4.00      | 1.5%        | 1.8%              | 1.05%
```

**Vantagem:** Rápido de executar, não precisa calcular nada
**Implementação:** Usar `sizer.stake_por_faixa_odd()`

---

### **Opção 2: Kelly 1/4 (MÁXIMA SEGURANÇA)**

Usar o Kelly Criterion completo com 1/4 de fração:

```python
stake = kelly_puro × 0.25 × bankroll
```

**Vantagem:** Matematicamente ótimo, muito seguro
**Desvantagem:** Requer mais cálculos
**Implementação:** Usar `sizer.stake_sizing_adaptativo()`

---

### **Opção 3: Kelly 1/2 (MEIO TERMO)**

Balance entre crescimento e segurança:

```python
stake = kelly_puro × 0.5 × bankroll
```

**Vantagem:** Mais crescimento que 1/4 Kelly, ainda seguro
**Implementação:** Modificar `kelly_fraction=0.5` no StakeSizer

---

## 🚀 Implementação Passo-a-Passo

### **Passo 1: Escolher o Método**

```python
from stake_sizing import StakeSizer

# Criar sizer com seu bankroll
sizer = StakeSizer(
    bankroll=10000,      # Seu bankroll
    roi_medio=0.18,      # 18% ROI (confirmado em backtest)
    kelly_fraction=0.25  # 1/4 Kelly (seguro)
)
```

### **Passo 2: Para Cada Aposta, Calcular o Stake**

```python
# Opção A: Método Simplificado (tabela)
resultado = sizer.stake_por_faixa_odd(
    odd=2.80,           # Odd encontrada
    cfxgh=0.82,         # CF do time da casa
    cfxga=0.75          # CF do time visitante
)
stake = resultado['stake']
print(f"Aposta sugerida: R$ {stake:.2f}")

# Opção B: Método Completo (Kelly)
resultado = sizer.stake_sizing_adaptativo(
    odd=2.80,
    cfxgh=0.82,
    cfxga=0.75
)
stake = resultado['stake']
roi_esperado = resultado['roi_esperado_stake']
print(f"Aposta: R$ {stake:.2f}, ROI esperado: R$ {roi_esperado:.2f}")
```

### **Passo 3: Integrar com `analisar_proxima_rodada.py`**

Adicionar após calcular odds:

```python
from integracao_stake_sizing import adicionar_stake_sizing_aos_jogos

# Seus jogos analisados
jogos_analise = [...]  # Lista de dicts com odd, cfxgh, cfxga

# Adicionar stakes
jogos_com_stakes = adicionar_stake_sizing_aos_jogos(
    jogos_analise,
    bankroll=10000,
    roi_medio=0.18
)

# Renderizar tabela HTML
html = renderizar_tabela_html_com_stakes(jogos_com_stakes)
```

---

## 📊 Exemplos Práticos com Seu Modelo

### **Cenário 1: Odd 1.95 (Favorita) - CF Alta (85%)**

```
Odd: 1.95
Bankroll: R$ 10.000
CF: 85% (alta confiança)

Cálculo:
- Prob. Implícita: 51.3%
- Prob. Ajustada: 54.5% (aumentada pela CF alta)
- Kelly Puro: 4.41%
- Kelly 1/4: 1.10%

✓ STAKE SUGERIDO: R$ 110
  - 1.1% do bankroll
  - ROI esperado: R$ 19.80
```

**Lógica:** Odd baixa + confiança alta = stake pequeno mas positivo
**Razão:** Odd baixa tem menos margem (51% × 18% = 9% edge)

---

### **Cenário 2: Odd 2.80 (Moderada) - CF Média (75%)**

```
Odd: 2.80
Bankroll: R$ 10.000
CF: 75% (confiança média)

Cálculo:
- Prob. Implícita: 35.7%
- Prob. Ajustada: 38.5% (ajustada pela CF média)
- Kelly Puro: 2.2%
- Kelly 1/4: 0.55%

✓ STAKE SUGERIDO: R$ 155 (via tabela simplificada)
  - 1.55% do bankroll
  - ROI esperado: R$ 27.90
```

**Lógica:** Odd moderada + confiança média = stake balanceado
**Razão:** Odd de 2.80 tem melhor relação risco/retorno (35.7% × 18% = 6.4% edge)

---

### **Cenário 3: Odd 4.50 (Alta) - CF Baixa (60%)**

```
Odd: 4.50
Bankroll: R$ 10.000
CF: 60% (confiança baixa)

Cálculo:
- Prob. Implícita: 22.2%
- Prob. Ajustada: 22.2% (reduzida pela CF baixa)
- Kelly Puro: -0.2% (NEGATIVO!)
- Kelly 1/4: 0%

✓ STAKE SUGERIDO: R$ 100 (mínimo)
  - 1.0% do bankroll
  - ROI esperado: R$ 18
```

**Lógica:** Odd alta + confiança baixa = NÃO RECOMENDADO
**Razão:** Muito risco (22.2% × 18% = 4% edge apenas)

---

## 💡 Regras de Ouro

### **1. Nunca Exceder 5% por Aposta**

```
✗ ERRADO: Apostar 10% em uma aposta
✓ CORRETO: Máximo 5% de uma vez
  - Protege seu bankroll contra losing streaks
```

### **2. Escalar com Confiança**

```
CF Baixa (< 0.5)   → Stake Mínimo (1-1.5%)
CF Média (0.5-0.7) → Stake Médio (2-3%)
CF Alta (> 0.7)    → Stake Máximo (3-5%)
```

### **3. Reduzir com Odd Alta**

```
Odd 1.50 → 5.0% do bankroll
Odd 2.00 → 3.5% do bankroll
Odd 3.00 → 2.5% do bankroll
Odd 4.00 → 1.5% do bankroll
Odd 5.00 → 1.0% do bankroll
```

### **4. Respeitar o Drawdown Máximo**

```
Drawdown Máximo Permitido: 30% do bankroll

Se bankroll = R$ 10.000
Limite de perda = R$ 3.000

Parar de apostar quando perder mais de 30%
```

---

## 📈 Cenário Mensal Completo

**Suposição:**
- Bankroll: R$ 10.000
- Stakes médios: 2.5% (R$ 250)
- 20 apostas por mês
- ROI real: 12% (conservador vs 18% backtest)

```
Apostas:        20
Total Apostado: R$ 5.000
ROI 12%:        R$ 600
Crescimento:    6% ao mês

Após 12 meses com crescimento composto:
Bankroll Inicial: R$ 10.000
Crescimento 6% ao mês (composto): 2.01x
Bankroll Final:   R$ 20.100

Ganho Total: R$ 10.100 (101% de crescimento anual)
```

**Se aumentar stakes 2% por semana após lucro:**
```
Crescimento esperado: 2.5x ao ano (150%+)
```

---

## ⚠️ Riscos e Mitigações

### **Risco 1: Streak Negativo**

```
Problema: Perder 5-10 apostas seguidas
Probabilidade: ~10% com ROI 18%

Mitigação:
- Usar Kelly 1/4 (reduz volatilidade)
- Manter drawdown máximo 30%
- Nunca aumentar stakes em losing streak
```

### **Risco 2: Model Decay**

```
Problema: ROI real cai de 18% para 8%
Sinal: Após 50+ apostas, ROI real ≠ esperado

Mitigação:
- Monitorar ROI mensalmente
- Ajustar stakes conforme ROI real
- Revisar coeficientes CF se necessário
```

### **Risco 3: Erro de Execução**

```
Problema: Apostar valor errado (2x ou 0.5x)
Impacto: Perdas ampliadas ou crescimento lento

Mitigação:
- Usar sistema automatizado (seu site)
- Revisar sempre antes de clicar
- Manter log de todas apostas
```

---

## 🎓 Tabela Rápida de Consulta

### **Bankroll de R$ 10.000**

| Odd | CF 85% | CF 75% | CF 60% | CF 50% |
|---|---|---|---|---|
| 1.50 | R$ 460 | R$ 400 | R$ 300 | R$ 250 |
| 1.75 | R$ 402 | R$ 350 | R$ 263 | R$ 220 |
| 2.00 | R$ 345 | R$ 300 | R$ 225 | R$ 188 |
| 2.50 | R$ 288 | R$ 250 | R$ 188 | R$ 156 |
| 3.00 | R$ 230 | R$ 200 | R$ 150 | R$ 125 |
| 3.50 | R$ 172 | R$ 150 | R$ 112 | R$ 94 |
| 4.00 | R$ 115 | R$ 100 | R$ 75 | R$ 62 |

### **Bankroll de R$ 5.000**

Dividir todos os valores por 2

---

## ✅ Checklist Antes de Cada Aposta

- [ ] CF >= 60%? (senão, considerar não apostar)
- [ ] Calculei o stake correto? (verificar 2x)
- [ ] Stake <= 5% do bankroll? (máximo permitido)
- [ ] Bankroll atual > drawdown mínimo? (não no 30% de perda)
- [ ] Tenho ROI real rastreado? (para ajustes futuros)
- [ ] Anotei a aposta no log? (para análise posterior)

---

## 🚀 Próximos Passos

1. ✅ Testar `stake_sizing.py` com exemplos
2. ✅ Integrar `integracao_stake_sizing.py` com seu sistema
3. ✅ Adicionar coluna de "Stake Sugerido" no HTML de `buscar_proxima_rodada.py`
4. ✅ Criar log automático de apostas com timestamps
5. ✅ Calcular ROI real mensal vs esperado
6. ✅ Ajustar parâmetros se ROI real divergir > 5% do esperado

---

## 📞 Suporte Rápido

**"Por que o stake é tão pequeno?"**
→ Odds altas têm menos edge, então stakes menores protegem seu bankroll

**"Posso aumentar o Kelly fraction?"**
→ Sim (1/2 ou Kelly completo), mas aumenta volatilidade. Recomendo 1/4 para volume alto

**"Como ajusto se ganhar muito?"**
→ Aumente stakes 5-10% a cada semana de lucro. Máximo 5% por aposta

**"E se perder mais de 30%?"**
→ Pause apostas, revise o sistema, procure o erro antes de continuar
