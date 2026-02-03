"""
Converter backtest_entradas_reais.json para backtest_acumulado.json
Usa os dados REAIS de cada entrada individual com DxG correto
"""

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / 'fixtures'
BACKTEST_ENTRADAS_REAIS = FIXTURES_DIR / 'backtest_entradas_reais.json'
BACKTEST_ACUMULADO = FIXTURES_DIR / 'backtest_acumulado.json'

def converter_entradas_reais():
    """Converte entradas reais para formato backtest_acumulado"""
    
    # Verificar se arquivo com entradas reais existe
    if not BACKTEST_ENTRADAS_REAIS.exists():
        print(f"❌ Arquivo não encontrado: {BACKTEST_ENTRADAS_REAIS.name}")
        print("\n⚠️  Você precisa executar NOVAMENTE o backtest com a versão modificada:")
        print("    python executar_backtest_completo.py")
        print("\n   Isso vai gerar: backtest_entradas_reais.json")
        return False
    
    print("📖 Lendo entradas reais...")
    with open(BACKTEST_ENTRADAS_REAIS, 'r', encoding='utf-8') as f:
        entradas_reais = json.load(f)
    
    print(f"   ✓ {len(entradas_reais):,} entradas carregadas")
    
    # Converter para formato backtest_acumulado
    # Format: lista de entradas com campos: liga, temporada, entrada, dxg, lp
    entradas_formatadas = []
    
    print("\n🔄 Formatando entradas para backtest_acumulado...")
    
    for entrada in entradas_reais:
        entrada_formatada = {
            'liga': entrada.get('liga'),
            'temporada': entrada.get('temporada'),
            'entrada': entrada.get('entrada'),
            'dxg': entrada.get('dxg'),
            'lp': entrada.get('lp')
        }
        entradas_formatadas.append(entrada_formatada)
    
    # Salvar
    print(f"   ✓ Salvando {len(entradas_formatadas):,} entradas formatadas...")
    with open(BACKTEST_ACUMULADO, 'w', encoding='utf-8') as f:
        json.dump(entradas_formatadas, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Sucesso!")
    print(f"   📁 Arquivo: {BACKTEST_ACUMULADO.name}")
    print(f"   📊 Total de entradas: {len(entradas_formatadas):,}")
    
    # Análise rápida
    print("\n📈 Análise dos dados:")
    
    # Contar por tipo DxG
    por_dxg = {}
    for entrada in entradas_formatadas:
        dxg = entrada['dxg']
        if dxg not in por_dxg:
            por_dxg[dxg] = {'positivos': 0, 'negativos': 0, 'total': 0, 'lucro': 0}
        
        por_dxg[dxg]['total'] += 1
        por_dxg[dxg]['lucro'] += entrada['lp']
        
        if entrada['lp'] > 0:
            por_dxg[dxg]['positivos'] += 1
        else:
            por_dxg[dxg]['negativos'] += 1
    
    print("\n   Por tipo de DxG:")
    for dxg in ['FH', 'LH', 'EQ', 'LA', 'FA']:
        if dxg in por_dxg:
            dados = por_dxg[dxg]
            winrate = (dados['positivos'] / dados['total'] * 100) if dados['total'] > 0 else 0
            roi = (dados['lucro'] / dados['total'] * 100) if dados['total'] > 0 else 0
            print(f"     {dxg}: {dados['total']:5d} entradas | {winrate:5.1f}% | Lucro: R${dados['lucro']:8.2f} | ROI: {roi:6.2f}%")
    
    # Contar por entrada (HOME/AWAY)
    por_entrada = {}
    for entrada in entradas_formatadas:
        tipo = entrada['entrada']
        if tipo not in por_entrada:
            por_entrada[tipo] = {'positivos': 0, 'negativos': 0, 'total': 0, 'lucro': 0}
        
        por_entrada[tipo]['total'] += 1
        por_entrada[tipo]['lucro'] += entrada['lp']
        
        if entrada['lp'] > 0:
            por_entrada[tipo]['positivos'] += 1
        else:
            por_entrada[tipo]['negativos'] += 1
    
    print("\n   Por tipo de entrada (HOME/AWAY):")
    for tipo in ['HOME', 'AWAY']:
        if tipo in por_entrada:
            dados = por_entrada[tipo]
            winrate = (dados['positivos'] / dados['total'] * 100) if dados['total'] > 0 else 0
            roi = (dados['lucro'] / dados['total'] * 100) if dados['total'] > 0 else 0
            print(f"     {tipo:4s}: {dados['total']:5d} entradas | {winrate:5.1f}% | Lucro: R${dados['lucro']:8.2f} | ROI: {roi:6.2f}%")
    
    print(f"\n✨ A página http://localhost:5001/backtest_resumo_entradas.html agora carregará dados REAIS!")
    
    return True

if __name__ == '__main__':
    try:
        converter_entradas_reais()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
