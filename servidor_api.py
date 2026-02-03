"""
Servidor API Flask para gerenciar jogos salvos
"""
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import sys
import os
import json
from pathlib import Path

# Configurar stdout/stderr para UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Definir pasta de arquivos estáticos
BASE_DIR = Path(__file__).parent
FIXTURES_DIR = BASE_DIR / 'fixtures'
BACKTEST_DIR = BASE_DIR / 'backtest'

# Função auxiliar para aplicar desconto de 4,5% nos lucros
def aplicar_desconto_lucro(lp):
    """
    Aplica desconto de 4,5% nos lucros de apostas vencedoras.
    - Se lp > 0: aplica desconto de 4,5%
    - Se lp <= 0: mantém o valor como está (perda não tem desconto)
    """
    try:
        lp_float = float(lp)
        if lp_float > 0:
            return lp_float * 0.955  # 100% - 4.5% = 95.5% = 0.955
        return lp_float
    except (ValueError, TypeError):
        return 0.0

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
    elif 'text/html' in response.headers.get('Content-Type', ''):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    else:
        response.headers['Content-Type'] = response.headers.get('Content-Type', 'application/octet-stream') + '; charset=utf-8'
    return response

@app.route('/')
def index():
    """Rota raiz - redireciona para análise de jogos salvos"""
    return send_from_directory(str(FIXTURES_DIR), 'analise_salvos.html')

@app.route('/<path:filepath>')
def serve_files(filepath):
    """Serve arquivos HTML e estáticos"""
    # Tentar servir da pasta fixtures primeiro
    if (FIXTURES_DIR / filepath).is_file():
        return send_from_directory(str(FIXTURES_DIR), filepath)
    
    # Se não encontrar em fixtures, tentar em backtest
    if (BACKTEST_DIR / filepath).is_file():
        return send_from_directory(str(BACKTEST_DIR), filepath)
    
    # Se não encontrar, retornar 404
    return jsonify({'error': f'Arquivo não encontrado: {filepath}'}), 404

