import pandas as pd
import numpy as np
from pathlib import Path
import glob
import warnings
from scipy.stats import poisson

# Suprimir warnings do pandas
warnings.filterwarnings('ignore')

print(f"{'='*80}")
print(f"ANÁLISE DA PRÓXIMA RODADA - MÉDIAS HISTÓRICAS")
print(f"{'='*80}\n")

# Mapeamento de códigos de liga para arquivos
mapeamento_ligas = {
    # Premier League e divisões inglesas
    'E0': 'dados_ligas/E0_completo.csv',
    'E1': 'dados_ligas/E1_completo.csv',
    # Alemanha
    'D1': 'dados_ligas/D1_completo.csv',
    'D2': 'dados_ligas/D2_completo.csv',
    # Itália
    'I1': 'dados_ligas/I1_completo.csv',
    'I2': 'dados_ligas/I2_completo.csv',
    # França
    'F1': 'dados_ligas/F1_completo.csv',
    'F2': 'dados_ligas/F2_completo.csv',
    # Espanha
    'SP1': 'dados_ligas/SP1_completo.csv',
    'SP2': 'dados_ligas/SP2_completo.csv',
    # Portugal
    'P1': 'dados_ligas/P1_completo.csv',
    # Grécia
    'G1': 'dados_ligas/G1_completo.csv',
    # Turquia
    'T1': 'dados_ligas/T1_completo.csv',
    # Holanda
    'N1': 'dados_ligas/N1_completo.csv',
    # Bélgica
    'B1': 'dados_ligas/B1_completo.csv',
    # Ligas do padrão /new
    'ARG': 'dados_ligas_new/ARG.csv',
    'AUT': 'dados_ligas_new/AUT.csv',
    'BRA': 'dados_ligas_new/BRA.csv',
    'Serie A': 'dados_ligas_new/BRA.csv',  # Alias para Brasil
    'CHN': 'dados_ligas_new/CHN.csv',
    'DNK': 'dados_ligas_new/DNK.csv',
    'FIN': 'dados_ligas_new/FIN.csv',
    'IRL': 'dados_ligas_new/IRL.csv',
    'JPN': 'dados_ligas_new/JPN.csv',
    'MEX': 'dados_ligas_new/MEX.csv',
    'NOR': 'dados_ligas_new/NOR.csv',
    'POL': 'dados_ligas_new/POL.csv',
    'ROU': 'dados_ligas_new/ROU.csv',
    'RUS': 'dados_ligas_new/RUS.csv',
    'SWE': 'dados_ligas_new/SWE.csv',
    'SWZ': 'dados_ligas_new/SWZ.csv',
    'USA': 'dados_ligas_new/USA.csv',
}

# Cache para históricos das ligas
cache_historicos = {}

def carregar_historico_liga(codigo_liga):
    """Carrega o histórico de uma liga do cache ou do arquivo"""
    if codigo_liga in cache_historicos:
        return cache_historicos[codigo_liga]
    
    if codigo_liga not in mapeamento_ligas:
        return None
    
    arquivo = mapeamento_ligas[codigo_liga]
    if not Path(arquivo).exists():
        return None
    
    try:
        df = pd.read_csv(arquivo, low_memory=False)
        # Verificar se tem as colunas necessárias
        colunas_necessarias = ['CGH', 'CGA', 'VGH', 'VGA']
        if not all(col in df.columns for col in colunas_necessarias):
            return None
        
        cache_historicos[codigo_liga] = df
        return df
    except:
        return None

