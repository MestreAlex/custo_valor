"""
Servidor API APENAS para análise de BACKTESTS com IA
Porta: 5001
Função: Analisar dados de backtests em fixtures/backtest_acumulado.json
"""
from flask import Flask, request, jsonify, send_from_directory
import json
from pathlib import Path
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Função auxiliar para aplicar desconto de 4,5% nos lucros
def aplicar_desconto_lucro(lp):
    """
    Aplica desconto de 4,5% nos lucros de apostas vencedoras.
    - Se lp > 0: aplica desconto de 4,5%
    - Se lp <= 0: mantém o valor como está (perda não tem desconto)
    """
    if lp > 0:
        return lp * 0.955  # 100% - 4.5% = 95.5% = 0.955
    return lp

# Definir pasta de arquivos estáticos
BASE_DIR = Path(__file__).parent
BACKTEST_DIR = BASE_DIR / 'backtest'
FIXTURES_DIR = BASE_DIR / 'fixtures'

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
            # ATENÇÃO: Os campos vêm em MINÚSCULAS do arquivo JSON
            gh = float(b.get('fthg') or b.get('GH') or 0)
            ga = float(b.get('ftag') or b.get('GA') or 0)
            xgh = float(b.get('xgh') or b.get('xGH') or 0)
            xga = float(b.get('xga') or b.get('xGA') or 0)
            lp = float(b.get('lp') or b.get('LP') or 0)
            liga = str(b.get('liga') or b.get('LIGA') or 'Desconhecida')
            
            # Debug dos primeiros 2 registros
            if i < 2:
                print(f"[DEBUG] Registro {i}: xgh={xgh}, xga={xga}, lp={lp}, liga={liga}", flush=True)
            
            if xgh > 0 or xga > 0:  # Ter pelo menos um xG válido
                dados_validos.append({
                    'GH': gh, 'GA': ga, 'xGH': xgh, 'xGA': xga,
                    'LP': lp, 'LIGA': liga,
                    'ENTRADA': (b.get('entrada') or b.get('ENTRADA') or 'HOME').upper()
                })
        except Exception as e:
            if i < 5:
                print(f"[DEBUG] Erro ao processar registro {i}: {e}", flush=True)
            continue
    
    print(f"[DEBUG] Dados válidos após normalização: {len(dados_validos)}", flush=True)
    
    if len(dados_validos) < 3:
        return {
            'resumo': f'Apenas {len(dados_validos)} resultado(s) com dados válidos. Minimo de 3 necessarios.',
            'insights': [],
            'recomendacoes': []
        }
    
    # Análise por DxG
    insights = []
    stats_globais = {'total': 0, 'lucro': 0, 'acertos': 0}
    
    # Calcular estatísticas globais
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
        if dxg_tipo not in por_dxg:
            continue
        
        jogos = por_dxg[dxg_tipo]
        if len(jogos) == 0:
            continue
        
        total_lp = sum(j['LP'] for j in jogos)
        acertos = sum(1 for j in jogos if j['LP'] > 0)
        winrate = (acertos / len(jogos) * 100) if len(jogos) > 0 else 0
        roi = (total_lp / len(jogos) * 100) if len(jogos) > 0 else 0
        
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
                winrate_liga = (stats['acertos'] / stats['count'] * 100) if stats['count'] > 0 else 0
                insights.append(f"    - {liga}: +{lp:.2f} ({stats['count']} jogos, {winrate_liga:.1f}%)")
        
        insights.append("")
    
    # Recomendações
    recomendacoes = []
    recomendacoes.append("="*80)
    recomendacoes.append("RECOMENDAÇÕES DE ESTRATÉGIA")
    recomendacoes.append("="*80)
    recomendacoes.append("")
    
    # Encontrar melhor DxG
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

app = Flask(__name__, static_folder=str(BACKTEST_DIR), static_url_path='')

# Configurar CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    # Apenas adicionar charset UTF-8 para JSON, não sobrescrever HTML
    if 'application/json' in response.headers.get('Content-Type', ''):
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    elif 'text/html' not in response.headers.get('Content-Type', ''):
        response.headers['Content-Type'] = response.headers.get('Content-Type', 'application/octet-stream') + '; charset=utf-8'
    return response

@app.route('/')
def index():
    """Rota raiz - serve análise de backtests"""
    return send_from_directory(str(BACKTEST_DIR), 'backtest_salvos.html')

@app.route('/<path:filepath>')
def serve_files(filepath):
    """Serve arquivos HTML e estáticos de backtest"""
    if (BACKTEST_DIR / filepath).is_file():
        return send_from_directory(str(BACKTEST_DIR), filepath)
    return jsonify({'error': f'Arquivo não encontrado: {filepath}'}), 404

