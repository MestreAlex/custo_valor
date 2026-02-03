"""
Script para executar backtest histórico em TODAS as ligas disponíveis
Versão completa com processamento paralelo e relatórios detalhados
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from collections import defaultdict
import concurrent.futures
import time

# Adicionar pasta backtest ao path
sys.path.append(str(Path(__file__).parent / 'backtest'))
from backtest_engine import BacktestEngine

# TODAS as ligas disponíveis
TODAS_LIGAS = {
    'E0': 'Premier League (Inglaterra)',
    'E1': 'Championship (Inglaterra)',
    'SP1': 'La Liga (Espanha)',
    'SP2': 'La Liga 2 (Espanha)',
    'I1': 'Serie A (Itália)',
    'I2': 'Serie B (Itália)',
    'D1': 'Bundesliga (Alemanha)',
    'D2': 'Bundesliga 2 (Alemanha)',
    'F1': 'Ligue 1 (França)',
    'F2': 'Ligue 2 (França)',
    'B1': 'Jupiler Pro League (Bélgica)',
    'N1': 'Eredivisie (Holanda)',
    'P1': 'Primeira Liga (Portugal)',
    'T1': 'Süper Lig (Turquia)',
    'ARG': 'Primera División (Argentina)',
    'AUT': 'Bundesliga (Áustria)',
    'BRA': 'Série A (Brasil)',
    'CHN': 'Super League (China)',
    'DNK': 'Superliga (Dinamarca)',
    'FIN': 'Veikkausliiga (Finlândia)',
    'IRL': 'Premier Division (Irlanda)',
    'JPN': 'J-League (Japão)',
    'MEX': 'Liga MX (México)',
    'NOR': 'Eliteserien (Noruega)',
    'POL': 'Ekstraklasa (Polônia)',
    'ROU': 'Liga I (Romênia)',
    'RUS': 'Premier League (Rússia)',
    'SWE': 'Allsvenskan (Suécia)',
    'SWZ': 'Super League (Suíça)',
    'USA': 'MLS (Estados Unidos)'
}

def detectar_temporadas_disponiveis(liga):
    """Detecta quais temporadas existem no arquivo da liga"""
    pasta_dados = Path(__file__).parent / 'dados_ligas'
    arquivo = pasta_dados / f'{liga}_completo.csv'
    
    if not arquivo.exists():
        pasta_dados = Path(__file__).parent / 'dados_ligas_new'
        arquivo = pasta_dados / f'{liga}.csv'
    
    if not arquivo.exists():
        return []
    
    try:
        df = pd.read_csv(arquivo, low_memory=False)
        
        # Detectar coluna de temporada
        coluna_season = None
        for col in df.columns:
            if 'season' in col.lower():
                coluna_season = col
                break
        
        if not coluna_season:
            return []
        
        temporadas = sorted(df[coluna_season].unique())
        return [str(t).strip() for t in temporadas if pd.notna(t)]
    
    except Exception as e:
        print(f"⚠️  Erro ao detectar temporadas para {liga}: {e}")
        return []

def preparar_dados_treino(liga, temporadas_treino):
    """Prepara dados de treino usando temporadas históricas"""
    pasta_dados = Path(__file__).parent / 'dados_ligas'
    arquivo_original = pasta_dados / f'{liga}_completo.csv'
    
    if not arquivo_original.exists():
        pasta_dados = Path(__file__).parent / 'dados_ligas_new'
        arquivo_original = pasta_dados / f'{liga}.csv'
    
    if not arquivo_original.exists():
        return False
    
    try:
        df = pd.read_csv(arquivo_original, low_memory=False)
        
        # Detectar coluna de temporada
        coluna_season = None
        for col in df.columns:
            if 'season' in col.lower():
                coluna_season = col
                break
        
        if not coluna_season:
            return False
        
        # Filtrar apenas temporadas de treino
        df_treino = df[df[coluna_season].isin(temporadas_treino)]
        
        if len(df_treino) == 0:
            # Se não há dados nas temporadas especificadas, usar os dados mais antigos disponíveis
            temporadas_disponiveis = sorted(df[coluna_season].unique())
            if len(temporadas_disponiveis) > 0:
                # Pegar os primeiros 7 anos de dados
                temp_treino = temporadas_disponiveis[:min(7, len(temporadas_disponiveis))]
                df_treino = df[df[coluna_season].isin(temp_treino)]
                
                if len(df_treino) == 0:
                    return False
        
        # Salvar arquivo de treino
        pasta_backtest = Path(__file__).parent / 'backtest'
        arquivo_treino = pasta_backtest / f'{liga}_treino.csv'
        df_treino.to_csv(arquivo_treino, index=False)
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao preparar dados para {liga}: {e}")
        return False

def executar_backtest_temporada(liga, temporada):
    """Executa backtest para uma liga e temporada"""
    try:
        engine = BacktestEngine(liga=liga, temporada=temporada)
        
        if len(engine.df_teste) == 0:
            return None
        
        # Executar backtest rodada por rodada
        while True:
            try:
                resultado = engine.processar_rodada()
                if not resultado:  # Backtest completo
                    break
            except:
                break
        
        stats = engine.obter_status()
        
        # Coletar entradas individuais do engine
        entradas_individuais = []
        for entrada in engine.resultados.get('entradas', []):
            entradas_individuais.append({
                'liga': liga,
                'temporada': temporada,
                'entrada': entrada.get('entrada', 'HOME'),
                'dxg': entrada.get('dxg', 'EQ'),
                'lp': entrada.get('lp', -1),
                'home': entrada.get('home', ''),
                'away': entrada.get('away', ''),
                'b365h': entrada.get('b365h', 0),
                'b365a': entrada.get('b365a', 0)
            })
        
        return {
            'liga': liga,
            'temporada': temporada,
            'jogos_processados': stats['jogos_processados'],
            'stats': stats,
            'entradas': entradas_individuais
        }
    
    except Exception as e:
        return None

def processar_liga_completa(liga, temporadas_treino, temporadas_teste):
    """Processa todas as temporadas de uma liga"""
    print(f"\n{'='*60}")
    print(f"🏆 {liga} - {TODAS_LIGAS.get(liga, liga)}")
    print(f"{'='*60}")
    
    # Preparar dados de treino
    if not preparar_dados_treino(liga, temporadas_treino):
        print(f"❌ Falha ao preparar dados de treino")
        return None
    
    # Detectar temporadas disponíveis
    temporadas_disponiveis = detectar_temporadas_disponiveis(liga)
    temporadas_processar = [t for t in temporadas_disponiveis if t in temporadas_teste]
    
    if not temporadas_processar:
        print(f"⚠️  Sem temporadas disponíveis no período")
        return None
    
    print(f"📅 Temporadas: {len(temporadas_processar)}")
    
    resultados = []
    for i, temporada in enumerate(temporadas_processar, 1):
        print(f"   [{i}/{len(temporadas_processar)}] {temporada}...", end=' ', flush=True)
        resultado = executar_backtest_temporada(liga, temporada)
        if resultado:
            stats = resultado['stats']
            lucro = stats.get('lucro_total', 0)
            roi = stats.get('roi', 0)
            print(f"✓ Lucro: R$ {lucro:.2f} | ROI: {roi:.2f}%")
            resultados.append(resultado)
        else:
            print(f"✗ Sem dados")
    
    if not resultados:
        return None
    
    # Calcular resumo
    total_jogos = sum(r['jogos_processados'] for r in resultados)
    total_entradas = sum(r['stats'].get('total_entradas', 0) for r in resultados)
    lucro_total = sum(r['stats'].get('lucro_total', 0) for r in resultados)
    rois = [r['stats'].get('roi', 0) for r in resultados if r['stats'].get('roi', 0) != 0]
    roi_medio = sum(rois) / len(rois) if rois else 0
    
    resumo = {
        'liga': liga,
        'nome_completo': TODAS_LIGAS.get(liga, liga),
        'temporadas_processadas': len(resultados),
        'total_jogos': total_jogos,
        'total_entradas': total_entradas,
        'lucro_total': round(lucro_total, 2),
        'roi_medio': round(roi_medio, 2),
        'detalhes': resultados
    }
    
    print(f"\n📊 Resumo {liga}:")
    print(f"   ✓ {resumo['temporadas_processadas']} temporadas | {resumo['total_jogos']:,} jogos | {resumo['total_entradas']:,} entradas")
    print(f"   💰 Lucro: R$ {resumo['lucro_total']:,.2f} | ROI: {resumo['roi_medio']:.2f}%")
    
    return resumo

def main():
    print("\n" + "="*80)
    print("🚀 BACKTEST HISTÓRICO COMPLETO - TODAS AS LIGAS (2013-2026)")
    print("="*80 + "\n")
    
    # Definir períodos - apenas 2012/2013 para treino
    temporadas_treino_pattern = ["2012/2013"]
    temporadas_teste_pattern = [f"{ano}/{ano+1}" for ano in range(2013, 2026)]
    
    # Adicionar formato alternativo (apenas ano)
    temporadas_treino_alt = ["2012"]
    temporadas_teste_alt = [str(ano) for ano in range(2013, 2026)]
    
    temporadas_treino = temporadas_treino_pattern + temporadas_treino_alt
    temporadas_teste = temporadas_teste_pattern + temporadas_teste_alt
    
    print(f"📅 Período de treino: 2012/2013 (1 temporada de histórico)")
    print(f"📅 Período de teste: 2013-2026 ({len(temporadas_teste_pattern)} temporadas)")
    print(f"🏆 Total de ligas: {len(TODAS_LIGAS)}")
    print(f"ℹ️  Nota: Primeira temporada (2013/2014) terá poucas entradas\n")
    
    # Mostrar ligas
    print("Ligas a serem processadas:")
    for i, (codigo, nome) in enumerate(TODAS_LIGAS.items(), 1):
        print(f"  {i:2d}. {codigo:5s} - {nome}")
    
    print("\n" + "="*80)
    resposta = input("Deseja continuar? (S/N): ").strip().upper()
    if resposta != 'S':
        print("❌ Operação cancelada")
        return
    
    print("\n" + "="*80)
    print("INICIANDO PROCESSAMENTO")
    print("="*80)
    
    inicio = time.time()
    resultados_todas_ligas = []
    
    # Processar cada liga sequencialmente (mais estável)
    for i, liga in enumerate(TODAS_LIGAS.keys(), 1):
        print(f"\n[{i}/{len(TODAS_LIGAS)}] Processando {liga}...")
        resultado = processar_liga_completa(liga, temporadas_treino, temporadas_teste)
        if resultado:
            resultados_todas_ligas.append(resultado)
    
    tempo_total = time.time() - inicio
    
    # Consolidar resultados finais
    print("\n" + "="*80)
    print("📊 CONSOLIDANDO RESULTADOS FINAIS")
    print("="*80 + "\n")
    
    consolidado = {
        'timestamp_geracao': datetime.now().isoformat(),
        'periodo': '2013-2026 (Treino: 2012/2013)',
        'tempo_processamento_segundos': round(tempo_total, 2),
        'total_ligas_processadas': len(resultados_todas_ligas),
        'ligas': resultados_todas_ligas,
        'resumo_geral': {
            'total_temporadas': sum(r['temporadas_processadas'] for r in resultados_todas_ligas),
            'total_jogos': sum(r['total_jogos'] for r in resultados_todas_ligas),
            'total_entradas': sum(r['total_entradas'] for r in resultados_todas_ligas),
            'lucro_total': round(sum(r['lucro_total'] for r in resultados_todas_ligas), 2),
            'roi_medio_geral': 0
        }
    }
    
    # Calcular ROI médio ponderado
    rois_validos = [(r['roi_medio'], r['total_entradas']) for r in resultados_todas_ligas if r['total_entradas'] > 0]
    if rois_validos:
        roi_ponderado = sum(roi * entradas for roi, entradas in rois_validos) / sum(e for _, e in rois_validos)
        consolidado['resumo_geral']['roi_medio_geral'] = round(roi_ponderado, 2)
    
    # Top 10 ligas mais lucrativas
    ligas_ordenadas = sorted(resultados_todas_ligas, key=lambda x: x['lucro_total'], reverse=True)
    consolidado['top_10_ligas_lucrativas'] = [
        {
            'liga': r['liga'],
            'nome': r['nome_completo'],
            'lucro': r['lucro_total'],
            'roi': r['roi_medio'],
            'entradas': r['total_entradas']
        }
        for r in ligas_ordenadas[:10]
    ]
    
    # Salvar resultados
    arquivo_saida = Path(__file__).parent / 'backtest' / 'backtest_historico_completo_2012_2026.json'
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(consolidado, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Resultados salvos: {arquivo_saida.name}")
    
    # Coletar e salvar TODAS as entradas individuais
    print("\n🔄 Coletando entradas individuais de todas as ligas...")
    todas_entradas = []
    for liga_resultado in resultados_todas_ligas:
        for temporada_resultado in liga_resultado.get('detalhes', []):
            for entrada in temporada_resultado.get('entradas', []):
                todas_entradas.append(entrada)
    
    if todas_entradas:
        arquivo_entradas = Path(__file__).parent / 'fixtures' / 'backtest_entradas_reais.json'
        with open(arquivo_entradas, 'w', encoding='utf-8') as f:
            json.dump(todas_entradas, f, indent=2, ensure_ascii=False)
        print(f"✅ Entradas individuais salvas: {arquivo_entradas.name}")
        print(f"   📊 Total de entradas: {len(todas_entradas):,}")
    
    
    # Exibir resumo final
    print("\n" + "="*80)
    print("🎉 BACKTEST HISTÓRICO COMPLETO - RESUMO FINAL")
    print("="*80)
    print(f"⏱️  Tempo total: {tempo_total/60:.1f} minutos")
    print(f"🏆 Ligas processadas: {consolidado['total_ligas_processadas']}/{len(TODAS_LIGAS)}")
    print(f"📅 Temporadas: {consolidado['resumo_geral']['total_temporadas']}")
    print(f"⚽ Jogos: {consolidado['resumo_geral']['total_jogos']:,}")
    print(f"🎯 Entradas: {consolidado['resumo_geral']['total_entradas']:,}")
    print(f"💰 Lucro total: R$ {consolidado['resumo_geral']['lucro_total']:,.2f}")
    print(f"📈 ROI médio: {consolidado['resumo_geral']['roi_medio_geral']:.2f}%")
    
    print("\n🏆 TOP 10 LIGAS MAIS LUCRATIVAS:")
    print("-" * 80)
    for i, liga in enumerate(consolidado['top_10_ligas_lucrativas'], 1):
        print(f"{i:2d}. {liga['liga']:5s} | {liga['nome']:40s} | R$ {liga['lucro']:10,.2f} | ROI: {liga['roi']:6.2f}%")
    
    print("="*80 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
