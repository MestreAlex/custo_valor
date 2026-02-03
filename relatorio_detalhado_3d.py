"""
Relatório detalhado tridimensional: LIGA / TIPO (DxG) / ENTRADA (HOME/AWAY)
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

def formatar_tabela(dados_lista, titulo, colunas):
    """Formata e exibe uma tabela"""
    if not dados_lista:
        return
    
    print(f"\n{titulo}")
    print("=" * 150)
    
    # Cabeçalho
    linha_header = ""
    for col in colunas:
        if col.get('align') == 'left':
            linha_header += f"{col['nome']:<{col['width']}} "
        elif col.get('align') == 'center':
            linha_header += f"{col['nome']:^{col['width']}} "
        else:
            linha_header += f"{col['nome']:>{col['width']}} "
    
    print(linha_header)
    print("-" * 150)
    
    # Dados
    for item in dados_lista:
        linha = ""
        for col in colunas:
            valor = item.get(col['key'], '')
            if col.get('align') == 'left':
                linha += f"{str(valor):<{col['width']}} "
            elif col.get('align') == 'center':
                linha += f"{str(valor):^{col['width']}} "
            else:
                linha += f"{str(valor):>{col['width']}} "
        print(linha)

def relatorio_detalhado():
    """Gera relatório tridimensional com filtros"""
    
    print("📖 Carregando dados...")
    print(f"   Filtros: Entradas >= {MIN_ENTRADAS}, ROI >= {MIN_ROI}%, Lucro >= R${MIN_LUCRO:.2f}")
    with open(BACKTEST_ACUMULADO, 'r', encoding='utf-8') as f:
        entradas = json.load(f)
    
    print(f"   ✓ {len(entradas):,} entradas carregadas\n")
    
    # Agrupar por liga, tipo, entrada
    grupos_3d = defaultdict(lambda: {
        'entradas': 0,
        'lucro': 0.0,
        'positivos': 0,
        'negativos': 0
    })
    
    print("🔄 Processando dados em 3 dimensões...")
    
    for entrada in entradas:
        liga = entrada['liga']
        tipo = entrada['dxg']
        entrada_tipo = entrada['entrada']  # HOME ou AWAY
        lp = entrada['lp']
        
        # Chave: LIGA + TIPO + ENTRADA
        chave = f"{liga}|{tipo}|{entrada_tipo}"
        
        grupos_3d[chave]['liga'] = liga
        grupos_3d[chave]['tipo'] = tipo
        grupos_3d[chave]['entrada'] = entrada_tipo
        grupos_3d[chave]['entradas'] += 1
        grupos_3d[chave]['lucro'] += lp
        
        if lp > 0:
            grupos_3d[chave]['positivos'] += 1
        else:
            grupos_3d[chave]['negativos'] += 1
    
    # Calcular ROI e winrate
    for dados in grupos_3d.values():
        if dados['entradas'] > 0:
            dados['winrate'] = (dados['positivos'] / dados['entradas']) * 100
            dados['roi'] = (dados['lucro'] / dados['entradas']) * 100
    
    # Aplicar filtros
    grupos_filtrados = {}
    for chave, dados in grupos_3d.items():
        if (dados['entradas'] >= MIN_ENTRADAS and 
            dados['roi'] >= MIN_ROI and 
            dados['lucro'] >= MIN_LUCRO):
            grupos_filtrados[chave] = dados
    
    print(f"   ✓ {len(grupos_3d)} combinações processadas")
    print(f"   ✓ {len(grupos_filtrados)} combinações atendem aos filtros\n")
    
    # ===== RELATÓRIO POR LIGA =====
    print("\n" + "=" * 150)
    print("📊 RELATÓRIO DETALHADO POR LIGA")
    print("=" * 150)
    
    # Agrupar por liga
    por_liga = defaultdict(lambda: {
        'entradas': 0,
        'lucro': 0.0,
        'positivos': 0,
        'tipos': defaultdict(lambda: {
            'entradas': 0,
            'lucro': 0.0,
            'positivos': 0
        })
    })
    
    for chave, dados in grupos_filtrados.items():
        liga = dados['liga']
        tipo = dados['tipo']
        
        por_liga[liga]['entradas'] += dados['entradas']
        por_liga[liga]['lucro'] += dados['lucro']
        por_liga[liga]['positivos'] += dados['positivos']
        
        por_liga[liga]['tipos'][tipo]['entradas'] += dados['entradas']
        por_liga[liga]['tipos'][tipo]['lucro'] += dados['lucro']
        por_liga[liga]['tipos'][tipo]['positivos'] += dados['positivos']
    
    # Exibir por liga
    for liga in sorted(por_liga.keys()):
        dados_liga = por_liga[liga]
        roi_liga = (dados_liga['lucro'] / dados_liga['entradas']) * 100 if dados_liga['entradas'] > 0 else 0
        wr_liga = (dados_liga['positivos'] / dados_liga['entradas']) * 100 if dados_liga['entradas'] > 0 else 0
        
        print(f"\n🏟️  LIGA: {liga}")
        print(f"   📊 Total: {dados_liga['entradas']:,} entradas | Lucro: R$ {dados_liga['lucro']:,.2f} | ROI: {roi_liga:.2f}% | Winrate: {wr_liga:.1f}%")
        
        # Tabela por tipo para esta liga
        print(f"\n   {'Tipo':<6} {'Entrada':<8} {'Entradas':>10} {'Winrate':>10} {'Lucro':>15} {'ROI':>8}")
        print(f"   {'-'*70}")
        
        for chave, dados in sorted(grupos_filtrados.items()):
            if dados['liga'] == liga:
                print(f"   {dados['tipo']:<6} {dados['entrada']:<8} {dados['entradas']:>10} {dados['winrate']:>9.1f}% R${dados['lucro']:>13.2f} {dados['roi']:>7.2f}%")
    
    # ===== RELATÓRIO POR TIPO =====
    print("\n\n" + "=" * 150)
    print("🎯 RELATÓRIO DETALHADO POR TIPO (DxG)")
    print("=" * 150)
    
    por_tipo = defaultdict(lambda: {
        'entradas': 0,
        'lucro': 0.0,
        'positivos': 0,
        'ligas': defaultdict(lambda: {
            'entradas': 0,
            'lucro': 0.0,
            'positivos': 0
        })
    })
    
    for chave, dados in grupos_filtrados.items():
        tipo = dados['tipo']
        liga = dados['liga']
        
        por_tipo[tipo]['entradas'] += dados['entradas']
        por_tipo[tipo]['lucro'] += dados['lucro']
        por_tipo[tipo]['positivos'] += dados['positivos']
        
        por_tipo[tipo]['ligas'][liga]['entradas'] += dados['entradas']
        por_tipo[tipo]['ligas'][liga]['lucro'] += dados['lucro']
        por_tipo[tipo]['ligas'][liga]['positivos'] += dados['positivos']
    
    for tipo in ['FH', 'LH', 'EQ', 'LA', 'FA']:
        if tipo in por_tipo:
            dados_tipo = por_tipo[tipo]
            roi_tipo = (dados_tipo['lucro'] / dados_tipo['entradas']) * 100 if dados_tipo['entradas'] > 0 else 0
            wr_tipo = (dados_tipo['positivos'] / dados_tipo['entradas']) * 100 if dados_tipo['entradas'] > 0 else 0
            
            print(f"\n🎯 TIPO: {tipo}")
            print(f"   📊 Total: {dados_tipo['entradas']:,} entradas | Lucro: R$ {dados_tipo['lucro']:,.2f} | ROI: {roi_tipo:.2f}% | Winrate: {wr_tipo:.1f}%")
            
            # Tabela HOME/AWAY para este tipo
            home_away = defaultdict(lambda: {'entradas': 0, 'lucro': 0.0, 'positivos': 0})
            
            for chave, dados in grupos_filtrados.items():
                if dados['tipo'] == tipo:
                    entrada = dados['entrada']
                    home_away[entrada]['entradas'] += dados['entradas']
                    home_away[entrada]['lucro'] += dados['lucro']
                    home_away[entrada]['positivos'] += dados['positivos']
            
            print(f"\n   {'Entrada':<8} {'Liga':<8} {'Entradas':>10} {'Winrate':>10} {'Lucro':>15} {'ROI':>8}")
            print(f"   {'-'*70}")
            
            for chave, dados in sorted(grupos_3d.items()):
                if dados['tipo'] == tipo:
                    print(f"   {dados['entrada']:<8} {dados['liga']:<8} {dados['entradas']:>10} {dados['winrate']:>9.1f}% R${dados['lucro']:>13.2f} {dados['roi']:>7.2f}%")
    
    # ===== RELATÓRIO POR ENTRADA (HOME/AWAY) =====
    print("\n\n" + "=" * 150)
    print("🔄 RELATÓRIO DETALHADO POR ENTRADA (HOME/AWAY)")
    print("=" * 150)
    
    por_entrada = defaultdict(lambda: {
        'entradas': 0,
        'lucro': 0.0,
        'positivos': 0
    })
    
    for chave, dados in grupos_filtrados.items():
        entrada = dados['entrada']
        
        por_entrada[entrada]['entradas'] += dados['entradas']
        por_entrada[entrada]['lucro'] += dados['lucro']
        por_entrada[entrada]['positivos'] += dados['positivos']
    
    print()
    for entrada in ['HOME', 'AWAY']:
        if entrada in por_entrada and por_entrada[entrada]['entradas'] > 0:
            dados_entrada = por_entrada[entrada]
            roi_entrada = (dados_entrada['lucro'] / dados_entrada['entradas']) * 100 if dados_entrada['entradas'] > 0 else 0
            wr_entrada = (dados_entrada['positivos'] / dados_entrada['entradas']) * 100 if dados_entrada['entradas'] > 0 else 0
            
            print(f"\n🔄 ENTRADA: {entrada}")
            print(f"   📊 Total: {dados_entrada['entradas']:,} entradas | Lucro: R$ {dados_entrada['lucro']:,.2f} | ROI: {roi_entrada:.2f}% | Winrate: {wr_entrada:.1f}%")
            
            # Tabela tipo/liga para esta entrada
            print(f"\n   {'Tipo':<6} {'Liga':<8} {'Entradas':>10} {'Winrate':>10} {'Lucro':>15} {'ROI':>8}")
            print(f"   {'-'*70}")
            
            for chave, dados in sorted(grupos_filtrados.items()):
                if dados['entrada'] == entrada:
                    print(f"   {dados['tipo']:<6} {dados['liga']:<8} {dados['entradas']:>10} {dados['winrate']:>9.1f}% R${dados['lucro']:>13.2f} {dados['roi']:>7.2f}%")
    
    # ===== RESUMO GERAL =====
    print("\n\n" + "=" * 150)
    print("📈 RESUMO GERAL (FILTRADO)")
    print("=" * 150)
    
    total_entradas = sum(d['entradas'] for d in grupos_filtrados.values())
    total_lucro = sum(d['lucro'] for d in grupos_filtrados.values())
    total_positivos = sum(d['positivos'] for d in grupos_filtrados.values())
    
    roi_geral = (total_lucro / total_entradas * 100) if total_entradas > 0 else 0
    wr_geral = (total_positivos / total_entradas * 100) if total_entradas > 0 else 0
    
    print(f"\n📊 Total de combinações (LIGA/TIPO/ENTRADA): {len(grupos_filtrados)}")
    print(f"📝 Total de entradas: {total_entradas:,}")
    print(f"💰 Lucro total: R$ {total_lucro:,.2f}")
    print(f"📈 ROI geral: {roi_geral:.2f}%")
    print(f"🎯 Winrate geral: {wr_geral:.1f}%")
    
    # Top 10 melhores combinações
    print("\n\n" + "=" * 150)
    print("🏆 TOP 10 MELHORES COMBINAÇÕES (MAIOR LUCRO)")
    print("=" * 150)
    
    top_10 = sorted(grupos_filtrados.items(), key=lambda x: x[1]['lucro'], reverse=True)[:10]
    
    print(f"\n{'#':<3} {'Liga':<8} {'Tipo':<6} {'Entrada':<8} {'Entradas':>10} {'Winrate':>10} {'Lucro':>15} {'ROI':>8}")
    print("-" * 150)
    
    for i, (chave, dados) in enumerate(top_10, 1):
        print(f"{i:<3} {dados['liga']:<8} {dados['tipo']:<6} {dados['entrada']:<8} {dados['entradas']:>10} {dados['winrate']:>9.1f}% R${dados['lucro']:>13.2f} {dados['roi']:>7.2f}%")
    
    # Top 10 piores combinações (se houver negativas)
    negativas = [item for item in grupos_filtrados.items() if item[1]['lucro'] < 0]
    if negativas:
        print("\n\n" + "=" * 150)
        print("⚠️  TOP 10 PIORES COMBINAÇÕES (MENOR LUCRO)")
        print("=" * 150)
        
        bottom_10 = sorted(negativas, key=lambda x: x[1]['lucro'])[:10]
        
        print(f"\n{'#':<3} {'Liga':<8} {'Tipo':<6} {'Entrada':<8} {'Entradas':>10} {'Winrate':>10} {'Lucro':>15} {'ROI':>8}")
        print("-" * 150)
        
        for i, (chave, dados) in enumerate(bottom_10, 1):
            print(f"{i:<3} {dados['liga']:<8} {dados['tipo']:<6} {dados['entrada']:<8} {dados['entradas']:>10} {dados['winrate']:>9.1f}% R${dados['lucro']:>13.2f} {dados['roi']:>7.2f}%")
    else:
        print("\n✅ Não há combinações com lucro negativo após filtros!")
    
    print("\n" + "=" * 150)

if __name__ == '__main__':
    try:
        relatorio_detalhado()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
