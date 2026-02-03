import json
from collections import defaultdict
from pathlib import Path

# Função de desconto
def aplicar_desconto_lucro(lp):
    return lp * 0.955

# Carregar dados
with open('fixtures/backtest_acumulado.json', 'r', encoding='utf-8') as f:
    entradas = json.load(f)

# Estrutura: { liga_tipo_dxg: {entradas, lucro, winrate, roi} }
resumo = defaultdict(lambda: {'entradas': 0, 'lucro': 0.0, 'acertos': 0})

for entrada in entradas:
    liga = entrada.get('liga', 'Desconhecida')
    lp = float(entrada.get('lp', 0))
    lp_com_desconto = aplicar_desconto_lucro(lp)
    tipo_entrada = entrada.get('entrada', 'HOME')
    dxg_tipo = entrada.get('dxg', 'EQ')
    
    chave = f'{liga}|{tipo_entrada}|{dxg_tipo}'
    
    dados = resumo[chave]
    dados['entradas'] += 1
    dados['lucro'] += lp_com_desconto
    if lp_com_desconto > 0:
        dados['acertos'] += 1

# Calcular winrate e ROI, e filtrar
resultados_filtrados = []
for chave, dados in resumo.items():
    if dados['entradas'] > 0:
        dados['winrate'] = (dados['acertos'] / dados['entradas']) * 100
        dados['roi'] = (dados['lucro'] / dados['entradas']) * 100
    
    # Aplicar filtros: entradas >= 30, ROI >= 5%, lucro >= 5
    if dados['entradas'] >= 30 and dados['roi'] >= 5.0 and dados['lucro'] >= 5.0:
        liga, tipo, dxg = chave.split('|')
        resultados_filtrados.append({
            'liga': liga,
            'tipo': tipo,
            'dxg': dxg,
            'entradas': dados['entradas'],
            'lucro': round(dados['lucro'], 2),
            'roi': round(dados['roi'], 2),
            'winrate': round(dados['winrate'], 2)
        })

# Ordenar por ROI decrescente
resultados_filtrados.sort(key=lambda x: x['roi'], reverse=True)

# Exibir resultados
print(f'\n📊 RELATÓRIO - ENTRADAS QUE ATENDEM OS CRITÉRIOS')
print(f'='*100)
print(f'Filtros Aplicados:')
print(f'  - Quantidade de entradas >= 30')
print(f'  - ROI >= 5%')
print(f'  - Lucro >= 5.0')
print(f'\nTotal de Entradas Qualificadas: {len(resultados_filtrados)}')
print(f'='*100)
print()

# Cabeçalho da tabela
print(f'{"Nº":<4} {"Liga":<12} {"Tipo":<6} {"DxG":<5} {"Entradas":<10} {"Lucro":<10} {"ROI %":<10} {"Winrate %":<12}')
print(f'-'*100)

for i, r in enumerate(resultados_filtrados, 1):
    print(f'{i:<4} {r["liga"]:<12} {r["tipo"]:<6} {r["dxg"]:<5} {r["entradas"]:<10} {r["lucro"]:<10.2f} {r["roi"]:<10.2f} {r["winrate"]:<12.2f}')

print(f'='*100)

# Estatísticas gerais
print(f'\n📈 ESTATÍSTICAS GERAIS:')
print(f'Total de combinações qualificadas: {len(resultados_filtrados)}')

# Contar por tipo
tipos_count = defaultdict(int)
for r in resultados_filtrados:
    tipos_count[r['tipo']] += 1

print(f'\nDistribuição por Tipo:')
for tipo, count in sorted(tipos_count.items()):
    print(f'  {tipo}: {count} entradas')

# Contar por DxG
dxg_count = defaultdict(int)
for r in resultados_filtrados:
    dxg_count[r['dxg']] += 1

print(f'\nDistribuição por DxG:')
for dxg, count in sorted(dxg_count.items()):
    print(f'  {dxg}: {count} entradas')

# Contar por Liga
liga_count = defaultdict(int)
for r in resultados_filtrados:
    liga_count[r['liga']] += 1

print(f'\nDistribuição por Liga:')
for liga, count in sorted(liga_count.items(), key=lambda x: x[1], reverse=True):
    print(f'  {liga}: {count} entradas')

# Salvar relatório em arquivo
with open('RELATORIO_ENTRADAS_QUALIFICADAS.txt', 'w', encoding='utf-8') as f:
    f.write('='*100 + '\n')
    f.write('📊 RELATÓRIO - ENTRADAS QUE ATENDEM OS CRITÉRIOS\n')
    f.write('='*100 + '\n')
    f.write(f'Filtros Aplicados:\n')
    f.write(f'  - Quantidade de entradas >= 30\n')
    f.write(f'  - ROI >= 5%\n')
    f.write(f'  - Lucro >= 5.0\n')
    f.write(f'\nTotal de Entradas Qualificadas: {len(resultados_filtrados)}\n')
    f.write('='*100 + '\n\n')
    
    f.write(f'{"Nº":<4} {"Liga":<12} {"Tipo":<6} {"DxG":<5} {"Entradas":<10} {"Lucro":<10} {"ROI %":<10} {"Winrate %":<12}\n')
    f.write(f'-'*100 + '\n')
    
    for i, r in enumerate(resultados_filtrados, 1):
        f.write(f'{i:<4} {r["liga"]:<12} {r["tipo"]:<6} {r["dxg"]:<5} {r["entradas"]:<10} {r["lucro"]:<10.2f} {r["roi"]:<10.2f} {r["winrate"]:<12.2f}\n')
    
    f.write('='*100 + '\n')
    
    f.write(f'\n📈 ESTATÍSTICAS GERAIS:\n')
    f.write(f'Total de combinações qualificadas: {len(resultados_filtrados)}\n')
    
    f.write(f'\nDistribuição por Tipo:\n')
    for tipo, count in sorted(tipos_count.items()):
        f.write(f'  {tipo}: {count} entradas\n')
    
    f.write(f'\nDistribuição por DxG:\n')
    for dxg, count in sorted(dxg_count.items()):
        f.write(f'  {dxg}: {count} entradas\n')
    
    f.write(f'\nDistribuição por Liga:\n')
    for liga, count in sorted(liga_count.items(), key=lambda x: x[1], reverse=True):
        f.write(f'  {liga}: {count} entradas\n')

print(f'\n✅ Relatório salvo em: RELATORIO_ENTRADAS_QUALIFICADAS.txt')
