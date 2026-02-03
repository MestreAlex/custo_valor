import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def _proximo_id(jogos_salvos):
    if not jogos_salvos:
        return 0
    ids = [j.get('id', -1) for j in jogos_salvos if isinstance(j.get('id', None), int)]
    return (max(ids) + 1) if ids else 0

def _normalizar_ids(jogos_salvos):
    """Garante IDs unicos e sequenciais para jogos salvos."""
    ids = [j.get('id', None) for j in jogos_salvos]
    ids_validos = [i for i in ids if isinstance(i, int)]
    if len(ids_validos) != len(ids) or len(set(ids_validos)) != len(ids_validos):
        for novo_id, jogo in enumerate(jogos_salvos):
            jogo['id'] = novo_id
        return True
    return False

def _calcular_lp(jogo, gh_val, ga_val):
    """
    Calcula Lucro/Perda baseado no resultado e estratégia de value bet
    
    Lógica:
    1. Identifica se havia value bet:
       - Back Home: B365H > ODD_H_CALC * 1.1 (10% de margem)
       - Back Away: B365A > ODD_A_CALC * 1.1 (10% de margem)
    
    2. Calcula resultado:
       - Se home venceu (GH > GA):
         - Se há value em home: LP = (B365H - 1) * 0.955 (desconto 4,5% de taxa)
         - Senão: LP = -1
       - Se away venceu (GA > GH):
         - Se há value em away: LP = (B365A - 1) * 0.955 (desconto 4,5% de taxa)
         - Senão: LP = -1
       - Se empate: LP = -1
    """
    try:
        b365h = jogo.get('B365H', None)
        b365a = jogo.get('B365A', None)
        odd_h_calc = jogo.get('ODD_H_CALC', None)
        odd_a_calc = jogo.get('ODD_A_CALC', None)

        if b365h is None or b365a is None or odd_h_calc is None or odd_a_calc is None:
            return None

        b365h = float(b365h)
        b365a = float(b365a)
        odd_h_calc = float(odd_h_calc)
        odd_a_calc = float(odd_a_calc)

        # Verificar value bets (10% de margem)
        value_home = b365h > (odd_h_calc * 1.1)
        value_away = b365a > (odd_a_calc * 1.1)

        # Se casa venceu
        if gh_val > ga_val:
            if value_home:
                return (b365h - 1) * 0.955  # Desconto de 4,5% aplicado
            else:
                return -1  # Perda (venceu mas sem value)
        
        # Se visitante venceu
        if ga_val > gh_val:
            if value_away:
                return (b365a - 1) * 0.955  # Desconto de 4,5% aplicado
            else:
                return -1  # Perda (venceu mas sem value)
        
        # Se empatou (nenhum resultado esperado)
        return -1
    except Exception:
        return None

def _format_confidence(valor):
    try:
        v = float(valor)
    except Exception:
        return '-'
    return f"{v * 100:.1f}%"

def _confidence_style(valor):
    try:
        v = float(valor)
    except Exception:
        return ""
    v = max(0.0, min(1.0, v))
    if v <= 0.5:
        green = int(255 * (v / 0.5))
        return f"background-color: rgb(255, {green}, 0); color: #000;"
    red = int(255 * (1 - (v - 0.5) / 0.5))
    return f"background-color: rgb({red}, 255, 0); color: #000;"

def _calcular_cfg(cfxgh, cfxga):
    """Calcula a Confiança Geral (CFG) baseada em CFxGH e CFxGA"""
    try:
        gh = float(cfxgh) if cfxgh is not None else 0
        ga = float(cfxga) if cfxga is not None else 0
        
        if gh == 0 or ga == 0:
            return 0
        
        import math
        return math.sqrt(gh * ga)
    except Exception:
        return 0

def _calcular_dxg(xgh, xga):
    """Calcula a classificação DxG baseada na diferença entre xGH e xGA"""
    try:
        gh = float(xgh) if xgh is not None else 0
        ga = float(xga) if xga is not None else 0
        diff = gh - ga
        
        if diff < -1.0:
            return 'FA'  # Forte Away
        elif -1.0 <= diff < -0.3:
            return 'LA'  # Leve Away
        elif -0.3 <= diff <= 0.3:
            return 'EQ'  # Equilibrado
        elif 0.3 < diff <= 1.0:
            return 'LH'  # Leve Home
        else:  # diff > 1.0
            return 'FH'  # Forte Home
    except Exception:
        return '-'

def salvar_jogo(index_jogo):
    """Salva um jogo específico da próxima rodada para análise futura"""
    
    # Carregar fixtures atuais
    fixtures_dir = Path("fixtures")
    csv_analise = fixtures_dir / "proxima_rodada_com_analise.csv"
    
    if not csv_analise.exists():
        print("Erro: Arquivo de analise nao encontrado!")
        return False
    
    df_fixtures = pd.read_csv(csv_analise)
    
    if index_jogo < 0 or index_jogo >= len(df_fixtures):
        print(f"Erro: Indice {index_jogo} invalido!")
        return False
    
    # Carregar jogos salvos existentes
    salvos_file = fixtures_dir / "jogos_salvos.json"
    if salvos_file.exists():
        with open(salvos_file, 'r', encoding='utf-8') as f:
            jogos_salvos = json.load(f)
    else:
        jogos_salvos = []

    # Normalizar IDs caso existam duplicados
    if _normalizar_ids(jogos_salvos):
        with open(salvos_file, 'w', encoding='utf-8') as f:
            json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
    
    # Pegar o jogo selecionado
    jogo = df_fixtures.iloc[index_jogo].to_dict()
    
    # Converter NaN para None (válido em JSON)
    import math
    for key, value in jogo.items():
        if isinstance(value, float) and math.isnan(value):
            jogo[key] = None
    
    # Adicionar metadata
    jogo['data_salvo'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    jogo['GH'] = None  # Gols reais home (a ser preenchido depois)
    jogo['GA'] = None  # Gols reais away (a ser preenchido depois)
    jogo['id'] = _proximo_id(jogos_salvos)  # ID unico
    
    # Verificar se já existe (evitar duplicatas)
    for salvo in jogos_salvos:
        if (salvo.get('DATA') == jogo.get('DATA') and 
            salvo.get('HOME') == jogo.get('HOME') and 
            salvo.get('AWAY') == jogo.get('AWAY')):
            print("Jogo ja foi salvo anteriormente!")
            return False
    
    # Adicionar aos salvos
    jogos_salvos.append(jogo)
    
    # Salvar arquivo
    with open(salvos_file, 'w', encoding='utf-8') as f:
        json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
    
    # Regenerar pagina HTML para refletir o novo jogo salvo
    try:
        gerar_pagina_salvos()
    except Exception as e:
        print(f"Aviso: falha ao gerar pagina de jogos salvos: {e}")

    print(f"OK Jogo salvo: {jogo['HOME']} vs {jogo['AWAY']}")
    return True

def atualizar_campos_faltantes():
    """Atualiza jogos salvos calculando CFxGH e CFxGA a partir dos dados existentes"""
    
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        print("Nenhum jogo salvo encontrado!")
        return False
    
    # Carregar jogos salvos
    with open(salvos_file, 'r', encoding='utf-8') as f:
        jogos_salvos = json.load(f)
    
    atualizados = 0
    for jogo in jogos_salvos:
        # Sempre recalcular CF (para corrigir valores errados)
        try:
            mcgh = jogo.get('MCGH')
            mvgh = jogo.get('MVGH')
            mcga = jogo.get('MCGA')
            mvga = jogo.get('MVGA')
            
            if all(x is not None for x in [mcgh, mvgh, mcga, mvga]):
                # Calcular coeficientes de variação
                cv_cgh = (mvgh / mcgh) if mcgh != 0 else 0
                cv_vgh = (mvgh / mvgh) if mvgh != 0 else 0  # sempre 1
                cv_cga = (mvga / mcga) if mcga != 0 else 0
                cv_vga = (mvga / mvga) if mvga != 0 else 0  # sempre 1
                
                # Calcular confiança (quanto menor CV, maior confiança) - valores entre 0 e 1
                import math
                cfxgh = (1 / (1 + math.sqrt(cv_cgh**2 + cv_vgh**2))) if (cv_cgh or cv_vgh) else 0
                cfxga = (1 / (1 + math.sqrt(cv_cga**2 + cv_vga**2))) if (cv_cga or cv_vga) else 0
                
                jogo['CFxGH'] = cfxgh
                jogo['CFxGA'] = cfxga
                atualizados += 1
        except Exception as e:
            print(f"Erro ao calcular CF para {jogo.get('HOME')} vs {jogo.get('AWAY')}: {e}")
    
    # Salvar jogos atualizados
    with open(salvos_file, 'w', encoding='utf-8') as f:
        json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {atualizados} jogos tiveram CFxGH e CFxGA calculados")
    return True

def atualizar_resultado(jogo_id, gh, ga):
    """Atualiza o resultado real de um jogo salvo"""
    
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        print("Erro: Nenhum jogo salvo encontrado!")
        return False
    
    with open(salvos_file, 'r', encoding='utf-8') as f:
        jogos_salvos = json.load(f)

    # Normalizar IDs caso existam duplicados
    if _normalizar_ids(jogos_salvos):
        with open(salvos_file, 'w', encoding='utf-8') as f:
            json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
    
    # Encontrar e atualizar o jogo
    for jogo in jogos_salvos:
        if jogo['id'] == jogo_id:
            jogo['GH'] = gh
            jogo['GA'] = ga
            jogo['LP'] = _calcular_lp(jogo, gh, ga)
            jogo['data_atualizado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Salvar
            with open(salvos_file, 'w', encoding='utf-8') as f:
                json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
            
            try:
                gerar_pagina_salvos()
            except Exception as e:
                print(f"Aviso: falha ao gerar pagina de jogos salvos: {e}")

            print(f"OK Resultado atualizado: {jogo['HOME']} {gh} x {ga} {jogo['AWAY']}")
            return True
    
    print(f"Erro: Jogo ID {jogo_id} nao encontrado!")
    return False

def atualizar_resultado_com_lp(jogo_id, gh, ga, lp):
    """Atualiza o resultado real e L/P de um jogo salvo"""
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        print("Erro: Nenhum jogo salvo encontrado!")
        return False

    with open(salvos_file, 'r', encoding='utf-8') as f:
        jogos_salvos = json.load(f)

    if _normalizar_ids(jogos_salvos):
        with open(salvos_file, 'w', encoding='utf-8') as f:
            json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)

    for jogo in jogos_salvos:
        if jogo['id'] == jogo_id:
            jogo['GH'] = gh
            jogo['GA'] = ga
            jogo['LP'] = lp if lp is not None else _calcular_lp(jogo, gh, ga)
            jogo['data_atualizado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(salvos_file, 'w', encoding='utf-8') as f:
                json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)

            try:
                gerar_pagina_salvos()
            except Exception as e:
                print(f"Aviso: falha ao gerar pagina de jogos salvos: {e}")

            print(f"OK Resultado atualizado: {jogo['HOME']} {gh} x {ga} {jogo['AWAY']} (LP: {lp})")
            return True

    print(f"Erro: Jogo ID {jogo_id} nao encontrado!")
    return False

def excluir_jogo(jogo_id):
    """Exclui um jogo salvo"""
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        print("Erro: Nenhum jogo salvo encontrado!")
        return False

    with open(salvos_file, 'r', encoding='utf-8') as f:
        jogos_salvos = json.load(f)

    # Normalizar IDs caso existam duplicados
    if _normalizar_ids(jogos_salvos):
        with open(salvos_file, 'w', encoding='utf-8') as f:
            json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)

    jogos_filtrados = [j for j in jogos_salvos if j.get('id') != jogo_id]
    if len(jogos_filtrados) == len(jogos_salvos):
        print(f"Erro: Jogo ID {jogo_id} nao encontrado!")
        return False

    with open(salvos_file, 'w', encoding='utf-8') as f:
        json.dump(jogos_filtrados, f, ensure_ascii=False, indent=2)

    try:
        gerar_pagina_salvos()
    except Exception as e:
        print(f"Aviso: falha ao gerar pagina de jogos salvos: {e}")

    print(f"OK Jogo excluido: ID {jogo_id}")
    return True

