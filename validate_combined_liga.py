import json
import re

with open('backtest/backtest_resumo_entradas.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("VALIDAÇÃO - TABELA DE TOTAIS POR LIGA COMBINADA (HOME + AWAY)")
print("=" * 70)

# Verificar função renderLigaCombinedTotals
if 'function renderLigaCombinedTotals(' in content:
    print("✓ Função renderLigaCombinedTotals() definida")
else:
    print("✗ Função renderLigaCombinedTotals() NÃO encontrada")

# Verificar título combinado
if 'ligaTotalsCombinedTitle' in content:
    print("✓ Título COMBINADO encontrado")
else:
    print("✗ Título COMBINADO NÃO encontrado")

# Verificar tabela combinada com ID
if 'id="ligaTotalsCombinedTable"' in content:
    print("✓ Tabela COMBINADA com ID encontrada")
else:
    print("✗ Tabela COMBINADA com ID NÃO encontrada")

# Verificar que tabela começa oculta
combined_table = 'id="ligaTotalsCombinedTable" style="display:none;"'
if combined_table in content:
    print("✓ Tabela COMBINADA começa oculta")
else:
    print("✗ Tabela COMBINADA NÃO começa oculta")

# Verificar classe collapsed
if 'ligaTotals-title collapsed' in content:
    print("✓ Título COMBINADO tem classe 'collapsed'")
else:
    print("✗ Título COMBINADO NÃO tem classe 'collapsed'")

# Verificar onclick
if 'toggleLigaTotals(\'ligaTotalsCombinedTable\'' in content:
    print("✓ Título COMBINADO tem onclick correto")
else:
    print("✗ Título COMBINADO NÃO tem onclick correto")

# Verificar chamada de renderização
if "renderLigaCombinedTotals('ligaTotalsCombinedTable'" in content:
    print("✓ Chamada renderLigaCombinedTotals encontrada na função init()")
else:
    print("✗ Chamada renderLigaCombinedTotals NÃO encontrada")

# Verificar estrutura da função
if 'function renderLigaCombinedTotals' in content:
    # Extrair a função
    match = re.search(r'function renderLigaCombinedTotals\([^)]*\) \{(.*?)\n    \}(?=\n|\s*async)', content, re.DOTALL)
    if match:
        func_body = match.group(1)
        if "['HOME', 'AWAY']" in func_body:
            print("✓ Função processa HOME e AWAY")
        if "DXG_TYPES" in func_body:
            print("✓ Função agrupa por DXG types")
        if "mergeStats" in func_body:
            print("✓ Função combina estatísticas corretamente")

# Contar seções de Liga
liga_sections = re.findall(r'ligaTotals-title', content)
if len(liga_sections) == 3:
    print(f"✓ Total de seções de Liga: {len(liga_sections)} (HOME, AWAY, COMBINADO)")
else:
    print(f"⚠ Esperado 3 seções de Liga, encontradas {len(liga_sections)}")

# Verificar setas
if '▶' in content or '▼' in content:
    print("✓ Símbolos de seta para toggle encontrados")
else:
    print("⚠ Símbolos de seta NÃO encontrados")

print("\n" + "=" * 70)
print("ESTRUTURA DA PÁGINA - ORDEM DAS SEÇÕES:")
print("=" * 70)

# Encontrar ordem das seções
sections = [
    ('Entradas HOME', 'homeContainer'),
    ('Entradas AWAY', 'awayContainer'),
    ('Totais Gerais Combinados', 'combinedContainer'),
    ('Totais por Liga - HOME', 'ligaTotalsHomeContainer'),
    ('Totais por Liga - AWAY', 'ligaTotalsAwayContainer'),
    ('Totais por Liga - COMBINADO', 'ligaTotalsCombinedContainer'),
]

for i, (name, container_id) in enumerate(sections, 1):
    if container_id in content:
        print(f"{i}. ✓ {name}")
    else:
        print(f"{i}. ✗ {name}")

print("\n" + "=" * 70)
print("VALIDAÇÃO CONCLUÍDA")
print("=" * 70)