@app.route('/api/salvar_jogo', methods=['POST'])
def salvar_jogo_api():
    """Endpoint para salvar um jogo"""
    try:
        data = request.get_json()
        index = data.get('index')
        
        print(f"[DEBUG] Recebido pedido para salvar jogo index: {index}")
        
        if index is None:
            print("[DEBUG] Index não fornecido!")
            return jsonify({'success': False, 'message': 'Index não fornecido'}), 400
        
        # Executar o script de salvamento
        print(f"[DEBUG] Executando: python salvar_jogo.py salvar {index}")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, 'salvar_jogo.py', 'salvar', str(index)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            env=env
        )
        
        print(f"[DEBUG] Return code: {result.returncode}")
        print(f"[DEBUG] Stdout: {result.stdout}")
        print(f"[DEBUG] Stderr: {result.stderr}")
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Jogo salvo com sucesso!'}), 200

        error_msg = result.stderr if result.stderr else result.stdout
        if "ja foi salvo anteriormente" in error_msg or "já foi salvo anteriormente" in error_msg:
            return jsonify({'success': True, 'message': 'Este jogo ja estava salvo.'}), 200

        print(f"[ERROR] Falha ao salvar: {error_msg}")
        return jsonify({'success': False, 'message': error_msg}), 500
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atualizar_resultado', methods=['POST'])
def atualizar_resultado_api():
    """Endpoint para atualizar resultado de um jogo"""
    try:
        data = request.get_json()
        jogo_id = data.get('id') if data else None
        if jogo_id is None:
            jogo_id = data.get('jogo_id') if data else None
        gh = data.get('gh')
        ga = data.get('ga')
        lp = data.get('lp')
        
        if jogo_id is None or gh is None or ga is None:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Verificar se há jogos salvos
        salvos_file = Path(__file__).parent / 'fixtures' / 'jogos_salvos.json'
        if not salvos_file.exists():
            return jsonify({'success': False, 'message': 'Nenhum jogo salvo encontrado. Salve jogos primeiro em Próximos Jogos.'}), 404
        
        try:
            with open(salvos_file, 'r', encoding='utf-8') as f:
                jogos_salvos = json.load(f)
        except json.JSONDecodeError:
            try:
                with open(salvos_file, 'r', encoding='utf-8-sig') as f:
                    jogos_salvos = json.load(f)
                with open(salvos_file, 'w', encoding='utf-8') as f:
                    json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
            except Exception:
                return jsonify({'success': False, 'message': 'Erro ao ler arquivo de jogos salvos'}), 500

        if not jogos_salvos:
            return jsonify({'success': False, 'message': 'Nenhum jogo salvo encontrado. Salve jogos primeiro em Próximos Jogos.'}), 404
        
        # Executar o script de atualização
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        args = [sys.executable, 'salvar_jogo.py', 'atualizar', str(jogo_id), str(gh), str(ga)]
        if lp is not None:
            args.append(str(lp))

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            env=env
        )
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Resultado atualizado com sucesso!'})
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            if 'nao encontrado' in error_msg.lower():
                return jsonify({'success': False, 'message': f'Jogo ID {jogo_id} não encontrado. Verifique o ID do jogo.'}), 404
            return jsonify({'success': False, 'message': error_msg}), 500
            return jsonify({'success': False, 'message': error_msg}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/gerar_pagina_salvos', methods=['POST'])
def gerar_pagina_salvos_api():
    """Endpoint para gerar a página de jogos salvos"""
    try:
        # Executar o script de geração
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, 'salvar_jogo.py', 'gerar'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            env=env
        )
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Página gerada com sucesso!'})
        else:
            return jsonify({'success': False, 'message': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/excluir_jogo', methods=['POST'])
def excluir_jogo_api():
    """Endpoint para excluir um jogo salvo"""
    try:
        data = request.get_json()
        jogo_id = data.get('id') if data else None
        if jogo_id is None:
            jogo_id = data.get('jogo_id') if data else None

        if jogo_id is None:
            return jsonify({'success': False, 'message': 'ID nao fornecido'}), 400

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, 'salvar_jogo.py', 'excluir', str(jogo_id)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            env=env
        )

        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Jogo excluido com sucesso!'}), 200

        error_msg = result.stderr if result.stderr else result.stdout
        return jsonify({'success': False, 'message': error_msg}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/salvar_backtest_json', methods=['POST'])
def salvar_backtest_json_api():
    """Endpoint para salvar dados do backtest em arquivo JSON (sem duplicatas)"""
    try:
        data = request.get_json()
        novos_dados = data.get('entradas', data.get('dados', [])) if data else []
        
        print(f"DEBUG API: Recebidos {len(novos_dados)} entradas para salvar", flush=True)
        
        # Contar ligas e entradas por liga dos novos dados
        ligas_count = {}
        for entrada in novos_dados:
            liga = entrada.get('liga', 'Desconhecida')
            ligas_count[liga] = ligas_count.get(liga, 0) + 1
        print(f"DEBUG API: Ligas presentes: {ligas_count}", flush=True)
        
        # Caminho do arquivo
        backtest_file = Path("fixtures/backtest_acumulado.json")
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
        # Chave: liga|temporada|date|home|away
        def criar_chave(entrada):
            return f"{entrada.get('liga', '')}|{entrada.get('temporada', '')}|{entrada.get('date', '')}|{entrada.get('home', '')}|{entrada.get('away', '')}"
        
        # Mapear dados existentes por chave
        dados_map = {criar_chave(e): e for e in dados_existentes}
        print(f"DEBUG API: {len(dados_map)} entradas únicas no arquivo existente", flush=True)
        
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
        
        print(f"DEBUG API: Novos adicionados: {novos_adicionados}, Duplicatas substituídas: {duplicatas_substituidas}", flush=True)
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
        print(f"DEBUG API: Erro ao salvar backtest JSON: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/backtest_acumulado', methods=['GET', 'OPTIONS'])
def carregar_backtest_acumulado_api():
    """Endpoint para carregar backtest acumulado salvo em arquivo JSON com desconto de 4,5% aplicado"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        backtest_file = Path("fixtures/backtest_acumulado.json")
        if not backtest_file.exists():
            return jsonify({'success': True, 'entradas': [], 'message': 'Arquivo não encontrado'}), 200

        with open(backtest_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Mapear nomes de campos do JSON para o formato esperado pelo HTML e aplicar desconto
        dados_mapeados = []
        for jogo in dados:
            lp_original = float(jogo.get('lp', 0))
            lp_com_desconto = aplicar_desconto_lucro(lp_original)
            
            jogo_mapeado = {
                'data': jogo.get('data', ''),  # Pode estar vazio no JSON original
                'liga': jogo.get('liga', 'ARG'),
                'casa': jogo.get('home', 'Unknown'),
                'visitante': jogo.get('away', 'Unknown'),
                'gc': jogo.get('fthg', 0),  # Full Time Home Goals
                'gv': jogo.get('ftag', 0),  # Full Time Away Goals
                'odd_casa': jogo.get('b365h', jogo.get('odd_home_calc', 0)),  # Bet365 Home ou odd calculada
                'odd_visitante': jogo.get('b365a', jogo.get('odd_away_calc', 0)),  # Bet365 Away
                'xg_casa': jogo.get('xgh', 0),  # xG Home
                'xg_visitante': jogo.get('xga', 0),  # xG Away
                'dxg': jogo.get('dxg', 'EQ'),  # Diferença xG
                'entrada': jogo.get('entrada', 'HOME'),
                'lp': lp_com_desconto,  # Lucro com desconto aplicado
                'temporada': jogo.get('temporada', '2024-25')
            }
            dados_mapeados.append(jogo_mapeado)

        return jsonify({
            'success': True,
            'entradas': dados_mapeados,
            'total': len(dados_mapeados)
        }), 200
    except Exception as e:
        print(f"DEBUG API: Erro ao carregar backtest acumulado: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analisar_ia', methods=['POST'])
def analisar_ia_api():
    """Endpoint de análise DxG simplificada de jogos salvos"""
    print(">>> ENDPOINT /api/analisar_ia CHAMADO <<<", flush=True)
    try:
        print("DEBUG API: Requisição para análise DxG de jogos salvos", flush=True)
        
        # Importar nova função de análise DxG
        from salvar_jogo import analisar_dxg_e_odds
        import json
        from pathlib import Path
        
        # Carregar dados dos jogos salvos
        salvos_file = Path("fixtures") / "jogos_salvos.json"
        if not salvos_file.exists():
            print("DEBUG API: Arquivo jogos_salvos.json não encontrado", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum jogo salvo encontrado'}), 400
        
        with open(salvos_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        print(f"DEBUG API: Carregados {len(dados)} jogos salvos", flush=True)
        
        # Executar análise
        analise = analisar_dxg_e_odds(dados)
        
        if analise:
            print(f"DEBUG API: Análise completa! Resumo: {analise.get('resumo', 'N/A')}", flush=True)
            print(f"DEBUG API: Insights: {len(analise.get('insights', []))}", flush=True)
            print(f"DEBUG API: Recomendações: {len(analise.get('recomendacoes', []))}", flush=True)
            return jsonify({'success': True, 'data': analise}), 200
        else:
            print("DEBUG API: Análise retornou None", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum dado disponível para análise'}), 400
            
    except Exception as e:
        print(f"DEBUG API: Exception no endpoint: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analisar_padroes_jogos', methods=['POST'])
def analisar_padroes_jogos_api():
    """Endpoint para analisar padroes de JOGOS SALVOS (fixtures) com IA"""
    return jsonify({'debug': 'OK'}), 200

@app.route('/api/analisar_padroes_backtest', methods=['POST'])
def analisar_padroes_backtest_api():
    """Endpoint para analisar padrões de BACKTESTS SALVOS com IA"""
    try:
        print("DEBUG API: Iniciando análise de BACKTESTS SALVOS com IA...", flush=True)
        
        data = request.get_json()
        salvamento = data.get('salvamento', '') if data else ''
        dados = data.get('dados', []) if data else []
        
        print(f"DEBUG API: Salvamento: {salvamento}, Total de entradas: {len(dados)}", flush=True)
        
        # Importar e executar função diretamente
        from salvar_jogo import analisar_padroes_ia
        
        print("DEBUG API: Executando análise de backtest salvo...", flush=True)
        # A função vai ler automaticamente de fixtures/backtest_acumulado.json
        analise = analisar_padroes_ia()
        
        if analise:
            print(f"DEBUG API: Análise de backtest completa!", flush=True)
            return jsonify({'success': True, 'data': analise}), 200
        else:
            print("DEBUG API: Análise retornou None", flush=True)
            return jsonify({'success': False, 'message': 'Nenhum dado disponível para análise'}), 400
            
    except Exception as e:
        print(f"DEBUG API: Exception na análise de backtest: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atualizar_proxima_rodada', methods=['POST'])
def atualizar_proxima_rodada():
    """
    Endpoint que executa o script buscar_proxima_rodada.py para atualizar dados
    """
    try:
        print("Iniciando busca de dados da próxima rodada...")
        
        # Executar o script Python
        resultado = subprocess.run(
            [sys.executable, 'buscar_proxima_rodada.py'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if resultado.returncode == 0:
            # Script executado com sucesso
            print("✓ Busca de dados concluída com sucesso")
            print("stdout:", resultado.stdout)
            return jsonify({
                'success': True, 
                'message': 'Dados da próxima rodada atualizados com sucesso!',
                'output': resultado.stdout
            })
        else:
            # Script retornou erro
            error_msg = resultado.stderr or resultado.stdout or "Erro desconhecido"
            print(f"✗ Erro ao executar buscar_proxima_rodada.py: {error_msg}")
            return jsonify({
                'success': False,
                'message': 'Nenhum dado disponível no momento. Tente novamente em alguns instantes.',
                'error': error_msg
            }), 200
            
    except subprocess.TimeoutExpired:
        print("✗ Timeout ao buscar dados da próxima rodada")
        return jsonify({
            'success': False,
            'message': 'A busca demorou muito tempo. Tente novamente.'
        }), 504
    except Exception as e:
        print(f"✗ Erro ao buscar dados da próxima rodada: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar dados. Verifique se os dados estão disponíveis no football-data.'
        }), 500

@app.route('/api/jogos_salvos', methods=['GET', 'OPTIONS'])
def carregar_jogos_salvos_api():
    """Endpoint para carregar jogos salvos com desconto de 4,5% aplicado"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        jogos_file = FIXTURES_DIR / 'jogos_salvos.json'
        if not jogos_file.exists():
            return jsonify({'success': True, 'jogos': [], 'message': 'Arquivo não encontrado'}), 200

        with open(jogos_file, 'r', encoding='utf-8') as f:
            jogos = json.load(f)

        # Aplicar desconto de 4,5% em todos os lucros
        jogos_com_desconto = []
        for jogo in jogos:
            jogo_copia = jogo.copy()
            
            # Aplicar desconto ao campo LP ou similarmente nomeado
            if 'LP' in jogo_copia:
                lp_original = float(jogo_copia.get('LP', 0))
                jogo_copia['LP'] = aplicar_desconto_lucro(lp_original)
            elif 'lp' in jogo_copia:
                lp_original = float(jogo_copia.get('lp', 0))
                jogo_copia['lp'] = aplicar_desconto_lucro(lp_original)
            
            jogos_com_desconto.append(jogo_copia)

        return jsonify({
            'success': True,
            'jogos': jogos_com_desconto,
            'total': len(jogos_com_desconto)
        }), 200
    except Exception as e:
        print(f"DEBUG API: Erro ao carregar jogos salvos: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("="*80)
    print("Servidor API iniciado em http://localhost:8000")
    print("Endpoints disponíveis:")
    print("  POST /api/salvar_jogo - Salvar um jogo")
    print("  POST /api/atualizar_resultado - Atualizar resultado de um jogo")
    print("  POST /api/gerar_pagina_salvos - Gerar página de jogos salvos")
    print("  POST /api/analisar_padroes_jogos - Analisar padrões de jogos salvos")
    print("  POST /api/analisar_padroes_backtest - Analisar padrões de backtests")
    print("  POST /api/atualizar_proxima_rodada - Buscar dados da próxima rodada")
    print("="*80)
    app.run(debug=False, port=8000)
