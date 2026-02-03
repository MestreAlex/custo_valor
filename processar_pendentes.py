import pandas as pd
import numpy as np
from pathlib import Path

# Função para processar um arquivo
def processar_arquivo(filepath):
    """
    Adiciona colunas calculadas:
    - CGH = 1 / (ODDS_H * GH), quando GH = 0, CGH = 1
    - CGA = 1 / (ODDS_A * GA), quando GA = 0, CGA = 1
    - VGH = GH / ODDS_A
    - VGA = GA / ODDS_H
    """
    try:
        df = pd.read_csv(filepath)
        total_original = len(df)
        
        # Identificar colunas de gols (pode ser FTHG/FTAG ou HG/AG)
        if 'FTHG' in df.columns and 'FTAG' in df.columns:
            col_gh = 'FTHG'
            col_ga = 'FTAG'
        elif 'HG' in df.columns and 'AG' in df.columns:
            col_gh = 'HG'
            col_ga = 'AG'
        else:
            return None, "Colunas de gols não encontradas"
        
        # Verificar se tem odds disponíveis (prioridade: B365, B365C, Pinnacle, Max, Avg)
        odds_h_col = None
        odds_a_col = None
        
        # Tentar encontrar colunas de odds (ordem de prioridade)
        odds_options = [
            ('B365H', 'B365A'),      # Bet365 abertura
            ('B365CH', 'B365CA'),    # Bet365 fechamento
            ('PSCH', 'PSCA'),        # Pinnacle fechamento
            ('PSH', 'PSA'),          # Pinnacle abertura
            ('MaxCH', 'MaxCA'),      # Máxima fechamento
            ('MaxH', 'MaxA'),        # Máxima abertura
            ('AvgCH', 'AvgCA'),      # Média fechamento
            ('AvgH', 'AvgA')         # Média abertura
        ]
        
        for h_col, a_col in odds_options:
            if h_col in df.columns and a_col in df.columns:
                odds_h_col = h_col
                odds_a_col = a_col
                break
        
        if not odds_h_col or not odds_a_col:
            return None, "Colunas de odds não encontradas"
        
        # Remover linhas sem placares ou odds
        df_filtrado = df.dropna(subset=[col_gh, col_ga, odds_h_col, odds_a_col])
        
        # Remover linhas com odds = 0 (para evitar divisão por zero)
        df_filtrado = df_filtrado[(df_filtrado[odds_h_col] != 0) & (df_filtrado[odds_a_col] != 0)]
        
        removidos = total_original - len(df_filtrado)
        
        if len(df_filtrado) == 0:
            return None, "Nenhum jogo com dados completos"
        
        # Calcular CGH = 1 / (ODDS_H * GH), quando GH = 0, CGH = 1
        df_filtrado = df_filtrado.copy()
        df_filtrado['CGH'] = df_filtrado.apply(
            lambda row: 1.0 if row[col_gh] == 0 else 1 / (row[odds_h_col] * row[col_gh]),
            axis=1
        )
        
        # Calcular CGA = 1 / (ODDS_A * GA), quando GA = 0, CGA = 1
        df_filtrado['CGA'] = df_filtrado.apply(
            lambda row: 1.0 if row[col_ga] == 0 else 1 / (row[odds_a_col] * row[col_ga]),
            axis=1
        )
        
        # Calcular VGH = GH / ODDS_A
        df_filtrado['VGH'] = df_filtrado[col_gh] / df_filtrado[odds_a_col]
        
        # Calcular VGA = GA / ODDS_H
        df_filtrado['VGA'] = df_filtrado[col_ga] / df_filtrado[odds_h_col]
        
        # Substituir infinitos e NaN por valores apropriados
        df_filtrado['CGH'] = df_filtrado['CGH'].replace([np.inf, -np.inf], np.nan)
        df_filtrado['CGA'] = df_filtrado['CGA'].replace([np.inf, -np.inf], np.nan)
        df_filtrado['VGH'] = df_filtrado['VGH'].replace([np.inf, -np.inf], np.nan)
        df_filtrado['VGA'] = df_filtrado['VGA'].replace([np.inf, -np.inf], np.nan)
        
        # Salvar arquivo processado
        df_filtrado.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return len(df_filtrado), f"Processado: {len(df_filtrado)} jogos (removidos: {removidos}) [Odds: {odds_h_col}]"
        
    except Exception as e:
        return None, f"Erro: {str(e)}"

# Processar arquivos
print("="*80)
print("PROCESSANDO ARQUIVOS CORRIGIDOS")
print("="*80)

arquivos = [
    ('dados_ligas/E1_completo.csv', 'Championship (E1)'),
    ('dados_ligas_new/SWZ.csv', 'Suíça (SWZ)')
]

for filepath, nome in arquivos:
    print(f"\nProcessando {nome}...", end=" ")
    jogos, mensagem = processar_arquivo(filepath)
    
    if jogos:
        print(f"✓ {mensagem}")
    else:
        print(f"✗ {mensagem}")

print("\n" + "="*80)
print("CONCLUÍDO!")
print("="*80)
