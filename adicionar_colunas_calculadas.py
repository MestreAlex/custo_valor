import pandas as pd
import numpy as np
from pathlib import Path
import glob

print(f"{'='*80}")
print(f"PROCESSAMENTO DE DADOS - ADIÇÃO DE COLUNAS CALCULADAS")
print(f"{'='*80}\n")

# Diretórios para processar
diretorios = [
    "dados_premier_league",
    "dados_ligas"
]

# Função para processar um arquivo
def processar_arquivo(filepath):
    """
    Adiciona colunas calculadas:
    - CGH = 1 / (B365H * GH), quando GH = 0, CGH = 1
    - CGA = 1 / (B365A * GA), quando GA = 0, CGA = 1
    - VGH = GH / B365A
    - VGA = GA / B365H
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

# Processar arquivos em cada diretório
total_arquivos = 0
total_jogos = 0
resumo = []

for diretorio in diretorios:
    dir_path = Path(diretorio)
    
    if not dir_path.exists():
        print(f"⚠ Diretório não encontrado: {diretorio}")
        continue
    
    print(f"\n{'='*80}")
    print(f"PROCESSANDO: {diretorio}")
    print(f"{'='*80}")
    
    # Buscar arquivos CSV (excluir arquivos temporários e individuais)
    arquivos = glob.glob(str(dir_path / "*_completo.csv"))
    
    if not arquivos:
        # Tentar padrão alternativo
        arquivos = glob.glob(str(dir_path / "*.csv"))
        # Filtrar apenas consolidados
        arquivos = [f for f in arquivos if '_completo' in f or 'premier_league_completo' in f]
    
    if not arquivos:
        print(f"  ⚠ Nenhum arquivo encontrado")
        continue
    
    print(f"  Encontrados {len(arquivos)} arquivos\n")
    
    for arquivo in sorted(arquivos):
        filename = Path(arquivo).name
        print(f"  Processando {filename}...", end=" ")
        
        jogos, mensagem = processar_arquivo(arquivo)
        
        if jogos:
            print(f"✓ {mensagem}")
            total_arquivos += 1
            total_jogos += jogos
            resumo.append({
                'arquivo': filename,
                'jogos': jogos,
                'status': 'OK'
            })
        else:
            print(f"✗ {mensagem}")
            resumo.append({
                'arquivo': filename,
                'jogos': 0,
                'status': mensagem
            })

# Processar arquivos do padrão /new
dir_new = Path("dados_ligas_new")
if dir_new.exists():
    print(f"\n{'='*80}")
    print(f"PROCESSANDO: dados_ligas_new")
    print(f"{'='*80}")
    
    arquivos_new = glob.glob(str(dir_new / "*.csv"))
    # Excluir relatórios
    arquivos_new = [f for f in arquivos_new if 'relatorio' not in f.lower()]
    
    print(f"  Encontrados {len(arquivos_new)} arquivos\n")
    
    for arquivo in sorted(arquivos_new):
        filename = Path(arquivo).name
        print(f"  Processando {filename}...", end=" ")
        
        jogos, mensagem = processar_arquivo(arquivo)
        
        if jogos:
            print(f"✓ {mensagem}")
            total_arquivos += 1
            total_jogos += jogos
            resumo.append({
                'arquivo': filename,
                'jogos': jogos,
                'status': 'OK'
            })
        else:
            print(f"✗ {mensagem}")
            resumo.append({
                'arquivo': filename,
                'jogos': 0,
                'status': mensagem
            })

# Relatório final
print(f"\n{'='*80}")
print(f"RELATÓRIO FINAL")
print(f"{'='*80}\n")

df_resumo = pd.DataFrame(resumo)
df_resumo_ok = df_resumo[df_resumo['status'] == 'OK']

if len(df_resumo_ok) > 0:
    print(f"✓ Arquivos processados com sucesso: {len(df_resumo_ok)}")
    print(f"✓ Total de jogos processados: {total_jogos:,}")
    print(f"\nArquivos processados:")
    for _, row in df_resumo_ok.iterrows():
        print(f"  - {row['arquivo']}: {row['jogos']:,} jogos")

if len(df_resumo[df_resumo['status'] != 'OK']) > 0:
    print(f"\n⚠ Arquivos com problemas: {len(df_resumo[df_resumo['status'] != 'OK'])}")
    for _, row in df_resumo[df_resumo['status'] != 'OK'].iterrows():
        print(f"  - {row['arquivo']}: {row['status']}")

print(f"\n{'='*80}")
print(f"COLUNAS ADICIONADAS:")
print(f"{'='*80}")
print(f"  • CGH = 1 / (B365H * GH), quando GH = 0, CGH = 1")
print(f"  • CGA = 1 / (B365A * GA), quando GA = 0, CGA = 1")
print(f"  • VGH = GH / B365A")
print(f"  • VGA = GA / B365H")
print(f"\n{'='*80}")
print(f"CONCLUÍDO!")
print(f"{'='*80}")