def gerar_pagina_salvos():
    """Gera página HTML com jogos salvos"""
    
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        jogos_salvos = []
    else:
        with open(salvos_file, 'r', encoding='utf-8') as f:
            jogos_salvos = json.load(f)

    # Normalizar IDs caso existam duplicados
    if _normalizar_ids(jogos_salvos):
        with open(salvos_file, 'w', encoding='utf-8') as f:
            json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
    
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Jogos Salvos - Análise</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }
        
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            padding: 15px 0;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            transition: background 0.3s;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.4);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 15px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .stat-box {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .stat-number {
            font-size: 1.8em;
            font-weight: bold;
            color: #1e3c72;
        }
        
        .stat-label {
            font-size: 0.85em;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .ligas-lucro-container {
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }

        .ligas-lucro-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        
        .liga-lucro-btn {
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            background-color: #f1f3f5;
            color: #333;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .liga-lucro-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .liga-lucro-btn.positivo {
            background-color: #b7f0c1;
            color: #1b4332;
        }
        
        .liga-lucro-btn.negativo {
            background-color: #f6b3b3;
            color: #7f1d1d;
        }
        
        .table-container {
            overflow-x: auto;
            padding: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }
        
        thead {
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #1e3c72;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e9ecef;
        }

        th.compact-col, td.compact-col {
            padding: 5px 4px;
        }
        
        tbody tr {
            transition: background-color 0.2s;
        }
        
        tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        .center-cell {
            text-align: center;
        }
        
        .liga-badge {
            display: inline-block;
            padding: 5px 12px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .team {
            font-weight: 500;
            color: white;
        }
        
        .odds {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 3px 6px;
            background: #e9ecef;
            border-radius: 4px;
            display: inline-block;
            min-width: 36px;
            text-align: center;
            font-size: 0.85em;
        }
        
        .calc-odd {
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
        }

        .confidence {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 3px 5px;
            border-radius: 4px;
            display: inline-block;
            min-width: 40px;
            text-align: center;
            font-size: 0.8em;
        }
        
        .value-bet {
            background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
            color: #000;
            font-weight: 900;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.3);
            border: 2px solid #00ff88;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .value-bet::before { content: "✓ "; margin-right: 3px; }
        
        .bad-bet {
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
            font-weight: 900;
            box-shadow: 0 0 15px rgba(255, 68, 68, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.2);
            border: 2px solid #ff4444;
        }
        
        .bad-bet::before { content: "✗ "; margin-right: 3px; }
        
        .neutral-bet {
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            font-weight: 700;
            box-shadow: 0 0 12px rgba(255, 170, 0, 0.5);
            border: 2px solid #ffaa00;
        }
        
        .neutral-bet::before { content: "◆ "; margin-right: 3px; }
        
        .gol-input {
            width: 42px;
            padding: 4px 6px;
            text-align: center;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 0.85em;
        }
        
        .gol-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-salvar-resultado {
            background: #28a745;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.8em;
        }
        
        .btn-salvar-resultado:hover {
            background: #218838;
        }

        .btn-excluir {
            background: #dc3545;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.8em;
            margin-left: 4px;
        }

        .gol-input {
            width: 42px;
            padding: 4px 6px;
            font-size: 0.85em;
            text-align: center;
        }

        .lp-input {
            width: 55px;
            padding: 4px 6px;
            font-size: 0.85em;
            text-align: center;
        }

        .btn-excluir:hover {
            background: #c82333;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
        }
        
        .no-games {
            text-align: center;
            padding: 60px;
            color: #6c757d;
            font-size: 1.2em;
        }
        .filters-container {
            background: white;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .filters-title {
            font-size: 1.1em;
            font-weight: 700;
            color: #1e3c72;
            margin-bottom: 15px;
        }
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            align-items: end;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .filter-label {
            font-size: 0.9em;
            font-weight: 600;
            color: #495057;
        }
        .filter-select {
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 0.95em;
            background: white;
            cursor: pointer;
        }
        .filter-select:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-limpar-filtros {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            height: fit-content;
        }
        .btn-limpar-filtros:hover {
            background: #5a6268;
        }

        /* Tema baseado em backtest_resumo_entradas */
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ecf0f1;
        }
        .container {
            background: transparent;
            box-shadow: none;
        }
        .header {
            background: rgba(0, 0, 0, 0.3);
            color: #00d4ff;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #00d4ff;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }
        .nav-links {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 12px 0 18px;
        }
        .nav-link {
            color: #00d4ff;
            background: rgba(0, 212, 255, 0.12);
            border: 1px solid rgba(0, 212, 255, 0.35);
        }
        .nav-link:hover {
            background: rgba(0, 212, 255, 0.25);
        }
        .stats, .filters-container, .table-container, .ligas-lucro-container {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 212, 255, 0.35);
            color: #ecf0f1;
        }
        .stat-box {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(0, 212, 255, 0.35);
        }
        .stat-number {
            color: #00d4ff;
        }
        .stat-label {
            color: #b0c4de;
        }
        .filter-select, .filter-range-inputs input {
            background: rgba(0, 0, 0, 0.35);
            color: #ecf0f1;
            border: 1px solid rgba(0, 212, 255, 0.35);
        }
        table {
            color: #ecf0f1;
        }
        thead {
            background: #0a5f7e;
            border-bottom: 2px solid #0a5f7e;
        }
        th {
            color: #00d4ff;
            border: 1px solid #0a5f7e;
        }
        td {
            border: 1px solid #333;
        }
        tbody tr:nth-child(odd) {
            background: rgba(0, 212, 255, 0.05);
        }
        tbody tr:hover {
            background: rgba(0, 212, 255, 0.15);
        }
        .liga-badge {
            background: rgba(0, 212, 255, 0.2);
            color: #00d4ff;
            border: 1px solid rgba(0, 212, 255, 0.35);
        }
        .odds, .calc-odd, .confidence {
            background: rgba(0, 0, 0, 0.35);
            color: #ecf0f1;
        }
        .btn, .btn-limpar-filtros {
            background: #00d4ff;
            color: #1a1a2e;
            border: 1px solid rgba(0, 212, 255, 0.35);
        }
        .footer {
            background: rgba(0, 0, 0, 0.3);
            color: #b0c4de;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⭐ Jogos Salvos para Análise</h1>
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
                <div class="stat-number" id="totalJogos">""" + str(len(jogos_salvos)) + """</div>
                <div class="stat-label">Jogos Salvos</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="totalResultados">""" + str(sum(1 for j in jogos_salvos if j.get('GH') is not None)) + """</div>
                <div class="stat-label">Resultados</div>
            </div>
        </div>
"""
    
    if not jogos_salvos:
        html_content += """
        <div class="no-games">
            <p>Nenhum jogo salvo ainda.</p>
            <p>Vá para a página de próximos jogos e clique em "Salvar" para adicionar jogos aqui.</p>
        </div>
"""
    else:
        # Coletar datas e ligas únicas para os filtros
        datas_unicas = sorted(set(j.get('DATA', '') for j in jogos_salvos if j.get('DATA')), reverse=True)
        ligas_unicas = sorted(set(j.get('LIGA', '') for j in jogos_salvos if j.get('LIGA')))
        
        html_content += """
        <div class="filters-container">
            <div class="filters-title">🔍 Filtros</div>
            <div class="filters-grid">
                <div class="filter-group">
                    <label class="filter-label">Data:</label>
                    <select id="filtroData" class="filter-select" multiple onchange="aplicarFiltros()">
"""
        for data in datas_unicas:
            html_content += f"""                        <option value="{data}">{data}</option>\n"""
        
        html_content += """                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">Liga:</label>
                    <select id="filtroLiga" class="filter-select" multiple onchange="aplicarFiltros()">
"""
        for liga in ligas_unicas:
            html_content += f"""                        <option value="{liga}">{liga}</option>\n"""
        
        html_content += """                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">DxG:</label>
                    <select id="filtroDxG" class="filter-select" multiple onchange="aplicarFiltros()">
                        <option value="FH">FH</option>
                        <option value="LH">LH</option>
                        <option value="EQ">EQ</option>
                        <option value="LA">LA</option>
                        <option value="FA">FA</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">Resultado:</label>
                    <select id="filtroResultado" class="filter-select" multiple onchange="aplicarFiltros()">
                        <option value="sem_resultado">Sem Resultado</option>
                        <option value="com_resultado">Com Resultado</option>
                    </select>
                </div>
                <div class="filter-group">
                    <button class="btn-limpar-filtros" onclick="limparFiltros()">Limpar Filtros</button>
                </div>
            </div>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>DATA</th>
                        <th>LIGA</th>
                        <th>HOME</th>
                        <th>AWAY</th>
                        <th class="compact-col">CASA</th>
                        <th class="compact-col">EMPATE</th>
                        <th class="compact-col">VISITANTE</th>
                        <th class="compact-col">xGH</th>
                        <th class="compact-col">xGA</th>
                        <th class="compact-col">DxG</th>
                        <th class="compact-col">CFG</th>
                        <th class="compact-col">ODD H CALC</th>
                        <th class="compact-col">ODD D CALC</th>
                        <th class="compact-col">ODD A CALC</th>
                        <th class="compact-col">GH</th>
                        <th class="compact-col">GA</th>
                        <th class="compact-col">L/P</th>
                        <th>AÇÃO</th>
                    </tr>
                </thead>
                <tbody id="tabelaJogos">
"""
        
        for jogo in jogos_salvos:
            jogo_id = jogo.get('id', 0)
            data = jogo.get('DATA', '-')
            liga = jogo.get('LIGA', '-')
            home = jogo.get('HOME', '-')
            away = jogo.get('AWAY', '-')
            b365h = jogo.get('B365H', '-')
            b365d = jogo.get('B365D', '-')
            b365a = jogo.get('B365A', '-')
            xgh = jogo.get('xGH', '-')
            xga = jogo.get('xGA', '-')
            cfxgh = jogo.get('CFxGH', None)
            cfxga = jogo.get('CFxGA', None)
            odd_h_calc = jogo.get('ODD_H_CALC', '-')
            odd_d_calc = jogo.get('ODD_D_CALC', '-')
            odd_a_calc = jogo.get('ODD_A_CALC', '-')
            gh = jogo.get('GH', '')
            ga = jogo.get('GA', '')
            lp = jogo.get('LP', '')
            
            # Formatação
            b365h_fmt = f"{float(b365h):.2f}" if b365h != '-' and b365h is not None else '-'
            b365d_fmt = f"{float(b365d):.2f}" if b365d != '-' and b365d is not None else '-'
            b365a_fmt = f"{float(b365a):.2f}" if b365a != '-' and b365a is not None else '-'
            xgh_fmt = f"{float(xgh):.2f}" if xgh != '-' and xgh is not None else '-'
            xga_fmt = f"{float(xga):.2f}" if xga != '-' and xga is not None else '-'
            dxg = _calcular_dxg(xgh, xga)
            cfg = _calcular_cfg(cfxgh, cfxga)
            cfg_fmt = _format_confidence(cfg)
            cfg_style = _confidence_style(cfg)
            odd_h_calc_fmt = f"{float(odd_h_calc):.2f}" if odd_h_calc != '-' and odd_h_calc is not None else '-'
            odd_d_calc_fmt = f"{float(odd_d_calc):.2f}" if odd_d_calc != '-' and odd_d_calc is not None else '-'
            odd_a_calc_fmt = f"{float(odd_a_calc):.2f}" if odd_a_calc != '-' and odd_a_calc is not None else '-'
            gh_value = gh if gh is not None and gh != '' else ''
            ga_value = ga if ga is not None and ga != '' else ''
            lp_value = f"{float(lp):.2f}" if lp is not None and lp != '' else ''

            odd_h_class = ""
            odd_d_class = ""
            odd_a_class = ""

            try:
                if b365h is not None and odd_h_calc is not None and b365h != '-' and odd_h_calc != '-':
                    if float(b365h) > float(odd_h_calc) * 1.10:
                        odd_h_class = "value-bet"
                    elif float(b365h) < float(odd_h_calc):
                        odd_h_class = "bad-bet"
                    else:
                        odd_h_class = "neutral-bet"
            except Exception:
                odd_h_class = ""

            try:
                if b365d is not None and odd_d_calc is not None and b365d != '-' and odd_d_calc != '-':
                    if float(b365d) > float(odd_d_calc) * 1.10:
                        odd_d_class = "value-bet"
                    elif float(b365d) < float(odd_d_calc):
                        odd_d_class = "bad-bet"
                    else:
                        odd_d_class = "neutral-bet"
            except Exception:
                odd_d_class = ""

            try:
                if b365a is not None and odd_a_calc is not None and b365a != '-' and odd_a_calc != '-':
                    if float(b365a) > float(odd_a_calc) * 1.10:
                        odd_a_class = "value-bet"
                    elif float(b365a) < float(odd_a_calc):
                        odd_a_class = "bad-bet"
                    else:
                        odd_a_class = "neutral-bet"
            except Exception:
                odd_a_class = ""
            
            html_content += f"""
                    <tr data-data="{data}" data-liga="{liga}" data-dxg="{dxg}">
                        <td>{data}</td>
                        <td><span class="liga-badge">{liga}</span></td>
                        <td class="team">{home}</td>
                        <td class="team">{away}</td>
                        <td class="center-cell compact-col"><span class="odds">{b365h_fmt}</span></td>
                        <td class="center-cell compact-col"><span class="odds">{b365d_fmt}</span></td>
                        <td class="center-cell compact-col"><span class="odds">{b365a_fmt}</span></td>
                        <td class="center-cell compact-col">{xgh_fmt}</td>
                        <td class="center-cell compact-col">{xga_fmt}</td>
                        <td class="center-cell compact-col"><strong>{dxg}</strong></td>
                        <td class="center-cell compact-col"><span class="confidence" style="{cfg_style}">{cfg_fmt}</span></td>
                        <td class="center-cell compact-col"><span class="calc-odd {odd_h_class}">{odd_h_calc_fmt}</span></td>
                        <td class="center-cell compact-col"><span class="calc-odd {odd_d_class}">{odd_d_calc_fmt}</span></td>
                        <td class="center-cell compact-col"><span class="calc-odd {odd_a_class}">{odd_a_calc_fmt}</span></td>
                        <td class="center-cell">
                            <input type="number" class="gol-input" id="gh_{jogo_id}" value="{gh_value}" min="0" max="20" step="1" inputmode="numeric" data-jogo-id="{jogo_id}" data-b365h="{b365h}" data-b365a="{b365a}" data-odd-h-calc="{odd_h_calc}" data-odd-a-calc="{odd_a_calc}" onchange="calcularLP(this)">
                        </td>
                        <td class="center-cell">
                            <input type="number" class="gol-input" id="ga_{jogo_id}" value="{ga_value}" min="0" max="20" step="1" inputmode="numeric" data-jogo-id="{jogo_id}" data-b365h="{b365h}" data-b365a="{b365a}" data-odd-h-calc="{odd_h_calc}" data-odd-a-calc="{odd_a_calc}" onchange="calcularLP(this)">
                        </td>
                        <td class="center-cell">
                            <input type="number" class="lp-input" id="lp_{jogo_id}" value="{lp_value}" step="0.01" inputmode="decimal">
                        </td>
                        <td class="center-cell">
                            <button class="btn-salvar-resultado" onclick="salvarResultado({jogo_id})">Salvar</button>
                            <button class="btn-excluir" onclick="excluirJogo({jogo_id})">Excluir</button>
                        </td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
"""
    
    html_content += """
        <div class="footer">
            <p>Jogos salvos para análise futura</p>
            <p><a href="proxima_rodada.html">← Voltar para Próximos Jogos</a></p>
        </div>
    </div>
    
    <script>
        function aplicarFiltros() {
            const filtroData = Array.from(document.getElementById('filtroData').selectedOptions).map(opt => opt.value);
            const filtroLiga = Array.from(document.getElementById('filtroLiga').selectedOptions).map(opt => opt.value);
            const filtroDxG = Array.from(document.getElementById('filtroDxG').selectedOptions).map(opt => opt.value);
            const filtroResultado = Array.from(document.getElementById('filtroResultado').selectedOptions).map(opt => opt.value);
            const linhas = document.querySelectorAll('#tabelaJogos tr');
            
            let jogosFiltrados = 0;
            let resultadosFiltrados = 0;
            
            linhas.forEach(linha => {
                const dataLinha = linha.getAttribute('data-data');
                const ligaLinha = linha.getAttribute('data-liga');
                const dxgLinha = linha.getAttribute('data-dxg');
                
                let mostrar = true;
                
                if (filtroData.length > 0 && !filtroData.includes(dataLinha)) {
                    mostrar = false;
                }
                
                if (filtroLiga.length > 0 && !filtroLiga.includes(ligaLinha)) {
                    mostrar = false;
                }
                
                // Filtro DxG
                if (filtroDxG.length > 0 && !filtroDxG.includes(dxgLinha)) {
                    mostrar = false;
                }
                
                // Filtro de resultado
                const jogoId = linha.querySelector('input[id^="gh_"]')?.dataset.jogoId;
                if (jogoId && filtroResultado.length > 0) {
                    const ghInput = document.getElementById('gh_' + jogoId);
                    const gaInput = document.getElementById('ga_' + jogoId);
                    const temResultado = ghInput && ghInput.value !== '' && gaInput && gaInput.value !== '';
                    
                    let resultadoMatch = false;
                    if (filtroResultado.includes('sem_resultado') && !temResultado) resultadoMatch = true;
                    if (filtroResultado.includes('com_resultado') && temResultado) resultadoMatch = true;
                    
                    if (!resultadoMatch) {
                        mostrar = false;
                    }
                }
                
                if (mostrar) {
                    linha.style.display = '';
                    jogosFiltrados++;
                    
                    // Verificar se tem resultado (GH preenchido)
                    if (jogoId) {
                        const ghInput = document.getElementById('gh_' + jogoId);
                        if (ghInput && ghInput.value !== '') {
                            resultadosFiltrados++;
                        }
                    }
                } else {
                    linha.style.display = 'none';
                }
            });
            
            // Atualizar contadores
            document.getElementById('totalJogos').textContent = jogosFiltrados;
            document.getElementById('totalResultados').textContent = resultadosFiltrados;
        }
        
        function limparFiltros() {
            document.getElementById('filtroData').selectedIndex = -1;
            document.getElementById('filtroLiga').selectedIndex = -1;
            document.getElementById('filtroDxG').selectedIndex = -1;
            document.getElementById('filtroResultado').selectedIndex = -1;
            aplicarFiltros();
        }

        function calcularLP(element) {
            const jogoId = element.dataset.jogoId;
            const b365h = parseFloat(element.dataset.b365h);
            const b365a = parseFloat(element.dataset.b365a);
            const oddHCalc = parseFloat(element.dataset.oddHCalc);
            const oddACalc = parseFloat(element.dataset.oddACalc);
            
            const ghInput = document.getElementById('gh_' + jogoId);
            const gaInput = document.getElementById('ga_' + jogoId);
            const lpInput = document.getElementById('lp_' + jogoId);
            
            const gh = ghInput.value === '' ? null : parseInt(ghInput.value, 10);
            const ga = gaInput.value === '' ? null : parseInt(gaInput.value, 10);
            
            // Se não preencheu ambos, não calcula
            if (gh === null || ga === null || isNaN(gh) || isNaN(ga)) {
                lpInput.value = '';
                return;
            }
            
            // Se alguma odd está faltando, não calcula
            if (!b365h || !b365a || !oddHCalc || !oddACalc || isNaN(b365h) || isNaN(b365a) || isNaN(oddHCalc) || isNaN(oddACalc)) {
                lpInput.value = '';
                return;
            }
            
            let lp = -1; // padrão: perda
            
            // Value bet com 10% de margem
            const valueHome = b365h > (oddHCalc * 1.1);
            const valueAway = b365a > (oddACalc * 1.1);
            
            if (gh > ga) {
                // Casa venceu
                if (valueHome) {
                    lp = (b365h - 1) * 0.955;  // Desconto de 4,5%
                } else {
                    lp = -1;
                }
            } else if (ga > gh) {
                // Visitante venceu
                if (valueAway) {
                    lp = (b365a - 1) * 0.955;  // Desconto de 4,5%
                } else {
                    lp = -1;
                }
            } else {
                // Empate
                lp = -1;
            }
            
            lpInput.value = lp.toFixed(2);
        }

        function salvarResultado(jogoId) {
            const gh = document.getElementById('gh_' + jogoId).value;
            const ga = document.getElementById('ga_' + jogoId).value;
            const lp = document.getElementById('lp_' + jogoId).value;
            
            if (gh === '' || ga === '') {
                alert('Por favor, preencha ambos os gols (GH e GA)');
                return;
            }

            const ghInt = parseInt(gh, 10);
            const gaInt = parseInt(ga, 10);
            const lpVal = (lp === '' ? null : parseFloat(lp));
            if (Number.isNaN(ghInt) || Number.isNaN(gaInt)) {
                alert('Digite apenas numeros inteiros para GH e GA');
                return;
            }
            if (lp !== '' && Number.isNaN(lpVal)) {
                alert('Digite um numero valido para L/P');
                return;
            }
            
            // Fazer requisição para salvar
            fetch('http://localhost:8000/api/atualizar_resultado', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: jogoId,
                    gh: ghInt,
                    ga: gaInt,
                    lp: lpVal
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Resultado salvo com sucesso!');
                    location.reload();
                } else {
                    alert('Erro ao salvar: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao salvar resultado. Verifique o console.');
            });
        }

        function excluirJogo(jogoId) {
            if (!confirm('Deseja excluir este jogo salvo?')) {
                return;
            }

            fetch('http://localhost:8000/api/excluir_jogo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: jogoId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Jogo excluido com sucesso!');
                    location.reload();
                } else {
                    alert('Erro ao excluir: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao excluir jogo. Verifique o console.');
            });
        }
    </script>
</body>
</html>
"""
    
    output_file = Path("fixtures/jogos_salvos.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"OK Pagina de jogos salvos gerada: {output_file}")

    # Gerar pagina de analise sempre que atualizar os jogos salvos
    try:
        gerar_pagina_analise()
    except Exception as e:
        print(f"Aviso: falha ao gerar pagina de analise: {e}")
    return True

def analisar_padroes_ia(dados_fornecidos=None):
    """Analisa padroes nos dados salvos com relatorio detalhado de odds, xG, estrategias, confianca e combinacoes
    
    Args:
        dados_fornecidos: Lista de jogos para analisar. Se None, lê do arquivo fixtures/backtest_acumulado.json
    """
    import sys
    
    def _estrategia_local(jogo):
        try:
            b365h = jogo.get('B365H', None)
            b365a = jogo.get('B365A', None)
            odd_h_calc = jogo.get('ODD_H_CALC', None)
            odd_a_calc = jogo.get('ODD_A_CALC', None)
            if b365h is None or b365a is None or odd_h_calc is None or odd_a_calc is None:
                return None
            b365h = float(b365h)
            b365a = float(b365a)
            odd_h_calc = float(odd_h_calc)
            odd_a_calc = float(odd_a_calc)
            if b365h > odd_h_calc * 1.1:
                return 'Back Home'
            if b365a > odd_a_calc * 1.1:
                return 'Back Away'
            return None
        except Exception:
            return None
    
    # Se dados foram fornecidos, usar eles; caso contrário, ler do arquivo de backtest
    if dados_fornecidos is not None:
        jogos_salvos = dados_fornecidos
        print(f"DEBUG: Usando dados fornecidos: {len(jogos_salvos)} jogos", file=sys.stderr)
    else:
        # Tentar ler do arquivo de backtest primeiro
        backtest_file = Path("fixtures/backtest_acumulado.json")
        if backtest_file.exists():
            print(f"DEBUG: Lendo do arquivo de backtest: {backtest_file}", file=sys.stderr)
            with open(backtest_file, 'r', encoding='utf-8') as f:
                jogos_salvos = json.load(f)
            print(f"DEBUG: Total de jogos lidos do backtest: {len(jogos_salvos)}", file=sys.stderr)
        else:
            # Fallback para arquivo antigo
            salvos_file = Path("fixtures/jogos_salvos.json")
            if not salvos_file.exists():
                print("DEBUG: Nenhum arquivo de dados encontrado", file=sys.stderr)
                return None
            
            print(f"DEBUG: Lendo do arquivo antigo: {salvos_file}", file=sys.stderr)
            with open(salvos_file, 'r', encoding='utf-8') as f:
                jogos_salvos = json.load(f)
            print(f"DEBUG: Total de jogos lidos do arquivo antigo: {len(jogos_salvos)}", file=sys.stderr)
    
    if not jogos_salvos:
        print("DEBUG: jogos_salvos está vazio", file=sys.stderr)
        return None
    
    # Separar jogos com resultados (aceita tanto maiúsculas quanto minúsculas)
    resultados = []
    for i, j in enumerate(jogos_salvos):
        # Verificar se tem resultados (GH/gc, GA/gv, LP/lp)
        gh = j.get('GH') if j.get('GH') is not None else j.get('gc')
        ga = j.get('GA') if j.get('GA') is not None else j.get('gv')
        lp = j.get('LP') if j.get('LP') is not None else j.get('lp')
        
        # Debug: mostrar valores para os primeiros 3 jogos
        if i < 3:
            print(f"DEBUG: Jogo {i}: GH={gh}, GA={ga}, LP={lp}, LP_type={type(lp)}", file=sys.stderr)
        
        # Converter LP para float se for string (pode vir com vírgula no formato brasileiro)
        if lp is not None and isinstance(lp, str):
            try:
                lp = float(lp.replace(',', '.'))
            except:
                lp = None
        
        if gh is not None and ga is not None and lp is not None:
            # Normalizar campos para maiúsculas para compatibilidade
            jogo_normalizado = j.copy()
            if 'gc' in j and 'GH' not in j:
                jogo_normalizado['GH'] = gh
            if 'gv' in j and 'GA' not in j:
                jogo_normalizado['GA'] = ga
            if 'lp' in j and 'LP' not in j:
                jogo_normalizado['LP'] = lp
            # Garantir que LP é um float
            if 'LP' in jogo_normalizado and isinstance(jogo_normalizado['LP'], str):
                try:
                    jogo_normalizado['LP'] = float(jogo_normalizado['LP'].replace(',', '.'))
                except:
                    pass
            # Normalizar outros campos comuns
            if 'casa' in j and 'CASA' not in j:
                jogo_normalizado['CASA'] = j['casa']
            if 'visitante' in j and 'VISITANTE' not in j:
                jogo_normalizado['VISITANTE'] = j['visitante']
            if 'liga' in j and 'LIGA' not in j:
                jogo_normalizado['LIGA'] = j['liga']
            if 'xg_casa' in j and 'xGH' not in j:
                jogo_normalizado['xGH'] = j['xg_casa']
            if 'xg_visitante' in j and 'xGA' not in j:
                jogo_normalizado['xGA'] = j['xg_visitante']
            if 'odd_casa' in j and 'B365H' not in j:
                jogo_normalizado['B365H'] = j['odd_casa']
            if 'odd_visitante' in j and 'B365A' not in j:
                jogo_normalizado['B365A'] = j['odd_visitante']
            
            # Calcular odds esperadas se não existirem (baseado em xG)
            if 'ODD_H_CALC' not in jogo_normalizado and 'xGH' in jogo_normalizado:
                xgh_val = float(jogo_normalizado.get('xGH', 1))
                xga_val = float(jogo_normalizado.get('xGA', 1))
                # Fórmula simplificada: odd_casa = 1 / (xGH / (xGH + xGA))
                if (xgh_val + xga_val) > 0:
                    prob_casa = xgh_val / (xgh_val + xga_val)
                    jogo_normalizado['ODD_H_CALC'] = 1 / prob_casa if prob_casa > 0 else 2.0
                    jogo_normalizado['ODD_A_CALC'] = 1 / (1 - prob_casa) if (1 - prob_casa) > 0 else 2.0
            
            # Adicionar CFxGH e CFxGA com valor padrão se não existirem
            if 'CFxGH' not in jogo_normalizado:
                jogo_normalizado['CFxGH'] = 0.5  # Valor neutro
            if 'CFxGA' not in jogo_normalizado:
                jogo_normalizado['CFxGA'] = 0.5  # Valor neutro
            
            resultados.append(jogo_normalizado)
    
    print(f"DEBUG: Jogos com resultados completos: {len(resultados)}", file=sys.stderr)
    
    if len(resultados) < 3:
        print(f"DEBUG: Retornando mensagem de poucos resultados: {len(resultados)}", file=sys.stderr)
        return {
            'resumo': f'Apenas {len(resultados)} resultado(s) disponivel(is). Minimo de 3 necessarios para analise.',
            'insights': [],
            'recomendacoes': []
        }
    
    print(f"DEBUG: Iniciando análise com {len(resultados)} jogos", file=sys.stderr)
    insights = []
    recomendacoes = []
    
    # SEÇÕES 1-4 REMOVIDAS - FOCO APENAS EM 4.5, 4.6 E 5 (ANÁLISE DE TENDÊNCIAS)
    
    # ==================== SECAO 4.5: ANALISE DE DxG POR LIGA ====================
    print("\nDEBUG: === INICIANDO SECAO 4.5: ANALISE DE DxG POR LIGA ===", file=sys.stderr)
    insights.append("═" * 80)
    insights.append("SECAO 4.5: ANALISE DE LUCRO, ROI E WINRATE POR DxG E LIGA")
    insights.append("═" * 80)
    
    # Dicionário para armazenar dados por liga e DxG
    analise_por_liga = {}
    
    # Categorias DxG
    categorias_dxg = ['FH', 'LH', 'EQ', 'LA', 'FA']
    
    # Processar cada jogo
    for jogo in resultados:
        try:
            liga = jogo.get('LIGA', 'Desconhecida')
            
            # Determinar DxG do jogo
            xgh = float(jogo.get('xGH', 0))
            xga = float(jogo.get('xGA', 0))
            diff = xgh - xga
            
            if diff > 1.0:
                dxg = 'FH'  # Forte Home
            elif 0.3 < diff <= 1.0:
                dxg = 'LH'  # Leve Home
            elif -0.3 <= diff <= 0.3:
                dxg = 'EQ'  # Equilibrado
            elif -1.0 <= diff < -0.3:
                dxg = 'LA'  # Leve Away
            else:
                dxg = 'FA'  # Forte Away
            
            # Inicializar estrutura se necessário
            if liga not in analise_por_liga:
                analise_por_liga[liga] = {}
            if dxg not in analise_por_liga[liga]:
                analise_por_liga[liga][dxg] = {'jogos': [], 'por_odd': {}}
            
            # Adicionar jogo
            analise_por_liga[liga][dxg]['jogos'].append(jogo)
            
            # Classificar por faixa de odd
            b365h = float(jogo.get('B365H', 0))
            b365a = float(jogo.get('B365A', 0))
            odd_h_calc = float(jogo.get('ODD_H_CALC', 1))
            odd_a_calc = float(jogo.get('ODD_A_CALC', 1))
            
            odd_apostada = None
            if b365h > odd_h_calc * 1.1:
                odd_apostada = b365h
            elif b365a > odd_a_calc * 1.1:
                odd_apostada = b365a
            
            if odd_apostada:
                # Determinar faixa de odd
                if odd_apostada < 1.5:
                    faixa_odd = '1.0-1.5'
                elif odd_apostada < 2.0:
                    faixa_odd = '1.5-2.0'
                elif odd_apostada < 3.0:
                    faixa_odd = '2.0-3.0'
                elif odd_apostada < 5.0:
                    faixa_odd = '3.0-5.0'
                else:
                    faixa_odd = '5.0+'
                
                if faixa_odd not in analise_por_liga[liga][dxg]['por_odd']:
                    analise_por_liga[liga][dxg]['por_odd'][faixa_odd] = []
                
                analise_por_liga[liga][dxg]['por_odd'][faixa_odd].append(jogo)
        
        except Exception as e:
            print(f"DEBUG: Erro ao processar jogo na seção DxG por liga: {e}", file=sys.stderr)
            pass
    
    # Gerar relatório por liga
    for liga in sorted(analise_por_liga.keys()):
        insights.append("")
        insights.append(f"  ▼ LIGA: {liga}")
        insights.append("  " + "─" * 76)
        
        dados_liga = analise_por_liga[liga]
        
        # Calcular total de entradas nesta liga para determinar threshold de relevância
        total_entradas_liga = sum(len(dados_liga[d]['jogos']) for d in categorias_dxg if d in dados_liga)
        # Threshold: mínimo 3 entradas OU 15% do total da liga (o que for maior)
        threshold_minimo = max(3, int(total_entradas_liga * 0.15))
        
        for dxg in categorias_dxg:
            if dxg not in dados_liga or not dados_liga[dxg]['jogos']:
                continue
            
            jogos_dxg = dados_liga[dxg]['jogos']
            apostas = len(jogos_dxg)
            
            # Verificar se este DxG tem entradas suficientes para ser relevante
            if apostas < threshold_minimo:
                # Mostrar como não relevante (silenciosamente omitir)
                continue
            
            lps = [float(j.get('LP', 0)) for j in jogos_dxg]
            acertos = sum(1 for lp in lps if lp > 0)
            total_lp = sum(lps)
            taxa = (acertos / apostas * 100) if apostas > 0 else 0
            roi = (total_lp / apostas * 100) if apostas > 0 else 0
            
            status = "★ LUCRATIVO" if total_lp > 0 and roi > 0 else "✗ PREJUIZO"
            insights.append(f"    {dxg}: {apostas} apostas | {acertos} acertos ({taxa:.1f}%) | L/P: {total_lp:+.2f} | ROI: {roi:+.1f}% | {status}")
            
            # Analisar melhores faixas de odd para este DxG
            melhor_faixa = None
            melhor_roi_faixa = -999
            
            for faixa_odd, jogos_faixa in sorted(dados_liga[dxg]['por_odd'].items()):
                if not jogos_faixa:
                    continue
                
                apostas_faixa = len(jogos_faixa)
                
                # Também aplicar threshold de relevância por faixa de odd
                threshold_faixa = max(2, int(apostas * 0.20))  # Mínimo 2 ou 20% do DxG
                if apostas_faixa < threshold_faixa:
                    continue  # Pular faixas com poucas entradas
                
                lps_faixa = [float(j.get('LP', 0)) for j in jogos_faixa]
                acertos_faixa = sum(1 for lp in lps_faixa if lp > 0)
                total_lp_faixa = sum(lps_faixa)
                taxa_faixa = (acertos_faixa / apostas_faixa * 100) if apostas_faixa > 0 else 0
                roi_faixa = (total_lp_faixa / apostas_faixa * 100) if apostas_faixa > 0 else 0
                
                status_faixa = "✓" if total_lp_faixa > 0 else "✗"
                insights.append(f"      Odds {faixa_odd}: {apostas_faixa} ap. | {acertos_faixa} acertos ({taxa_faixa:.1f}%) | L/P: {total_lp_faixa:+.2f} | ROI: {roi_faixa:+.1f}% {status_faixa}")
                
                if roi_faixa > melhor_roi_faixa and total_lp_faixa > 0:
                    melhor_roi_faixa = roi_faixa
                    melhor_faixa = faixa_odd
            
            # Adicionar recomendação se houver melhor faixa
            if melhor_faixa and melhor_roi_faixa > 0:
                insights.append(f"      ★ MELHOR FAIXA: {melhor_faixa} com ROI {melhor_roi_faixa:+.1f}%")
                recomendacoes.append(f"★ {liga} - {dxg}: Focar odds {melhor_faixa} (ROI {melhor_roi_faixa:+.1f}%)")
    
    insights.append("")
    
    # ==================== SECAO 4.6: ANALISE DE DxG POR MOMENTO DA TEMPORADA ====================
    print("\nDEBUG: === INICIANDO SECAO 4.6: ANALISE DE DxG POR MOMENTO DA TEMPORADA ===", file=sys.stderr)
    insights.append("═" * 80)
    insights.append("SECAO 4.6: ANALISE DE DxG POR MOMENTO DA TEMPORADA (INICIO, MEIO, FIM)")
    insights.append("═" * 80)
    
    # Para cada liga, dividir em 3 momentos: início (5 primeiros), meio, fim (5 últimos)
    for liga in sorted(analise_por_liga.keys()):
        dados_liga = analise_por_liga[liga]
        
        # Coletar todos os jogos desta liga com datas (ordenados)
        todos_jogos_liga = []
        for dxg in categorias_dxg:
            if dxg in dados_liga:
                todos_jogos_liga.extend(dados_liga[dxg]['jogos'])
        
        if not todos_jogos_liga:
            continue
        
        # Tentar ordenar por data (campo 'data' ou similar)
        try:
            todos_jogos_liga.sort(key=lambda x: x.get('data', ''))
        except:
            pass  # Se não houver data, manter ordem original
        
        total_jogos = len(todos_jogos_liga)
        
        # Definir os limites por percentual: 25% início, 50% meio, 25% fim
        inicio_count = max(2, int(total_jogos * 0.25))  # 25% das partidas
        fim_count = max(2, int(total_jogos * 0.25))     # 25% das partidas
        
        jogos_inicio = todos_jogos_liga[:inicio_count]
        jogos_fim = todos_jogos_liga[-fim_count:] if fim_count > 0 else []
        jogos_meio = todos_jogos_liga[inicio_count:total_jogos - fim_count] if fim_count > 0 else todos_jogos_liga[inicio_count:]
        
        # Análise por momento
        momentos = [
            ('INÍCIO', jogos_inicio),
            ('MEIO', jogos_meio),
            ('FIM', jogos_fim)
        ]
        
        insights.append("")
        insights.append(f"  ▼ LIGA: {liga} (Total: {total_jogos} jogos | Início: {len(jogos_inicio)} | Meio: {len(jogos_meio)} | Fim: {len(jogos_fim)})")
        insights.append("  " + "─" * 76)
        
        for momento_nome, jogos_momento in momentos:
            if not jogos_momento:
                continue
            
            insights.append(f"    └─ {momento_nome} ({len(jogos_momento)} jogos):")
            
            # Classificar os jogos deste momento por DxG
            dxg_momento = {}
            for jogo in jogos_momento:
                try:
                    xgh = float(jogo.get('xGH', 0))
                    xga = float(jogo.get('xGA', 0))
                    diff = xgh - xga
                    
                    if diff > 1.0:
                        dxg_class = 'FH'
                    elif 0.3 < diff <= 1.0:
                        dxg_class = 'LH'
                    elif -0.3 <= diff <= 0.3:
                        dxg_class = 'EQ'
                    elif -1.0 <= diff < -0.3:
                        dxg_class = 'LA'
                    else:
                        dxg_class = 'FA'
                    
                    if dxg_class not in dxg_momento:
                        dxg_momento[dxg_class] = []
                    dxg_momento[dxg_class].append(jogo)
                except:
                    pass
            
            # Mostrar estatísticas por DxG neste momento
            for dxg in categorias_dxg:
                if dxg not in dxg_momento or not dxg_momento[dxg]:
                    continue
                
                jogos_dxg = dxg_momento[dxg]
                apostas = len(jogos_dxg)
                
                # Aplicar relevância mínima também por momento
                if apostas < 2:
                    continue
                
                lps = [float(j.get('LP', 0)) for j in jogos_dxg]
                acertos = sum(1 for lp in lps if lp > 0)
                total_lp = sum(lps)
                taxa = (acertos / apostas * 100) if apostas > 0 else 0
                roi = (total_lp / apostas * 100) if apostas > 0 else 0
                
                status = "★" if total_lp > 0 and roi > 0 else "✗"
                insights.append(f"       {dxg}: {apostas} ap. | {acertos} acer. ({taxa:.1f}%) | L/P: {total_lp:+.2f} | ROI: {roi:+.1f}% {status}")
    
    insights.append("")
    
    # ==================== SECAO 5: ANALISE DE TENDENCIAS (4.5 + 4.6 + MULTI-TEMPORADA) ====================
    print("\nDEBUG: === INICIANDO SECAO 5: ANALISE DE TENDENCIAS ===", file=sys.stderr)
    insights.append("═" * 80)
    insights.append("SECAO 5: TENDENCIAS E RECOMENDACOES POR LIGA (INCLUINDO COMPARACAO MULTI-TEMPORADA)")
    insights.append("═" * 80)
    
    # ==================== SECAO 5.1: ANALISE COMPARATIVA ENTRE TEMPORADAS ====================
    print("\nDEBUG: === INICIANDO SECAO 5.1: COMPARACAO MULTI-TEMPORADA ===", file=sys.stderr)
    insights.append("")
    insights.append("─" * 80)
    insights.append("SECAO 5.1: COMPARACAO DE ESTRATEGIAS ENTRE TEMPORADAS")
    insights.append("─" * 80)
    
    # Estrutura: {liga: {temporada: {dxg: [jogos]}}}
    dados_por_temporada = {}
    
    # Agrupar jogos por liga, temporada e DxG
    for jogo in resultados:
        try:
            liga = jogo.get('LIGA', 'Desconhecida')
            temporada = jogo.get('temporada', '2024-25')  # Fallback para temporada padrão
            
            # Determinar DxG
            xgh = float(jogo.get('xGH', 0))
            xga = float(jogo.get('xGA', 0))
            diff = xgh - xga
            
            if diff > 1.0:
                dxg = 'FH'
            elif 0.3 < diff <= 1.0:
                dxg = 'LH'
            elif -0.3 <= diff <= 0.3:
                dxg = 'EQ'
            elif -1.0 <= diff < -0.3:
                dxg = 'LA'
            else:
                dxg = 'FA'
            
            # Inicializar estrutura
            if liga not in dados_por_temporada:
                dados_por_temporada[liga] = {}
            if temporada not in dados_por_temporada[liga]:
                dados_por_temporada[liga][temporada] = {}
            if dxg not in dados_por_temporada[liga][temporada]:
                dados_por_temporada[liga][temporada][dxg] = []
            
            dados_por_temporada[liga][temporada][dxg].append(jogo)
        except Exception as e:
            print(f"DEBUG: Erro ao agrupar por temporada: {e}", file=sys.stderr)
            pass
    
    # Analisar cada liga para comparar temporadas
    for liga in sorted(dados_por_temporada.keys()):
        temporadas_liga = dados_por_temporada[liga]
        
        # Só analisar se houver pelo menos 2 temporadas
        if len(temporadas_liga) < 2:
            continue
        
        insights.append("")
        insights.append(f"  ▼ LIGA: {liga} ({len(temporadas_liga)} temporadas)")
        insights.append("  " + "─" * 76)
        
        # Calcular ROI por DxG em cada temporada
        roi_por_dxg_temporada = {}  # {dxg: {temporada: roi}}
        
        for temporada in sorted(temporadas_liga.keys(), reverse=True):
            dados_temp = temporadas_liga[temporada]
            
            # Calcular total da temporada
            total_jogos_temp = sum(len(dados_temp[d]) for d in categorias_dxg if d in dados_temp)
            total_lp_temp = sum(float(j.get('LP', 0)) for d in categorias_dxg if d in dados_temp for j in dados_temp[d])
            roi_temp = (total_lp_temp / total_jogos_temp * 100) if total_jogos_temp > 0 else 0
            
            insights.append(f"    📅 TEMPORADA {temporada}: {total_jogos_temp} jogos | ROI: {roi_temp:+.1f}%")
            
            for dxg in categorias_dxg:
                if dxg not in dados_temp or not dados_temp[dxg]:
                    continue
                
                jogos_dxg = dados_temp[dxg]
                apostas = len(jogos_dxg)
                
                # Threshold mínimo de 2 jogos
                if apostas < 2:
                    continue
                
                lps = [float(j.get('LP', 0)) for j in jogos_dxg]
                acertos = sum(1 for lp in lps if lp > 0)
                total_lp = sum(lps)
                taxa = (acertos / apostas * 100) if apostas > 0 else 0
                roi = (total_lp / apostas * 100) if apostas > 0 else 0
                
                # Armazenar ROI para comparação
                if dxg not in roi_por_dxg_temporada:
                    roi_por_dxg_temporada[dxg] = {}
                roi_por_dxg_temporada[dxg][temporada] = roi
                
                status = "✓" if total_lp > 0 else "✗"
                insights.append(f"       {dxg}: {apostas} ap. | {acertos} acer. ({taxa:.1f}%) | ROI: {roi:+.1f}% {status}")
        
        # Análise de consistência entre temporadas
        insights.append("")
        insights.append("    🔍 ANALISE DE CONSISTENCIA ENTRE TEMPORADAS:")
        
        estrategias_consistentes = []
        estrategias_variacao_alta = []
        
        for dxg in categorias_dxg:
            if dxg not in roi_por_dxg_temporada:
                continue
            
            rois = list(roi_por_dxg_temporada[dxg].values())
            
            # Precisa de pelo menos 2 temporadas para comparar
            if len(rois) < 2:
                continue
            
            roi_medio = sum(rois) / len(rois)
            rois_positivos = sum(1 for r in rois if r > 0)
            taxa_sucesso = (rois_positivos / len(rois) * 100)
            
            # Calcular desvio padrão (variação)
            variancia = sum((r - roi_medio) ** 2 for r in rois) / len(rois)
            desvio = variancia ** 0.5
            
            # Classificar estratégia
            temporadas_str = ", ".join(sorted(roi_por_dxg_temporada[dxg].keys(), reverse=True))
            
            # Estratégia consistente: ROI médio positivo e baixa variação
            if roi_medio > 5 and desvio < 20:
                estrategias_consistentes.append({
                    'dxg': dxg,
                    'roi_medio': roi_medio,
                    'desvio': desvio,
                    'taxa_sucesso': taxa_sucesso,
                    'temporadas': temporadas_str
                })
                insights.append(f"       ★★ {dxg}: ESTRATEGIA CONSISTENTE - ROI médio {roi_medio:+.1f}% | Variação: {desvio:.1f}% | Lucro em {rois_positivos}/{len(rois)} temporadas")
                recomendacoes.append(f"★★ {liga} - {dxg}: Estratégia CONSISTENTE entre temporadas (ROI médio {roi_medio:+.1f}%)")
            
            # Estratégia com alta variação: pode ser afetada por fatores externos
            elif desvio > 40:
                estrategias_variacao_alta.append({
                    'dxg': dxg,
                    'roi_medio': roi_medio,
                    'desvio': desvio,
                    'temporadas': temporadas_str
                })
                insights.append(f"       ⚠ {dxg}: ALTA VARIACAO - ROI médio {roi_medio:+.1f}% | Variação: {desvio:.1f}% | Instável entre temporadas")
            
            # Estratégia lucrativa mas não muito estável
            elif roi_medio > 0:
                insights.append(f"       ★ {dxg}: LUCRATIVA - ROI médio {roi_medio:+.1f}% | Variação: {desvio:.1f}% | Lucro em {rois_positivos}/{len(rois)} temporadas")
            
            # Estratégia não lucrativa
            else:
                insights.append(f"       ✗ {dxg}: NÃO LUCRATIVA - ROI médio {roi_medio:+.1f}% | Evitar")
        
        # Resumo da liga
        if estrategias_consistentes:
            insights.append("")
            insights.append(f"    💎 MELHORES ESTRATEGIAS PARA {liga}:")
            for est in sorted(estrategias_consistentes, key=lambda x: x['roi_medio'], reverse=True)[:3]:
                insights.append(f"       1º {est['dxg']}: ROI {est['roi_medio']:+.1f}% (±{est['desvio']:.1f}%)")
        
        # ==================== ANALISE POR MOMENTO DA TEMPORADA (MULTI-TEMPORADA) ====================
        insights.append("")
        insights.append("    ⏱ ANALISE POR MOMENTO DA TEMPORADA (INICIO/MEIO/FIM):")
        
        # Estrutura: {dxg: {momento: {temporada: roi}}}
        roi_por_momento_temporada = {}
        
        for temporada in sorted(temporadas_liga.keys(), reverse=True):
            dados_temp = temporadas_liga[temporada]
            
            # Coletar todos os jogos desta temporada ordenados por data
            jogos_temp_todos = []
            for dxg in categorias_dxg:
                if dxg in dados_temp:
                    jogos_temp_todos.extend(dados_temp[dxg])
            
            if not jogos_temp_todos:
                continue
            
            # Ordenar por data
            try:
                jogos_temp_todos.sort(key=lambda x: x.get('data', ''))
            except:
                pass
            
            total_jogos_temp = len(jogos_temp_todos)
            
            # Dividir em início (25%), meio (50%), fim (25%)
            inicio_count = max(2, int(total_jogos_temp * 0.25))
            fim_count = max(2, int(total_jogos_temp * 0.25))
            
            jogos_inicio = jogos_temp_todos[:inicio_count]
            jogos_fim = jogos_temp_todos[-fim_count:] if fim_count > 0 else []
            jogos_meio = jogos_temp_todos[inicio_count:total_jogos_temp - fim_count] if fim_count > 0 else jogos_temp_todos[inicio_count:]
            
            momentos = {
                'INICIO': jogos_inicio,
                'MEIO': jogos_meio,
                'FIM': jogos_fim
            }
            
            # Analisar cada momento
            for momento_nome, jogos_momento in momentos.items():
                if not jogos_momento:
                    continue
                
                # Classificar por DxG
                for jogo in jogos_momento:
                    try:
                        xgh = float(jogo.get('xGH', 0))
                        xga = float(jogo.get('xGA', 0))
                        diff = xgh - xga
                        
                        if diff > 1.0:
                            dxg = 'FH'
                        elif 0.3 < diff <= 1.0:
                            dxg = 'LH'
                        elif -0.3 <= diff <= 0.3:
                            dxg = 'EQ'
                        elif -1.0 <= diff < -0.3:
                            dxg = 'LA'
                        else:
                            dxg = 'FA'
                        
                        # Inicializar estrutura
                        if dxg not in roi_por_momento_temporada:
                            roi_por_momento_temporada[dxg] = {}
                        if momento_nome not in roi_por_momento_temporada[dxg]:
                            roi_por_momento_temporada[dxg][momento_nome] = {}
                        
                        if temporada not in roi_por_momento_temporada[dxg][momento_nome]:
                            roi_por_momento_temporada[dxg][momento_nome][temporada] = []
                        
                        roi_por_momento_temporada[dxg][momento_nome][temporada].append(jogo)
                    except:
                        pass
        
        # Calcular ROI por momento e temporada
        for dxg in categorias_dxg:
            if dxg not in roi_por_momento_temporada:
                continue
            
            insights.append(f"       {dxg}:")
            
            for momento in ['INICIO', 'MEIO', 'FIM']:
                if momento not in roi_por_momento_temporada[dxg]:
                    continue
                
                temporadas_momento = roi_por_momento_temporada[dxg][momento]
                
                if len(temporadas_momento) < 2:
                    continue
                
                # Calcular ROI para cada temporada neste momento
                rois_momento = []
                temporadas_info = []
                
                for temp in sorted(temporadas_momento.keys(), reverse=True):
                    jogos = temporadas_momento[temp]
                    
                    if len(jogos) < 2:
                        continue
                    
                    lps = [float(j.get('LP', 0)) for j in jogos]
                    total_lp = sum(lps)
                    roi = (total_lp / len(jogos) * 100) if len(jogos) > 0 else 0
                    
                    rois_momento.append(roi)
                    temporadas_info.append(f"{temp}:{roi:+.1f}%")
                
                if len(rois_momento) < 2:
                    continue
                
                # Calcular estatísticas do momento
                roi_medio_momento = sum(rois_momento) / len(rois_momento)
                variancia_momento = sum((r - roi_medio_momento) ** 2 for r in rois_momento) / len(rois_momento)
                desvio_momento = variancia_momento ** 0.5
                rois_positivos_momento = sum(1 for r in rois_momento if r > 0)
                
                # Determinar se o momento é consistentemente bom
                if roi_medio_momento > 5 and desvio_momento < 15:
                    status = "★★ CONSISTENTE"
                    recomendacoes.append(f"★★ {liga} - {dxg} no {momento}: Altamente consistente (ROI médio {roi_medio_momento:+.1f}%)")
                elif roi_medio_momento > 0:
                    status = "★ LUCRATIVO"
                else:
                    status = "✗"
                
                temporadas_str = " | ".join(temporadas_info)
                insights.append(f"          {momento}: ROI médio {roi_medio_momento:+.1f}% (±{desvio_momento:.1f}%) | {rois_positivos_momento}/{len(rois_momento)} temp. lucrativas | {status}")
                insights.append(f"             [{temporadas_str}]")
        
        # Identificar padrões de momento que se repetem
        insights.append("")
        insights.append("    🎯 PADROES IDENTIFICADOS:")
        
        for dxg in categorias_dxg:
            if dxg not in roi_por_momento_temporada:
                continue
            
            # Calcular ROI médio por momento
            roi_por_momento = {}
            
            for momento in ['INICIO', 'MEIO', 'FIM']:
                if momento not in roi_por_momento_temporada[dxg]:
                    continue
                
                temporadas_momento = roi_por_momento_temporada[dxg][momento]
                
                if len(temporadas_momento) < 2:
                    continue
                
                rois = []
                for temp in temporadas_momento.keys():
                    jogos = temporadas_momento[temp]
                    if len(jogos) >= 2:
                        lps = [float(j.get('LP', 0)) for j in jogos]
                        roi = (sum(lps) / len(jogos) * 100)
                        rois.append(roi)
                
                if rois:
                    roi_por_momento[momento] = sum(rois) / len(rois)
            
            if len(roi_por_momento) >= 2:
                # Identificar melhor e pior momento
                melhor_momento = max(roi_por_momento, key=roi_por_momento.get)
                pior_momento = min(roi_por_momento, key=roi_por_momento.get)
                
                diferenca = roi_por_momento[melhor_momento] - roi_por_momento[pior_momento]
                
                if diferenca > 15:
                    insights.append(f"       • {dxg}: FORTE preferência pelo {melhor_momento} (ROI {roi_por_momento[melhor_momento]:+.1f}% vs {roi_por_momento[pior_momento]:+.1f}% no {pior_momento})")
                    recomendacoes.append(f"⏱ {liga} - {dxg}: Focar no {melhor_momento} da temporada (+{diferenca:.1f}% de diferença)")
                elif diferenca > 8:
                    insights.append(f"       • {dxg}: Melhor desempenho no {melhor_momento} (ROI {roi_por_momento[melhor_momento]:+.1f}%)")
    
    insights.append("")
    
    # ==================== SECAO 5.2: TENDENCIAS POR LIGA (ANÁLISE GERAL) ====================
    print("\nDEBUG: === INICIANDO SECAO 5.2: TENDENCIAS POR LIGA ===", file=sys.stderr)
    insights.append("─" * 80)
    insights.append("SECAO 5.2: TENDENCIAS GERAIS POR LIGA")
    insights.append("─" * 80)
    
    # Analisar tendências de cada liga baseado nas seções 4.5 e 4.6
    for liga in sorted(analise_por_liga.keys()):
        dados_liga = analise_por_liga[liga]
        
        # Coletar todos os jogos desta liga
        todos_jogos_liga = []
        for dxg in categorias_dxg:
            if dxg in dados_liga:
                todos_jogos_liga.extend(dados_liga[dxg]['jogos'])
        
        if not todos_jogos_liga:
            continue
        
        total_entradas_liga = len(todos_jogos_liga)
        total_lp_liga = sum(float(j.get('LP', 0)) for j in todos_jogos_liga)
        total_acertos_liga = sum(1 for j in todos_jogos_liga if float(j.get('LP', 0)) > 0)
        taxa_liga = (total_acertos_liga / total_entradas_liga * 100) if total_entradas_liga > 0 else 0
        roi_liga = (total_lp_liga / total_entradas_liga * 100) if total_entradas_liga > 0 else 0
        
        insights.append("")
        insights.append(f"  ▼ LIGA: {liga}")
        insights.append(f"     Total: {total_entradas_liga} apostas | Taxa: {taxa_liga:.1f}% | L/P: {total_lp_liga:+.2f} | ROI: {roi_liga:+.1f}%")
        
        # Analisar melhor DxG da liga
        melhor_dxg_roi = None
        melhor_dxg_valor = -999
        
        for dxg in categorias_dxg:
            if dxg not in dados_liga or not dados_liga[dxg]['jogos']:
                continue
            
            jogos_dxg = dados_liga[dxg]['jogos']
            apostas_dxg = len(jogos_dxg)
            
            # Threshold de relevância
            threshold_minimo = max(3, int(total_entradas_liga * 0.15))
            if apostas_dxg < threshold_minimo:
                continue
            
            lps_dxg = [float(j.get('LP', 0)) for j in jogos_dxg]
            total_lp_dxg = sum(lps_dxg)
            roi_dxg = (total_lp_dxg / apostas_dxg * 100) if apostas_dxg > 0 else 0
            
            if roi_dxg > melhor_dxg_valor:
                melhor_dxg_valor = roi_dxg
                melhor_dxg_roi = dxg
        
        # Analisar desempenho por momento da temporada
        try:
            todos_jogos_liga.sort(key=lambda x: x.get('data', ''))
        except:
            pass
        
        inicio_count = max(2, int(total_entradas_liga * 0.25))
        fim_count = max(2, int(total_entradas_liga * 0.25))
        
        jogos_inicio = todos_jogos_liga[:inicio_count]
        jogos_fim = todos_jogos_liga[-fim_count:] if fim_count > 0 else []
        
        # Calcular performance por momento
        desempenho_inicio = None
        desempenho_fim = None
        
        if jogos_inicio:
            lps_inicio = [float(j.get('LP', 0)) for j in jogos_inicio]
            roi_inicio = (sum(lps_inicio) / len(jogos_inicio) * 100) if len(jogos_inicio) > 0 else 0
            desempenho_inicio = roi_inicio
        
        if jogos_fim:
            lps_fim = [float(j.get('LP', 0)) for j in jogos_fim]
            roi_fim = (sum(lps_fim) / len(jogos_fim) * 100) if len(jogos_fim) > 0 else 0
            desempenho_fim = roi_fim
        
        # Gerar recomendações baseadas nas análises
        tendencias = []
        
        # Tendência 1: Melhor DxG
        if melhor_dxg_roi:
            tendencias.append(f"★ DxG {melhor_dxg_roi} é mais lucrativo (ROI {melhor_dxg_valor:+.1f}%)")
            recomendacoes.append(f"★ {liga}: Priorizar DxG {melhor_dxg_roi} (ROI {melhor_dxg_valor:+.1f}%)")
        
        # Tendência 2: Desempenho por momento
        if desempenho_inicio is not None and desempenho_fim is not None:
            if desempenho_inicio > desempenho_fim + 20:
                tendencias.append(f"★ TEMPORADA: Melhor desempenho no INÍCIO (ROI {desempenho_inicio:+.1f}% vs {desempenho_fim:+.1f}%)")
                recomendacoes.append(f"★ {liga}: Aumentar volume no INÍCIO da temporada")
            elif desempenho_fim > desempenho_inicio + 20:
                tendencias.append(f"★ TEMPORADA: Melhor desempenho no FIM (ROI {desempenho_fim:+.1f}% vs {desempenho_inicio:+.1f}%)")
                recomendacoes.append(f"★ {liga}: Aumentar volume no FIM da temporada")
            else:
                tendencias.append(f"★ TEMPORADA: Desempenho equilibrado entre início e fim")
        
        # Tendência 3: Saúde geral
        if roi_liga > 20:
            tendencias.append(f"★ SAUDE: Liga com ROI positivo e consistente (+{roi_liga:.1f}%)")
        elif roi_liga > 0:
            tendencias.append(f"★ SAUDE: Liga com ROI positivo mas marginal (+{roi_liga:.1f}%)")
        else:
            tendencias.append(f"★ SAUDE: Liga com ROI negativo ({roi_liga:.1f}%) - Revisar estratégia")
        
        for tendencia in tendencias:
            insights.append(f"     {tendencia}")
    
    insights.append("")
    
    # Resumo executivo
    total_jogos = len(resultados)
    total_lp = sum(float(j.get('LP', 0)) for j in resultados)
    total_wins = sum(1 for j in resultados if float(j.get('LP', 0)) > 0)
    taxa_geral = (total_wins / total_jogos * 100) if total_jogos > 0 else 0
    roi_geral = (total_lp / total_jogos * 100) if total_jogos > 0 else 0
    
    resumo = f"ANALISE COMPLETA: {total_jogos} resultados | Taxa Geral: {taxa_geral:.1f}% | L/P Total: {total_lp:+.2f} | ROI Geral: {roi_geral:+.1f}%"
    
    print(f"\nDEBUG: === ANALISE CONCLUIDA ===", file=sys.stderr)
    print(f"DEBUG: Resumo: {resumo}", file=sys.stderr)
    print(f"DEBUG: Total de insights: {len(insights)}", file=sys.stderr)
    print(f"DEBUG: Total de recomendações: {len(recomendacoes)}", file=sys.stderr)
    
    return {
        'resumo': resumo,
        'insights': insights,
        'recomendacoes': recomendacoes
    }

def gerar_pagina_analise():
    """Gera pagina HTML com analise dos jogos salvos"""
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        jogos_salvos = []
    else:
        with open(salvos_file, 'r', encoding='utf-8') as f:
            jogos_salvos = json.load(f)

    # Normalizar IDs caso existam duplicados
    if _normalizar_ids(jogos_salvos):
        with open(salvos_file, 'w', encoding='utf-8') as f:
            json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)

    resultados = [j for j in jogos_salvos if j.get('GH') is not None and j.get('GA') is not None]
    lp_values = [j.get('LP') for j in resultados if j.get('LP') is not None]
    wins = sum(1 for v in lp_values if v is not None and v > 0)
    losses = sum(1 for v in lp_values if v is not None and v <= 0)
    total_lp = sum(v for v in lp_values if v is not None)
    avg_lp = (total_lp / len(lp_values)) if lp_values else 0
    hit_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0

    def _estrategia(jogo):
        try:
            b365h = jogo.get('B365H', None)
            b365a = jogo.get('B365A', None)
            odd_h_calc = jogo.get('ODD_H_CALC', None)
            odd_a_calc = jogo.get('ODD_A_CALC', None)
            if b365h is None or b365a is None or odd_h_calc is None or odd_a_calc is None:
                return None
            b365h = float(b365h)
            b365a = float(b365a)
            odd_h_calc = float(odd_h_calc)
            odd_a_calc = float(odd_a_calc)
            if b365h > odd_h_calc * 1.1:
                return "back_home"
            if b365a > odd_a_calc * 1.1:
                return "back_away"
            return None
        except Exception:
            return None

    home_lp = []
    away_lp = []
    for j in resultados:
        estrategia = _estrategia(j)
        lp = j.get('LP')
        if lp is None:
            continue
        if estrategia == "back_home":
            home_lp.append(lp)
        elif estrategia == "back_away":
            away_lp.append(lp)

    def _stats(vals):
        v = [x for x in vals if x is not None]
        w = sum(1 for x in v if x > 0)
        l = sum(1 for x in v if x <= 0)
        total = sum(v) if v else 0
        avg = (total / len(v)) if v else 0
        hit = (w / (w + l)) * 100 if (w + l) > 0 else 0
        return len(v), w, l, total, avg, hit

    home_count, home_w, home_l, home_total, home_avg, home_hit = _stats(home_lp)
    away_count, away_w, away_l, away_total, away_avg, away_hit = _stats(away_lp)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Analise de Jogos Salvos</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
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
        .ai-panel {{
            background: #ffffff;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            margin: 20px;
            padding: 15px 20px;
        }}
        .ai-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }}
        .ai-title {{
            font-weight: 700;
            color: #1e3c72;
        }}
        .ai-toggle {{
            background: #2a5298;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .ai-content {{
            margin-top: 12px;
            color: #495057;
            font-size: 0.95em;
            display: none;
        }}
        .ai-start-btn {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .ai-start-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        }}
        .ai-start-btn:active {{
            transform: translateY(0);
        }}
        .ai-loading {{
            text-align: center;
            padding: 20px;
            color: #1e3c72;
            font-weight: 600;
            font-size: 1.1em;
        }}
        .ai-results {{
            margin-top: 20px;
        }}
        .ai-resumo {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 600;
            font-size: 1.05em;
        }}
        .ai-insights {{
            background: #f0f7ff;
            border-left: 4px solid #0066cc;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        .ai-insights-title {{
            font-weight: 700;
            color: #0066cc;
            margin-bottom: 10px;
        }}
        .ai-insight-item {{
            padding: 8px 0;
            border-bottom: 1px solid #ddd;
            color: #333;
            font-family: 'Courier New', monospace;
            white-space: pre;
            line-height: 1.6;
        }}
        .ai-insight-item:last-child {{
            border-bottom: none;
        }}
        .ai-recomendacoes {{
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            padding: 15px 20px;
            border-radius: 8px;
        }}
        .ai-recomendacoes-title {{
            font-weight: 700;
            color: #ff9800;
            margin-bottom: 10px;
        }}
        .ai-recomendacao-item {{
            padding: 8px 0;
            border-bottom: 1px solid #ddd;
            color: #333;
            font-family: 'Courier New', monospace;
            white-space: pre;
            line-height: 1.6;
        }}
        .ai-recomendacao-item:last-child {{
            border-bottom: none;
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
        .stat-number {{ font-size: 1.8em; font-weight: bold; color: #1e3c72; }}
        .stat-label {{ font-size: 0.85em; color: #6c757d; margin-top: 5px; }}
        .ligas-lucro-container {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }}
        .ligas-lucro-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }}
        .liga-lucro-btn {{
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            background-color: #f1f3f5;
            color: #333;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            cursor: default;
        }}
        .liga-lucro-btn.positivo {{
            background-color: #b7f0c1;
            color: #1b4332;
        }}
        .liga-lucro-btn.negativo {{
            background-color: #f6b3b3;
            color: #7f1d1d;
        }}
        .table-container {{ overflow-x: auto; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 0.95em; }}
        thead {{ background: #f8f9fa; border-bottom: 2px solid #e9ecef; }}
        th {{ padding: 12px; text-align: left; font-weight: 600; color: #1e3c72; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e9ecef; font-size: 0.75em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        th.entrada-col {{ width: 80px; }}
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
        .value-bet::before {{ content: "✓ "; margin-right: 3px; }}
        .bad-bet {{
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
            font-weight: 900;
            box-shadow: 0 0 15px rgba(255, 68, 68, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.2);
            border: 2px solid #ff4444;
        }}
        .bad-bet::before {{ content: "✗ "; margin-right: 3px; }}
        .neutral-bet {{
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            font-weight: 700;
            box-shadow: 0 0 12px rgba(255, 170, 0, 0.5);
            border: 2px solid #ffaa00;
        }}
        .neutral-bet::before {{ content: "◆ "; margin-right: 3px; }}
        .center-cell {{ text-align: center; font-size: 0.85em; }}
        .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #6c757d; }}
        .filters-container {{
            background: white;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .filters-title {{
            font-size: 1.1em;
            font-weight: 700;
            color: #1e3c72;
            margin-bottom: 15px;
        }}
        .filters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(136px, 1fr));
            gap: 15px;
            align-items: end;
        }}
        .filter-range-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .filter-range-inputs {{
            display: flex;
            gap: 5px;
            align-items: center;
        }}
        .filter-range-inputs input {{
            padding: 6px 8px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 0.9em;
            width: 60px;
        }}
        .filter-range-inputs input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .filter-range-separator {{
            font-weight: bold;
            color: #495057;
        }}
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .filter-label {{
            font-size: 0.9em;
            font-weight: 600;
            color: #495057;
        }}
        .filter-select {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 0.95em;
            background: white;
            cursor: pointer;
            min-height: 38px;
        }}
        .filter-select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .btn-limpar-filtros {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            height: fit-content;
        }}
        .btn-limpar-filtros:hover {{
            background: #5a6268;
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
        .ai-panel, .filters-container, .table-container, .stats, .ligas-lucro-container {{
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
        .calc-odd, .confidence {{
            background: rgba(0, 0, 0, 0.35);
            color: #ecf0f1;
        }}
        .ai-toggle, .ai-start-btn {{
            background: #00d4ff;
            color: #1a1a2e;
            border: 1px solid rgba(0, 212, 255, 0.35);
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
            <h1>📊 Analise dos Jogos Salvos</h1>
            <div class="nav-links">
                <a href="http://localhost:8000/proxima_rodada.html" class="nav-link">Próxima Rodada</a>
                <a href="http://localhost:8000/jogos_salvos.html" class="nav-link">Jogos Salvos</a>
                <a href="http://localhost:8000/analise_salvos.html" class="nav-link">Análise Salvos</a>
                <a href="http://localhost:5001/backtest.html" class="nav-link">Backtest</a>
                <a href="http://localhost:5001/backtest_salvos.html" class="nav-link">Backtests Salvos</a>
                <a href="http://localhost:5001/backtest_resumo_entradas.html" class="nav-link">Resumo Entradas</a>
            </div>
        </div>
        <div class="ai-panel">
            <div class="ai-header">
                <div class="ai-title">Analise de padroes por IA</div>
                <button class="ai-toggle" onclick="toggleAI()">Mostrar</button>
            </div>
            <div id="aiContent" class="ai-content">
                <button id="iniciarBtn" class="ai-start-btn" onclick="iniciarAnalise()">INICIAR ANALISE</button>
                <div id="aiLoading" class="ai-loading" style="display: none;">
                    Analisando dados...
                </div>
                <div id="aiResults" class="ai-results" style="display: none;">
                    <div id="aiResumo" class="ai-resumo"></div>
                    <div id="aiInsights" class="ai-insights"></div>
                    <div id="aiRecomendacoes" class="ai-recomendacoes"></div>
                </div>
            </div>
        </div>
"""

    # Coletar datas, ligas e DxGs únicos para os filtros
    datas_unicas = sorted(set(j.get('DATA', '') for j in resultados if j.get('DATA')), reverse=True)
    ligas_unicas = sorted(set(j.get('LIGA', '') for j in resultados if j.get('LIGA')))
    
    html_content += """
        <div class="filters-container">
            <div class="filters-title">🔍 Filtros</div>
            <div class="filters-grid">
                <div class="filter-group">
                    <label class="filter-label">Data:</label>
                    <select id="filtroData" class="filter-select" multiple onchange="aplicarFiltros()">
"""
    for data in datas_unicas:
        html_content += f"""                        <option value="{data}">{data}</option>\n"""
    
    html_content += """                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">Liga:</label>
                    <select id="filtroLiga" class="filter-select" multiple onchange="aplicarFiltros()">
"""
    for liga in ligas_unicas:
        html_content += f"""                        <option value="{liga}">{liga}</option>\n"""
    
    html_content += """                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">DxG:</label>
                    <select id="filtroDxG" class="filter-select" multiple onchange="aplicarFiltros()">
                        <option value="FH">FH</option>
                        <option value="LH">LH</option>
                        <option value="EQ">EQ</option>
                        <option value="LA">LA</option>
                        <option value="FA">FA</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">Entrada:</label>
                    <select id="filtroEntrada" class="filter-select" multiple onchange="aplicarFiltros()">
                        <option value="HOME">HOME</option>
                        <option value="AWAY">AWAY</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">L/P:</label>
                    <select id="filtroLP" class="filter-select" multiple onchange="aplicarFiltros()">
                        <option value="positivo">Positivo</option>
                        <option value="negativo">Negativo</option>
                    </select>
                </div>
                <div class="filter-range-group">
                    <label class="filter-label">ODD CASA:</label>
                    <div class="filter-range-inputs">
                        <input type="number" id="oddCasaMin" placeholder="Min" step="0.01" onchange="aplicarFiltros()">
                        <span class="filter-range-separator">-</span>
                        <input type="number" id="oddCasaMax" placeholder="Max" step="0.01" onchange="aplicarFiltros()">
                    </div>
                </div>
                <div class="filter-range-group">
                    <label class="filter-label">ODD VISIT:</label>
                    <div class="filter-range-inputs">
                        <input type="number" id="oddVisitMin" placeholder="Min" step="0.01" onchange="aplicarFiltros()">
                        <span class="filter-range-separator">-</span>
                        <input type="number" id="oddVisitMax" placeholder="Max" step="0.01" onchange="aplicarFiltros()">
                    </div>
                </div>
                <div class="filter-group">
                    <button class="btn-limpar-filtros" onclick="limparFiltros()">Limpar Filtros</button>
                </div>
            </div>
        </div>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number" id="winRate">-</div>
                <div class="stat-label">Win Rate (%)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="roi">-</div>
                <div class="stat-label">ROI (%)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="totalLucro">-</div>
                <div class="stat-label">Total de Lucro</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="totalFiltrados">0</div>
                <div class="stat-label">Jogos Filtrados</div>
            </div>
        </div>
        <div class="ligas-lucro-container">
            <div class="ligas-lucro-row" id="ligasLucroRow1"></div>
            <div class="ligas-lucro-row" id="ligasLucroRow2"></div>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>DATA</th>
                        <th>LIGA</th>
                        <th>HOME</th>
                        <th>AWAY</th>
                        <th class="center-cell">GH</th>
                        <th class="center-cell">GA</th>
                        <th class="center-cell">ODD CASA</th>
                        <th class="center-cell">ODD VISIT</th>
                        <th class="center-cell">CFG</th>
                        <th class="center-cell">DxG</th>
                        <th class="center-cell">xGH</th>
                        <th class="center-cell">xGA</th>
                        <th class="entrada-col">ENTRADA</th>
                        <th class="center-cell">L/P</th>
                    </tr>
                </thead>
                <tbody id="tabelaResultados">
"""

    for jogo in resultados:
        data = jogo.get('DATA', '-')
        liga = jogo.get('LIGA', '-')
        home = jogo.get('HOME', '-')
        away = jogo.get('AWAY', '-')
        gh = jogo.get('GH', '')
        ga = jogo.get('GA', '')
        b365h = jogo.get('B365H', None)
        b365a = jogo.get('B365A', None)
        cfxgh = jogo.get('CFxGH', None)
        cfxga = jogo.get('CFxGA', None)
        xgh = jogo.get('xGH', None)
        xga = jogo.get('xGA', None)
        lp = jogo.get('LP', None)
        back = jogo.get('BACK', '')

        b365h_fmt = f"{float(b365h):.2f}" if b365h is not None else '-'
        b365a_fmt = f"{float(b365a):.2f}" if b365a is not None else '-'
        cfg = _calcular_cfg(cfxgh, cfxga)
        cfg_fmt = _format_confidence(cfg)
        cfg_style = _confidence_style(cfg)
        dxg = _calcular_dxg(xgh, xga)
        xgh_fmt = f"{float(xgh):.2f}" if xgh is not None else '-'
        xga_fmt = f"{float(xga):.2f}" if xga is not None else '-'
        lp_fmt = f"{float(lp):.2f}" if lp is not None else '-'
        
        # Determinar tipo de entrada e cor baseada em L/P
        entrada_text = ''
        entrada_style = ''
        if back:
            lp_value = float(lp) if lp is not None else 0
            if back.upper() == 'HOME':
                entrada_text = 'HOME'
                entrada_style = 'background-color: #28a745; color: white;' if lp_value > 0 else 'background-color: #dc3545; color: white;'
            elif back.upper() == 'AWAY':
                entrada_text = 'AWAY'
                entrada_style = 'background-color: #007bff; color: white;' if lp_value > 0 else 'background-color: #dc3545; color: white;'

        lp_status = 'positivo' if (lp is not None and float(lp) > 0) else ('negativo' if (lp is not None and float(lp) <= 0) else '')
        b365h_num = float(b365h) if b365h is not None and b365h != '-' else 0
        b365a_num = float(b365a) if b365a is not None and b365a != '-' else 0
        
        html_content += f"""
                    <tr data-data="{data}" data-liga="{liga}" data-dxg="{dxg}" data-entrada="{entrada_text}" data-lp="{lp_status}" data-odds-casa="{b365h_num}" data-odds-visit="{b365a_num}">
                        <td>{data}</td>
                        <td>{liga}</td>
                        <td>{home}</td>
                        <td>{away}</td>
                        <td class="center-cell">{gh if gh is not None else ''}</td>
                        <td class="center-cell">{ga if ga is not None else ''}</td>
                        <td class="center-cell">{b365h_fmt}</td>
                        <td class="center-cell">{b365a_fmt}</td>
                        <td class="center-cell"><span class="confidence" style="{cfg_style}">{cfg_fmt}</span></td>
                        <td class="center-cell"><strong>{dxg}</strong></td>
                        <td class="center-cell">{xgh_fmt}</td>
                        <td class="center-cell">{xga_fmt}</td>
                        <td class="center-cell"><span class="confidence" style="{entrada_style}">{entrada_text}</span></td>
                        <td class="center-cell">{lp_fmt}</td>
                    </tr>
"""

    html_content += """
                </tbody>
            </table>
        </div>
        <div class="footer">
            <p>Analise baseada nos jogos salvos</p>
        </div>
    </div>
    <script>
        function aplicarFiltros() {
            const filtroDataEl = document.getElementById('filtroData');
            const filtroLigaEl = document.getElementById('filtroLiga');
            const filtroDxGEl = document.getElementById('filtroDxG');
            const filtroEntradaEl = document.getElementById('filtroEntrada');
            const filtroLPEl = document.getElementById('filtroLP');
            
            const filtroData = Array.from(filtroDataEl.selectedOptions).map(opt => opt.value);
            const filtroLiga = Array.from(filtroLigaEl.selectedOptions).map(opt => opt.value);
            const filtroDxG = Array.from(filtroDxGEl.selectedOptions).map(opt => opt.value);
            const filtroEntrada = Array.from(filtroEntradaEl.selectedOptions).map(opt => opt.value);
            const filtroLP = Array.from(filtroLPEl.selectedOptions).map(opt => opt.value);
            
            const oddCasaMin = parseFloat(document.getElementById('oddCasaMin').value) || 0;
            const oddCasaMax = parseFloat(document.getElementById('oddCasaMax').value) || Infinity;
            const oddVisitMin = parseFloat(document.getElementById('oddVisitMin').value) || 0;
            const oddVisitMax = parseFloat(document.getElementById('oddVisitMax').value) || Infinity;
            
            const linhas = document.querySelectorAll('#tabelaResultados tr');
            
            let jogosFiltrados = 0;
            let acertos = 0;
            let totalLP = 0;
            const ligasLucro = {}; // Objeto para armazenar lucro por liga
            
            linhas.forEach(linha => {
                const dataLinha = linha.getAttribute('data-data');
                const ligaLinha = linha.getAttribute('data-liga');
                const dxgLinha = linha.getAttribute('data-dxg');
                const entradaLinha = linha.getAttribute('data-entrada');
                const lpLinha = linha.getAttribute('data-lp');
                const oddsCasaLinha = parseFloat(linha.getAttribute('data-odds-casa')) || 0;
                const oddsVisitLinha = parseFloat(linha.getAttribute('data-odds-visit')) || 0;
                
                let mostrar = true;
                
                if (filtroData.length > 0 && !filtroData.includes(dataLinha)) {
                    mostrar = false;
                }
                
                if (filtroLiga.length > 0 && !filtroLiga.includes(ligaLinha)) {
                    mostrar = false;
                }
                
                if (filtroDxG.length > 0 && !filtroDxG.includes(dxgLinha)) {
                    mostrar = false;
                }
                
                if (filtroEntrada.length > 0 && !filtroEntrada.includes(entradaLinha)) {
                    mostrar = false;
                }
                
                if (filtroLP.length > 0 && !filtroLP.includes(lpLinha)) {
                    mostrar = false;
                }
                
                if (oddsCasaLinha > 0 && (oddsCasaLinha < oddCasaMin || oddsCasaLinha > oddCasaMax)) {
                    mostrar = false;
                }
                
                if (oddsVisitLinha > 0 && (oddsVisitLinha < oddVisitMin || oddsVisitLinha > oddVisitMax)) {
                    mostrar = false;
                }
                
                if (mostrar) {
                    linha.style.display = '';
                    jogosFiltrados++;
                    
                    // Calcular estatísticas
                    const lpCell = linha.cells[13]; // Coluna L/P
                    if (lpCell) {
                        const lpValue = parseFloat(lpCell.textContent);
                        if (!isNaN(lpValue)) {
                            totalLP += lpValue;
                            if (lpValue > 0) {
                                acertos++;
                            }
                            
                            // Acumular lucro por liga
                            if (!ligasLucro[ligaLinha]) {
                                ligasLucro[ligaLinha] = 0;
                            }
                            ligasLucro[ligaLinha] += lpValue;
                        }
                    }
                } else {
                    linha.style.display = 'none';
                }
            });
            
            // Atualizar estatísticas
            const winRate = jogosFiltrados > 0 ? (acertos / jogosFiltrados * 100).toFixed(1) : '-';
            const roi = jogosFiltrados > 0 ? (totalLP / jogosFiltrados * 100).toFixed(1) : '-';
            const totalLucroFormatado = jogosFiltrados > 0 ? (totalLP >= 0 ? '+' : '') + totalLP.toFixed(2) : '-';
            
            document.getElementById('winRate').textContent = winRate;
            document.getElementById('roi').textContent = roi;
            document.getElementById('totalLucro').textContent = totalLucroFormatado;
            document.getElementById('totalFiltrados').textContent = jogosFiltrados;
            
            // Colorir ROI baseado no valor
            const roiElement = document.getElementById('roi');
            if (roi !== '-') {
                const roiValue = parseFloat(roi);
                if (roiValue > 0) {
                    roiElement.style.color = '#28a745';
                } else if (roiValue < 0) {
                    roiElement.style.color = '#dc3545';
                } else {
                    roiElement.style.color = '#6c757d';
                }
            } else {
                roiElement.style.color = '#6c757d';
            }
            
            // Colorir Total de Lucro baseado no valor
            const totalLucroElement = document.getElementById('totalLucro');
            if (totalLucroFormatado !== '-') {
                if (totalLP > 0) {
                    totalLucroElement.style.color = '#28a745';
                } else if (totalLP < 0) {
                    totalLucroElement.style.color = '#dc3545';
                } else {
                    totalLucroElement.style.color = '#6c757d';
                }
            } else {
                totalLucroElement.style.color = '#6c757d';
            }
            
            // Colorir WinRate baseado no valor
            const winRateElement = document.getElementById('winRate');
            if (winRate !== '-') {
                const winRateValue = parseFloat(winRate);
                if (winRateValue >= 60) {
                    winRateElement.style.color = '#28a745';
                } else if (winRateValue >= 50) {
                    winRateElement.style.color = '#ffc107';
                } else {
                    winRateElement.style.color = '#dc3545';
                }
            } else {
                winRateElement.style.color = '#6c757d';
            }
            
            // Renderizar botões de ligas com lucro
            const ligasLucroRow1 = document.getElementById('ligasLucroRow1');
            const ligasLucroRow2 = document.getElementById('ligasLucroRow2');
            ligasLucroRow1.innerHTML = '';
            ligasLucroRow2.innerHTML = '';
            
            // Ordenar ligas alfabeticamente
            const ligasOrdenadas = Object.keys(ligasLucro).sort();
            
            const renderizarBotoes = (lista, container) => {
                lista.forEach(liga => {
                    const lucroLiga = ligasLucro[liga];
                    const lucroFormatado = (lucroLiga >= 0 ? '+' : '') + lucroLiga.toFixed(2);
                    const classe = lucroLiga > 0 ? 'positivo' : 'negativo';
                    
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = `liga-lucro-btn ${classe}`;
                    btn.textContent = `${liga}: ${lucroFormatado}`;
                    
                    container.appendChild(btn);
                });
            };
            
            if (ligasOrdenadas.length > 18) {
                const metade = Math.ceil(ligasOrdenadas.length / 2);
                const ligasLinha1 = ligasOrdenadas.slice(0, metade);
                const ligasLinha2 = ligasOrdenadas.slice(metade);
                renderizarBotoes(ligasLinha1, ligasLucroRow1);
                renderizarBotoes(ligasLinha2, ligasLucroRow2);
                ligasLucroRow2.style.display = 'flex';
            } else {
                renderizarBotoes(ligasOrdenadas, ligasLucroRow1);
                ligasLucroRow2.style.display = 'none';
            }
        }
        
        function limparFiltros() {
            document.getElementById('filtroData').selectedIndex = -1;
            document.getElementById('filtroLiga').selectedIndex = -1;
            document.getElementById('filtroDxG').selectedIndex = -1;
            document.getElementById('filtroEntrada').selectedIndex = -1;
            document.getElementById('filtroLP').selectedIndex = -1;
            document.getElementById('oddCasaMin').value = '';
            document.getElementById('oddCasaMax').value = '';
            document.getElementById('oddVisitMin').value = '';
            document.getElementById('oddVisitMax').value = '';
            aplicarFiltros();
        }
        
        // Aplicar filtros ao carregar a página para calcular estatísticas iniciais
        window.addEventListener('DOMContentLoaded', function() {
            aplicarFiltros();
        });

        function toggleAI() {
            const content = document.getElementById('aiContent');
            const btn = document.querySelector('.ai-toggle');
            const isHidden = content.style.display === '' || content.style.display === 'none';
            content.style.display = isHidden ? 'block' : 'none';
            btn.textContent = isHidden ? 'Ocultar' : 'Mostrar';
        }

        async function iniciarAnalise() {
            const btn = document.getElementById('iniciarBtn');
            const loading = document.getElementById('aiLoading');
            const results = document.getElementById('aiResults');
            
            btn.style.display = 'none';
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                const response = await fetch('http://localhost:8000/api/analisar_ia', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                
                if (!response.ok) {
                    throw new Error('Erro na requisicao');
                }
                
                const data = await response.json();
                
                if (data.success && data.data) {
                    exibirResultados(data.data);
                } else {
                    alert('Erro ao analisar padroes');
                    btn.style.display = 'block';
                    loading.style.display = 'none';
                }
            } catch (erro) {
                console.error('Erro:', erro);
                alert('Erro ao conectar com a API: ' + erro.message);
                btn.style.display = 'block';
                loading.style.display = 'none';
            }
        }

        function exibirResultados(dados) {
            const loading = document.getElementById('aiLoading');
            const results = document.getElementById('aiResults');
            const resumoDiv = document.getElementById('aiResumo');
            const insightsDiv = document.getElementById('aiInsights');
            const recomendacoesDiv = document.getElementById('aiRecomendacoes');
            
            // Resumo
            resumoDiv.innerHTML = '<strong>' + (dados.resumo || 'Sem dados') + '</strong>';
            
            // Insights
            if (dados.insights && dados.insights.length > 0) {
                let insightsHtml = '<div class="ai-insights-title">Insights Identificados</div>';
                dados.insights.forEach(function(insight) {
                    insightsHtml += '<div class="ai-insight-item">' + formatarComTabulacao(insight) + '</div>';
                });
                insightsDiv.innerHTML = insightsHtml;
            } else {
                insightsDiv.innerHTML = '<div class="ai-insights-title">Insights Identificados</div><div class="ai-insight-item">Nenhum insight disponivel</div>';
            }
            
            // Recomendacoes
            if (dados.recomendacoes && dados.recomendacoes.length > 0) {
                let recomendacoesHtml = '<div class="ai-recomendacoes-title">Recomendacoes para Maximizar Lucros</div>';
                dados.recomendacoes.forEach(function(rec) {
                    recomendacoesHtml += '<div class="ai-recomendacao-item"><strong>✓</strong> ' + formatarComTabulacao(rec) + '</div>';
                });
                recomendacoesDiv.innerHTML = recomendacoesHtml;
            } else {
                recomendacoesDiv.innerHTML = '<div class="ai-recomendacoes-title">Recomendacoes para Maximizar Lucros</div><div class="ai-recomendacao-item">Nenhuma recomendacao disponivel</div>';
            }
            
            loading.style.display = 'none';
            results.style.display = 'block';
        }

        function formatarComTabulacao(text) {
            // Escapa HTML primeiro
            text = escapeHtml(text);
            
            // Remove espaços/tabs entre sinais de +/- e números para colá-los
            text = text.replace(/([+\\-])\\s+(\\d)/g, '$1$2');
            
            // Identifica padrões comuns e adiciona tabulação
            // Padrão: "Label: Valor" ou "Label - Valor"
            text = text.replace(/([A-Za-zÀ-ÿ\\s]+):\\s*/g, '$1:\\t');
            text = text.replace(/([A-Za-zÀ-ÿ\\s]+)\\s*-\\s*/g, '$1 -\\t');
            
            // Adiciona tabulação após números seguidos de texto
            text = text.replace(/(\\d+\\.?\\d*%?)\\s+([A-Za-zÀ-ÿ])/g, '$1\\t$2');
            
            return text;
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, function(m) { return map[m]; });
        }
    </script>
</body>
</html>
"""

    output_file = Path("fixtures/analise_salvos.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"OK Pagina de analise gerada: {output_file}")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        try:
            if comando == "salvar" and len(sys.argv) > 2:
                index = int(sys.argv[2])
                sucesso = salvar_jogo(index)
                sys.exit(0 if sucesso else 1)
            elif comando == "atualizar" and len(sys.argv) > 4:
                jogo_id = int(sys.argv[2])
                gh = int(sys.argv[3])
                ga = int(sys.argv[4])
                lp = None
                if len(sys.argv) > 5:
                    try:
                        lp = float(sys.argv[5])
                    except Exception:
                        lp = None

                if lp is not None:
                    sucesso = atualizar_resultado_com_lp(jogo_id, gh, ga, lp)
                else:
                    sucesso = atualizar_resultado(jogo_id, gh, ga)
                sys.exit(0 if sucesso else 1)
            elif comando == "excluir" and len(sys.argv) > 2:
                jogo_id = int(sys.argv[2])
                sucesso = excluir_jogo(jogo_id)
                sys.exit(0 if sucesso else 1)
            elif comando == "gerar_analise":
                sucesso = gerar_pagina_analise()
                sys.exit(0 if sucesso else 1)
            elif comando == "gerar":
                sucesso = gerar_pagina_salvos()
                sys.exit(0 if sucesso else 1)
            elif comando == "atualizar_campos":
                sucesso = atualizar_campos_faltantes()
                sys.exit(0 if sucesso else 1)
            elif comando == "analisar":
                import sys
                import io
                # Fix encoding for Windows console
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
                analise = analisar_padroes_ia()
                if analise:
                    import json
                    try:
                        print(json.dumps(analise, ensure_ascii=False, indent=2))
                        sys.exit(0)
                    except Exception as e:
                        print(f"Erro ao gerar JSON: {e}", file=sys.stderr)
                        sys.exit(0)  # Retorna sucesso mesmo com erro de encoding
                else:
                    print(json.dumps({'resumo': 'Sem dados para analise', 'insights': [], 'recomendacoes': []}))
                    sys.exit(0)
            else:
                print("Erro: Comando ou argumentos inválidos")
                sys.exit(1)
        except Exception as e:
            print(f"Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("Uso:")
        print("  python salvar_jogo.py salvar <index>")
        print("  python salvar_jogo.py atualizar <jogo_id> <gh> <ga>")
        print("  python salvar_jogo.py gerar")
        print("  python salvar_jogo.py gerar_analise")
        sys.exit(1)

def analisar_dxg_e_odds(dados_fornecidos=None):
    """
    Análise FOCADA: DxG por tipo + Ligas lucrativas + Melhores odds
    
    Apenas analisa:
    1. Breakdown por tipo DxG (FH, LH, EQ, LA, FA)
    2. Ligas mais lucrativas para cada tipo
    3. Melhores intervalos de odds para cada tipo
    """
    
    import json
    import pandas as pd
    from pathlib import Path
    
    try:
        # Obter dados
        if dados_fornecidos:
            dados = dados_fornecidos
        else:
            salvos_file = Path("fixtures") / "jogos_salvos.json"
            if not salvos_file.exists():
                return {'insights': [], 'recomendacoes': [], 'resumo': 'Sem dados'}
            
            with open(salvos_file, 'r', encoding='utf-8') as f:
                dados_raw = json.load(f)
            dados = [d for d in dados_raw if d.get('GH') is not None and d.get('GA') is not None]
        
        if not dados or len(dados) == 0:
            return {'insights': [], 'recomendacoes': [], 'resumo': 'Sem dados para análise'}
        
        # Converter para DataFrame
        df = pd.DataFrame(dados)
        
        # Calcular DxG se não existir
        if 'DxG' not in df.columns:
            df['DxG'] = df.apply(lambda row: _calcular_dxg(row.get('xGH'), row.get('xGA')), axis=1)
        
        # Calcular L/P se não existir
        if 'LP' not in df.columns or df['LP'].isna().any():
            df['LP'] = df.apply(
                lambda row: _calcular_lp(row.to_dict(), row.get('GH'), row.get('GA')),
                axis=1
            )
        
        # Converter LP para float
        df['LP'] = pd.to_numeric(df['LP'], errors='coerce')
        
        # Tipos de DxG
        tipos_dxg = ['FH', 'LH', 'EQ', 'LA', 'FA']
        insights = []
        recomendacoes = []
        
        # ANÁLISE 1: Breakdown por tipo DxG
        resumo_tipos = {}
        for tipo in tipos_dxg:
            df_tipo = df[df['DxG'] == tipo]
            if len(df_tipo) > 0:
                lp_total = df_tipo['LP'].sum()
                taxa_ganho = (df_tipo['LP'] > 0).sum() / len(df_tipo) * 100
                roi = (lp_total / len(df_tipo)) / 1.0 * 100 if len(df_tipo) > 0 else 0
                
                resumo_tipos[tipo] = {
                    'jogos': len(df_tipo),
                    'lp_total': round(lp_total, 2),
                    'taxa_ganho': round(taxa_ganho, 1),
                    'roi': round(roi, 1)
                }
                
                insight = f"DxG {tipo}: {len(df_tipo)} jogos | L/P: {lp_total:.2f} | Taxa: {taxa_ganho:.1f}% | ROI: {roi:.1f}%"
                insights.append(insight)
        
        # ANÁLISE 2: Ligas mais lucrativas por tipo DxG
        ligas_por_tipo = {}
        for tipo in tipos_dxg:
            df_tipo = df[df['DxG'] == tipo]
            if len(df_tipo) > 0:
                ligas = df_tipo.groupby('LIGA').agg({
                    'LP': ['sum', 'count', 'mean']
                }).round(2)
                
                ligas = ligas.sort_values(('LP', 'sum'), ascending=False)
                
                for liga, row in ligas.iterrows():
                    if row[('LP', 'count')] >= 2:  # Mínimo 2 jogos
                        lp = row[('LP', 'sum')]
                        num_jogos = int(row[('LP', 'count')])
                        media = row[('LP', 'mean')]
                        
                        ligas_por_tipo.setdefault(tipo, []).append({
                            'liga': liga,
                            'lp_total': lp,
                            'jogos': num_jogos,
                            'lp_media': media
                        })
                
                # Insights das ligas mais lucrativas
                if tipo in ligas_por_tipo:
                    top_liga = ligas_por_tipo[tipo][0]
                    insight = f"{tipo} - Liga {top_liga['liga']}: L/P {top_liga['lp_total']:.2f} ({top_liga['jogos']} jogos, média {top_liga['lp_media']:.2f})"
                    insights.append(insight)
        
        # ANÁLISE 3: Melhores intervalos de odds por tipo DxG
        for tipo in tipos_dxg:
            df_tipo = df[df['DxG'] == tipo]
            if len(df_tipo) > 0:
                # Usar ODD_H_CALC ou B365H como proxy
                odd_col = 'ODD_H_CALC' if 'ODD_H_CALC' in df_tipo.columns else 'B365H'
                if odd_col in df_tipo.columns:
                    df_tipo_odds = df_tipo.dropna(subset=[odd_col])
                    if len(df_tipo_odds) > 0:
                        # Dividir em intervalos de 0.5
                        df_tipo_odds['ODD_BIN'] = (df_tipo_odds[odd_col] / 0.5).astype(int) * 0.5
                        
                        odds_rentaveis = df_tipo_odds.groupby('ODD_BIN').agg({
                            'LP': ['sum', 'count', 'mean']
                        }).round(2)
                        
                        odds_rentaveis = odds_rentaveis[odds_rentaveis[('LP', 'count')] >= 2]
                        odds_rentaveis = odds_rentaveis.sort_values(('LP', 'mean'), ascending=False)
                        
                        if len(odds_rentaveis) > 0:
                            melhor_intervalo = odds_rentaveis.index[0]
                            lp = odds_rentaveis.iloc[0][('LP', 'sum')]
                            count = int(odds_rentaveis.iloc[0][('LP', 'count')])
                            media = odds_rentaveis.iloc[0][('LP', 'mean')]
                            
                            insight = f"{tipo} - Melhor odds {melhor_intervalo:.2f}: L/P {lp:.2f} ({count} jogos, média {media:.2f})"
                            insights.append(insight)
        
        # Recomendações baseadas em análise
        if resumo_tipos:
            # Qual tipo tem melhor ROI?
            melhor_tipo = max(resumo_tipos.items(), key=lambda x: x[1]['roi'])
            if melhor_tipo[1]['roi'] > 0:
                recomendacoes.append(f"✓ Focar em {melhor_tipo[0]} (ROI positivo de {melhor_tipo[1]['roi']:.1f}%)")
            
            # Qual tipo tem pior ROI?
            pior_tipo = min(resumo_tipos.items(), key=lambda x: x[1]['roi'])
            if pior_tipo[1]['roi'] < 0:
                recomendacoes.append(f"✗ Evitar {pior_tipo[0]} (ROI negativo de {pior_tipo[1]['roi']:.1f}%)")
        
        # Ligas mais lucrativas em geral
        df_com_lp = df[df['LP'].notna()]
        if len(df_com_lp) > 0:
            ligas_gerais = df_com_lp.groupby('LIGA').agg({
                'LP': ['sum', 'count']
            }).round(2)
            ligas_gerais = ligas_gerais.sort_values(('LP', 'sum'), ascending=False)
            
            if len(ligas_gerais) > 0:
                melhor_liga = ligas_gerais.index[0]
                lp_total = ligas_gerais.iloc[0][('LP', 'sum')]
                count = int(ligas_gerais.iloc[0][('LP', 'count')])
                recomendacoes.append(f"Liga {melhor_liga}: L/P {lp_total:.2f} ({count} jogos)")
        
        # Resumo geral
        lp_total_geral = df['LP'].sum()
        num_jogos_ganhos = (df['LP'] > 0).sum()
        taxa_geral = (num_jogos_ganhos / len(df) * 100) if len(df) > 0 else 0
        roi_geral = (lp_total_geral / len(df)) * 100 if len(df) > 0 else 0
        
        resumo = f"Total: {len(df)} jogos | L/P: {lp_total_geral:.2f} | Taxa de ganho: {taxa_geral:.1f}% | ROI: {roi_geral:.1f}%"
        
        return {
            'insights': insights,
            'recomendacoes': recomendacoes,
            'resumo': resumo
        }
    
    except Exception as e:
        import traceback
        print(f"Erro na análise: {str(e)}")
        traceback.print_exc()
        return {'insights': [], 'recomendacoes': [], 'resumo': f'Erro: {str(e)}'}


# Alias para compatibilidade com API
def analisar_padroes_jogos_ia(dados_fornecidos=None):
    """Alias para nova análise focada em DxG - compatibilidade com API"""
    return analisar_dxg_e_odds(dados_fornecidos)