def calcular_medias_historicas(time, eh_home, odd_time, odd_adversario, historico_liga, range_percent=0.07):
    """
    Calcula médias e desvios padrão históricas de CGH/VGH ou CGA/VGA baseado em ranges de probabilidade
    
    Args:
        time: Nome do time
        eh_home: True se o time joga em casa
        odd_time: Odd do time (oddH se home, oddA se away)
        odd_adversario: Odd do adversário (oddA se time home, oddH se time away)
        historico_liga: DataFrame com histórico da liga
        range_percent: Porcentagem do range (padrão 7% = 0.07)
    
    Returns:
        (media_cg, media_vg, std_cg, std_vg) ou (None, None, None, None) se não houver dados
    """
    if historico_liga is None or len(historico_liga) == 0:
        return None, None, None, None
    
    # Calcular probabilidades
    prob_time = 1 / odd_time if odd_time > 0 else 0
    prob_adversario = 1 / odd_adversario if odd_adversario > 0 else 0
    
    # Calcular ranges (±7%)
    prob_time_min = prob_time * (1 - range_percent)
    prob_time_max = prob_time * (1 + range_percent)
    prob_adv_min = prob_adversario * (1 - range_percent)
    prob_adv_max = prob_adversario * (1 + range_percent)
    
    # Identificar colunas de odds (preferir B365H para compatibilidade com fixtures)
    col_odd_h, col_odd_a = None, None
    odds_priority = [
        ('B365H', 'B365A'),      # Bet365 abertura (mais comum nos fixtures)
        ('B365CH', 'B365CA'),    # Bet365 fechamento
        ('PSCH', 'PSCA'),        # Pinnacle fechamento
        ('PSH', 'PSA'),          # Pinnacle abertura
        ('MaxCH', 'MaxCA'),
        ('MaxH', 'MaxA'),
        ('AvgCH', 'AvgCA'),
        ('AvgH', 'AvgA')
    ]
    
    for h_col, a_col in odds_priority:
        if h_col in historico_liga.columns and a_col in historico_liga.columns:
            col_odd_h = h_col
            col_odd_a = a_col
            break
    
    if not col_odd_h or not col_odd_a:
        return None, None, None, None
    
    # Identificar coluna de time
    col_home = 'HomeTeam' if 'HomeTeam' in historico_liga.columns else 'Home'
    col_away = 'AwayTeam' if 'AwayTeam' in historico_liga.columns else 'Away'
    
    if eh_home:
        # Time joga em casa: buscar jogos onde ele foi mandante
        jogos_time = historico_liga[historico_liga[col_home] == time].copy()
        
        if len(jogos_time) == 0:
            return None, None, None, None
        
        # Calcular probabilidades das odds históricas
        jogos_time['prob_h'] = 1 / jogos_time[col_odd_h]
        jogos_time['prob_a'] = 1 / jogos_time[col_odd_a]
        
        # Filtrar por range de probabilidade
        jogos_filtrados = jogos_time[
            (jogos_time['prob_h'] >= prob_time_min) & 
            (jogos_time['prob_h'] <= prob_time_max) &
            (jogos_time['prob_a'] >= prob_adv_min) & 
            (jogos_time['prob_a'] <= prob_adv_max)
        ]
        
        if len(jogos_filtrados) == 0:
            return None, None, None, None
        
        # Calcular médias e desvios padrão de CGH e VGH
        media_cgh = jogos_filtrados['CGH'].mean()
        media_vgh = jogos_filtrados['VGH'].mean()
        std_cgh = jogos_filtrados['CGH'].std()
        std_vgh = jogos_filtrados['VGH'].std()
        
        return media_cgh, media_vgh, std_cgh, std_vgh
    
    else:
        # Time joga fora: buscar jogos onde ele foi visitante
        jogos_time = historico_liga[historico_liga[col_away] == time].copy()
        
        if len(jogos_time) == 0:
            return None, None, None, None
        
        # Calcular probabilidades das odds históricas
        jogos_time['prob_h'] = 1 / jogos_time[col_odd_h]
        jogos_time['prob_a'] = 1 / jogos_time[col_odd_a]
        
        # Filtrar por range de probabilidade (invertido: odd do time é oddA, do adversário é oddH)
        jogos_filtrados = jogos_time[
            (jogos_time['prob_a'] >= prob_time_min) & 
            (jogos_time['prob_a'] <= prob_time_max) &
            (jogos_time['prob_h'] >= prob_adv_min) & 
            (jogos_time['prob_h'] <= prob_adv_max)
        ]
        
        if len(jogos_filtrados) == 0:
            return None, None, None, None
        
        # Calcular médias e desvios padrão de CGA e VGA
        media_cga = jogos_filtrados['CGA'].mean()
        media_vga = jogos_filtrados['VGA'].mean()
        std_cga = jogos_filtrados['CGA'].std()
        std_vga = jogos_filtrados['VGA'].std()
        
        return media_cga, media_vga, std_cga, std_vga

