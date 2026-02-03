# 📊 Guia de Backtest Histórico (2013-2026)

## 🎯 Objetivo

Executar backtest robusto usando dados históricos de 2013 a 2026 para todas as ligas disponíveis. O sistema usa 2012/2013 como período de treino para ter histórico de comparação, iniciando o backtest a partir de 2013/2014.

## ⚠️ Importante: Período de Treino

O modelo precisa de **pelo menos 1 temporada de histórico** para fazer comparações estatísticas (xG, LP, etc.). Por isso:
- **Treino:** 2012/2013 (1 temporada)
- **Teste:** 2013/2014 a 2025/2026 (13 temporadas)
- **Nota:** A temporada 2013/2014 terá **poucas entradas** devido ao histórico limitado (apenas 1 temporada para comparar)

## 📂 Scripts Disponíveis

### 1. `executar_backtest_historico.py` - Top 5 Ligas
Processa as 5 principais ligas (teste rápido).

**Uso:**
```bash
python executar_backtest_historico.py
```

**Características:**
- ✅ Rápido (15-30 minutos)
- ✅ Ligas: E0, E1, SP1, SP2, I1
- ✅ Ideal para testes iniciais
- ✅ Gera: `backtest_historico_2012_2026.json`
- ℹ️  Usa 2012/2013 para treino, testa 2013/2014 em diante

---

### 2. `executar_backtest_completo.py` - TODAS as Ligas
Processa todas as 31 ligas disponíveis (análise completa).

**Uso:**
```bash
python executar_backtest_completo.py
```

**Características:**
- ⏱️ Demorado (2-4 horas)
- ✅ 31 ligas processadas
- ✅ Análise estatística robusta
- ✅ Top 10 ligas mais lucrativas
- ✅ Gera: `backtest_historico_completo_2012_2026.json`

---

## 📋 Metodologia

### Período de Treino
**2012/2013** (1 temporada)
- Dados usados para calibrar o modelo
- Estatísticas históricas para cálculo de xG, LP, etc.
- Base mínima necessária para comparações

### Período de Teste
**2013/2014 a 2025/2026** (13 temporadas)
- Backtest executado temporada por temporada
- Simula entradas reais com odds históricas
- Calcula lucro, ROI, win rate, etc.
- **Primeira temporada (2013/2014) terá poucas entradas** devido ao histórico limitado

### Evolução do Histórico
```
2013/2014 → Compara com 1 temporada (2012/2013)
2014/2015 → Compara com 2 temporadas (2012-2014)
2015/2016 → Compara com 3 temporadas (2012-2015)
...
2025/2026 → Compara com 13 temporadas (2012-2025)
```

### Processo
```
1. Preparar dados de treino (apenas 2012/2013)
   ↓
2. Para cada temporada (2013/2014 a 2025/2026):
   ↓
   a. Carregar jogos da temporada
   ↓
   b. Simular jogo por jogo
   ↓
   c. Calcular entradas válidas (com base no histórico acumulado)
   ↓
   d. Registrar resultados
   ↓
3. Consolidar estatísticas
   ↓
4. Gerar relatório JSON
```

---

## 📊 Estrutura dos Resultados

### JSON Gerado

```json
{
  "timestamp_geracao": "2026-02-03T...",
  "periodo": "2012-2026",
  "total_ligas_processadas": 31,
  "resumo_geral": {
    "total_temporadas": 434,
    "total_jogos": 165234,
    "total_entradas": 45678,
    "lucro_total": 12345.67,
    "roi_medio_geral": 8.45
  },
  "ligas": [
    {
      "liga": "E0",
      "nome_completo": "Premier League",
      "temporadas_processadas": 14,
      "total_jogos": 5320,
      "total_entradas": 1456,
      "lucro_total": 2345.67,
      "roi_medio": 12.34,
      "detalhes": [...]
    }
  ],
  "top_10_ligas_lucrativas": [...]
}
```

---

## 🚀 Como Executar

### Passo 1: Escolher Script

**Para teste rápido (30 min):**
```bash
python executar_backtest_historico.py
```

**Para análise completa (3 horas):**
```bash
python executar_backtest_completo.py
```

### Passo 2: Confirmar Execução

O script exibirá:
- Período de análise
- Ligas selecionadas
- Estimativa de tempo

Digite **S** para continuar.

### Passo 3: Aguardar Processamento

