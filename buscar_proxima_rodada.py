import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

# URLs dos fixtures
urls = [
    "https://www.football-data.co.uk/fixtures.csv",
    "https://www.football-data.co.uk/new_league_fixtures.csv"
]

# Diretório de saída
output_dir = Path("fixtures")
output_dir.mkdir(exist_ok=True)

print(f"{'='*80}")
print(f"DOWNLOAD DOS JOGOS DA PRÓXIMA RODADA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# Carregar entradas qualificadas para validação
def carregar_entradas_qualificadas():
    """Carrega as entradas que foram validadas nos critérios"""
    entradas_qualificadas = set()
    
    try:
        # Opção 1: Carregar do arquivo de dados bruto
        with open('fixtures/backtest_acumulado.json', 'r', encoding='utf-8') as f:
            entradas = json.load(f)
        
        resumo = defaultdict(lambda: {'entradas': 0, 'lucro': 0.0, 'acertos': 0})
        
        for entrada in entradas:
            liga = entrada.get('liga', 'Desconhecida')
            lp = float(entrada.get('lp', 0))
            lp_com_desconto = lp * 0.955
            tipo_entrada = entrada.get('entrada', 'HOME')
            dxg_tipo = entrada.get('dxg', 'EQ')
            
            chave = f'{liga}|{tipo_entrada}|{dxg_tipo}'
            
            dados = resumo[chave]
            dados['entradas'] += 1
            dados['lucro'] += lp_com_desconto
            if lp_com_desconto > 0:
                dados['acertos'] += 1
        
        # Calcular ROI e adicionar à lista de qualificadas
        for chave, dados in resumo.items():
            if dados['entradas'] > 0:
                dados['roi'] = (dados['lucro'] / dados['entradas']) * 100
            
            # Filtrar: entradas >= 75, ROI >= 5%, lucro >= 20
            if dados['entradas'] >= 75 and dados['roi'] >= 5.0 and dados['lucro'] >= 20.0:
                entradas_qualificadas.add(chave)
        
        print(f"[OK] Carregadas {len(entradas_qualificadas)} entradas qualificadas para validação\n")
        
    except Exception as e:
        print(f"[AVISO] Erro ao carregar entradas qualificadas: {str(e)}\n")
    
    return entradas_qualificadas

entradas_validas = carregar_entradas_qualificadas()

todos_jogos = []

# Baixar e processar cada arquivo
for idx, url in enumerate(urls, 1):
    try:
        print(f"Baixando {url}...", end=" ")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Salvar arquivo bruto
        filename = f"fixtures_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = output_dir / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Ler CSV
        df = pd.read_csv(filepath)
        print(f"[OK] {len(df)} jogos")
        
        # Adicionar à lista
        todos_jogos.append(df)
        
    except Exception as e:
        print(f"[ERRO] Erro: {str(e)}")

# Consolidar todos os jogos
if todos_jogos:
    # Normalizar colunas de cada DataFrame antes de concatenar
    dfs_normalizados = []
    
    # Mapeamento de países para códigos de liga
    country_to_league = {
        'Argentina': 'ARG',
        'Austria': 'AUT',
        'Brazil': 'BRA',
        'China': 'CHN',
        'Denmark': 'DNK',
        'Finland': 'FIN',
        'Ireland': 'IRL',
        'Japan': 'JPN',
        'Mexico': 'MEX',
        'Norway': 'NOR',
        'Poland': 'POL',
        'Romania': 'ROU',
        'Russia': 'RUS',
        'Sweden': 'SWE',
        'Switzerland': 'SWZ',
        'USA': 'USA'
    }
    
    for df in todos_jogos:
        df_norm = df.copy()
        
        # Padronizar nomes de colunas
        rename_dict = {}
        if 'Home' in df_norm.columns and 'HomeTeam' not in df_norm.columns:
            rename_dict['Home'] = 'HomeTeam'
        if 'Away' in df_norm.columns and 'AwayTeam' not in df_norm.columns:
            rename_dict['Away'] = 'AwayTeam'
        
        # Para CSVs com "Country" (new_league_fixtures), mapear país para código de liga
        if 'Country' in df_norm.columns:
            df_norm['Div'] = df_norm['Country'].map(country_to_league)
            # Se o mapeamento falhar, usar o próprio valor do Country
            df_norm['Div'] = df_norm['Div'].fillna(df_norm['Country'])
        elif 'League' in df_norm.columns and 'Div' not in df_norm.columns:
            rename_dict['League'] = 'Div'
        
        if rename_dict:
            df_norm.rename(columns=rename_dict, inplace=True)
        
        dfs_normalizados.append(df_norm)
    
    df_completo = pd.concat(dfs_normalizados, ignore_index=True)
    
    # Colunas essenciais + todas as odds disponíveis
    colunas_essenciais = ['Date', 'Div', 'HomeTeam', 'AwayTeam']
    colunas_odds = ['B365H', 'B365D', 'B365A', 'B365CH', 'B365CD', 'B365CA', 
                    'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA',
                    'MaxH', 'MaxD', 'MaxA', 'MaxCH', 'MaxCD', 'MaxCA',
                    'AvgH', 'AvgD', 'AvgA', 'AvgCH', 'AvgCD', 'AvgCA']
    
    # Verificar quais colunas existem
    colunas_disponiveis = [col for col in colunas_essenciais if col in df_completo.columns]
    colunas_disponiveis += [col for col in colunas_odds if col in df_completo.columns]
    
    if colunas_disponiveis:
        df_filtrado = df_completo[colunas_disponiveis].copy()
        
        # Renomear colunas para português
        rename_map = {
            'Date': 'DATA',
            'Div': 'LIGA',
            'HomeTeam': 'HOME',
            'AwayTeam': 'AWAY',
            'B365H': 'B365H',
            'B365D': 'B365D',
            'B365A': 'B365A'
        }
        df_filtrado.rename(columns=rename_map, inplace=True)
        
        # Remover linhas com dados faltantes essenciais
        df_filtrado = df_filtrado.dropna(subset=['DATA', 'HOME', 'AWAY'])
        
        # Filtrar apenas jogos FUTUROS (a partir de hoje)
        try:
            from datetime import datetime, timedelta
            hoje = datetime.now().date()
            
            # Tentar converter a coluna DATA para datetime
            df_filtrado['DATA_temp'] = pd.to_datetime(df_filtrado['DATA'], format='%d/%m/%Y', errors='coerce')
            
            # Se houver alguma data válida, filtrar
            if df_filtrado['DATA_temp'].notna().any():
                df_filtrado = df_filtrado[df_filtrado['DATA_temp'].dt.date >= hoje]
                df_filtrado = df_filtrado.drop('DATA_temp', axis=1)
                
                if len(df_filtrado) == 0:
                    print(f"\n[AVISO] Nenhum jogo encontrado para {hoje.strftime('%d/%m/%Y')} ou datas futuras")
                    exit(0)
            else:
                df_filtrado = df_filtrado.drop('DATA_temp', axis=1)
        except Exception as e:
            print(f"[AVISO] Erro ao filtrar por data: {str(e)}")
        
        
        # Filtrar apenas ligas que temos histórico E que têm entradas validadas
        # Ligas SEM combinações validadas (critério: >= 75 entradas, >= 5% ROI, >= 20 lucro)
        ligas_sem_validadas = {'ARG', 'AUT', 'B1', 'D1', 'D2', 'DNK', 'G1', 'I1'}
        
        ligas_disponiveis = [
            'E0', 'E1', 'I2', 'F1', 'F2', 
            'SP1', 'SP2', 'P1', 'T1', 'N1',
            'BRA', 'CHN', 'FIN', 'IRL', 'JPN', 
            'MEX', 'NOR', 'POL', 'ROU', 'RUS', 'SWE', 'SWZ', 'USA',
            'Series A'  # Alias para BRA
        ]
        
        total_antes = len(df_filtrado)
        df_filtrado = df_filtrado[df_filtrado['LIGA'].isin(ligas_disponiveis)]
        excluidos = total_antes - len(df_filtrado)
        
        if excluidos > 0:
            print(f"\n[AVISO] {excluidos} jogos excluídos (ligas sem histórico)")
        
        # Ordenar por data e liga
        if 'DATA' in df_filtrado.columns:
            df_filtrado['DATA'] = pd.to_datetime(df_filtrado['DATA'], format='%d/%m/%Y', errors='coerce')
            df_filtrado = df_filtrado.sort_values(['DATA', 'LIGA'])
            df_filtrado['DATA'] = df_filtrado['DATA'].dt.strftime('%d/%m/%Y')
        
        # Salvar CSV processado
        csv_output = output_dir / f"proxima_rodada_{datetime.now().strftime('%Y%m%d')}.csv"
        df_filtrado.to_csv(csv_output, index=False, encoding='utf-8-sig')
        
        print(f"\n[OK] Dados consolidados: {len(df_filtrado)} jogos")
        print(f"[OK] Arquivo CSV salvo: {csv_output}")
        
        # Executar análise histórica
        print(f"\nExecutando análise histórica...")
        try:
            import subprocess
            result = subprocess.run(['python', 'analisar_proxima_rodada.py'], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"[OK] Análise histórica concluída")
                # Carregar arquivo com análise
                csv_analise = output_dir / "proxima_rodada_com_analise.csv"
                if csv_analise.exists():
                    df_filtrado = pd.read_csv(csv_analise)
            else:
                print(f"[AVISO] Análise histórica falhou (código {result.returncode})")
                if result.stderr:
                    print(f"Erro: {result.stderr[:200]}")
        except Exception as e:
            print(f"[AVISO] Erro na análise histórica: {str(e)}")
        
        # Gerar página HTML
        html_output = output_dir / "proxima_rodada.html"
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="refresh" content="300">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .nav-links {{
            display: flex;
            justify-content: center;
            gap: 15px;
            padding: 15px 0;
        }}
        
        .nav-link {{
            color: white;
            text-decoration: none;
            padding: 8px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            transition: background 0.3s;
        }}
        
        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.4);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 15px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .stat-box {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #1e3c72;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        
        .filters {{
            padding: 20px;
            background: #fff;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .filter-input {{
            width: 100%;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}
        
        .filter-input:focus {{
            outline: none;
            border-color: #2a5298;
        }}
        
        .table-container {{
            overflow-x: auto;
            padding: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.75em;
        }}
        
        thead {{
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        th {{
            padding: 8px 6px;
            text-align: left;
            font-weight: 600;
            color: #1e3c72;
        }}
        
        td {{
            padding: 6px 6px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        tbody tr {{
            transition: background-color 0.2s;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .liga-badge {{
            display: inline-block;
            padding: 5px 12px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .team {{
            font-weight: 500;
            color: white;
        }}
        
        .odds {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 3px 6px;
            background: #e9ecef;
            border-radius: 4px;
            display: inline-block;
            min-width: 38px;
            text-align: center;
            font-size: 0.85em;
        }}
        
        .odds.home {{ background: #d4edda; color: #155724; }}
        .odds.draw {{ background: #fff3cd; color: #856404; }}
        .odds.away {{ background: #f8d7da; color: #721c24; }}
        
        .date-col {{
            color: #6c757d;
            font-weight: 500;
        }}
        
        .center-cell {{
            text-align: center;
            font-size: 0.85em;
        }}
        
        .calc-odd {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 6px 10px;
            border-radius: 6px;
            display: inline-block;
            min-width: 45px;
            text-align: center;
            font-size: 0.9em;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        
        .confidence {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .value-bet {{
            background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
            color: #000;
            font-weight: 900;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.3);
            border: 2px solid #00ff88;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .value-bet::before {{
            content: "✓ ";
            margin-right: 3px;
        }}
        
        .bad-bet {{
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
            font-weight: 900;
            box-shadow: 0 0 15px rgba(255, 68, 68, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.2);
            border: 2px solid #ff4444;
        }}
        
        .bad-bet::before {{
            content: "✗ ";
            margin-right: 3px;
        }}
        
        .neutral-bet {{
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            font-weight: 700;
            box-shadow: 0 0 12px rgba(255, 170, 0, 0.5);
            border: 2px solid #ffaa00;
        }}
        
        .neutral-bet::before {{
            content: "◆ ";
            margin-right: 3px;
        }}
        
        .save-btn {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            font-weight: 500;
            transition: background-color 0.3s;
        }}
        
        .save-btn:hover {{
            background-color: #0056b3;
        }}
        
        .save-btn:disabled {{
            background-color: #6c757d;
            cursor: not-allowed;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-size: 1.2em;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                flex-direction: column;
            }}
            
            th, td {{
                padding: 10px 8px;
                font-size: 0.9em;
            }}
        }}

        /* Tema baseado em backtest_resumo_entradas */
        body {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ecf0f1;
        }}
        .container {{
            background: transparent;
            box-shadow: none;
        }}
        .header {{
            background: rgba(0, 0, 0, 0.3);
            color: #00d4ff;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #00d4ff;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        .header p {{
            color: #ecf0f1;
        }}
        .nav-links {{
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 12px 0 18px;
        }}
        .nav-link {{
            color: #00d4ff;
            background: rgba(0, 212, 255, 0.12);
            border: 1px solid rgba(0, 212, 255, 0.35);
        }}
        .nav-link:hover {{
            background: rgba(0, 212, 255, 0.25);
        }}
        .stats, .filters, .table-container {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 212, 255, 0.35);
            color: #ecf0f1;
        }}
        .stat-box {{
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(0, 212, 255, 0.35);
        }}
        .stat-number {{
            color: #00d4ff;
        }}
        .stat-label {{
            color: #b0c4de;
        }}
        .filter-input {{
            background: rgba(0, 0, 0, 0.35);
            color: #ecf0f1;
            border: 1px solid rgba(0, 212, 255, 0.35);
        }}
        table {{
            color: #ecf0f1;
        }}
        thead {{
            background: #0a5f7e;
            border-bottom: 2px solid #0a5f7e;
        }}
        th {{
            color: #00d4ff;
            border: 1px solid #0a5f7e;
        }}
        td {{
            border: 1px solid #333;
        }}
        tbody tr:nth-child(odd) {{
            background: rgba(0, 212, 255, 0.05);
        }}
        tbody tr:hover {{
            background: rgba(0, 212, 255, 0.15);
        }}
        .liga-badge {{
            background: rgba(0, 212, 255, 0.2);
            color: #00d4ff;
            border: 1px solid rgba(0, 212, 255, 0.35);
        }}
        .odds, .calc-odd, .confidence {{
            background: rgba(0, 0, 0, 0.35);
            color: #ecf0f1;
        }}
        .save-btn {{
            background: #00d4ff;
            color: #1a1a2e;
            border: 1px solid rgba(0, 212, 255, 0.35);
        }}
        .save-btn:hover {{
            background: rgba(0, 212, 255, 0.85);
        }}
        .footer {{
            background: rgba(0, 0, 0, 0.3);
            color: #b0c4de;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ Próxima Rodada</h1>
            <p>Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} | Version: {int(datetime.now().timestamp())}</p>
            <div class="nav-links">
                <a href="http://localhost:8000/proxima_rodada.html" class="nav-link">Próxima Rodada</a>
                <a href="http://localhost:8000/jogos_salvos.html" class="nav-link">Jogos Salvos</a>
                <a href="http://localhost:8000/analise_salvos.html" class="nav-link">Análise Salvos</a>
                <a href="http://localhost:5001/backtest.html" class="nav-link">Backtest</a>
                <a href="http://localhost:5001/backtest_salvos.html" class="nav-link">Backtests Salvos</a>
                <a href="http://localhost:5001/backtest_resumo_entradas.html" class="nav-link">Resumo Entradas</a>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(df_filtrado)}</div>
                <div class="stat-label">Total de Jogos</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{df_filtrado['LIGA'].nunique() if 'LIGA' in df_filtrado.columns else 'N/A'}</div>
                <div class="stat-label">Ligas</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{df_filtrado['DATA'].nunique() if 'DATA' in df_filtrado.columns else 'N/A'}</div>
                <div class="stat-label">Datas</div>
            </div>
        </div>
        
        <div class="filters">
            <input type="text" id="searchInput" class="filter-input" placeholder="🔍 Buscar por time, liga ou data..." onkeyup="filterTable()">
        </div>
        
        <div class="table-container">
            <table id="gamesTable">
                <thead>
                    <tr>
                        <th>DATA</th>
                        <th>LIGA</th>
                        <th>HOME</th>
                        <th>AWAY</th>
                        <th>CASA</th>
                        <th>EMPATE</th>
                        <th>VISITANTE</th>
                        <th>xGH</th>
                        <th>xGA</th>
                        <th>DxG</th>
                        <th>CFG</th>
                        <th>ODD H CALC</th>
                        <th>ODD D CALC</th>
                        <th>ODD A CALC</th>
                        <th>VALIDADA</th>
                        <th>AÇÃO</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Adicionar linhas da tabela (usar indice sequencial)
        df_filtrado_reset = df_filtrado.reset_index(drop=True)
        for idx, row in df_filtrado_reset.iterrows():
            data = row.get('DATA', '-')
            liga = row.get('LIGA', '-')
            home = row.get('HOME', '-')
            away = row.get('AWAY', '-')
            b365h = row.get('B365H', '-')
            b365d = row.get('B365D', '-')
            b365a = row.get('B365A', '-')
            
            # Formatar odds
            b365h_fmt = f"{b365h:.2f}" if pd.notna(b365h) and b365h != '-' else '-'
            b365d_fmt = f"{b365d:.2f}" if pd.notna(b365d) and b365d != '-' else '-'
            b365a_fmt = f"{b365a:.2f}" if pd.notna(b365a) and b365a != '-' else '-'
            
            # Formatar médias históricas
            mcgh = row.get('MCGH', None)
            mvgh = row.get('MVGH', None)
            mcga = row.get('MCGA', None)
            mvga = row.get('MVGA', None)
            xgh = row.get('xGH', None)
            xga = row.get('xGA', None)
            cfxgh = row.get('CFxGH', None)
            cfxga = row.get('CFxGA', None)
            odd_h_calc = row.get('ODD_H_CALC', None)
            odd_d_calc = row.get('ODD_D_CALC', None)
            odd_a_calc = row.get('ODD_A_CALC', None)
            
            mcgh_fmt = f"{mcgh:.3f}" if pd.notna(mcgh) else '-'
            mvgh_fmt = f"{mvgh:.3f}" if pd.notna(mvgh) else '-'
            mcga_fmt = f"{mcga:.3f}" if pd.notna(mcga) else '-'
            mvga_fmt = f"{mvga:.3f}" if pd.notna(mvga) else '-'
            xgh_fmt = f"{xgh:.2f}" if pd.notna(xgh) else '-'
            xga_fmt = f"{xga:.2f}" if pd.notna(xga) else '-'
            
            # Calcular DxG (classificação da força do xG)
            if pd.notna(xgh) and pd.notna(xga):
                diff = xgh - xga
                if diff < -1.0:
                    dxg = 'FA'  # Forte Away
                elif -1.0 <= diff < -0.3:
                    dxg = 'LA'  # Leve Away
                elif -0.3 <= diff <= 0.3:
                    dxg = 'EQ'  # Equilibrado
                elif 0.3 < diff <= 1.0:
                    dxg = 'LH'  # Leve Home
                else:  # diff > 1.0
                    dxg = 'FH'  # Forte Home
            else:
                dxg = '-'
            
            # Calcular CFG (Confiança Geral)
            if pd.notna(cfxgh) and pd.notna(cfxga) and cfxgh > 0 and cfxga > 0:
                import math
                cfg = math.sqrt(cfxgh * cfxga)
            else:
                cfg = 0
            cfg_fmt = f"{cfg*100:.1f}%" if cfg > 0 else '-'
            
            odd_h_calc_fmt = f"{odd_h_calc:.2f}" if pd.notna(odd_h_calc) else '-'
            odd_d_calc_fmt = f"{odd_d_calc:.2f}" if pd.notna(odd_d_calc) else '-'
            odd_a_calc_fmt = f"{odd_a_calc:.2f}" if pd.notna(odd_a_calc) else '-'
            
            # Função para calcular cor baseada na confiança com escala gradual contínua
            def get_confidence_color(cf_value):
                if pd.isna(cf_value):
                    return ""
                # cf_value está entre 0 e 1
                # Escala contínua: Vermelho (0%) -> Amarelo (50%) -> Verde (100%)
                
                # Garantir que o valor esteja entre 0 e 1
                cf_value = max(0, min(1, cf_value))
                
                if cf_value <= 0.5:
                    # De vermelho (255,0,0) para amarelo (255,255,0)
                    # Interpolar o canal verde de 0 para 255
                    green = int(255 * (cf_value / 0.5))
                    return f"background-color: rgb(255, {green}, 0); color: #000;"
                else:
                    # De amarelo (255,255,0) para verde (0,255,0)
                    # Interpolar o canal vermelho de 255 para 0
                    red = int(255 * (1 - (cf_value - 0.5) / 0.5))
                    return f"background-color: rgb({red}, 255, 0); color: #000;"
            
            # Aplicar cor à confiança geral
            cfg_color = get_confidence_color(cfg if cfg > 0 else None)
            
            # Determinar classes CSS para odds calculadas
            odd_h_class = ""
            odd_d_class = ""
            odd_a_class = ""
            
            if pd.notna(odd_h_calc) and pd.notna(b365h):
                if b365h > odd_h_calc * 1.10:
                    odd_h_class = "value-bet"
                elif b365h < odd_h_calc:
                    odd_h_class = "bad-bet"
                else:
                    odd_h_class = "neutral-bet"
            
            if pd.notna(odd_d_calc) and pd.notna(b365d):
                if b365d > odd_d_calc * 1.10:
                    odd_d_class = "value-bet"
                elif b365d < odd_d_calc:
                    odd_d_class = "bad-bet"
                else:
                    odd_d_class = "neutral-bet"
            
            if pd.notna(odd_a_calc) and pd.notna(b365a):
                if b365a > odd_a_calc * 1.10:
                    odd_a_class = "value-bet"
                elif b365a < odd_a_calc:
                    odd_a_class = "bad-bet"
                else:
                    odd_a_class = "neutral-bet"
            
            # Validar se a entrada está qualificada (HOME ou AWAY)
            chave_home = f'{liga}|HOME|{dxg}'
            chave_away = f'{liga}|AWAY|{dxg}'
            
            validacao_home = "SIM" if chave_home in entradas_validas else "NÃO"
            validacao_away = "SIM" if chave_away in entradas_validas else "NÃO"
            
            # Determinar cor da validação
            cor_home = "background-color: #00ff88; color: #000;" if validacao_home == "SIM" else "background-color: #ff4444; color: white;"
            cor_away = "background-color: #00ff88; color: #000;" if validacao_away == "SIM" else "background-color: #ff4444; color: white;"
            
            html_content += f"""                    <tr>
                        <td class="date-col">{data}</td>
                        <td><span class="liga-badge">{liga}</span></td>
                        <td class="team">{home}</td>
                        <td class="team">{away}</td>
                        <td><span class="odds home">{b365h_fmt}</span></td>
                        <td><span class="odds draw">{b365d_fmt}</span></td>
                        <td><span class="odds away">{b365a_fmt}</span></td>
                        <td class="center-cell">{xgh_fmt}</td>
                        <td class="center-cell">{xga_fmt}</td>
                        <td class="center-cell"><strong>{dxg}</strong></td>
                        <td class="center-cell"><span class="confidence" style="{cfg_color}">{cfg_fmt}</span></td>
                        <td class="center-cell"><span class="calc-odd {odd_h_class}">{odd_h_calc_fmt}</span></td>
                        <td class="center-cell"><span class="calc-odd {odd_d_class}">{odd_d_calc_fmt}</span></td>
                        <td class="center-cell"><span class="calc-odd {odd_a_class}">{odd_a_calc_fmt}</span></td>
                        <td class="center-cell"><div style="display: flex; gap: 8px; font-weight: bold; font-size: 0.85em;"><span style="{cor_home}; padding: 4px 8px; border-radius: 4px;">{validacao_home}</span><span style="{cor_away}; padding: 4px 8px; border-radius: 4px;">{validacao_away}</span></div></td>
                        <td class="center-cell"><button class="save-btn" onclick="salvarJogo(this, {idx})">Salvar</button></td>
                    </tr>
"""
        
        html_content += """                </tbody>
            </table>
            <div id="noResults" class="no-results" style="display: none;">
                Nenhum jogo encontrado com os critérios de busca.
            </div>
        </div>
        
        <div class="footer">
            <p>Dados: <a href="https://www.football-data.co.uk" target="_blank">Football-Data.co.uk</a></p>
            <p>Odds: Bet365 (B365)</p>
        </div>
    </div>
    
    <script>
        function filterTable() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const table = document.getElementById('gamesTable');
            const tbody = table.getElementsByTagName('tbody')[0];
            const tr = tbody.getElementsByTagName('tr');
            const noResults = document.getElementById('noResults');
            let visibleCount = 0;
            
            for (let i = 0; i < tr.length; i++) {
                const td = tr[i].getElementsByTagName('td');
                let found = false;
                
                for (let j = 0; j < td.length; j++) {
                    if (td[j]) {
                        const txtValue = td[j].textContent || td[j].innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            found = true;
                            break;
                        }
                    }
                }
                
                if (found) {
                    tr[i].style.display = '';
                    visibleCount++;
                } else {
                    tr[i].style.display = 'none';
                }
            }
            
            if (visibleCount === 0) {
                table.style.display = 'none';
                noResults.style.display = 'block';
            } else {
                table.style.display = 'table';
                noResults.style.display = 'none';
            }
        }
        
        function salvarJogo(btn, index) {
            btn.disabled = true;
            btn.textContent = 'Salvando...';
            
            // Chamar o script Python para salvar o jogo
            fetch('http://localhost:8000/api/salvar_jogo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ index: index })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Forcar geracao da pagina de jogos salvos
                    fetch('http://localhost:8000/api/gerar_pagina_salvos', { method: 'POST' });
                    btn.textContent = 'Salvo!';
                    btn.style.backgroundColor = '#28a745';
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.textContent = 'Salvar';
                        btn.style.backgroundColor = '#007bff';
                    }, 2000);
                } else {
                    alert('Erro ao salvar: ' + data.message);
                    btn.disabled = false;
                    btn.textContent = 'Salvar';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao salvar o jogo. Verifique se o servidor está rodando.');
                btn.disabled = false;
                btn.textContent = 'Salvar';
            });
        }
    </script>
</body>
</html>
"""
        
        # Salvar HTML
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] Página HTML salva: {html_output}")
        print(f"\n{'='*80}")
        print(f"Visualize a página em: file:///{html_output.absolute()}")
        print(f"{'='*80}")
        
    else:
        print("\n[AVISO] Colunas necessárias não encontradas nos dados")
else:
    print("\n[AVISO] Nenhum dado foi baixado")
