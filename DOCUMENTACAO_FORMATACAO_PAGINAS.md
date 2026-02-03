# 📋 Documentação de Formatação das 6 Páginas HTML

**Data de Criação:** 3 de fevereiro de 2026  
**Última Atualização:** 3 de fevereiro de 2026

---

## 🎨 Tema Visual Global

### Cores Principais
- **Fundo Primário:** `linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)` (gradiente azul escuro)
- **Cor Destaque:** `#00d4ff` (cyan)
- **Branco:** `#ecf0f1` (texto claro)
- **Preto Semitransparente:** `rgba(0, 0, 0, 0.3)` (sobreposições)

### Estrutura de Navegação (Idêntica em Todas as Páginas)
Todas as 6 páginas compartilham a mesma barra de navegação com 6 links:

```html
<div class="nav-links">
    <a href="http://localhost:8000/proxima_rodada.html" class="nav-link">Próxima Rodada</a>
    <a href="http://localhost:8000/jogos_salvos.html" class="nav-link">Jogos Salvos</a>
    <a href="http://localhost:8000/analise_salvos.html" class="nav-link">Análise Salvos</a>
    <a href="http://localhost:5001/backtest.html" class="nav-link">Backtest</a>
    <a href="http://localhost:5001/backtest_salvos.html" class="nav-link">Backtests Salvos</a>
    <a href="http://localhost:5001/backtest_resumo_entradas.html" class="nav-link">Resumo Entradas</a>
</div>
```

**CSS da Navegação:**
```css
.nav-links {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 12px 0 18px;
    display: flex;
    justify-content: center;
    gap: 15px;
}

.nav-link {
    color: #00d4ff;
    background: rgba(0, 212, 255, 0.12);
    border: 1px solid rgba(0, 212, 255, 0.35);
    padding: 8px 20px;
    border-radius: 5px;
    text-decoration: none;
    transition: background 0.3s;
}

.nav-link:hover {
    background: rgba(0, 212, 255, 0.25);
}
```

---

## 📄 6 Páginas HTML

### 1. **proxima_rodada.html** (Porta 8000)
**Script Gerador:** `buscar_proxima_rodada.py`  
**Função:** Exibe jogos da próxima rodada com análise de odds

#### Formatações Especiais:

**Coluna TIME (HOME/AWAY):**
```css
.team {
    font-weight: 500;
    color: white;  /* ← BRANCO */
}
```

**Colunas ODD H CALC / ODD D CALC / ODD A CALC:**
```css
.calc-odd {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    padding: 6px 10px;
    border-radius: 6px;
    display: inline-block;
    min-width: 45px;
    text-align: center;
    font-size: 0.9em;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

/* Value Bet - Verde Vibrante */
.value-bet {
    background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
    color: #000;
    font-weight: 900;
    box-shadow: 0 0 15px rgba(0, 255, 136, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.3);
    border: 2px solid #00ff88;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.value-bet::before { content: "✓ "; margin-right: 3px; }

/* Bad Bet - Vermelho */
.bad-bet {
    background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
    color: white;
    font-weight: 900;
    box-shadow: 0 0 15px rgba(255, 68, 68, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.2);
    border: 2px solid #ff4444;
}
.bad-bet::before { content: "✗ "; margin-right: 3px; }

/* Neutral Bet - Laranja */
.neutral-bet {
    background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
    color: #000;
    font-weight: 700;
    box-shadow: 0 0 12px rgba(255, 170, 0, 0.5);
    border: 2px solid #ffaa00;
}
.neutral-bet::before { content: "◆ "; margin-right: 3px; }
```

**Instruções de Manutenção:**
- Se precisar alterar formatação das odds, editar linhas 392-448 do `buscar_proxima_rodada.py`
- Se precisar alterar a cor dos times (HOME/AWAY), editar linha 361-364
- Sempre executar: `python buscar_proxima_rodada.py` após fazer alterações

---