# Carregar fixtures da próxima rodada
# Buscar o arquivo mais recente (excluir o arquivo com_analise.csv)
fixture_files = sorted(Path("fixtures").glob("proxima_rodada_[0-9]*.csv"), reverse=True)
if not fixture_files:
    print("Arquivo de fixtures nao encontrado!")
    exit(1)

fixture_path = fixture_files[0]
print("Carregando fixtures da proxima rodada...")
df_fixtures = pd.read_csv(fixture_path)
print(f"{len(df_fixtures)} jogos encontrados\n")

# Criar colunas para as médias
df_fixtures['MCGH'] = np.nan
df_fixtures['MVGH'] = np.nan
df_fixtures['MCGA'] = np.nan
df_fixtures['MVGA'] = np.nan
df_fixtures['DesvioPadrão_MCGH'] = np.nan
df_fixtures['DesvioPadrão_MVGH'] = np.nan
df_fixtures['DesvioPadrão_MCGA'] = np.nan
df_fixtures['DesvioPadrão_MVGA'] = np.nan
df_fixtures['CFxGH'] = np.nan
df_fixtures['CFxGA'] = np.nan
df_fixtures['xGH'] = np.nan
df_fixtures['xGA'] = np.nan
df_fixtures['PROB_H'] = np.nan
df_fixtures['PROB_D'] = np.nan
df_fixtures['PROB_A'] = np.nan
df_fixtures['ODD_H_CALC'] = np.nan
df_fixtures['ODD_D_CALC'] = np.nan
df_fixtures['ODD_A_CALC'] = np.nan

print("Calculando médias históricas...\n")

sucessos = 0
sem_historico = 0
sem_dados = 0

