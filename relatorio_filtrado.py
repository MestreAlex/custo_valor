"""
Gerar relatório filtrado do backtest com critérios específicos
Filtros:
- Quantidade de entradas >= 75
- ROI >= 5%
- Lucro >= 20
"""

import json
from pathlib import Path
from collections import defaultdict

FIXTURES_DIR = Path(__file__).parent / 'fixtures'
BACKTEST_ACUMULADO = FIXTURES_DIR / 'backtest_acumulado.json'

# Critérios de filtro
MIN_ENTRADAS = 75
MIN_ROI = 5.0
MIN_LUCRO = 20.0

def aplicar_filtros():
    """Aplica filtros e gera relatório"""
    
    # Carregar dados
    print("📖 Carregando dados...")
    with open(BACKTEST_ACUMULADO, 'r', encoding='utf-8') as f:
        entradas = json.load(f)
    
    print(f"   ✓ {len(entradas):,} entradas carregadas")
    
    # Agrupar por liga + temporada + tipo
    print("\n🔄 Agrupando dados e aplicando filtros...")
    
    grupos = defaultdict(lambda: {
        'entradas': 0,
        'lucro': 0.0,
        'positivos': 0,
        'negativos': 0
    })
    
    for entrada in entradas:
        liga = entrada['liga']
        temporada = entrada['temporada']
        tipo = entrada['dxg']
        lp = entrada['lp']
        
        # Criar chave única
        chave = f"{liga}_{temporada}_{tipo}"
        
        grupos[chave]['liga'] = liga
        grupos[chave]['temporada'] = temporada
        grupos[chave]['tipo'] = tipo
        grupos[chave]['entradas'] += 1
        grupos[chave]['lucro'] += lp
        
        if lp > 0:
            grupos[chave]['positivos'] += 1
        else:
            grupos[chave]['negativos'] += 1
    
    # Calcular ROI para cada grupo
    for chave, dados in grupos.items():
        if dados['entradas'] > 0:
            dados['winrate'] = (dados['positivos'] / dados['entradas']) * 100
            dados['roi'] = (dados['lucro'] / dados['entradas']) * 100
        else:
            dados['winrate'] = 0
            dados['roi'] = 0
    
    # Filtrar
    print("\n🎯 Aplicando filtros:")
    print(f"   - Entradas >= {MIN_ENTRADAS}")
    print(f"   - ROI >= {MIN_ROI}%")
    print(f"   - Lucro >= R${MIN_LUCRO:.2f}")
    
    resultados_filtrados = []
    
    for chave, dados in grupos.items():
        if (dados['entradas'] >= MIN_ENTRADAS and 
            dados['roi'] >= MIN_ROI and 
            dados['lucro'] >= MIN_LUCRO):
            resultados_filtrados.append(dados)
    
    # Ordenar por lucro descendente
    resultados_filtrados.sort(key=lambda x: x['lucro'], reverse=True)
    
    print(f"\n✅ {len(resultados_filtrados)} combinações atendem aos critérios!\n")
    
    # Exibir relatório em tabela
    if resultados_filtrados:
        print("=" * 120)
        print("📊 RELATÓRIO FILTRADO - BACKTEST HISTÓRICO (2013-2026)")
        print("=" * 120)
        
        # Preparar dados para tabela
        tabela_dados = []
        for i, dados in enumerate(resultados_filtrados, 1):
            tabela_dados.append([
                i,
                dados['liga'],
                dados['temporada'],
                dados['tipo'],
                dados['entradas'],
                f"{dados['winrate']:.1f}%",
                f"R$ {dados['lucro']:.2f}",
                f"{dados['roi']:.2f}%"
            ])
        
        # Exibir tabela
        headers = ['#', 'Liga', 'Temporada', 'Tipo', 'Entradas', 'Winrate', 'Lucro', 'ROI']
        
        # Montar string com formato de tabela
        print(f"\n{'#':^3} {'Liga':^8} {'Temporada':^12} {'Tipo':^6} {'Entradas':^10} {'Winrate':^10} {'Lucro':^15} {'ROI':^10}")
        print("-" * 120)
        
        for i, dados in enumerate(resultados_filtrados, 1):
            print(f"{i:3d} {dados['liga']:^8} {dados['temporada']:^12} {dados['tipo']:^6} {dados['entradas']:>10} {dados['winrate']:>9.1f}% R${dados['lucro']:>13.2f} {dados['roi']:>9.2f}%")
        
        # Estatísticas gerais
        print("\n" + "=" * 120)
        print("📈 ESTATÍSTICAS GERAIS")
        print("=" * 120)
        
        total_entradas = sum(d['entradas'] for d in resultados_filtrados)
        total_lucro = sum(d['lucro'] for d in resultados_filtrados)
        roi_medio = (total_lucro / total_entradas * 100) if total_entradas > 0 else 0
        total_positivos = sum(d['positivos'] for d in resultados_filtrados)
        winrate_geral = (total_positivos / total_entradas * 100) if total_entradas > 0 else 0
        
        print(f"\n📊 Combinações filtradas: {len(resultados_filtrados)}")
        print(f"📝 Total de entradas: {total_entradas:,}")
        print(f"💰 Lucro total: R$ {total_lucro:,.2f}")
        print(f"📈 ROI médio: {roi_medio:.2f}%")
        print(f"🎯 Winrate geral: {winrate_geral:.1f}%")
        
        # Top 5
        print("\n" + "=" * 120)
        print("🏆 TOP 5 - MAIOR LUCRO")
        print("=" * 120 + "\n")
        
        for i, dados in enumerate(resultados_filtrados[:5], 1):
            print(f"{i}. {dados['liga']} - {dados['temporada']} - {dados['tipo']:2s}")
            print(f"   Entradas: {dados['entradas']:4d} | Winrate: {dados['winrate']:5.1f}% | Lucro: R$ {dados['lucro']:8.2f} | ROI: {dados['roi']:6.2f}%\n")
        
        # Por tipo (DxG)
        print("=" * 120)
        print("📊 ANÁLISE POR TIPO (DxG)")
        print("=" * 120)
        
        por_tipo = defaultdict(lambda: {'entradas': 0, 'lucro': 0.0, 'positivos': 0})
        
        for dados in resultados_filtrados:
            tipo = dados['tipo']
            por_tipo[tipo]['entradas'] += dados['entradas']
            por_tipo[tipo]['lucro'] += dados['lucro']
            por_tipo[tipo]['positivos'] += dados['positivos']
        
        tipo_tabela = []
        for tipo in ['FH', 'LH', 'EQ', 'LA', 'FA']:
            if tipo in por_tipo:
                dados_tipo = por_tipo[tipo]
                roi = (dados_tipo['lucro'] / dados_tipo['entradas'] * 100) if dados_tipo['entradas'] > 0 else 0
                winrate = (dados_tipo['positivos'] / dados_tipo['entradas'] * 100) if dados_tipo['entradas'] > 0 else 0
                tipo_tabela.append([
                    tipo,
                    dados_tipo['entradas'],
                    f"{winrate:.1f}%",
                    f"R$ {dados_tipo['lucro']:.2f}",
                    f"{roi:.2f}%"
                ])
        
        headers_tipo = ['Tipo', 'Entradas', 'Winrate', 'Lucro', 'ROI']
        
        print(f"\n{'Tipo':^8} {'Entradas':^12} {'Winrate':^12} {'Lucro':^18} {'ROI':^10}")
        print("-" * 70)
        
        for tipo in ['FH', 'LH', 'EQ', 'LA', 'FA']:
            if tipo in por_tipo:
                dados_tipo = por_tipo[tipo]
                roi = (dados_tipo['lucro'] / dados_tipo['entradas'] * 100) if dados_tipo['entradas'] > 0 else 0
                winrate = (dados_tipo['positivos'] / dados_tipo['entradas'] * 100) if dados_tipo['entradas'] > 0 else 0
                print(f"{tipo:^8} {dados_tipo['entradas']:>12} {winrate:>11.1f}% R${dados_tipo['lucro']:>16.2f} {roi:>9.2f}%")
        
        # Por liga
        print("\n" + "=" * 120)
        print("🏟️  ANÁLISE POR LIGA")
        print("=" * 120)
        
        por_liga = defaultdict(lambda: {'entradas': 0, 'lucro': 0.0, 'positivos': 0})
        
        for dados in resultados_filtrados:
            liga = dados['liga']
            por_liga[liga]['entradas'] += dados['entradas']
            por_liga[liga]['lucro'] += dados['lucro']
            por_liga[liga]['positivos'] += dados['positivos']
        
        print(f"\n{'Liga':^8} {'Entradas':^12} {'Winrate':^12} {'Lucro':^18} {'ROI':^10}")
        print("-" * 70)
        
        for liga, dados_liga in sorted(por_liga.items(), key=lambda x: x[1]['lucro'], reverse=True):
            roi = (dados_liga['lucro'] / dados_liga['entradas'] * 100) if dados_liga['entradas'] > 0 else 0
            winrate = (dados_liga['positivos'] / dados_liga['entradas'] * 100) if dados_liga['entradas'] > 0 else 0
            print(f"{liga:^8} {dados_liga['entradas']:>12} {winrate:>11.1f}% R${dados_liga['lucro']:>16.2f} {roi:>9.2f}%")
        
        print("\n" + "=" * 120)
        
    else:
        print("❌ Nenhuma combinação atende aos critérios!")
        print("\nResumo geral de todas as combinações:")
        
        # Mostrar distribuição
        todas_dados = list(grupos.values())
        
        print(f"\nTotal de combinações: {len(todas_dados)}")
        print(f"Entradas médias: {sum(d['entradas'] for d in todas_dados) / len(todas_dados):.0f}")
        print(f"ROI médio: {sum(d['roi'] for d in todas_dados) / len(todas_dados):.2f}%")
        print(f"Lucro médio: R$ {sum(d['lucro'] for d in todas_dados) / len(todas_dados):.2f}")
        
        # Contar quantas atendem cada critério
        atende_entradas = sum(1 for d in todas_dados if d['entradas'] >= MIN_ENTRADAS)
        atende_roi = sum(1 for d in todas_dados if d['roi'] >= MIN_ROI)
        atende_lucro = sum(1 for d in todas_dados if d['lucro'] >= MIN_LUCRO)
        
        print(f"\nCombinações que atendem CADA critério individualmente:")
        print(f"  - Entradas >= {MIN_ENTRADAS}: {atende_entradas} ({atende_entradas/len(todas_dados)*100:.1f}%)")
        print(f"  - ROI >= {MIN_ROI}%: {atende_roi} ({atende_roi/len(todas_dados)*100:.1f}%)")
        print(f"  - Lucro >= R${MIN_LUCRO:.2f}: {atende_lucro} ({atende_lucro/len(todas_dados)*100:.1f}%)")

if __name__ == '__main__':
    try:
        aplicar_filtros()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
