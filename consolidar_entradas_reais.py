"""
Consolidar todas as entradas individuais do backtest em um arquivo JSON
Lê os dados salvos pelo BacktestEngine e cria um arquivo com TODAS as entradas
com dados reais de liga, temporada, entrada, dxg, lp
"""

import json
from pathlib import Path
from collections import defaultdict

BACKTEST_DIR = Path(__file__).parent / 'backtest'
FIXTURES_DIR = Path(__file__).parent / 'fixtures'

def consolidar_entradas_reais():
    """Lê os arquivos de resultados salvos e consolida entradas reais"""
    
    # Ligas conhecidas (as que foram processadas)
    TODAS_LIGAS = {
        'E0': 'Premier League',
        'E1': 'Championship',
        'SP1': 'La Liga',
        'SP2': 'La Liga 2',
        'I1': 'Serie A',
        'I2': 'Serie B',
        'D1': 'Bundesliga',
        'D2': 'Bundesliga 2',
        'F1': 'Ligue 1',
        'F2': 'Ligue 2',
        'B1': 'Jupiler Pro League',
        'N1': 'Eredivisie',
        'P1': 'Primeira Liga',
        'T1': 'Süper Lig',
        'ARG': 'Primera División',
        'AUT': 'Bundesliga Áustria',
        'BRA': 'Série A Brasil',
        'CHN': 'Super League',
        'DNK': 'Superliga',
        'FIN': 'Veikkausliiga',
        'IRL': 'League of Ireland',
        'JPN': 'J1 League',
        'MEX': 'Liga MX',
        'NOR': 'Eliteserien',
        'POL': 'Ekstraklasa',
        'ROU': 'Liga 1',
        'RUS': 'Premier League',
        'SWE': 'Allsvenskan',
        'SWZ': 'Super League',
        'USA': 'MLS'
    }
    
    entradas_consolidadas = []
    liga_counter = 0
    
    print("🔍 Consolidando entradas individuais do backtest...")
    print("=" * 80)
    
    # Para cada liga, procurar pelos arquivos de resultados
    for liga_codigo, liga_nome in sorted(TODAS_LIGAS.items()):
        # Verificar se há arquivo de treino com essa liga
        arquivo_treino = BACKTEST_DIR / f'{liga_codigo}_treino.csv'
        
        if arquivo_treino.exists():
            # Carregar arquivo de resultados
            # O BacktestEngine salva em backtest_resultados.json durante a execução
            # Mas para cada liga, precisamos buscar os dados salvos
            
            # Estratégia: usar backtest_historico_completo_2012_2026.json
            # e extrair dados por liga
            pass
    
    # Melhor estratégia: ler backtest_historico_completo_2012_2026.json
    # e para cada entrada acumulada, criar registros individuais
    # Mas isso é artificial
    
    # Estratégia CORRETA: Modificar executar_backtest_completo.py para salvar
    # todas as entradas individuais em um arquivo consolidado
    # Por enquanto, retornar mensagem
    
    print("\n❌ Não foi encontrada estrutura com entradas individuais por liga")
    print("\n🔧 Solução necessária:")
    print("   1. Modificar executar_backtest_completo.py para coletar")
    print("      entradas de cada BacktestEngine")
    print("   2. Salvar em arquivo: backtest_entradas_reais.json")
    print("   3. Ler desse arquivo para popular backtest_acumulado.json")
    
    return None

if __name__ == '__main__':
    consolidar_entradas_reais()