for idx, row in df_fixtures.iterrows():
    liga = row['LIGA']
    home = row['HOME']
    away = row['AWAY']
    
    print(f"[{idx+1}/{len(df_fixtures)}] {liga}: {home} vs {away}", end=" ")
    
    # Carregar histórico da liga primeiro
    historico = carregar_historico_liga(liga)
    if historico is None:
        print("Sem historico")
        sem_historico += 1
        continue
    
    # Range fixo de ±7% para todas as ligas
    range_percent = 0.07
    
    # Identificar quais odds usar baseado no histórico e fixtures
    odds_h_col, odds_a_col = None, None
    odds_options = [
        ('B365H', 'B365A'),      # Bet365 abertura (mais comum nos fixtures)
        ('B365CH', 'B365CA'),    # Bet365 fechamento
        ('PSCH', 'PSCA'),        # Pinnacle fechamento
        ('PSH', 'PSA'),          # Pinnacle abertura
        ('MaxCH', 'MaxCA'),      # Máxima fechamento
        ('MaxH', 'MaxA'),        # Máxima abertura
        ('AvgCH', 'AvgCA'),      # Média fechamento
        ('AvgH', 'AvgA')         # Média abertura
    ]
    
    # Primeiro tentar encontrar odds que existem em ambos (histórico e fixtures)
    for h_col, a_col in odds_options:
        if (h_col in historico.columns and a_col in historico.columns and 
            h_col in row.index and a_col in row.index and
            pd.notna(row.get(h_col)) and pd.notna(row.get(a_col))):
            odds_h_col = h_col
            odds_a_col = a_col
            break
    
    # Se não encontrou, usar B365H dos fixtures com qualquer odds do histórico
    if not odds_h_col and 'B365H' in row.index and 'B365A' in row.index:
        if pd.notna(row.get('B365H')) and pd.notna(row.get('B365A')):
            # Usar B365H dos fixtures
            odds_h_col = 'B365H'
            odds_a_col = 'B365A'
    
    if not odds_h_col:
        print("Sem odds compativeis")
        sem_dados += 1
        continue
    
    odd_h = row.get(odds_h_col, np.nan)
    odd_a = row.get(odds_a_col, np.nan)
    
    # Verificar se tem odds válidas
    if pd.isna(odd_h) or pd.isna(odd_a) or odd_h <= 0 or odd_a <= 0:
        print("Sem odds validas")
        sem_dados += 1
        continue
    
    # Calcular médias para time home
    mcgh, mvgh, std_mcgh, std_mvgh = calcular_medias_historicas(home, True, odd_h, odd_a, historico, range_percent=range_percent)
    
    # Calcular médias para time away
    mcga, mvga, std_mcga, std_mvga = calcular_medias_historicas(away, False, odd_a, odd_h, historico, range_percent=range_percent)
    
    # Atualizar DataFrame
    if mcgh is not None:
        df_fixtures.at[idx, 'MCGH'] = mcgh
        df_fixtures.at[idx, 'MVGH'] = mvgh
        if pd.notna(std_mcgh):
            df_fixtures.at[idx, 'DesvioPadrão_MCGH'] = std_mcgh
        if pd.notna(std_mvgh):
            df_fixtures.at[idx, 'DesvioPadrão_MVGH'] = std_mvgh
    
    if mcga is not None:
        df_fixtures.at[idx, 'MCGA'] = mcga
        df_fixtures.at[idx, 'MVGA'] = mvga
        if pd.notna(std_mcga):
            df_fixtures.at[idx, 'DesvioPadrão_MCGA'] = std_mcga
        if pd.notna(std_mvga):
            df_fixtures.at[idx, 'DesvioPadrão_MVGA'] = std_mvga
    
    # Calcular coeficientes de confiança (CF)
    if (mcgh is not None and pd.notna(std_mcgh) and pd.notna(std_mvgh) and 
        mcgh > 0 and mvgh > 0):
        try:
            cv_cgh = std_mcgh / mcgh
            cv_vgh = std_mvgh / mvgh
            cfxgh = 1 / (1 + np.sqrt(cv_cgh**2 + cv_vgh**2))
            df_fixtures.at[idx, 'CFxGH'] = cfxgh
        except:
            pass
    
    if (mcga is not None and pd.notna(std_mcga) and pd.notna(std_mvga) and 
        mcga > 0 and mvga > 0):
        try:
            cv_cga = std_mcga / mcga
            cv_vga = std_mvga / mvga
            cfxga = 1 / (1 + np.sqrt(cv_cga**2 + cv_vga**2))
            df_fixtures.at[idx, 'CFxGA'] = cfxga
        except:
            pass
    
    # Calcular xGH e xGA
    if mcgh is not None and mcga is not None and mvgh is not None:
        try:
            # xGH = (1 + MCGH * MVGH * oddH * oddA) / (2 * MCGH * oddH)
            xgh = (1 + mcgh * mvgh * odd_h * odd_a) / (2 * mcgh * odd_h)
            df_fixtures.at[idx, 'xGH'] = xgh
        except:
            pass
    
    if mcga is not None and mcgh is not None and mvga is not None:
        try:
            # xGA = (1 + MCGA * MVGA * oddH * oddA) / (2 * MCGA * oddA)
            xga = (1 + mcga * mvga * odd_h * odd_a) / (2 * mcga * odd_a)
            df_fixtures.at[idx, 'xGA'] = xga
        except:
            pass
    
    # Calcular probabilidades usando Poisson se temos xGH e xGA
    xgh = df_fixtures.at[idx, 'xGH']
    xga = df_fixtures.at[idx, 'xGA']
    
    if pd.notna(xgh) and pd.notna(xga) and xgh > 0 and xga > 0:
        try:
            # Calcular odds esperadas usando distribuição de Poisson (0-6 gols)
            # Implementação idêntica ao backtest_engine.py
            
            # Probabilidade de vitória da casa
            prob_home_win = 0.0
            for h in range(0, 6):
                for a in range(0, 6):
                    if h > a:
                        prob_home_win += poisson.pmf(h, xgh) * poisson.pmf(a, xga)
            
            # Probabilidade de vitória visitante
            prob_away_win = 0.0
            for h in range(0, 6):
                for a in range(0, 6):
                    if a > h:
                        prob_away_win += poisson.pmf(h, xgh) * poisson.pmf(a, xga)
            
            # Probabilidade de empate (mais preciso: 1 - soma das outras)
            prob_draw = 1.0 - prob_home_win - prob_away_win
            
            # Salvar probabilidades
            df_fixtures.at[idx, 'PROB_H'] = prob_home_win
            df_fixtures.at[idx, 'PROB_D'] = prob_draw
            df_fixtures.at[idx, 'PROB_A'] = prob_away_win
            
            # Converter para odds com margem de segurança (5% mínimo, odd máxima 20)
            odd_home_calc = 1 / prob_home_win if prob_home_win > 0.05 else 20.0
            odd_draw_calc = 1 / prob_draw if prob_draw > 0.05 else 20.0
            odd_away_calc = 1 / prob_away_win if prob_away_win > 0.05 else 20.0
            
            df_fixtures.at[idx, 'ODD_H_CALC'] = odd_home_calc
            df_fixtures.at[idx, 'ODD_D_CALC'] = odd_draw_calc
            df_fixtures.at[idx, 'ODD_A_CALC'] = odd_away_calc
        except Exception as e:
            print(f"  ⚠️ Erro ao calcular Poisson: {e}")
            pass
    
    if mcgh is not None and mcga is not None:
        print(f"OK MCGH:{mcgh:.3f} MVGH:{mvgh:.3f} MCGA:{mcga:.3f} MVGA:{mvga:.3f}")
        sucessos += 1
    elif mcgh is not None or mcga is not None:
        print(f"Parcial")
        sucessos += 1
    else:
        print("Sem dados suficientes")
        sem_dados += 1

