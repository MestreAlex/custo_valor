import pandas as pd
import numpy as np
from pathlib import Path

print(f"{'='*100}")
print(f"ANÁLISE DE xGH E xGA - COMPARAÇÃO ENTRE LIGAS")
print(f"{'='*100}\n")

# Carregar arquivo com análise
df = pd.read_csv('fixtures/proxima_rodada_com_analise.csv')

print(f"Total de jogos: {len(df)}\n")

# Agrupar por liga
ligas = df['LIGA'].unique()
ligas = sorted(ligas)

print(f"{'LIGA':<6} {'Total':<8} {'xGH OK':<10} {'xGA OK':<10} {'PROB OK':<10} {'xGH (min/max)':<20} {'xGA (min/max)':<20}")
print(f"{'-'*100}")

for liga in ligas:
    df_liga = df[df['LIGA'] == liga]
    
    total = len(df_liga)
    xgh_ok = df_liga['xGH'].notna().sum()
    xga_ok = df_liga['xGA'].notna().sum()
    prob_ok = df_liga['PROB_H'].notna().sum()
    
    if xgh_ok > 0:
        xgh_min = df_liga['xGH'].min()
        xgh_max = df_liga['xGH'].max()
        xgh_range = f"{xgh_min:.2f} / {xgh_max:.2f}"
    else:
        xgh_range = "N/A"
    
    if xga_ok > 0:
        xga_min = df_liga['xGA'].min()
        xga_max = df_liga['xGA'].max()
        xga_range = f"{xga_min:.2f} / {xga_max:.2f}"
    else:
        xga_range = "N/A"
    
    print(f"{liga:<6} {total:<8} {xgh_ok:<10} {xga_ok:<10} {prob_ok:<10} {xgh_range:<20} {xga_range:<20}")

print(f"\n{'='*100}")
print(f"ANÁLISE DETALHADA - ARGENTINA vs OUTRAS LIGAS")
print(f"{'='*100}\n")

# Comparar Argentina com outras ligas
arg_df = df[df['LIGA'] == 'ARG'].copy()
outras_df = df[df['LIGA'] != 'ARG'].copy()

print("ARGENTINA:")
print(f"  Total jogos: {len(arg_df)}")
print(f"  Com xGH calculado: {arg_df['xGH'].notna().sum()}")
print(f"  Com xGA calculado: {arg_df['xGA'].notna().sum()}")
print(f"  Com PROB calculado: {arg_df['PROB_H'].notna().sum()}")

if arg_df['xGH'].notna().sum() > 0:
    print(f"\n  xGH - Estatísticas:")
    print(f"    Mínimo: {arg_df['xGH'].min():.4f}")
    print(f"    Máximo: {arg_df['xGH'].max():.4f}")
    print(f"    Média: {arg_df['xGH'].mean():.4f}")
    print(f"    Mediana: {arg_df['xGH'].median():.4f}")

if arg_df['xGA'].notna().sum() > 0:
    print(f"\n  xGA - Estatísticas:")
    print(f"    Mínimo: {arg_df['xGA'].min():.4f}")
    print(f"    Máximo: {arg_df['xGA'].max():.4f}")
    print(f"    Média: {arg_df['xGA'].mean():.4f}")
    print(f"    Mediana: {arg_df['xGA'].median():.4f}")

print(f"\n\nOUTRAS LIGAS (agregadas):")
print(f"  Total jogos: {len(outras_df)}")
print(f"  Com xGH calculado: {outras_df['xGH'].notna().sum()}")
print(f"  Com xGA calculado: {outras_df['xGA'].notna().sum()}")
print(f"  Com PROB calculado: {outras_df['PROB_H'].notna().sum()}")

if outras_df['xGH'].notna().sum() > 0:
    print(f"\n  xGH - Estatísticas:")
    print(f"    Mínimo: {outras_df['xGH'].min():.4f}")
    print(f"    Máximo: {outras_df['xGH'].max():.4f}")
    print(f"    Média: {outras_df['xGH'].mean():.4f}")
    print(f"    Mediana: {outras_df['xGH'].median():.4f}")

if outras_df['xGA'].notna().sum() > 0:
    print(f"\n  xGA - Estatísticas:")
    print(f"    Mínimo: {outras_df['xGA'].min():.4f}")
    print(f"    Máximo: {outras_df['xGA'].max():.4f}")
    print(f"    Média: {outras_df['xGA'].mean():.4f}")
    print(f"    Mediana: {outras_df['xGA'].median():.4f}")

print(f"\n{'='*100}")
print(f"AMOSTRA DE JOGOS - ARGENTINA")
print(f"{'='*100}\n")

# Mostrar amostra de Argentina
arg_sample = arg_df[['HOME', 'AWAY', 'MCGH', 'MVGH', 'MCGA', 'MVGA', 'xGH', 'xGA', 'PROB_H', 'PROB_D', 'PROB_A']].head(10)
print(arg_sample.to_string(index=False))

print(f"\n{'='*100}")
print(f"AMOSTRA DE JOGOS - OUTRAS LIGAS (primeiras 10)")
print(f"{'='*100}\n")

outras_sample = outras_df[['LIGA', 'HOME', 'AWAY', 'MCGH', 'MVGH', 'MCGA', 'MVGA', 'xGH', 'xGA', 'PROB_H']].head(10)
print(outras_sample.to_string(index=False))

print(f"\n{'='*100}")
print(f"VERIFICAÇÃO - CÁLCULO DE xGH E xGA")
print(f"{'='*100}\n")

print("Fórmula usado: xGH = (1 + MCGA * MVGA * oddH * oddA) / (2 * MCGH * oddH)")
print("              xGA = (1 + MCGH * MVGH * oddH * oddA) / (2 * MCGA * oddA)\n")

# Verificar alguns casos específicos de Argentina
print("Verificando valores de Argentina:")
for idx, row in arg_df.head(5).iterrows():
    print(f"\n{row['HOME']} vs {row['AWAY']}:")
    print(f"  MCGH={row['MCGH']:.4f}, MVGH={row['MVGH']:.4f}, MCGA={row['MCGA']:.4f}, MVGA={row['MVGA']:.4f}")
    
    if pd.notna(row['B365H']) and pd.notna(row['B365A']):
        odd_h = row['B365H']
        odd_a = row['B365A']
        print(f"  B365H={odd_h:.4f}, B365A={odd_a:.4f}")
        
        # Calcular xGH e xGA manualmente
        if row['MCGH'] > 0:
            xgh_calc = (1 + row['MCGA'] * row['MVGA'] * odd_h * odd_a) / (2 * row['MCGH'] * odd_h)
            print(f"  xGH calculado: {xgh_calc:.4f}")
            print(f"  xGH no arquivo: {row['xGH']}")
        
        if row['MCGA'] > 0:
            xga_calc = (1 + row['MCGH'] * row['MVGH'] * odd_h * odd_a) / (2 * row['MCGA'] * odd_a)
            print(f"  xGA calculado: {xga_calc:.4f}")
            print(f"  xGA no arquivo: {row['xGA']}")
    else:
        print(f"  Odds não disponíveis")
        if pd.notna(row['MCGH']):
            print(f"  Mas MCGH existe: {row['MCGH']}")

print(f"\n{'='*100}")
