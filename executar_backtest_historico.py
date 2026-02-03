"""
Script para executar backtest histórico de 2012 a 2026
Processa todas as temporadas disponíveis e gera relatório consolidado
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from collections import defaultdict

# Adicionar pasta backtest ao path
sys.path.append(str(Path(__file__).parent / 'backtest'))
from backtest_engine import BacktestEngine

# Ligas disponíveis
LIGAS_PRINCIPAIS = {
    'dados_ligas': ['E0', 'E1', 'SP1', 'SP2', 'I1', 'I2', 'D1', 'D2', 'F1', 'F2', 
                    'B1', 'N1', 'P1', 'T1'],
    'dados_ligas_new': ['ARG', 'AUT', 'BRA', 'CHN', 'DNK', 'FIN', 'IRL', 'JPN', 
                        'MEX', 'NOR', 'POL', 'ROU', 'RUS', 'SWE', 'SWZ', 'USA']
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

def gerar_lista_temporadas(ano_inicio=2012, ano_fim=2026):
    """Gera lista de temporadas no formato YYYY/YYYY"""
    temporadas = []
    for ano in range(ano_inicio, ano_fim):
        temporadas.append(f"{ano}/{ano+1}")
    return temporadas

def preparar_dados_treino(liga, temporadas_historicas):
    """
    Prepara dados de treino usando todas as temporadas históricas
    (2012 a 2019) para treinar o modelo
    """
    pasta_dados = Path(__file__).parent / 'dados_ligas'
    arquivo_original = pasta_dados / f'{liga}_completo.csv'
    
    if not arquivo_original.exists():
        pasta_dados = Path(__file__).parent / 'dados_ligas_new'
        arquivo_original = pasta_dados / f'{liga}.csv'
    
    if not arquivo_original.exists():
        print(f"❌ Arquivo não encontrado para liga {liga}")
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
            print(f"❌ Coluna Season não encontrada para {liga}")
            return False
        
        # Filtrar apenas temporadas históricas (2012-2019)
        df_treino = df[df[coluna_season].isin(temporadas_historicas)]
        
        if len(df_treino) == 0:
            print(f"⚠️  Nenhum dado de treino encontrado para {liga} no período 2012-2019")
            return False
        
        # Salvar arquivo de treino
        pasta_backtest = Path(__file__).parent / 'backtest'
        arquivo_treino = pasta_backtest / f'{liga}_treino.csv'
        df_treino.to_csv(arquivo_treino, index=False)
        
        print(f"✅ Dados de treino preparados para {liga}: {len(df_treino)} jogos ({df_treino[coluna_season].min()} a {df_treino[coluna_season].max()})")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao preparar dados de treino para {liga}: {e}")
        return False

def executar_backtest_temporada(liga, temporada):
    """Executa backtest para uma liga e temporada específica"""
    try:
        print(f"\n{'='*80}")
        print(f"🔵 Executando backtest: {liga} - {temporada}")
        print(f"{'='*80}")
        
        # Criar engine
        engine = BacktestEngine(liga=liga, temporada=temporada)
        
        # Verificar se há jogos disponíveis
        if len(engine.df_teste) == 0:
            print(f"⚠️  Nenhum jogo disponível para {liga} - {temporada}")
            return None
        
        print(f"📊 Total de jogos na temporada: {len(engine.df_teste)}")
        
        # Executar backtest rodada por rodada
        rodadas_processadas = 0
        while True:
            try:
                resultado = engine.processar_rodada()
                if not resultado:  # Backtest completo
                    break
                rodadas_processadas += 1
                if rodadas_processadas % 10 == 0:
                    status = engine.obter_status()
                    print(f"   Rodada {rodadas_processadas}: {status['jogos_processados']}/{len(engine.df_teste)} jogos, "
                          f"{status['total_entradas']} entradas, R$ {status['lucro_total']:.2f}")
            except Exception as e:
                print(f"   ⚠️  Erro na rodada {rodadas_processadas}: {e}")
                break
        
        # Obter estatísticas finais
        stats = engine.obter_status()
        
        print(f"\n✅ Backtest concluído: {liga} - {temporada}")
        print(f"   Rodadas processadas: {rodadas_processadas}")
        print(f"   Jogos processados: {stats['jogos_processados']}")
        print(f"   Entradas totais: {stats.get('total_entradas', 0)}")
        print(f"   Lucro total: R$ {stats.get('lucro_total', 0):.2f}")
        print(f"   ROI: {stats.get('roi', 0):.1f}%")
        
        return {
            'liga': liga,
            'temporada': temporada,
            'jogos_processados': stats['jogos_processados'],
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Erro ao executar backtest {liga} - {temporada}: {e}")
        return None

def consolidar_resultados(resultados_por_liga):
    """Consolida resultados de todas as ligas e temporadas"""
    consolidado = {
        'timestamp_geracao': datetime.now().isoformat(),
        'periodo': '2013-2026 (Treino: 2012/2013)',
        'total_ligas': len(resultados_por_liga),
        'ligas': resultados_por_liga,
        'resumo_geral': {
            'total_temporadas_processadas': 0,
            'total_jogos': 0,
            'total_entradas': 0,
            'lucro_total': 0,
            'roi_medio': 0
        }
    }
    
    # Calcular resumo geral
    total_temporadas = 0
    total_jogos = 0
    total_entradas = 0
    lucro_acumulado = 0
    soma_roi = 0
    count_roi = 0
    
    for liga, dados in resultados_por_liga.items():
        total_temporadas += len(dados['temporadas'])
        
        for temp_data in dados['temporadas']:
            stats = temp_data.get('stats', {})
            total_jogos += temp_data.get('jogos_processados', 0)
            total_entradas += stats.get('total_entradas', 0)
            lucro_acumulado += stats.get('lucro_total', 0)
            
            roi = stats.get('roi', 0)
            if roi != 0:
                soma_roi += roi
                count_roi += 1
    
    consolidado['resumo_geral']['total_temporadas_processadas'] = total_temporadas
    consolidado['resumo_geral']['total_jogos'] = total_jogos
    consolidado['resumo_geral']['total_entradas'] = total_entradas
    consolidado['resumo_geral']['lucro_total'] = round(lucro_acumulado, 2)
    consolidado['resumo_geral']['roi_medio'] = round(soma_roi / count_roi if count_roi > 0 else 0, 2)
    
    return consolidado

def main():
    print("\n" + "="*80)
    print("🚀 BACKTEST HISTÓRICO 2013-2026 (Treino: 2012/2013)")
    print("="*80 + "\n")
    
    # Definir período de treino (apenas 2012/2013) e teste (2013/2014 em diante)
    temporadas_treino = gerar_lista_temporadas(2012, 2013)  # Apenas 2012/2013
    temporadas_teste = gerar_lista_temporadas(2013, 2026)   # 2013/2014 a 2025/2026
    
    print(f"📅 Período de treino: {temporadas_treino[0]} (1 temporada de histórico)")
    print(f"📅 Período de teste: {temporadas_teste[0]} a {temporadas_teste[-1]}")
    print(f"📊 Total de temporadas para backtest: {len(temporadas_teste)}")
    print(f"ℹ️  Nota: Primeira temporada (2013/2014) terá poucas entradas devido ao histórico limitado\n")
    
    # Selecionar ligas para processar (começar com principais)
    ligas_processar = LIGAS_PRINCIPAIS['dados_ligas'][:5]  # Top 5 ligas para teste
    
    print(f"🎯 Ligas selecionadas: {', '.join(ligas_processar)}\n")
    
    # Perguntar confirmação
    resposta = input("Deseja continuar? (S/N): ").strip().upper()
    if resposta != 'S':
        print("❌ Operação cancelada pelo usuário")
        return
    
    print("\n" + "="*80)
    print("FASE 1: Preparando dados de treino (2012-2019)")
    print("="*80 + "\n")
    
    # Preparar dados de treino para cada liga
    ligas_preparadas = []
    for liga in ligas_processar:
        if preparar_dados_treino(liga, temporadas_treino):
            ligas_preparadas.append(liga)
    
    print(f"\n✅ {len(ligas_preparadas)} ligas preparadas com sucesso")
    
    print("\n" + "="*80)
    print("FASE 2: Executando backtests por temporada")
    print("="*80)
    
    # Executar backtest para cada liga e temporada
    resultados_por_liga = {}
    
    for liga in ligas_preparadas:
        print(f"\n🏆 Processando liga: {liga}")
        
        # Detectar temporadas disponíveis para esta liga
        temporadas_disponiveis = detectar_temporadas_disponiveis(liga)
        
        # Filtrar apenas temporadas do período de teste
        temporadas_processar = [t for t in temporadas_disponiveis if t in temporadas_teste]
        
        if not temporadas_processar:
            print(f"⚠️  Nenhuma temporada disponível para {liga} no período 2012-2026")
            continue
        
        print(f"📅 Temporadas encontradas: {len(temporadas_processar)}")
        
        resultados_liga = {
            'nome': liga,
            'temporadas': [],
            'resumo': {
                'total_temporadas': 0,
                'total_jogos': 0,
                'total_entradas': 0,
                'lucro_total': 0,
                'roi_medio': 0
            }
        }
        
        # Processar cada temporada
        for temporada in temporadas_processar:
            resultado = executar_backtest_temporada(liga, temporada)
            if resultado:
                resultados_liga['temporadas'].append(resultado)
        
        # Calcular resumo da liga
        if resultados_liga['temporadas']:
            total_jogos = sum(t['jogos_processados'] for t in resultados_liga['temporadas'])
            total_entradas = sum(t['stats'].get('total_entradas', 0) for t in resultados_liga['temporadas'])
            lucro_total = sum(t['stats'].get('lucro_total', 0) for t in resultados_liga['temporadas'])
            
            rois = [t['stats'].get('roi', 0) for t in resultados_liga['temporadas'] if t['stats'].get('roi', 0) != 0]
            roi_medio = sum(rois) / len(rois) if rois else 0
            
            resultados_liga['resumo'] = {
                'total_temporadas': len(resultados_liga['temporadas']),
                'total_jogos': total_jogos,
                'total_entradas': total_entradas,
                'lucro_total': round(lucro_total, 2),
                'roi_medio': round(roi_medio, 2)
            }
            
            print(f"\n📊 Resumo {liga}:")
            print(f"   Temporadas: {resultados_liga['resumo']['total_temporadas']}")
            print(f"   Jogos: {resultados_liga['resumo']['total_jogos']}")
            print(f"   Entradas: {resultados_liga['resumo']['total_entradas']}")
            print(f"   Lucro: R$ {resultados_liga['resumo']['lucro_total']:.2f}")
            print(f"   ROI médio: {resultados_liga['resumo']['roi_medio']:.2f}%")
        
        resultados_por_liga[liga] = resultados_liga
    
    # Consolidar e salvar resultados
    print("\n" + "="*80)
    print("FASE 3: Consolidando resultados")
    print("="*80 + "\n")
    
    consolidado = consolidar_resultados(resultados_por_liga)
    
    # Salvar em JSON
    arquivo_resultado = Path(__file__).parent / 'backtest' / 'backtest_historico_2012_2026.json'
    with open(arquivo_resultado, 'w', encoding='utf-8') as f:
        json.dump(consolidado, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Resultados salvos em: {arquivo_resultado.name}")
    
    # Exibir resumo final
    print("\n" + "="*80)
    print("📊 RESUMO GERAL DO BACKTEST HISTÓRICO")
    print("="*80)
    print(f"Período: {consolidado['periodo']}")
    print(f"Total de ligas: {consolidado['total_ligas']}")
    print(f"Total de temporadas: {consolidado['resumo_geral']['total_temporadas_processadas']}")
    print(f"Total de jogos: {consolidado['resumo_geral']['total_jogos']:,}")
    print(f"Total de entradas: {consolidado['resumo_geral']['total_entradas']:,}")
    print(f"Lucro total: R$ {consolidado['resumo_geral']['lucro_total']:,.2f}")
    print(f"ROI médio: {consolidado['resumo_geral']['roi_medio']:.2f}%")
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
