import requests
import pandas as pd
from pathlib import Path
import numpy as np

print(f"{'='*80}")
print(f"DOWNLOAD E PROCESSAMENTO - ARGENTINA (ARG)")
print(f"{'='*80}\n")

# Download do arquivo
url = "https://www.football-data.co.uk/new/ARG.csv"
output_dir = Path("dados_ligas_new")
output_dir.mkdir(exist_ok=True)

try:
    print(f"Baixando {url}...", end=" ")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # Salvar arquivo
    filepath = output_dir / "ARG.csv"
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    # Ler arquivo
    df = pd.read_csv(filepath)
    print(f"✓ {len(df)} registros baixados\n")
    
    print(f"Colunas disponíveis: {list(df.columns)}\n")
    print(f"Primeiras 5 linhas:")
    print(df.head())
    print(f"\n{'='*80}\n")
    
    # Identificar colunas de gols e odds
    print(f"Processando cálculo de Custo do Gol (CGH/CGA) e Valor do Gol (VGH/VGA)...\n")
    
    # Colunas de gols
    col_gh = None
    col_ga = None
    if 'HG' in df.columns and 'AG' in df.columns:
        col_gh = 'HG'
        col_ga = 'AG'
    elif 'FTHG' in df.columns and 'FTAG' in df.columns:
        col_gh = 'FTHG'
        col_ga = 'FTAG'
    
    # Colunas de odds (procurar na ordem de prioridade especificada)
    odds_h_col = None
    odds_a_col = None
    odds_d_col = None
    odds_options = [
        ('PSCH', 'PSCD', 'PSCA'),        # Pinnacle fechamento (prioridade 1)
        ('BFECH', 'BFECD', 'BFECA'),     # Betfair (prioridade 2)
        ('B365CH', 'B365CD', 'B365CA'),  # Bet365 fechamento (prioridade 3)
    ]
    
    for h_col, d_col, a_col in odds_options:
        if h_col in df.columns and d_col in df.columns and a_col in df.columns:
            odds_h_col = h_col
            odds_d_col = d_col
            odds_a_col = a_col
            break
    
    if col_gh and col_ga and odds_h_col and odds_a_col:
        print(f"✓ Coluna de gols casa: {col_gh}")
        print(f"✓ Coluna de gols visitante: {col_ga}")
        print(f"✓ Colunas de odds: {odds_h_col}, {odds_d_col}, {odds_a_col}")
        print()
        
        # Primeiro, filtrar apenas jogos que têm pelo menos uma das sequências de odds
        mask_tem_odds = (
            df[odds_h_col].notna() & df[odds_d_col].notna() & df[odds_a_col].notna()
        )
        
        df_com_odds = df[mask_tem_odds].copy()
        df_sem_odds = df[~mask_tem_odds].copy()
        
        print(f"✓ {len(df_com_odds)} jogos com odds válidas")
        print(f"✗ {len(df_sem_odds)} jogos sem odds válidas (serão excluídos)")
        print()
        
        # Criar cópias para evitar SettingWithCopyWarning
        df_processado = df_com_odds.copy()
        
        # Inicializar colunas
        df_processado['CGH'] = np.nan
        df_processado['CGA'] = np.nan
        df_processado['VGH'] = np.nan
        df_processado['VGA'] = np.nan
        
        # Processar linhas com dados válidos
        linhas_processadas = 0
        linhas_com_calculos = 0
        
        for idx, row in df_processado.iterrows():
            # Verificar se tem dados de gols e odds
            gh = row[col_gh]
            ag = row[col_ga]
            odds_h = row[odds_h_col]
            odds_a = row[odds_a_col]
            
            # Verificar se são números válidos (não NaN)
            if pd.notna(gh) and pd.notna(ag) and pd.notna(odds_h) and pd.notna(odds_a):
                linhas_processadas += 1
                
                # CGH (Custo do Gol Casa)
                if gh == 0:
                    df_processado.at[idx, 'CGH'] = 1.0
                else:
                    df_processado.at[idx, 'CGH'] = 1.0 / (odds_h * gh)
                
                # CGA (Custo do Gol Visitante)
                if ag == 0:
                    df_processado.at[idx, 'CGA'] = 1.0
                else:
                    df_processado.at[idx, 'CGA'] = 1.0 / (odds_a * ag)
                
                # VGH (Valor do Gol Casa)
                df_processado.at[idx, 'VGH'] = gh / odds_a if odds_a != 0 else 0
                
                # VGA (Valor do Gol Visitante)
                df_processado.at[idx, 'VGA'] = ag / odds_h if odds_h != 0 else 0
                
                linhas_com_calculos += 1
        
        print(f"✓ {linhas_processadas} registros processados")
        print(f"✓ {linhas_com_calculos} registros com cálculos aplicados")
        print()
        
        # Salvar apenas os jogos com odds (excluindo os sem odds)
        df_processado.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✓ Arquivo salvo: {filepath}")
        print(f"✓ Total de jogos no arquivo final: {len(df_processado)}")
        print()
        
        # Mostrar algumas amostras
        df_sample = df_processado[['Date', 'Home', 'Away', col_gh, col_ga, odds_h_col, odds_a_col, 'CGH', 'CGA', 'VGH', 'VGA']].dropna()
        print(f"Amostra de dados processados:")
        print(df_sample.head(10))
        
    else:
        print(f"✗ Colunas necessárias não encontradas")
        print(f"  - Colunas de gols: {col_gh}, {col_ga}")
        print(f"  - Colunas de odds: {odds_h_col}, {odds_a_col}")
    
except Exception as e:
    print(f"✗ Erro: {str(e)}")

print(f"\n{'='*80}")
