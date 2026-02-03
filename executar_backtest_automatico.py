#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar backtests automaticamente para todas as ligas e temporadas
De 2020 até a data atual (2026-02-01)
Salva resultados automaticamente após cada temporada
"""

import sys
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

# Adicionar pasta backtest ao path
sys.path.insert(0, str(Path(__file__).parent / 'backtest'))

from backtest_engine import BacktestEngine

# Ligas disponíveis
LIGAS = {
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

# Mapa de tradução: conversão de nomes em português para códigos de endpoint
MAPA_TRADUCAO = {
    'Bélgica': 'B1',
    'Alemanha': 'D1',
    'Inglaterra': 'E0',
    'França': 'F1',
    'Grécia': 'G1',
    'Itália': 'I1',
    'Holanda': 'N1',
    'Portugal': 'P1',
    'Espanha': 'SP1',
    'Turquia': 'T1',
    'Argentina': 'ARG',
    'Áustria': 'AUT',
    'Brasil': 'BRA',
    'China': 'CHN',
    'Dinamarca': 'DNK',
    'Finlândia': 'FIN',
    'Irlanda': 'IRL',
    'Japão': 'JPN',
    'México': 'MEX',
    'Noruega': 'NOR',
    'Polônia': 'POL',
    'Romênia': 'ROU',
    'Rússia': 'RUS',
    'Suécia': 'SWE',
    'Suíça': 'SWZ',
    'EUA': 'USA',
}

# Temporadas para processar
ANOS = list(range(2020, 2027))  # 2020 a 2026

# Cache de temporadas por liga (evita reler CSV a cada ano)
_CACHE_TEMPORADAS = {}

# Relatório de progresso
relatorio = {
    'data_inicio': datetime.now().isoformat(),
    'ligas_processadas': 0,
    'temporadas_processadas': 0,
    'erros': [],
    'sucesso': [],
}


def deve_parar_execucao():
    """Verifica se arquivo de parada foi criado"""
    arquivo_parada = Path(__file__).parent / 'PARAR_BACKTEST.stop'
    return arquivo_parada.exists()


def limpar_arquivo_parada():
    """Remove arquivo de parada"""
    arquivo_parada = Path(__file__).parent / 'PARAR_BACKTEST.stop'
    if arquivo_parada.exists():
        arquivo_parada.unlink()


def gerar_temporadas(ano):
    """Gera formato de temporada para cada ano"""
    return [
        f"{ano}-{str(ano+1)[-2:]}",      # 2024-25
        f"{ano}/{ano+1}",                # 2024/2025
        str(ano),                         # 2024
    ]


def _detectar_coluna_data(df):
    """Detecta a coluna de data"""
    for col in df.columns:
        if 'date' in col.lower():
            return col
    return None


def _detectar_coluna_season(df):
    """Detecta a coluna de temporada/season"""
    for col in df.columns:
        if 'season' in col.lower():
            return col
    for col in df.columns:
        if col.lower() in ['year', 'yr', 'ano']:
            return col
    return None


def _detectar_formato_temporada(df, coluna_season):
    """Detecta o formato de temporada (YYYY/YYYY ou YYYY)"""
    if coluna_season is None or coluna_season not in df.columns:
        return 'YYYY'

    samples = df[coluna_season].dropna().astype(str).unique()[:10]
    separador_count = sum(1 for s in samples if '/' in s)
    apenas_ano_count = sum(1 for s in samples if s.isdigit() and len(s) == 4)

    return 'YYYY/YYYY' if separador_count > apenas_ano_count else 'YYYY'


def _gerar_padroes_temporada(temporada, formato_detectado):
    """Gera padrões de busca para temporada"""
    padroes = []

    if '-' in temporada and len(temporada.split('-')[1]) == 2:
        ano_inicio = temporada.split('-')[0]
        ano_fim = temporada.split('-')[1]

        if formato_detectado == 'YYYY/YYYY':
            padroes.append(f"{ano_inicio}/20{ano_fim}")  # 2024/2025
            padroes.append(f"{ano_inicio}/{ano_fim}")    # 2024/25
            padroes.append(f"{ano_inicio}-20{ano_fim}")  # 2024-2025
            padroes.append(f"{ano_inicio}-{ano_fim}")    # 2024-25
        else:
            padroes.append(f"{ano_inicio}")              # 2024
            padroes.append(f"20{ano_fim}")               # 2025
            padroes.append(f"{ano_inicio}/20{ano_fim}")  # fallback

        padroes.append(temporada)

    elif len(temporada) == 4 and temporada.isdigit():
        ano = temporada

        if formato_detectado == 'YYYY/YYYY':
            padroes.append(f"{ano}/{int(ano)+1}")
            padroes.append(f"{int(ano)-1}/{ano}")
        else:
            padroes.append(ano)
            padroes.append(str(int(ano)+1))

        padroes.append(ano)

    elif '/' in temporada:
        ano_inicio, ano_fim = temporada.split('/')
        padroes.append(temporada)
        padroes.append(f"{ano_inicio}-{ano_fim[-2:]}")
        padroes.append(f"{ano_inicio}-{ano_fim}")

    return padroes


def _carregar_temporadas_disponiveis(liga):
    """Carrega e cacheia as temporadas disponíveis para a liga"""
    if liga in _CACHE_TEMPORADAS:
        return _CACHE_TEMPORADAS[liga]

    projeto_root = Path(__file__).parent
    arquivo_original = projeto_root / 'dados_ligas' / f'{liga}_completo.csv'
    if not arquivo_original.exists():
        arquivo_original = projeto_root / 'dados_ligas_new' / f'{liga}.csv'

    if not arquivo_original.exists():
        _CACHE_TEMPORADAS[liga] = ([], None, 'YYYY')
        return _CACHE_TEMPORADAS[liga]

    try:
        df_cols = pd.read_csv(arquivo_original, nrows=0)
        coluna_season = _detectar_coluna_season(df_cols)

        if coluna_season is None:
            _CACHE_TEMPORADAS[liga] = ([], None, 'YYYY')
            return _CACHE_TEMPORADAS[liga]

        df_seasons = pd.read_csv(arquivo_original, usecols=[coluna_season], low_memory=False)
        df_seasons[coluna_season] = df_seasons[coluna_season].astype(str).str.strip()
        temporadas = sorted(df_seasons[coluna_season].dropna().unique().tolist())

        formato = _detectar_formato_temporada(df_seasons, coluna_season)

        _CACHE_TEMPORADAS[liga] = (temporadas, coluna_season, formato)
        return _CACHE_TEMPORADAS[liga]

    except Exception:
        _CACHE_TEMPORADAS[liga] = ([], None, 'YYYY')
        return _CACHE_TEMPORADAS[liga]


def _resolver_temporada_real(liga, ano):
    """Resolve a temporada real existente no CSV para o ano informado"""
    temporadas, _, formato = _carregar_temporadas_disponiveis(liga)
    if not temporadas:
        return None

    temporada_base = f"{ano}-{str(ano+1)[-2:]}"
    padroes = _gerar_padroes_temporada(temporada_base, formato)

    for padrao in padroes:
        if padrao in temporadas:
            return padrao

    return None


def recriar_arquivo_treino(liga, temporada):
    """Recria o arquivo de treino usando todos os jogos antes da temporada informada"""
    projeto_root = Path(__file__).parent
    arquivo_original = projeto_root / 'dados_ligas' / f'{liga}_completo.csv'
    if not arquivo_original.exists():
        arquivo_original = projeto_root / 'dados_ligas_new' / f'{liga}.csv'

    arquivo_treino = projeto_root / 'backtest' / f'{liga}_treino.csv'

    if not arquivo_original.exists():
        print(f"  ⚠️  Arquivo original não encontrado para {liga}: {arquivo_original}")
        return False

    try:
        df = pd.read_csv(arquivo_original, low_memory=False)
        coluna_data = _detectar_coluna_data(df)
        coluna_season = _detectar_coluna_season(df)

        if coluna_data is None:
            print(f"  ⚠️  Coluna de data não encontrada para {liga}")
            return False

        df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
        df = df.dropna(subset=[coluna_data])

        # Descobrir data de início da temporada
        season_start = None
        if coluna_season and coluna_season in df.columns:
            formato = _detectar_formato_temporada(df, coluna_season)
            padroes = _gerar_padroes_temporada(temporada, formato)
            temporada_df = df[df[coluna_season].astype(str).str.strip().isin(padroes)].copy()

            if temporada_df.empty:
                print(f"  ⚠️  Temporada '{temporada}' não encontrada para {liga}. Pulando.")
                return False

            season_start = temporada_df[coluna_data].min()
        else:
            # Fallback: usar ano como referência
            ano = ''.join(ch for ch in temporada if ch.isdigit())[:4]
            if len(ano) == 4:
                season_start = pd.to_datetime(f"{ano}-01-01")
            else:
                print(f"  ⚠️  Não foi possível inferir a temporada para {liga}. Pulando.")
                return False

        df_treino = df[df[coluna_data] < season_start].copy()
        df_treino = df_treino.sort_values(coluna_data)
        df_treino.to_csv(arquivo_treino, index=False)

        print(f"  ✅ Treino recriado: {liga} até {season_start.date()} ({len(df_treino)} jogos)")
        return True

    except Exception as e:
        print(f"  ❌ Erro ao recriar treino para {liga} - {temporada}: {e}")
        return False


def processar_backtest(liga, temporada):
    """Processa backtest para uma liga e temporada específicas"""
    try:
        print(f"\n{'='*80}")
        print(f"🔵 Processando: {liga} - Temporada {temporada}")
        print(f"{'='*80}")

        # Recriar arquivo de treino com base nos jogos ANTERIORES à temporada
        if not recriar_arquivo_treino(liga, temporada):
            print(f"  ⚠️  Treino não foi recriado para {liga} - {temporada}. Pulando temporada.")
            return False
        
        # Criar engine
        engine = BacktestEngine(liga=liga, temporada=temporada)
        
        # Calcular limite máximo de rodadas (baseado em total de jogos)
        total_jogos = len(engine.df_teste)
        
        if total_jogos == 0:
            print(f"  ⚠️  Nenhum jogo encontrado para {liga} - {temporada}")
            return False
        
        # Limite seguro: número de times * 4 (em vez de apenas num_times * 2)
        # Para 20 times: 20*4 = 80 rodadas máximo (margem de segurança)
        max_rodadas = (engine.num_times * 4) if engine.num_times > 0 else 100
        
        print(f"  📊 Total de jogos: {total_jogos}, Máximo de rodadas esperado: {max_rodadas}")
        
        # Processar todas as rodadas com proteção contra loop infinito
        rodada_count = 0
        jogos_processados_anterior = 0
        rodadas_sem_progresso = 0
        
        while not engine.resultados.get('completo', False):
            # PROTEÇÃO 1: Limite máximo de iterações
            if rodada_count >= max_rodadas:
                print(f"  ⚠️  ATENÇÃO: Limite de {max_rodadas} rodadas atingido. Forçando conclusão.")
                engine.resultados['completo'] = True
                break
            
            # Processar rodada
            resultado = engine.processar_rodada()
            rodada_count += 1
            
            # PROTEÇÃO 2: Detectar se está progredindo
            jogos_processados_atual = engine.resultados.get('jogos_processados', 0)
            if jogos_processados_atual == jogos_processados_anterior:
                rodadas_sem_progresso += 1
                if rodadas_sem_progresso >= 10:
                    print(f"  ⚠️  ATENÇÃO: 10 rodadas sem progresso. Possível loop infinito. Forçando conclusão.")
                    engine.resultados['completo'] = True
                    break
            else:
                rodadas_sem_progresso = 0
            
            jogos_processados_anterior = jogos_processados_atual
            
            # Mostrar progresso
            if rodada_count % 5 == 0:
                print(f"  ✓ Rodadas: {rodada_count}, Jogos processados: {jogos_processados_atual}/{total_jogos}")
        
        # Salvar resultados
        engine.salvar_resultados()
        
        # Salvar também no arquivo acumulado
        salvar_em_acumulado(engine)
        
        info = {
            'liga': liga,
            'temporada': temporada,
            'rodadas': rodada_count,
            'total_jogos': len(engine.df_teste),
            'acertos': engine.resultados.get('acertos', 0),
            'erros': engine.resultados.get('erros', 0),
            'winrate': engine.resultados.get('winrate', 0),
            'roi': engine.resultados.get('roi', 0),
            'lucro': engine.resultados.get('lucro_total', 0),
            'timestamp': datetime.now().isoformat(),
        }
        
        print(f"✅ Sucesso: {liga} - {temporada}")
        print(f"   Rodadas: {rodada_count}, Jogos: {info['total_jogos']}, ROI: {info['roi']:.1f}%")
        
        relatorio['sucesso'].append(info)
        return True
        
    except Exception as e:
        erro_msg = f"{liga} - {temporada}: {str(e)}"
        print(f"❌ Erro: {erro_msg}")
        relatorio['erros'].append({
            'liga': liga,
            'temporada': temporada,
            'erro': str(e),
            'timestamp': datetime.now().isoformat(),
        })
        return False


def salvar_em_acumulado(engine):
    """Salva resultados também no arquivo acumulado"""
    try:
        arquivo_acumulado = Path(__file__).parent / 'fixtures' / 'backtest_acumulado.json'
        
        # Carregar dados existentes
        if arquivo_acumulado.exists():
            with open(arquivo_acumulado, 'r', encoding='utf-8') as f:
                dados_acumulados = json.load(f)
        else:
            dados_acumulados = []
        
        # Adicionar entradas do backtest atual
        if 'entradas' in engine.resultados:
            for entrada in engine.resultados['entradas']:
                # Adicionar informações da liga e temporada
                entrada_completa = entrada.copy()
                entrada_completa['liga'] = engine.liga
                entrada_completa['temporada'] = engine.temporada
                
                # Verificar se não é duplicada (por data, times e temporada)
                # Usar campos corretos: 'home'/'away' em vez de 'casa'/'visitante'
                existe = False
                for e_existente in dados_acumulados:
                    if (e_existente.get('home') == entrada_completa.get('home') and
                        e_existente.get('away') == entrada_completa.get('away') and
                        e_existente.get('temporada') == entrada_completa.get('temporada')):
                        existe = True
                        break
                
                if not existe:
                    dados_acumulados.append(entrada_completa)
        
        # Salvar
        with open(arquivo_acumulado, 'w', encoding='utf-8') as f:
            json.dump(dados_acumulados, f, ensure_ascii=False, indent=2)
        
        print(f"   📁 Dados salvos em arquivo acumulado ({len(dados_acumulados)} entradas)")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao salvar em arquivo acumulado: {e}")


def gerar_relatorio_final():
    """Gera relatório final de execução"""
    relatorio['data_fim'] = datetime.now().isoformat()
    relatorio['ligas_processadas'] = len(set(s['liga'] for s in relatorio['sucesso']))
    relatorio['temporadas_processadas'] = len(relatorio['sucesso'])
    
    # Salvar relatório
    arquivo_relatorio = Path(__file__).parent / 'relatorio_backtest_automatico.json'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*80}")
    print(f"Ligas processadas: {relatorio['ligas_processadas']}")
    print(f"Temporadas processadas: {relatorio['temporadas_processadas']}")
    print(f"Sucessos: {len(relatorio['sucesso'])}")
    print(f"Erros: {len(relatorio['erros'])}")
    print(f"Tempo total: {(datetime.fromisoformat(relatorio['data_fim']) - datetime.fromisoformat(relatorio['data_inicio'])).total_seconds() / 60:.1f} minutos")
    print(f"Relatório salvo em: {arquivo_relatorio}")
    
    if relatorio['erros']:
        print(f"\n⚠️  Erros encontrados:")
        for erro in relatorio['erros'][:5]:  # Mostrar primeiros 5
            print(f"   - {erro['liga']} ({erro['temporada']}): {erro['erro'][:60]}...")


def main():
    """Função principal"""
    print(f"{'='*80}")
    print("🚀 SISTEMA DE BACKTEST AUTOMÁTICO")
    print(f"{'='*80}")
    print(f"Ligas: {len(LIGAS)}")
    print(f"Temporadas: {len(ANOS)} anos (2020-2026)")
    print(f"Total de combinações: ~{len(LIGAS) * len(ANOS)} (1 temporada por ano)")
    print(f"Hora de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"💡 Dica: Para parar a execução graciosamente, crie um arquivo 'PARAR_BACKTEST.stop'")
    print(f"         ou pressione Ctrl+C")
    print(f"{'='*80}\n")
    
    # Limpar arquivo de parada anterior
    limpar_arquivo_parada()
    
    input("Pressione ENTER para iniciar ou Ctrl+C para cancelar...")
    
    tempo_inicio = time.time()
    
    # Processar cada liga
    for idx_liga, (codigo_liga, nome_liga) in enumerate(sorted(LIGAS.items()), 1):
        # VERIFICAÇÃO: Parada segura entre ligas
        if deve_parar_execucao():
            print(f"\n\n🛑 Parada solicitada via arquivo PARAR_BACKTEST.stop")
            break
        
        print(f"\n{'#'*80}")
        print(f"LIGA {idx_liga}/{len(LIGAS)}: {codigo_liga} - {nome_liga}")
        print(f"{'#'*80}")
        
        # Pré-carregar temporadas disponíveis da liga
        _carregar_temporadas_disponiveis(codigo_liga)
        temporadas_processadas = set()

        # Processar cada ano
        for idx_ano, ano in enumerate(ANOS, 1):
            # VERIFICAÇÃO: Parada segura entre anos também
            if deve_parar_execucao():
                print(f"\n\n🛑 Parada solicitada via arquivo PARAR_BACKTEST.stop")
                break
            
            print(f"\n  [{idx_ano}/{len(ANOS)}] Ano {ano}")
            
            # Resolver temporada real no CSV para este ano
            temporada_real = _resolver_temporada_real(codigo_liga, ano)

            if not temporada_real:
                if ano != ANOS[-1]:
                    print(f"  ⚠️  Temporada não encontrada para {codigo_liga} - {ano}")
                continue

            if temporada_real in temporadas_processadas:
                print(f"  ⚠️  Temporada já processada (evitando duplicação): {codigo_liga} - {temporada_real}")
                continue

            if processar_backtest(codigo_liga, temporada_real):
                temporadas_processadas.add(temporada_real)
            else:
                print(f"  ⚠️  Falha ao processar: {codigo_liga} - {temporada_real}")
            
            # Pausa entre processamentos
            time.sleep(0.5)
        
        # Quebra do loop externo se parada foi solicitada
        if deve_parar_execucao():
            break
    
    tempo_total = time.time() - tempo_inicio
    
    # Gerar relatório
    gerar_relatorio_final()
    
    # Limpar arquivo de parada
    limpar_arquivo_parada()
    
    print(f"\n✅ Processamento concluído em {tempo_total/60:.1f} minutos!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Execução cancelada pelo usuário")
        limpar_arquivo_parada()
        gerar_relatorio_final()
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        limpar_arquivo_parada()
        import traceback
        traceback.print_exc()
