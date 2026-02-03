import json
import re

with open('backtest/backtest_resumo_entradas.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 60)
print("VALIDAÇÃO - TOGGLE PARA TABELAS DE LIGA")
print("=" * 60)

# Verificar função toggleLigaTotals
if 'function toggleLigaTotals(' in content:
    print("✓ Função toggleLigaTotals() definida")
else:
    print("✗ Função toggleLigaTotals() NÃO encontrada")

# Verificar títulos com onclick
if 'ligaTotalsHomeTitle' in content and 'onclick="toggleLigaTotals' in content:
    print("✓ Título HOME com onclick encontrado")
else:
    print("✗ Título HOME com onclick NÃO encontrado")

if 'ligaTotalsAwayTitle' in content and 'onclick="toggleLigaTotals' in content:
    print("✓ Título AWAY com onclick encontrado")
else:
    print("✗ Título AWAY com onclick NÃO encontrado")

# Verificar tabelas com IDs
if 'id="ligaTotalsHomeTable"' in content:
    print("✓ Tabela HOME com ID encontrada")
else:
    print("✗ Tabela HOME com ID NÃO encontrada")

if 'id="ligaTotalsAwayTable"' in content:
    print("✓ Tabela AWAY com ID encontrada")
else:
    print("✗ Tabela AWAY com ID NÃO encontrada")

# Verificar que tabelas começam ocultas
homeTable = 'id="ligaTotalsHomeTable" style="display:none;"'
awayTable = 'id="ligaTotalsAwayTable" style="display:none;"'

if homeTable in content:
    print("✓ Tabela HOME começa oculta")
else:
    print("✗ Tabela HOME NÃO começa oculta")

if awayTable in content:
    print("✓ Tabela AWAY começa oculta")
else:
    print("✗ Tabela AWAY NÃO começa oculta")

# Verificar que títulos têm classe collapsed
if 'ligaTotals-title collapsed' in content:
    print("✓ Títulos de Liga têm classe 'collapsed'")
else:
    print("✗ Títulos de Liga NÃO têm classe 'collapsed'")

# Verificar chamadas de renderLigaTotalsTable com novo formato
calls = re.findall(r"renderLigaTotalsTable\('([^']+)',\s*'([^']+)',", content)
if len(calls) == 2:
    print(f"✓ Encontradas 2 chamadas de renderLigaTotalsTable com novo formato (containerID, tableID)")
    for i, (container, table) in enumerate(calls, 1):
        print(f"  {i}. container={container}, table={table}")
else:
    print(f"✗ Esperado 2 chamadas, encontradas {len(calls)}")

# Verificar setas para collapse/expand
if '▶' in content or '▼' in content:
    print("✓ Símbolos de seta para toggle encontrados")
else:
    print("⚠ Símbolos de seta NÃO encontrados (possível problema de encoding)")

print("\n" + "=" * 60)
print("VALIDAÇÃO CONCLUÍDA")
print("=" * 60)
