import pandas as pd
from pathlib import Path
import numpy as np

print(f"{'='*80}")
print(f"VERIFICAÇÃO DE DADOS - LIGAS NEW")
print(f"{'='*80}\n")

# Diretório das ligas new
dir_ligas = Path("dados_ligas_new")

# Listar todos os arquivos CSV
arquivos = sorted(dir_ligas.glob("*.csv"))

print(f"{'Liga':<6} {'Total':<8} {'CGH':<8} {'CGA':<8} {'VGH':<8} {'VGA':<8} {'Completo':<10} {'%':<6}")
print(f"{'-'*80}")

total_geral = 0
completo_geral = 0

for arquivo in arquivos:
    try:
        # Carregar CSV
        df = pd.read_csv(arquivo)
        
        # Nome da liga (sem extensão)
        liga = arquivo.stem
        
        # Total de jogos
        total = len(df)
        total_geral += total
        
        # Verificar quais jogos têm cada coluna com valor válido
        tem_cgh = 0
        tem_cga = 0
        tem_vgh = 0
        tem_vga = 0
        tem_completo = 0
        
        if 'CGH' in df.columns and 'CGA' in df.columns and 'VGH' in df.columns and 'VGA' in df.columns:
            # Contar jogos com valores válidos
            tem_cgh = df['CGH'].notna().sum()
            tem_cga = df['CGA'].notna().sum()
            tem_vgh = df['VGH'].notna().sum()
            tem_vga = df['VGA'].notna().sum()
            
            # Contar jogos com todos os valores válidos
            tem_completo = df[['CGH', 'CGA', 'VGH', 'VGA']].notna().all(axis=1).sum()
            completo_geral += tem_completo
        
        # Calcular percentual
        percentual = (tem_completo / total * 100) if total > 0 else 0
        
        # Imprimir linha
        print(f"{liga:<6} {total:<8} {tem_cgh:<8} {tem_cga:<8} {tem_vgh:<8} {tem_vga:<8} {tem_completo:<10} {percentual:>5.1f}%")
        
    except Exception as e:
        print(f"Erro ao processar {arquivo.name}: {e}")

print(f"{'-'*80}")
percentual_geral = (completo_geral / total_geral * 100) if total_geral > 0 else 0
print(f"{'TOTAL':<6} {total_geral:<8} {'':<8} {'':<8} {'':<8} {'':<8} {completo_geral:<10} {percentual_geral:>5.1f}%")

print(f"\n{'='*80}")
print(f"ANÁLISE DETALHADA - JOGOS SEM CÁLCULOS")
print(f"{'='*80}\n")

for arquivo in arquivos:
    try:
        df = pd.read_csv(arquivo)
        liga = arquivo.stem
        
        if 'CGH' in df.columns and 'CGA' in df.columns and 'VGH' in df.columns and 'VGA' in df.columns:
            # Jogos sem valores completos
            sem_completo = df[df[['CGH', 'CGA', 'VGH', 'VGA']].isna().any(axis=1)]
            
            if len(sem_completo) > 0:
                print(f"\n{liga} - {len(sem_completo)} jogos sem cálculos completos:")
                
                # Verificar se tem colunas de gols
                col_gh = 'HG' if 'HG' in df.columns else 'FTHG' if 'FTHG' in df.columns else None
                col_ga = 'AG' if 'AG' in df.columns else 'FTAG' if 'FTAG' in df.columns else None
                
                # Verificar colunas de odds
                odds_cols = [col for col in df.columns if 'B365' in col or 'Max' in col or 'Avg' in col or 'PS' in col]
                
                # Analisar causas
                sem_gols = 0
                sem_odds = 0
                gols_zero = 0
                odds_invalidas = 0
                
                for idx, row in sem_completo.iterrows():
                    # Verificar gols
                    if col_gh and col_ga:
                        if pd.isna(row[col_gh]) or pd.isna(row[col_ga]):
                            sem_gols += 1
                    
                    # Verificar odds
                    tem_odds = False
                    for odds_col in odds_cols:
                        if pd.notna(row.get(odds_col, np.nan)):
                            tem_odds = True
                            break
                    if not tem_odds:
                        sem_odds += 1
                
                print(f"  - Sem dados de gols: {sem_gols}")
                print(f"  - Sem odds disponíveis: {sem_odds}")
                
                # Mostrar amostra dos primeiros 3 jogos
                print(f"\n  Amostra dos primeiros 3 jogos:")
                colunas_exibir = ['Date', 'Home', 'Away']
                if col_gh: colunas_exibir.append(col_gh)
                if col_ga: colunas_exibir.append(col_ga)
                if 'B365CH' in df.columns: colunas_exibir.append('B365CH')
                if 'B365CA' in df.columns: colunas_exibir.append('B365CA')
                colunas_exibir.extend(['CGH', 'CGA', 'VGH', 'VGA'])
                
                colunas_disponiveis = [col for col in colunas_exibir if col in sem_completo.columns]
                print(sem_completo[colunas_disponiveis].head(3).to_string(index=False))
    
    except Exception as e:
        print(f"Erro ao analisar {arquivo.name}: {e}")

print(f"\n{'='*80}")