# Adicionar coluna BACK (entrada HOME ou AWAY baseado em value bet)
def calcular_entrada(row):
    """Determina se deve entrar em HOME ou AWAY baseado nas odds calculadas e DxG"""
    try:
        b365h = float(row.get('B365H', 0))
        b365a = float(row.get('B365A', 0))
        odd_h_calc = float(row.get('ODD_H_CALC', 0))
        odd_a_calc = float(row.get('ODD_A_CALC', 0))
        xgh = row.get('xGH')
        xga = row.get('xGA')
        
        # Calcular DxG
        dxg = ''
        if xgh is not None and xga is not None:
            try:
                diff = float(xgh) - float(xga)
                if diff < -1.0:
                    dxg = 'FA'
                elif -1.0 <= diff < -0.3:
                    dxg = 'LA'
                elif -0.3 <= diff <= 0.3:
                    dxg = 'EQ'
                elif 0.3 < diff <= 1.0:
                    dxg = 'LH'
                else:
                    dxg = 'FH'
            except:
                pass
        
        # Regra 1: Se CASA > (ODD H CALC * 1.1) → HOME
        if b365h > (odd_h_calc * 1.1) and odd_h_calc > 0:
            return 'HOME'
        
        # Regra 2: Se VISITANTE > (ODD A CALC * 1.1) → AWAY
        if b365a > (odd_a_calc * 1.1) and odd_a_calc > 0:
            return 'AWAY'
        
        # Regra 3: Se DxG = EQ
        if dxg == 'EQ':
            # Se CASA < VISITANTE → HOME
            if b365h < b365a:
                return 'HOME'
            # Se CASA > VISITANTE → AWAY
            elif b365h > b365a:
                return 'AWAY'
        
        return ''
    except:
        return ''

df_fixtures['BACK'] = df_fixtures.apply(calcular_entrada, axis=1)

# Salvar arquivo atualizado
output_csv = Path("fixtures/proxima_rodada_com_analise.csv")
df_fixtures.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"\n{'='*80}")
print(f"RESUMO")
print(f"{'='*80}")
print(f"Jogos analisados com sucesso: {sucessos}")
print(f"Jogos sem historico da liga: {sem_historico}")
print(f"Jogos sem dados suficientes: {sem_dados}")
print(f"\nArquivo salvo: {output_csv}")
print(f"{'='*80}")
print(f"{'='*80}")