### 2. **jogos_salvos.html** (Porta 8000)
**Script Gerador:** `salvar_jogo.py` - função `gerar_pagina_salvos()`  
**Função:** Exibe jogos que foram salvos com resultados

#### Formatações Especiais:

**Coluna TIME (HOME/AWAY):**
```css
.team {
    font-weight: 500;
    color: white;  /* ← BRANCO */
}
```

**Colunas ODD H CALC / ODD D CALC / ODD A CALC:**
Mesmas formatações de `proxima_rodada.html` (classes value-bet, bad-bet, neutral-bet)

**Instruções de Manutenção:**
- Editar CSS: linhas 572-625 de `salvar_jogo.py`
- Executar após alterações: `python salvar_jogo.py gerar`
- Também regenera `analise_salvos.html` automaticamente

---

### 3. **analise_salvos.html** (Porta 8000)
**Script Gerador:** `salvar_jogo.py` - função `gerar_pagina_analise()`  
**Função:** Exibe análise AI dos jogos salvos

#### Formatações Especiais:

**Coluna TIME (HOME/AWAY):**
```css
.team {
    font-weight: 500;
    color: white;  /* ← BRANCO */
}
```

**Colunas ODD H CALC / ODD D CALC / ODD A CALC:**
Mesmas formatações (classes value-bet, bad-bet, neutral-bet) - com double braces `{{` `}}`

**Instruções de Manutenção:**
- Editar CSS: linhas 2417-2470 de `salvar_jogo.py`
- Executar após alterações: `python salvar_jogo.py gerar_analise`
- Usa double braces `{{` `}}` porque é formatação de string Python

---

### 4. **backtest.html** (Porta 5001)
**Localização:** `backtest/backtest.html`  
**Gerador:** Gerado automaticamente pelo servidor backtest  
**Função:** Dashboard principal do sistema de backtesting

#### Formatações Especiais:
- Segue mesmo tema de cores cyan/dark
- Tabelas com fundo semitransparente

**Instruções de Manutenção:**
- Se precisar editar formatação, procurar no servidor que gera esse arquivo
- Verificar em `servidor_analise_backtest.py`

---

### 5. **backtest_salvos.html** (Porta 5001)
**Localização:** `backtest/backtest_salvos.html`  
**Gerador:** Gerado automaticamente pelo servidor backtest  
**Função:** Lista de backtests salvos

#### Formatações Especiais:
- Mesma paleta de cores (cyan, dark)
- Layout tabular com filtros

**Instruções de Manutenção:**
- Edições diretas no servidor gerador
- Procurar em `servidor_analise_backtest.py`

---

### 6. **backtest_resumo_entradas.html** (Porta 5001) ⭐ REFERÊNCIA PADRÃO
**Localização:** `backtest/backtest_resumo_entradas.html`  
**Gerador:** Gerado automaticamente pelo servidor backtest  
**Função:** Resumo de entradas com análise detalhada

#### Status Especial:
✅ **ESTA É A PÁGINA REFERÊNCIA PARA O TEMA VISUAL**
- Todas as outras 5 páginas têm sua formatação baseada nesta
- Navegação extraída desta página (6 links)
- Cores e tema copiados desta página

**Formatações CSS Principais:**
```css
/* Gradiente de fundo (base para todas as páginas) */
body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #ecf0f1;
}

/* Cabeçalho */
.header {
    background: rgba(0, 0, 0, 0.3);
    color: #00d4ff;
    border-radius: 8px;
}

.header h1 {
    color: #00d4ff;
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

/* Tabela */
thead {
    background: #0a5f7e;
}

th {
    color: #00d4ff;
}

tbody tr:nth-child(odd) {
    background: rgba(0, 212, 255, 0.05);
}

tbody tr:hover {
    background: rgba(0, 212, 255, 0.15);
}
```

**Instruções de Manutenção:**
- ⚠️ NÃO EDITAR MANUALMENTE - é gerada pelo servidor
- Se precisar mudar o tema, alterar o servidor e regenerar

