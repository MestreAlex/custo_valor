from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from backtest_engine import BacktestEngine
import json
import numpy as np
import os
from pathlib import Path
from collections import defaultdict

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Custom JSON encoder para lidar com numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Usar custom encoder para Flask
app.config['JSON_ENCODER_CLASS'] = NumpyEncoder

# Criar função para converter resultado antes de jsonify
def converter_resultado(obj):
    """Converte numpy types para types nativos do Python"""
    if isinstance(obj, dict):
        return {k: converter_resultado(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [converter_resultado(item) for item in obj]
    elif isinstance(obj, (np.floating, np.integer)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def _gerar_resumo_engine(eng, max_times=8):
    """Gera resumo da liga/temporada atual para validação"""
    try:
        times = set()
        if hasattr(eng, 'df_teste') and eng.df_teste is not None:
            df = eng.df_teste
            if eng.coluna_home in df.columns:
                times.update(df[eng.coluna_home].dropna().astype(str).tolist())
            if eng.coluna_away in df.columns:
                times.update(df[eng.coluna_away].dropna().astype(str).tolist())
        times_amostra = sorted(list(times))[:max_times]
    except Exception:
        times_amostra = []

    return {
        'liga': eng.liga,
        'temporada': eng.temporada,
        'total_jogos': len(eng.df_teste) if hasattr(eng, 'df_teste') else 0,
        'num_times': eng.num_times,
        'max_jogos_rodada': eng.max_jogos_rodada,
        'times_amostra': times_amostra
    }

def analisar_backtest_dxg(backtests):
    """Análise de backtests focado em DxG, ligas lucrativas e odds"""
    print(f"[DEBUG] analisar_backtest_dxg recebeu {len(backtests) if backtests else 0} registros", flush=True)
    
    if not backtests or len(backtests) < 3:
        return {
            'resumo': f'Apenas {len(backtests) if backtests else 0} resultado(s) disponivel(is). Minimo de 3 necessarios para analise.',
            'insights': [],
            'recomendacoes': []
        }
    
    # Normalizar e filtrar dados válidos
    dados_validos = []
    for i, b in enumerate(backtests):
        try:
            gh = float(b.get('fthg') or b.get('GH') or 0)
            ga = float(b.get('ftag') or b.get('GA') or 0)
            xgh = float(b.get('xgh') or b.get('xGH') or 0)
            xga = float(b.get('xga') or b.get('xGA') or 0)
            lp = float(b.get('lp') or b.get('LP') or 0)
            liga = str(b.get('liga') or b.get('LIGA') or 'Desconhecida')
            
            if xgh > 0 or xga > 0:
                dados_validos.append({
                    'GH': gh, 'GA': ga, 'xGH': xgh, 'xGA': xga,
                    'LP': lp, 'LIGA': liga,
                    'ENTRADA': (b.get('entrada') or b.get('ENTRADA') or 'HOME').upper()
                })
        except Exception as e:
            continue
    
    print(f"[DEBUG] Dados válidos após normalização: {len(dados_validos)}", flush=True)
    
    if len(dados_validos) < 3:
        return {
            'resumo': f'Apenas {len(dados_validos)} resultado(s) com dados válidos.',
            'insights': [],
            'recomendacoes': []
        }
    
    # Análise por DxG
    insights = []
    stats_globais = {'total': 0, 'lucro': 0, 'acertos': 0}
    
    for d in dados_validos:
        stats_globais['total'] += 1
        stats_globais['lucro'] += d['LP']
        if d['LP'] > 0:
            stats_globais['acertos'] += 1
    
    roi_global = (stats_globais['lucro'] / stats_globais['total'] * 100) if stats_globais['total'] > 0 else 0
    winrate_global = (stats_globais['acertos'] / stats_globais['total'] * 100) if stats_globais['total'] > 0 else 0
    
    resumo = f"📊 Total: {stats_globais['total']} jogos | Lucro: +{stats_globais['lucro']:.2f} | Taxa: {winrate_global:.1f}% | ROI: {roi_global:.1f}%"
    
    insights.append("="*80)
    insights.append("ANÁLISE POR TIPO DE DxG")
    insights.append("="*80)
    insights.append("")
    
    # Agrupar por DxG
    por_dxg = defaultdict(list)
    for d in dados_validos:
        diff = d['xGH'] - d['xGA']
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
        
        d['DXG'] = dxg
        por_dxg[dxg].append(d)
    
    # Análise por cada DxG
    for dxg_tipo in ['FH', 'LH', 'EQ', 'LA', 'FA']:
        if dxg_tipo not in por_dxg or len(por_dxg[dxg_tipo]) == 0:
            continue
        
        jogos = por_dxg[dxg_tipo]
        total_lp = sum(j['LP'] for j in jogos)
        acertos = sum(1 for j in jogos if j['LP'] > 0)
        winrate = (acertos / len(jogos) * 100)
        roi = (total_lp / len(jogos) * 100)
        
        insights.append(f"▶ {dxg_tipo} ({len(jogos)} jogos)")
        insights.append(f"  • Lucro: +{total_lp:.2f} | Taxa: {winrate:.1f}% | ROI: {roi:.1f}%")
        
        # Ligas mais lucrativas para este DxG
        por_liga = defaultdict(lambda: {'lp': 0, 'count': 0, 'acertos': 0})
        for j in jogos:
            liga = j['LIGA']
            por_liga[liga]['lp'] += j['LP']
            por_liga[liga]['count'] += 1
            if j['LP'] > 0:
                por_liga[liga]['acertos'] += 1
        
        ligas_ord = sorted(por_liga.items(), key=lambda x: x[1]['lp'], reverse=True)
        top_3_ligas = ligas_ord[:3]
        
        if top_3_ligas:
            insights.append(f"  • Ligas mais lucrativas:")
            for liga, stats in top_3_ligas:
                lp = stats['lp']
                winrate_liga = (stats['acertos'] / stats['count'] * 100)
                insights.append(f"    - {liga}: +{lp:.2f} ({stats['count']} jogos, {winrate_liga:.1f}%)")
        
        insights.append("")
    
    # Recomendações
    recomendacoes = []
    recomendacoes.append("="*80)
    recomendacoes.append("RECOMENDAÇÕES DE ESTRATÉGIA")
    recomendacoes.append("="*80)
    recomendacoes.append("")
    
    # Melhor DxG
    melhor_dxg = max(por_dxg.items(), 
                     key=lambda x: sum(j['LP'] for j in x[1]),
                     default=None)
    if melhor_dxg:
        dxg, jogos = melhor_dxg
        lp_total = sum(j['LP'] for j in jogos)
        recomendacoes.append(f"1️⃣ Tipo DxG mais lucrativo: {dxg} (+{lp_total:.2f})")
        recomendacoes.append(f"   Concentre entradas em matchups com este padrão DxG")
        recomendacoes.append("")
    
    # Ligas mais lucrativas globalmente
    por_liga_global = defaultdict(lambda: {'lp': 0, 'count': 0})
    for d in dados_validos:
        por_liga_global[d['LIGA']]['lp'] += d['LP']
        por_liga_global[d['LIGA']]['count'] += 1
    
    ligas_top = sorted(por_liga_global.items(), key=lambda x: x[1]['lp'], reverse=True)[:3]
    if ligas_top:
        recomendacoes.append(f"2️⃣ Ligas mais lucrativas:")
        for liga, stats in ligas_top:
            recomendacoes.append(f"   • {liga}: +{stats['lp']:.2f} ({stats['count']} jogos)")
        recomendacoes.append("")
    
    # Status geral
    if roi_global > 0:
        recomendacoes.append(f"3️⃣ Status geral: ✅ Estratégia LUCRATIVA (ROI: {roi_global:.1f}%)")
    else:
        recomendacoes.append(f"3️⃣ Status geral: ⚠️ Estratégia COM PREJUÍZO (ROI: {roi_global:.1f}%)")
        recomendacoes.append("   Revise a seleção de matchups e entradas")
    
    return {
        'resumo': resumo,
        'insights': insights,
        'recomendacoes': recomendacoes
    }

# Instância global do engine - Lazy initialization
engine = None
engine_liga_atual = 'E0'
engine_temporada_atual = '2024-25'

def get_engine():
    """Get or initialize the engine - recria se temporada/liga mudaram"""
    global engine, engine_liga_atual, engine_temporada_atual
    if engine is None or engine.liga != engine_liga_atual or engine.temporada != engine_temporada_atual:
        engine = BacktestEngine(liga=engine_liga_atual, temporada=engine_temporada_atual)
    return engine

def _atualizar_contexto_por_request(dados):
    """Atualiza liga/temporada globais a partir do request (quando informado)."""
    global engine_liga_atual, engine_temporada_atual
    if not dados:
        return
    liga = dados.get('liga')
    temporada = dados.get('temporada')

    if liga:
        if liga not in LIGAS_DISPONIVEIS:
            raise ValueError('Liga não encontrada')
        engine_liga_atual = liga

    if temporada:
        engine_temporada_atual = temporada

LIGAS_DISPONIVEIS = {
    'B1': 'Bélgica - Primeira Divisão',
    'D1': 'Alemanha - Bundesliga',
    'D2': 'Alemanha - Segunda Divisão',
    'E0': 'Inglaterra - Premier League',
    'E1': 'Inglaterra - Championship',
    'F1': 'França - Ligue 1',
    'F2': 'França - Ligue 2',
    'G1': 'Grécia - Super League',
    'I1': 'Itália - Serie A',
    'I2': 'Itália - Serie B',
    'N1': 'Holanda - Eredivisie',
    'P1': 'Portugal - Primeira Liga',
    'SP1': 'Espanha - La Liga',
    'SP2': 'Espanha - Segunda Divisão',
    'T1': 'Turquia - Super Lig',
    'ARG': 'Argentina - Super Liga',
    'AUT': 'Áustria - Bundesliga',
    'BRA': 'Brasil - Serie A',
    'CHN': 'China - Super League',
    'DNK': 'Dinamarca - Superligaen',
    'FIN': 'Finlândia - Veikkausliiga',
    'IRL': 'Irlanda - Premier Division',
    'JPN': 'Japão - J-League',
    'MEX': 'México - Liga MX',
    'NOR': 'Noruega - Eliteserien',
    'POL': 'Polônia - Ekstraklasa',
    'ROU': 'Romênia - Liga I',
    'RUS': 'Rússia - RPL',
    'SWE': 'Suécia - Allsvenskan',
    'SWZ': 'Suíça - Super Liga',
    'USA': 'EUA - MLS',
}

# Rotas para servir arquivos HTML
@app.route('/')
def index():
    """Redireciona para backtest.html"""
    return send_from_directory('.', 'backtest.html')

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve arquivos estáticos HTML, CSS, JS, etc"""
    if filename.endswith('.html') or filename.endswith('.json') or filename.endswith('.js') or filename.endswith('.css'):
        return send_from_directory('.', filename)
    return "File not found", 404

@app.route('/api/backtest/ligas', methods=['GET'])
def get_ligas():
    """Retorna lista de ligas disponíveis"""
    print("🔵 [API] Endpoint /api/backtest/ligas chamado")
    print(f"🔵 [API] LIGAS_DISPONIVEIS: {len(LIGAS_DISPONIVEIS)} ligas")
    print(f"🔵 [API] engine_liga_atual: {engine_liga_atual}")
    
    eng = get_engine()
    
    resultado = {
        'success': True, 
        'ligas': LIGAS_DISPONIVEIS, 
        'atual': engine_liga_atual
    }
    
    print(f"🔵 [API] Retornando: success=True, {len(resultado['ligas'])} ligas, atual={resultado['atual']}")
    return jsonify(resultado)

@app.route('/api/backtest/selecionar-liga', methods=['POST'])
def selecionar_liga():
    """Seleciona uma liga e temporada para o backtest"""
    try:
        global engine, engine_liga_atual, engine_temporada_atual
        dados = request.get_json()
        liga = dados.get('liga', 'E0')
        temporada = dados.get('temporada', '2024-25')
        
        print(f"🔵 [API] Selecionando Liga: {liga}, Temporada: {temporada}")
        
        if liga not in LIGAS_DISPONIVEIS:
            return jsonify({'success': False, 'error': 'Liga não encontrada'}), 400
        
        # Criar novo engine com liga e temporada especificadas
        print(f"🔵 [API] Criando BacktestEngine(liga={liga}, temporada={temporada})")
        engine = BacktestEngine(liga=liga, temporada=temporada)
        engine_liga_atual = liga
        engine_temporada_atual = temporada
        
        print(f"🔵 [API] Engine criado! Total de jogos na temporada: {len(engine.df_teste)}")
        print(f"🔵 [API] Arquivo de resultados: {engine.arquivo_resultados.name}")
        
        status = converter_resultado(engine.obter_status())
        return jsonify({
            'success': True,
            'mensagem': f'Liga {liga} e temporada {temporada} selecionadas com sucesso',
            'liga': liga,
            'temporada': temporada,
            'status': status
        })
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest/status', methods=['GET'])
def get_status():
    """Retorna status atual do backtest"""
    try:
        eng = get_engine()
        status = converter_resultado(eng.obter_status())
        # Adicionar informações da liga
        status['num_times'] = eng.num_times
        status['max_jogos_rodada'] = eng.max_jogos_rodada
        
        print(f"🔵 [API] Status - Liga: {engine_liga_atual}, Temporada: {engine_temporada_atual}")
        print(f"🔵 [API] Status - Total jogos: {status['total_jogos']}, Processados: {status['jogos_processados']}, Completo: {status['completo']}")
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        print(f"❌ [API] Erro em /api/backtest/status: {e}")
        print(tb_str)
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest/info-liga', methods=['GET'])
def info_liga():
    """Retorna informações sobre a liga atual"""
    try:
        eng = get_engine()
        return jsonify({
            'success': True,
            'liga': engine_liga_atual,
            'num_times': eng.num_times,
            'max_jogos_rodada': eng.max_jogos_rodada,
            'total_jogos': len(eng.df_teste),
            'jogos_processados': eng.resultados['jogos_processados']
        })
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest/resumo', methods=['GET', 'POST'])
def resumo():
    """Retorna resumo da liga/temporada atual (com amostra de times)"""
    try:
        if request.method == 'POST':
            dados = request.get_json(silent=True) or {}
            _atualizar_contexto_por_request(dados)

        eng = get_engine()
        resumo_data = _gerar_resumo_engine(eng)
        return jsonify({'success': True, 'resumo': resumo_data})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest/processar', methods=['POST'])
def processar_rodada():
    """Processa próxima rodada do backtest"""
    try:
        dados = request.get_json(silent=True) or {}
        _atualizar_contexto_por_request(dados)
        eng = get_engine()
        resultado = eng.processar_rodada()
        
        if resultado is None:
            return jsonify({
                'success': True,
                'completo': True,
                'mensagem': 'Backtest completo!'
            })
        
        resultado_convertido = converter_resultado(resultado)
        return jsonify({
            'success': True,
            'completo': False,
            'resultado': resultado_convertido
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        print(f"ERRO na API: {str(e)}")
        print(f"Traceback:\n{tb_str}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': tb_str
        }), 500

@app.route('/api/backtest/resetar', methods=['POST'])
def resetar():
    """Reseta o backtest da liga atual"""
    try:
        global engine
        dados = request.get_json(silent=True) or {}
        _atualizar_contexto_por_request(dados)
        eng = get_engine()
        resultado = eng.resetar()
        engine = BacktestEngine(liga=engine_liga_atual, temporada=engine_temporada_atual)
        return jsonify({'success': True, 'mensagem': resultado.get('mensagem', 'Resetado')})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest/resetar-todos', methods=['POST'])
def resetar_todos():
    """Reseta todos os backtests de todas as ligas e temporadas"""
    try:
        from pathlib import Path
        import glob
        pasta_backtest = Path(__file__).parent
        pasta_fixtures = pasta_backtest.parent / 'fixtures'
        
        resetados = []
        erros = []
        
        # Buscar todos os arquivos backtest_resultados_*.json (incluindo com temporadas)
        pattern = str(pasta_backtest / 'backtest_resultados_*.json')
        arquivos_encontrados = glob.glob(pattern)
        
        for arquivo_path in arquivos_encontrados:
            try:
                arquivo = Path(arquivo_path)
                nome_arquivo = arquivo.name
                arquivo.unlink()  # Deletar arquivo
                resetados.append(nome_arquivo)
            except Exception as e:
                erros.append(f'{nome_arquivo}: {str(e)}')
        
        # Limpar arquivo de salvamentos acumulados
        try:
            arquivo_acumulado = pasta_fixtures / 'backtest_acumulado.json'
            if arquivo_acumulado.exists():
                arquivo_acumulado.write_text('[]', encoding='utf-8')
                print(f'✅ Arquivo de salvamentos apagado: {arquivo_acumulado}')
        except Exception as e:
            erros.append(f'Erro ao limpar salvamentos: {str(e)}')
        
        resultado = {
            'success': True,
            'mensagem': f'Resetados {len(resetados)} backtests - localStorage também foi limpo',
            'ligas_resetadas': resetados,
            'erros': erros if erros else None,
            'instrucao_localStorage': 'Cliente deve limpar localStorage: localStorage.removeItem("backtest_acumulado")'
        }
        return jsonify(resultado)
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest/entradas', methods=['GET'])
def get_entradas():
    """Retorna todas as entradas do backtest"""
    try:
        eng = get_engine()
        entradas = converter_resultado(eng.resultados['entradas'])
        return jsonify({
            'success': True,
            'entradas': entradas
        })
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb_str}), 500

@app.route('/api/backtest_acumulado', methods=['GET'])
def get_backtest_acumulado():
    """Retorna todos os dados de backtest salvos"""
    try:
        from pathlib import Path

        def carregar_entradas_detalhadas():
            backtest_dir = Path(__file__).resolve().parent
            arquivos = sorted(backtest_dir.glob("backtest_resultados_*.json"))
            entradas = []

            for arquivo in arquivos:
                nome = arquivo.stem.replace("backtest_resultados_", "")
                if "_" in nome:
                    liga, temporada = nome.split("_", 1)
                else:
                    liga, temporada = nome, ""

                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        dados_arquivo = json.load(f)
                except UnicodeDecodeError:
                    with open(arquivo, 'r', encoding='utf-8-sig') as f:
                        dados_arquivo = json.load(f)

                for item in dados_arquivo.get('entradas', []):
                    entrada = dict(item)
                    entrada.setdefault('liga', liga)
                    entrada.setdefault('temporada', temporada)
                    entradas.append(entrada)

            return entradas

        backtest_file = Path(__file__).resolve().parent.parent / "fixtures" / "backtest_acumulado.json"

        if backtest_file.exists():
            try:
                with open(backtest_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except UnicodeDecodeError:
                with open(backtest_file, 'r', encoding='utf-8-sig') as f:
                    dados = json.load(f)

            if isinstance(dados, list) and dados:
                amostra = dados[0]
                possui_detalhe = all(campo in amostra for campo in ['home', 'away', 'entrada', 'dxg', 'lp'])
                if possui_detalhe:
                    print(f"DEBUG API: Retornando {len(dados)} entradas do backtest acumulado", flush=True)
                    return jsonify({'success': True, 'entradas': dados}), 200

        entradas_detalhadas = carregar_entradas_detalhadas()
        print(f"DEBUG API: Retornando {len(entradas_detalhadas)} entradas detalhadas (geradas)", flush=True)
        return jsonify({'success': True, 'entradas': entradas_detalhadas}), 200
        
    except Exception as e:
        import traceback
        print(f"ERRO ao carregar backtest acumulado: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/salvar_backtest_json', methods=['POST'])
def salvar_backtest_json():
    """Endpoint para salvar dados do backtest em arquivo JSON"""
    try:
        from pathlib import Path
        
        data = request.get_json()
        novos_dados = data.get('entradas', data.get('dados', [])) if data else []
        
        print(f"DEBUG API: Recebidos {len(novos_dados)} entradas para salvar", flush=True)
        
        # Caminho do arquivo
        backtest_file = Path("../fixtures/backtest_acumulado.json")
        backtest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Carregar dados existentes (se houver)
        dados_existentes = []
        if backtest_file.exists():
            try:
                with open(backtest_file, 'r', encoding='utf-8') as f:
                    dados_existentes = json.load(f)
                print(f"DEBUG API: Carregados {len(dados_existentes)} entradas existentes", flush=True)
            except:
                print("DEBUG API: Arquivo existente vazio ou inválido, iniciando novo", flush=True)
                dados_existentes = []
        
        # Criar conjunto de chaves únicas para identificar duplicatas
        def criar_chave(entrada):
            return f"{entrada.get('liga', '')}|{entrada.get('temporada', '')}|{entrada.get('date', '')}|{entrada.get('home', '')}|{entrada.get('away', '')}"
        
        # Mapear dados existentes por chave
        dados_map = {criar_chave(e): e for e in dados_existentes}
        
        # Adicionar novos dados (substituir se duplicado, adicionar se novo)
        novos_adicionados = 0
        duplicatas_substituidas = 0
        
        for entrada in novos_dados:
            chave = criar_chave(entrada)
            if chave in dados_map:
                duplicatas_substituidas += 1
            else:
                novos_adicionados += 1
            dados_map[chave] = entrada  # Adiciona ou substitui
        
        # Converter de volta para lista
        dados_finais = list(dados_map.values())
        
        print(f"DEBUG API: Total final: {len(dados_finais)} entradas", flush=True)
        
        # Salvar arquivo atualizado
        with open(backtest_file, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=2)
        
        print(f"DEBUG API: Backtest salvo em {backtest_file}", flush=True)
        
        return jsonify({
            'success': True, 
            'message': f'Backtest salvo com sucesso',
            'total': len(dados_finais),
            'novos': novos_adicionados,
            'substituidos': duplicatas_substituidas
        }), 200
        
    except Exception as e:
        import traceback
        print(f"ERRO ao salvar backtest: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analisar_padroes_backtest', methods=['POST', 'OPTIONS'])
def analisar_padroes_backtest():
    """Endpoint para analisar padrões de backtest com IA"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("[API BACKTEST] Requisição recebida para análise", flush=True)
        
        # Ler dados de backtest acumulado
        backtest_file = Path("../fixtures/backtest_acumulado.json")
        if not backtest_file.exists():
            print(f"[API BACKTEST] ERRO: Arquivo não encontrado: {backtest_file}", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum backtest salvo encontrado'}), 400
        
        with open(backtest_file, 'r', encoding='utf-8') as f:
            backtests = json.load(f)
        
        print(f"[API BACKTEST] Carregados {len(backtests)} backtests do arquivo", flush=True)
        
        # Executar análise
        analise = analisar_backtest_dxg(backtests)
        
        if analise and (len(analise.get('insights', [])) > 0 or len(analise.get('recomendacoes', [])) > 0):
            print(f"[API BACKTEST] Análise concluída: {len(analise['insights'])} insights, {len(analise['recomendacoes'])} recomendações", flush=True)
            return jsonify({'success': True, 'data': analise}), 200
        else:
            print(f"[API BACKTEST] Análise retornou vazia", flush=True)
            return jsonify({'success': False, 'message': 'Análise não gerou resultados'}), 400
    
    except Exception as e:
        import traceback
        print(f"[API BACKTEST] ERRO na análise: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("API Backtest rodando em http://localhost:5001")
    app.run(debug=False, host='127.0.0.1', port=5001, threaded=True)