@app.route('/api/analisar_padroes_backtest', methods=['POST', 'OPTIONS'])
def analisar_padroes_backtest_api():
    """Endpoint ÚNICO para analisar BACKTESTS com IA"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("[SERVIDOR BACKTEST] Requisição recebida", flush=True)
        
        data = request.get_json()
        
        # Ler dados de backtest acumulado
        backtest_file = FIXTURES_DIR / 'backtest_acumulado.json'
        if not backtest_file.exists():
            print(f"[SERVIDOR BACKTEST] ERRO: Arquivo não encontrado: {backtest_file}", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum backtest salvo encontrado'}), 400
        
        with open(backtest_file, 'r', encoding='utf-8') as f:
            backtests = json.load(f)
        
        print(f"[SERVIDOR BACKTEST] Carregados {len(backtests)} backtests do arquivo", flush=True)
        print(f"[SERVIDOR BACKTEST] Exemplo 1º registro: {backtests[0] if backtests else 'VAZIO'}", flush=True)
        
        # Executar análise DIRETAMENTE com os dados do arquivo
        # A função analisar_backtest_dxg já faz a normalização internamente
        analise = analisar_backtest_dxg(backtests)
        
        if analise and (len(analise.get('insights', [])) > 0 or len(analise.get('recomendacoes', [])) > 0):
            print(f"[SERVIDOR BACKTEST] Análise concluída: {len(analise['insights'])} insights, {len(analise['recomendacoes'])} recomendações", flush=True)
            return jsonify({'success': True, 'data': analise}), 200
        else:
            print(f"[SERVIDOR BACKTEST] Análise retornou: {analise}", flush=True)
            return jsonify({'success': True, 'data': analise or {'insights': [], 'recomendacoes': [], 'resumo': 'Análise sem resultados'}}) , 200
            
    except Exception as e:
        print(f"[SERVIDOR BACKTEST] EXCEPTION: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/backtest_acumulado', methods=['GET', 'OPTIONS'])
def carregar_backtest_acumulado_api():
    """Endpoint para carregar backtest acumulado com desconto de 4,5% aplicado"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        backtest_file = FIXTURES_DIR / 'backtest_acumulado.json'
        if not backtest_file.exists():
            return jsonify({'success': True, 'entradas': [], 'message': 'Arquivo não encontrado'}), 200

        with open(backtest_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Aplicar desconto de 4,5% em todos os lucros
        dados_com_desconto = []
        for jogo in dados:
            jogo_copia = jogo.copy()
            lp_original = float(jogo.get('lp', 0))
            lp_com_desconto = aplicar_desconto_lucro(lp_original)
            jogo_copia['lp'] = lp_com_desconto
            dados_com_desconto.append(jogo_copia)

        return jsonify({'success': True, 'entradas': dados_com_desconto}), 200
            
    except Exception as e:
        print(f"[SERVIDOR BACKTEST] EXCEPTION ao carregar: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/backtest_resumo_entradas.html')
def resumo_entradas_html():
    """Serve página de resumo de entradas"""
    return send_from_directory(str(BACKTEST_DIR), 'backtest_resumo_entradas.html')

@app.route('/api/resumo_entradas', methods=['GET', 'OPTIONS'])
def resumo_entradas_api():
    """API que retorna resumo de entradas por liga, tipo e temporada com desconto de 4,5% aplicado"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        backtest_file = FIXTURES_DIR / 'backtest_acumulado.json'
        if not backtest_file.exists():
            return jsonify({}), 200

        with open(backtest_file, 'r', encoding='utf-8') as f:
            entradas = json.load(f)
        
        # Estrutura: { liga: { "HOME_temporada_tipo": {entradas, lucro, winrate, roi}, ... } }
        resumo = defaultdict(lambda: {})
        
        for entrada in entradas:
            try:
                liga = entrada.get('liga', 'Desconhecida')
                temporada = entrada.get('temporada', '2020/2021')
                lp = float(entrada.get('lp', 0))
                
                # Aplicar desconto de 4,5% 
                lp_com_desconto = aplicar_desconto_lucro(lp)
                
                # Tipo de entrada é o campo 'entrada' que contém 'HOME' ou 'AWAY'
                tipo_entrada = entrada.get('entrada', 'HOME')
                
                # DxG já vem no campo 'dxg'
                dxg_tipo = entrada.get('dxg', 'EQ')
                
                # Chave única para esta combinação
                chave = f"{tipo_entrada}_{temporada}_{dxg_tipo}"
                
                # Inicializar se não existe
                if chave not in resumo[liga]:
                    resumo[liga][chave] = {
                        'entradas': 0,
                        'lucro': 0.0,
                        'acertos': 0,
                        'winrate': 0.0,
                        'roi': 0.0
                    }
                
                # Adicionar dados com desconto
                dados = resumo[liga][chave]
                dados['entradas'] += 1
                dados['lucro'] += lp_com_desconto
                if lp_com_desconto > 0:
                    dados['acertos'] += 1
                
                # Recalcular winrate e ROI
                if dados['entradas'] > 0:
                    dados['winrate'] = (dados['acertos'] / dados['entradas']) * 100
                    dados['roi'] = (dados['lucro'] / dados['entradas']) * 100
                    
            except Exception as e:
                print(f"[RESUMO ENTRADAS] Erro ao processar entrada: {e}", flush=True)
                continue
        
        # Converter defaultdict para dict regular
        resultado = {liga: dict(dados) for liga, dados in resumo.items()}
        
        print(f"[RESUMO ENTRADAS] Retornando dados para {len(resultado)} ligas com desconto de 4,5%", flush=True)
        
        return jsonify(resultado), 200
            
    except Exception as e:
        print(f"[RESUMO ENTRADAS] EXCEPTION: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({}), 200

if __name__ == '__main__':
    print("="*80)
    print("SERVIDOR DE ANALISE DE BACKTESTS")
    print("Porta: 5001")
    print("Função: Análise de backtests em fixtures/backtest_acumulado.json")
    print("Endpoint: POST /api/analisar_padroes_backtest")
    print("="*80)
    app.run(debug=False, port=5001)