O script exibirá progresso em tempo real:
```
🏆 E0 - Premier League
================================================================
📅 Temporadas: 14
   [1/14] 2012/2013... ✓ Lucro: R$ 234.50 | ROI: 8.5%
   [2/14] 2013/2014... ✓ Lucro: R$ 456.20 | ROI: 12.3%
   ...
```

### Passo 4: Analisar Resultados

Após conclusão, verifique:
- ✅ Arquivo JSON gerado em `/backtest/`
- ✅ Resumo geral no terminal
- ✅ Top 10 ligas mais lucrativas

---

## 📈 Interpretando os Resultados

### Métricas Principais

| Métrica | Descrição | Valor Bom |
|---------|-----------|-----------|
| **Total de Entradas** | Quantidade de apostas realizadas | > 1000 |
| **Lucro Total** | Ganho/perda em R$ | Positivo |
| **ROI Médio** | Retorno sobre investimento | > 5% |
| **Win Rate** | Taxa de acerto | > 50% |
| **Temporadas Processadas** | Cobertura histórica | 10-14 |

### Análise por Liga

**Ligas Lucrativas (ROI > 8%):**
- ✅ Ótimo desempenho histórico
- ✅ Padrões consistentes
- ✅ Recomendadas para apostas

**Ligas Moderadas (ROI 3-8%):**
- 🟡 Desempenho aceitável
- 🟡 Necessário filtros adicionais
- 🟡 Usar com cautela

**Ligas Negativas (ROI < 3%):**
- ❌ Evitar entradas
- ❌ Padrões inconsistentes
- ❌ Necessário revisão de critérios

---

## 🔍 Próximos Passos Após Backtest

### 1. Análise de Tipos de Entrada

Identificar quais tipos são mais lucrativos:
```python
# Ver arquivo: gerar_relatorio_entradas.py
python gerar_relatorio_entradas.py
```

### 2. Filtros Personalizados

Criar critérios baseados nos resultados:
- Ligas específicas (ex: apenas E0, SP1)
- Faixas de odds (ex: 1.5 - 2.5)
- Tipos de entrada (HOME/AWAY)
- DxG mínimo

### 3. Backtest Refinado

Re-executar com filtros aplicados:
```python
# Editar: executar_backtest_completo.py
# Adicionar filtros na linha X
```

### 4. Validação em Tempo Real

Comparar com próxima rodada:
```bash
python buscar_proxima_rodada.py
# Verificar coluna VALIDADA
```

---

## ⚠️ Observações Importantes

### Limitações

1. **Dados Históricos**
   - Odds podem ter mudado ao longo dos anos
   - Mercado evolui (menos valor em 2026 vs 2012)

2. **Viés de Sobrevivência**
   - Ligas podem ter mudado formato
   - Times promovidos/rebaixados

3. **Overfit**
   - Bom desempenho passado ≠ garantia futura
   - Sempre validar em dados recentes

### Boas Práticas

✅ **Executar backtest completo** antes de apostar real  
✅ **Atualizar dados** mensalmente  
✅ **Monitorar ROI real** vs backtest  
✅ **Ajustar critérios** conforme necessário  
✅ **Usar gestão de banca** adequada  

---

## 🆘 Troubleshooting

### Erro: "Arquivo não encontrado"
```bash
# Verificar se arquivos CSV existem
ls dados_ligas/
ls dados_ligas_new/
```

### Erro: "Memória insuficiente"
```bash
# Usar script parcial (top 5 ligas)
python executar_backtest_historico.py
```

### Backtest muito lento
```bash
# Reduzir número de ligas
# Editar: executar_backtest_completo.py
# Linha 15: TODAS_LIGAS = {...}  # Remover ligas
```

### Resultados inconsistentes
```bash
# Limpar cache e re-executar
rm backtest/*_treino.csv
rm backtest/backtest_resultados_*.json
python executar_backtest_completo.py
```

---

## 📞 Próximas Melhorias

- [ ] Processamento paralelo (reduzir tempo)
- [ ] Relatório HTML visual
- [ ] Gráficos de desempenho por temporada
- [ ] Análise de sazonalidade
- [ ] Comparação entre estratégias
- [ ] Export para Excel

---

**Versão:** 1.0  
**Data:** 3 de fevereiro de 2026  
**Status:** ✅ Pronto para uso
