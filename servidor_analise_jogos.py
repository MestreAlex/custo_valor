"""
Servidor API APENAS para análise de JOGOS SALVOS com IA
Porta: 9000
Função: Analisar dados salvos em fixtures/jogos_salvos.json
"""
from flask import Flask, request, jsonify, send_from_directory
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Definir pasta de arquivos estáticos
BASE_DIR = Path(__file__).parent
FIXTURES_DIR = BASE_DIR / 'fixtures'

app = Flask(__name__, static_folder=str(FIXTURES_DIR), static_url_path='')

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
    """Rota raiz - serve análise de jogos salvos"""
    return send_from_directory(str(FIXTURES_DIR), 'analise_salvos.html')

@app.route('/<path:filepath>')
def serve_files(filepath):
    """Serve arquivos HTML e estáticos de fixtures"""
    if (FIXTURES_DIR / filepath).is_file():
        return send_from_directory(str(FIXTURES_DIR), filepath)
    return jsonify({'error': f'Arquivo não encontrado: {filepath}'}), 404

@app.route('/api/jogos_salvos_com_desconto', methods=['GET', 'OPTIONS'])
def jogos_salvos_com_desconto_api():
    """Endpoint para carregar jogos salvos com desconto de 4,5% já aplicado no armazenamento"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        jogos_file = FIXTURES_DIR / 'jogos_salvos.json'
        if not jogos_file.exists():
            return jsonify({'success': True, 'jogos': [], 'message': 'Arquivo não encontrado'}), 200
        
        with open(jogos_file, 'r', encoding='utf-8') as f:
            jogos = json.load(f)
        
        # Retornar jogos como estão armazenados (desconto já foi aplicado em salvar_jogo.py)
        # NÃO aplicar desconto novamente aqui para evitar desconto duplo
        return jsonify({'success': True, 'jogos': jogos, 'total': len(jogos)}), 200
    except Exception as e:
        print(f"[SERVIDOR JOGOS] Erro ao carregar jogos: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analisar_padroes_jogos', methods=['POST', 'OPTIONS'])
def analisar_padroes_jogos_api():
    """Endpoint ÚNICO para analisar JOGOS SALVOS com IA"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("[SERVIDOR JOGOS] Requisição recebida", flush=True)
        
        data = request.get_json()
        filtro_data = data.get('filtro_data', []) if data else []
        filtro_liga = data.get('filtro_liga', []) if data else []
        
        print(f"[SERVIDOR JOGOS] Filtros: Data={filtro_data}, Liga={filtro_liga}", flush=True)
        
        # Ler jogos salvos
        jogos_file = FIXTURES_DIR / 'jogos_salvos.json'
        if not jogos_file.exists():
            print(f"[SERVIDOR JOGOS] ERRO: Arquivo não encontrado: {jogos_file}", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum jogo salvo encontrado'}), 400
        
        with open(jogos_file, 'r', encoding='utf-8') as f:
            jogos = json.load(f)
        
        print(f"[SERVIDOR JOGOS] Carregados {len(jogos)} jogos do arquivo", flush=True)
        
        # Converter LP de string para float
        for j in jogos:
            if 'LP' in j and isinstance(j['LP'], str):
                try:
                    j['LP'] = float(j['LP'].replace(',', '.'))
                except:
                    j['LP'] = None
        
        # Filtrar
        jogos_filtrados = jogos
        if filtro_data:
            jogos_filtrados = [j for j in jogos_filtrados if j.get('DATA') in filtro_data]
        if filtro_liga:
            jogos_filtrados = [j for j in jogos_filtrados if j.get('LIGA') in filtro_liga]
        
        print(f"[SERVIDOR JOGOS] Após filtros: {len(jogos_filtrados)} jogos", flush=True)
        
        # Importar função de análise NOVA (focada em DxG)
        from salvar_jogo import analisar_dxg_e_odds
        
        print(f"[SERVIDOR JOGOS] Executando análise DxG...", flush=True)
        analise = analisar_dxg_e_odds(jogos_filtrados)
        
        if analise:
            print(f"[SERVIDOR JOGOS] Análise concluída com sucesso", flush=True)
            return jsonify({'success': True, 'data': analise}), 200
        else:
            print(f"[SERVIDOR JOGOS] Análise retornou None", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum dado disponível para análise'}), 400
            
    except Exception as e:
        print(f"[SERVIDOR JOGOS] EXCEPTION: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("="*80)
    print("SERVIDOR DE ANALISE DE JOGOS SALVOS")
    print("Porta: 9000")
    print("Função: Análise de jogos salvos em fixtures/jogos_salvos.json")
    print("Endpoint: POST /api/analisar_padroes_jogos")
    print("="*80)
    app.run(debug=False, port=9000)
