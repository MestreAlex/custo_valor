"""
Script de teste rápido - Valida backtest histórico em uma única liga
Útil para testar a implementação antes de executar o backtest completo
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'backtest'))

from backtest_engine import BacktestEngine
import pandas as pd

def teste_rapido():
    print("\n" + "="*80)
    print("🧪 TESTE RÁPIDO - BACKTEST HISTÓRICO")
    print("="*80 + "\n")
    
    liga = 'E0'
    
    print(f"📊 Liga de teste: {liga} (Premier League)")
    
    # 1. Verificar dados disponíveis
    print("\n1️⃣ Verificando dados disponíveis...")
    arquivo = Path(__file__).parent / 'dados_ligas' / f'{liga}_completo.csv'
    if not arquivo.exists():
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return
    
    df = pd.read_csv(arquivo, low_memory=False)
    temporadas = sorted(df['Season'].unique())
    print(f"   ✓ Temporadas disponíveis: {len(temporadas)}")
    print(f"   ✓ Primeira: {temporadas[0]}")
    print(f"   ✓ Última: {temporadas[-1]}")
    print(f"   ✓ Total de jogos: {len(df):,}")
    
    # 2. Preparar dados de treino
    print("\n2️⃣ Preparando dados de treino (apenas 2012/2013)...")
    temporadas_treino = [t for t in temporadas if '2012' in str(t) and '2013' in str(t)]
    if not temporadas_treino:
        temporadas_treino = [t for t in temporadas if t.startswith('2012')]
    temporadas_treino = temporadas_treino[:1]  # Apenas primeira temporada
    
    if not temporadas_treino:
        print("   ⚠️  Nenhuma temporada de treino encontrada no período")
        return
    
    df_treino = df[df['Season'].isin(temporadas_treino)]
    arquivo_treino = Path(__file__).parent / 'backtest' / f'{liga}_treino.csv'
    df_treino.to_csv(arquivo_treino, index=False)
    print(f"   ✓ {len(temporadas_treino)} temporada de treino: {temporadas_treino[0]}")
    print(f"   ✓ {len(df_treino):,} jogos de treino")
    print(f"   ✓ Arquivo salvo: {arquivo_treino.name}")
    
    # 3. Testar 3 temporadas (começando de 2013/2014)
    print("\n3️⃣ Testando backtest em 3 temporadas...")
    
    # Pegar temporadas após 2012/2013
    temporadas_validas = [t for t in temporadas if t not in temporadas_treino]
    if len(temporadas_validas) < 3:
        temporadas_teste = temporadas_validas
    else:
        temporadas_teste = [
            temporadas_validas[0],   # Primeira (2013/2014)
            temporadas_validas[len(temporadas_validas)//2],  # Meio
            temporadas_validas[-2]   # Penúltima
        ]
    
    resultados = []
    for i, temp in enumerate(temporadas_teste, 1):
        print(f"\n   [{i}/3] Testando {temp}...")
        try:
            engine = BacktestEngine(liga=liga, temporada=temp)
            
            print(f"      📊 Jogos disponíveis: {len(engine.df_teste)}")
            
            if len(engine.df_teste) == 0:
                print(f"      ⚠️  Sem jogos disponíveis")
                continue
            
            # Simular primeiros 10 jogos (ou 5 rodadas)
            print(f"      🎯 Simulando primeiras 5 rodadas...")
            rodadas_processadas = 0
            for rodada_idx in range(5):  # Processar 5 rodadas
                try:
                    resultado = engine.processar_rodada()
                    if resultado:
                        rodadas_processadas += 1
                    else:
                        break  # Não há mais rodadas
                except Exception as e:
                    print(f"      ⚠️  Erro na rodada {rodada_idx}: {e}")
                    break
            
            stats = engine.obter_status()
            
            print(f"      ✓ Rodadas processadas: {rodadas_processadas}")
            print(f"      ✓ Jogos processados: {stats.get('jogos_processados', 0)}")
            print(f"      ✓ Entradas: {stats.get('total_entradas', 0)}")
            print(f"      ✓ Lucro: R$ {stats.get('lucro_total', 0):.2f}")
            print(f"      ✓ ROI: {stats.get('roi', 0):.1f}%")
            
            resultados.append({
                'temporada': temp,
                'jogos': stats.get('jogos_processados', 0),
                'entradas': stats.get('total_entradas', 0),
                'lucro': stats.get('lucro_total', 0),
                'roi': stats.get('roi', 0)
            })
            
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            continue
    
    # 4. Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DO TESTE")
    print("="*80)
    
    if resultados:
        print(f"\n✅ Teste concluído com sucesso!")
        print(f"\nResultados de {len(resultados)} temporadas testadas:")
        print("-" * 80)
        for r in resultados:
            print(f"{r['temporada']:12s} | Jogos: {r['jogos']:3d} | Entradas: {r['entradas']:3d} | "
                  f"Lucro: R$ {r['lucro']:8.2f} | ROI: {r['roi']:6.2f}%")
        print("-" * 80)
        
        total_entradas = sum(r['entradas'] for r in resultados)
        total_lucro = sum(r['lucro'] for r in resultados)
        roi_medio = sum(r['roi'] for r in resultados) / len(resultados) if resultados else 0
        
        print(f"\nTOTAL        | Jogos: {sum(r['jogos'] for r in resultados):3d} | "
              f"Entradas: {total_entradas:3d} | Lucro: R$ {total_lucro:8.2f} | ROI: {roi_medio:6.2f}%")
        
        print("\n✅ Sistema funcionando corretamente!")
        print("\n🚀 Próximo passo: Execute o backtest completo com:")
        print("   python executar_backtest_historico.py")
        print("   ou")
        print("   python executar_backtest_completo.py")
    else:
        print("\n⚠️  Nenhum resultado obtido. Verifique os dados.")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    try:
        teste_rapido()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