---

## 🔧 Como Reaplicar Formatações (Guia Rápido)

### Se as 3 Páginas do Porto 8000 Ficarem sem Formatação:

```bash
# Regenerar proxima_rodada.html
python buscar_proxima_rodada.py

# Regenerar jogos_salvos.html e analise_salvos.html
python salvar_jogo.py gerar
python salvar_jogo.py gerar_analise
```

### Se as 3 Páginas do Porto 5001 Ficarem sem Formatação:

Reiniciar o servidor:
```bash
# Parar servidor antigo
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Iniciar novo servidor backtest
python servidor_analise_backtest.py
```

---

## 📊 Mapeamento de Edições

| Página | Script | Função | Linhas CSS | Comando Regeneração |
|--------|--------|--------|-----------|-------------------|
| proxima_rodada.html | buscar_proxima_rodada.py | - | 361-448 | `python buscar_proxima_rodada.py` |
| jogos_salvos.html | salvar_jogo.py | gerar_pagina_salvos() | 572-625 | `python salvar_jogo.py gerar` |
| analise_salvos.html | salvar_jogo.py | gerar_pagina_analise() | 2417-2470 | `python salvar_jogo.py gerar_analise` |
| backtest.html | servidor_analise_backtest.py | - | - | Reiniciar servidor |
| backtest_salvos.html | servidor_analise_backtest.py | - | - | Reiniciar servidor |
| backtest_resumo_entradas.html | servidor_analise_backtest.py | - | - | Reiniciar servidor (REFERÊNCIA) |

---

## 🎯 Cores e Ícones (Padronizados)

### Value Bet (Melhor Opção)
- **Cor:** Verde vibrante (`#00ff88` → `#00cc6a`)
- **Ícone:** ✓
- **Uso:** Odds que oferecem valor (B365 > ODD_CALC * 1.10)

### Bad Bet (Evitar)
- **Cor:** Vermelho (`#ff4444` → `#cc0000`)
- **Ícone:** ✗
- **Uso:** Odds desfavoráveis (B365 < ODD_CALC)

### Neutral Bet (Aceitável)
- **Cor:** Laranja (`#ffaa00` → `#ff8800`)
- **Ícone:** ◆
- **Uso:** Odds medianas

---

## 💾 Arquivos de Configuração

### Principais Arquivos Python
- **buscar_proxima_rodada.py** - Gera proxima_rodada.html
- **salvar_jogo.py** - Gera jogos_salvos.html e analise_salvos.html
- **servidor_analise_backtest.py** - Gera páginas do backtest (porta 5001)
- **servidor_api.py** - Servidor HTTP principal (porta 8000)

### Headers HTTP (Cache)
Todas as respostas HTML têm headers para evitar cache:
```
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
```

---

## 📝 Checklist para Novas Mudanças

- [ ] Editar o arquivo Python correspondente (CSS ou HTML)
- [ ] Regenerar o arquivo HTML com o comando apropriado
- [ ] Verificar arquivo gerado em `fixtures/` ou `backtest/`
- [ ] Testar no navegador com Ctrl+F5 (hard refresh)
- [ ] Se compatível, aplicar mesma formatação nas outras páginas
- [ ] Atualizar esta documentação com as mudanças

---

## ⚡ Atalhos Úteis

### Regenerar Todas as Páginas Porto 8000
```bash
python buscar_proxima_rodada.py; python salvar_jogo.py gerar; python salvar_jogo.py gerar_analise
```

### Limpar Cache do Navegador
Abrir DevTools (F12) → Settings → Network → Desabilitar cache

### Hard Refresh (Bypass Cache)
- Windows: `Ctrl+F5`
- Mac: `Cmd+Shift+R`
- Firefox: `Ctrl+Shift+R`

---

**Documento Finalizado** ✅  
**Próximas Atualizações:** Registrar aqui qualquer mudança de formatação futura
