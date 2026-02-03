import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class BacktestEngine:
    def __init__(self, liga='E0', temporada='2024-25'):
        self.pasta_backtest = Path(__file__).parent
        self.liga = liga
        self.temporada = temporada  # NOVO: Armazenar temporada selecionada
        
        # Arquivos para a liga selecionada
        self.arquivo_original = self.pasta_backtest.parent / 'dados_ligas' / f'{liga}_completo.csv'
        if not self.arquivo_original.exists():
            self.arquivo_original = self.pasta_backtest.parent / 'dados_ligas_new' / f'{liga}.csv'
        
        self.arquivo_treino = self.pasta_backtest / f'{liga}_treino.csv'
        # MODIFICADO: Incluir temporada no nome do arquivo para separar backtests
        temporada_safe = temporada.replace('/', '-').replace('\\', '-')  # Seguro para nome de arquivo
        self.arquivo_resultados = self.pasta_backtest / f'backtest_resultados_{liga}_{temporada_safe}.json'
        
        # Carregar dados
        self.df_original = pd.read_csv(self.arquivo_original, low_memory=False)
        self.df_treino = pd.read_csv(self.arquivo_treino, low_memory=False)
        
        # Detectar colunas
        self.coluna_season = self._detectar_coluna_season()
        self.coluna_data = self._detectar_coluna_data()
        self.coluna_home = self._detectar_coluna('home|hometeam')
        self.coluna_away = self._detectar_coluna('away|awayteam')
        self.coluna_gols_home = self._detectar_coluna('fthg|hg')
        self.coluna_gols_away = self._detectar_coluna('ftag|ag')
        self.coluna_odds_home, self.coluna_odds_away = self._detectar_colunas_odds()
        
        # Detectar formato de temporada (YYYY/YYYY ou YYYY)
        self.formato_temporada = self._detectar_formato_temporada()
        print(f"🔵 [BacktestEngine] Formato de temporada detectado para {liga}: {self.formato_temporada}")
        
        # Filtrar apenas temporada 2024/2025 (ou equivalente)
        self.df_teste = self._filtrar_temporada_teste()
        
        # Converter data e ordenar cronologicamente
        self.df_teste['Date_dt'] = pd.to_datetime(self.df_teste[self.coluna_data], errors='coerce')
        self.df_teste = self.df_teste.sort_values('Date_dt').reset_index(drop=True)
        
        # Detectar número de equipes e jogos por rodada
        self.num_times = self._contar_equipes()
        self.max_jogos_rodada = self._detectar_max_jogos_rodada()
        
        # Estado do backtest
        self.resultados = self._carregar_resultados()

        # Garantir total_jogos atualizado para a temporada atual
        if self.resultados.get('total_jogos') != len(self.df_teste):
            self.resultados['total_jogos'] = len(self.df_teste)
            self._salvar_resultados()
        
    def _detectar_coluna(self, padroes):
        """Detecta coluna por padrão (case-insensitive)"""
        # Padrões específicos para melhor detecção
        patterns = {
            'home|hometeam': ['HomeTeam', 'Home'],
            'away|awayteam': ['AwayTeam', 'Away'],
            'fthg|hg': ['FTHG', 'HG'],
            'ftag|ag': ['FTAG', 'AG'],
        }
        
        # Verificar se temos um padrão específico
        for col in self.df_original.columns:
            col_upper = col.upper()
            col_lower = col.lower()
            
            for padrao in padroes.split('|'):
                padrao_lower = padrao.lower()
                
                # Correspondência exata prioritária
                if col_upper == padrao_lower.upper() or col_lower == padrao_lower:
                    return col
        
        # Caso 2: Correspondência parcial, mas evitar falsos positivos
        for col in self.df_original.columns:
            col_lower = col.lower()
            for padrao in padroes.split('|'):
                # Para colunas de gols, apenas palavras curtas
                if padrao in ['hg', 'ag', 'fthg', 'ftag']:
                    # Apenas colunas que terminam com a letra ou começam com F/H/A
                    if col_lower.startswith('f') or len(col_lower) <= 4:
                        if padrao in col_lower:
                            return col
                else:
                    # Para outras colunas (home, away)
                    if padrao in col_lower and 'league' not in col_lower and 'country' not in col_lower:
                        return col
        
        return None
    
    def _detectar_coluna_season(self):
        """Detecta a coluna de temporada/season"""
        for col in self.df_original.columns:
            if 'season' in col.lower():
                return col
        return 'Season'  # Padrão
    
    def _detectar_coluna_data(self):
        """Detecta a coluna de data"""
        for col in self.df_original.columns:
            if 'date' in col.lower():
                return col
        return 'Date'  # Padrão
    
    def _detectar_formato_temporada(self):
        """Detecta o formato de temporada usado no CSV (YYYY/YYYY ou YYYY)"""
        try:
            # Pegar algumas amostras de valores de season
            samples = self.df_original[self.coluna_season].unique()[:10]
            
            separador_count = 0
            apenas_ano_count = 0
            
            for sample in samples:
                sample_str = str(sample).strip()
                if '/' in sample_str:
                    separador_count += 1
                elif sample_str.isdigit() and len(sample_str) == 4:
                    apenas_ano_count += 1
            
            # Determinar formato baseado na amostragem
            if separador_count > apenas_ano_count:
                print(f"🔵 [BacktestEngine] Análise: {separador_count} com '/', {apenas_ano_count} apenas ano")
                return 'YYYY/YYYY'
            else:
                print(f"🔵 [BacktestEngine] Análise: {separador_count} com '/', {apenas_ano_count} apenas ano")
                return 'YYYY'
        except Exception as e:
            print(f"⚠️  [BacktestEngine] Erro ao detectar formato temporada: {e}")
            return 'YYYY/YYYY'  # Padrão seguro
    
    def _detectar_colunas_odds(self):
        """Detecta colunas de odds para home e away"""
        # Procurar por B365H/B365A (padrão) ou PSCH/PSCA (outras ligas)
        cols_home = [col for col in self.df_original.columns if 'b365h' in col.lower() or ('psch' in col.lower() and 'pscd' not in col.lower())]
        cols_away = [col for col in self.df_original.columns if 'b365a' in col.lower() or ('psca' in col.lower() and 'pscd' not in col.lower())]
        
        # Se não encontrou, procurar por padrões mais gerais
        if not cols_home:
            cols_home = [col for col in self.df_original.columns if col.upper().endswith('H') and 'home' not in col.lower()]
        if not cols_away:
            cols_away = [col for col in self.df_original.columns if col.upper().endswith('A') and 'away' not in col.lower()]
        
        coluna_home = cols_home[0] if cols_home else 'B365H'
        coluna_away = cols_away[0] if cols_away else 'B365A'
        
        return coluna_home, coluna_away
    def _filtrar_temporada_teste(self):
        """Filtra dados da temporada especificada - APENAS ATÉ A DATA ATUAL"""
        df = self.df_original.copy()
        
        print(f"\n{'='*80}")
        print(f"🔵 [BacktestEngine] Filtrando temporada: {self.temporada}")
        print(f"🔵 [BacktestEngine] Total de jogos no dataset: {len(df)}")
        print(f"🔵 [BacktestEngine] Coluna de temporada: {self.coluna_season}")
        
        # Data atual (1º de fevereiro de 2026)
        data_atual = pd.to_datetime('2026-02-01')
        print(f"🔵 [BacktestEngine] Data limite (hoje): {data_atual.date()}")
        
        # Mostrar valores únicos de temporada disponíveis
        try:
            temporadas_disponiveis = sorted(df[self.coluna_season].unique())
            print(f"🔵 [BacktestEngine] Temporadas disponíveis no CSV: {temporadas_disponiveis}")
        except:
            print(f"⚠ [BacktestEngine] Não foi possível listar temporadas disponíveis")
        
        # Converter temporada do formato YYYY-YY ou YYYY para padrões de busca
        padroes = self._gerar_padroes_temporada(self.temporada)
        
        # Tentar encontrar dados com os padrões gerados
        serie_season = df[self.coluna_season].astype(str).str.strip()
        for padrao in padroes:
            try:
                padrao_str = str(padrao).strip()
                resultado = df[serie_season == padrao_str]
                if len(resultado) > 0:
                    # FILTRO IMPORTANTE: Apenas jogos até a data atual
                    resultado['Date_dt'] = pd.to_datetime(resultado[self.coluna_data], errors='coerce')
                    resultado = resultado[resultado['Date_dt'] <= data_atual]
                    
                    print(f"🟢 [BacktestEngine] ✓ Temporada encontrada com padrão '{padrao}': {len(resultado)} jogos (até {data_atual.date()})")
                    print(f"{'='*80}\n")
                    return resultado
                else:
                    print(f"🟡 [BacktestEngine] ✗ Padrão '{padrao}' não retornou resultados")
            except Exception as e:
                print(f"🔴 [BacktestEngine] ✗ Erro ao buscar padrão '{padrao}': {e}")
        
        # Se nenhum padrão funcionar, retornar dados mais recentes (fallback)
        print(f"\n⚠️  [BacktestEngine] ATENÇÃO: Temporada '{self.temporada}' não encontrada!")
        print(f"⚠️  [BacktestEngine] Usando FALLBACK - dados dos últimos 600 dias")
        df['Date_dt'] = pd.to_datetime(df[self.coluna_data], errors='coerce')
        df = df[df['Date_dt'] <= data_atual]  # Também aplicar filtro por data no fallback
        data_limite = data_atual - pd.Timedelta(days=600)
        resultado_fallback = df[df['Date_dt'] >= data_limite]
        print(f"⚠️  [BacktestEngine] Fallback retornou {len(resultado_fallback)} jogos (últimos 600 dias até {data_atual.date()})")
        print(f"{'='*80}\n")
        return resultado_fallback
    
    def _gerar_padroes_temporada(self, temporada):
        """Gera diferentes padrões para buscar a temporada nos dados - inteligente com formato detectado"""
        padroes = []
        
        print(f"🔵 [BacktestEngine] Gerando padrões para '{temporada}' com formato detectado: {self.formato_temporada}")
        
        # Formato YYYY-YY (ex: 2024-25)
        if '-' in temporada and len(temporada.split('-')[1]) == 2:
            ano_inicio = temporada.split('-')[0]
            ano_fim = temporada.split('-')[1]
            
            # Se o CSV usa YYYY/YYYY, priorizar esse formato
            if self.formato_temporada == 'YYYY/YYYY':
                padroes.append(f"{ano_inicio}/20{ano_fim}")        # 2024/2025 - PRIORIDADE
                padroes.append(f"{ano_inicio}/{ano_fim}")          # 2024/25
                padroes.append(f"{ano_inicio}-20{ano_fim}")        # 2024-2025
                padroes.append(f"{ano_inicio}-{ano_fim}")          # 2024-25
            else:
                # Se usa apenas YYYY
                padroes.append(f"{ano_inicio}")                    # 2024 - PRIORIDADE
                padroes.append(f"20{ano_fim}")                     # 2025
                padroes.append(f"{ano_inicio}/{20}{ano_fim}")      # Fallback para YYYY/YYYY
            
            padroes.append(temporada)                              # Original
            
        # Formato YYYY (ex: 2024)
        elif len(temporada) == 4:
            ano = temporada
            
            if self.formato_temporada == 'YYYY/YYYY':
                padroes.append(f"{ano}/{int(ano)+1}")              # 2024/2025 - PRIORIDADE
                padroes.append(f"{int(ano)-1}/{ano}")              # 2023/2024 (se for ano final)
            else:
                padroes.append(ano)                                # 2024 - PRIORIDADE
                padroes.append(str(int(ano)+1))                    # 2025
            
            padroes.append(ano)                                    # 2024 (fallback)
            
        # Formato YYYY/YYYY (ex: 2024/2025) - já está no padrão
        elif '/' in temporada:
            ano_inicio, ano_fim = temporada.split('/')
            padroes.append(temporada)                              # Original
            padroes.append(f"{ano_inicio}-{ano_fim[-2:]}")         # Converter para YYYY-YY
            padroes.append(f"{ano_inicio}-{ano_fim}")              # YYYY-YYYY
            
        print(f"🔵 [BacktestEngine] Padrões de busca para '{temporada}': {padroes}")
        return padroes
    
    def _contar_equipes(self):
        """Conta o número único de equipes na temporada de teste"""
        times_home = set(self.df_teste[self.coluna_home].unique())
        times_away = set(self.df_teste[self.coluna_away].unique())
        times_totais = times_home.union(times_away)
        return len(times_totais)
    
    def _detectar_max_jogos_rodada(self):
        """
        Detecta o máximo de jogos que acontecem normalmente em uma rodada.
        Agrupa os jogos por data e encontra o maior número de jogos em um dia.
        Depois calcula a moda (valor mais frequente) para encontrar a rodada típica.
        """
        # Agrupar por data e contar jogos
        jogos_por_data = self.df_teste.groupby(self.coluna_data).size()
        
        if len(jogos_por_data) == 0:
            # Fallback: calcular baseado no número de times
            return max(1, self.num_times // 2)
        
        # Encontrar a moda (quantidade mais frequente de jogos por data)
        # Isso representa a rodada típica (descarta datas com adiamentos)
        moda_jogos = jogos_por_data.mode()
        
        if len(moda_jogos) > 0:
            max_jogos = int(moda_jogos.iloc[0])
        else:
            # Se não conseguir encontrar moda, usar máximo
            max_jogos = int(jogos_por_data.max())
        
        # Validar: máximo teórico é n_times / 2
        max_teorico = self.num_times // 2
        return min(max_jogos, max_teorico)
        
    def _carregar_resultados(self):
        """Carrega resultados salvos ou inicia novo backtest"""
        if self.arquivo_resultados.exists():
            try:
                with open(self.arquivo_resultados, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        return json.loads(conteudo)
            except (json.JSONDecodeError, Exception):
                pass
        
        return {
            'rodada_atual': 1,
            'jogos_processados': 0,
            'entradas': [],
            'lucro_total': 0,
            'acertos': 0,
            'erros': 0
        }
    
    def _salvar_resultados(self):
        """Salva resultados do backtest"""
        with open(self.arquivo_resultados, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, ensure_ascii=False, indent=2)

    def salvar_resultados(self):
        """Wrapper público para salvar resultados"""
        self._salvar_resultados()
    
    def obter_proxima_rodada(self):
        """Obtém jogos da próxima rodada para processar (bloco sem repetir equipes)"""
        jogos_ja_processados = self.resultados['jogos_processados']
        
        if jogos_ja_processados >= len(self.df_teste):
            return None, None  # Backtest completo
        
        # Obter próxima rodada
        jogos_restantes = self.df_teste.iloc[jogos_ja_processados:].reset_index(drop=True)
        
        # Agrupar jogos em blocos sem repetir equipes (rodada dinâmica)
        rodada_jogos = []
        times_usados = set()
        
        for _, jogo in jogos_restantes.iterrows():
            home = str(jogo[self.coluna_home])
            away = str(jogo[self.coluna_away])
            
            # Se a partida repete equipe, pula para tentar encaixar outras
            if home in times_usados or away in times_usados:
                continue
            
            # Caso contrário, adiciona ao bloco
            rodada_jogos.append(jogo)
            times_usados.add(home)
            times_usados.add(away)
            
            # Se já usamos todos os times possíveis, encerra o bloco
            if self.num_times > 0 and len(times_usados) >= self.num_times:
                break
        
        return self.resultados['rodada_atual'], rodada_jogos
    
    def calcular_medias_historicas_por_odds(self, time, eh_home, odd_time, odd_adversario, range_percent=0.07):
        """
        Calcula médias históricas de CGH/VGH ou CGA/VGA baseado em ranges de probabilidade das odds
        Implementação idêntica ao modelo Próxima Rodada
        
        Args:
            time: Nome do time
            eh_home: True se o time joga em casa
            odd_time: Odd do time
            odd_adversario: Odd do adversário
            range_percent: Porcentagem do range (padrão 7% = 0.07)
        
        Returns:
            (media_cg, media_vg, std_cg, std_vg) ou (None, None, None, None)
        """
        if self.df_treino is None or len(self.df_treino) == 0:
            return None, None, None, None
        
        # Calcular probabilidades
        prob_time = 1 / odd_time if odd_time > 0 else 0
        prob_adversario = 1 / odd_adversario if odd_adversario > 0 else 0
        
        # Calcular ranges (±7%)
        prob_time_min = prob_time * (1 - range_percent)
        prob_time_max = prob_time * (1 + range_percent)
        prob_adv_min = prob_adversario * (1 - range_percent)
        prob_adv_max = prob_adversario * (1 + range_percent)
        
        # Identificar colunas de odds (preferir B365H/B365A)
        col_odd_h, col_odd_a = None, None
        odds_priority = [
            ('B365H', 'B365A'),
            ('B365CH', 'B365CA'),
            ('PSCH', 'PSCA'),
            ('PSH', 'PSA'),
            ('MaxCH', 'MaxCA'),
            ('MaxH', 'MaxA'),
            ('AvgCH', 'AvgCA'),
            ('AvgH', 'AvgA')
        ]
        
        for h_col, a_col in odds_priority:
            if h_col in self.df_treino.columns and a_col in self.df_treino.columns:
                col_odd_h = h_col
                col_odd_a = a_col
                break
        
        if not col_odd_h or not col_odd_a:
            return None, None, None, None
        
        if eh_home:
            # Time joga em casa: buscar jogos onde ele foi mandante
            jogos_time = self.df_treino[self.df_treino[self.coluna_home] == time].copy()
            
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
            jogos_time = self.df_treino[self.df_treino[self.coluna_away] == time].copy()
            
            if len(jogos_time) == 0:
                return None, None, None, None
            
            # Calcular probabilidades das odds históricas
            jogos_time['prob_h'] = 1 / jogos_time[col_odd_h]
            jogos_time['prob_a'] = 1 / jogos_time[col_odd_a]
            
            # Filtrar por range de probabilidade (invertido para away)
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
    
    def calcular_xg_e_odds(self, home_team, away_team, odd_h=None, odd_a=None):
        """
        Calcula xG e odds esperadas usando fórmula completa com filtro por range de odds
        Implementação UNIFICADA com modelo Próxima Rodada
        
        Args:
            home_team: Nome do time da casa
            away_team: Nome do time visitante
            odd_h: Odd da casa (se None, usa valor padrão)
            odd_a: Odd visitante (se None, usa valor padrão)
        """
        # Se odds não fornecidas, tentar extrair do histórico ou usar padrão
        if odd_h is None or odd_a is None:
            # Buscar odd médio dos jogos do home_team como mandante
            jogos_home = self.df_treino[self.df_treino[self.coluna_home] == home_team]
            if len(jogos_home) > 0 and 'B365H' in jogos_home.columns:
                odd_h = jogos_home['B365H'].tail(5).mean()
                odd_a = jogos_home['B365A'].tail(5).mean()
            else:
                odd_h = 2.0  # Padrão
                odd_a = 2.0
        
        # Calcular médias históricas para time home (filtrado por range de odd)
        mcgh, mvgh, std_mcgh, std_mvgh = self.calcular_medias_historicas_por_odds(
            home_team, True, odd_h, odd_a, range_percent=0.07
        )
        
        # Calcular médias históricas para time away (filtrado por range de odd)
        mcga, mvga, std_mcga, std_mvga = self.calcular_medias_historicas_por_odds(
            away_team, False, odd_a, odd_h, range_percent=0.07
        )
        
        # Se não conseguiu calcular com dados no range, retornar valores nulos
        if mcgh is None or mcga is None or mvgh is None or mvga is None:
            # Não há dados suficientes no range ±7%
            # Retornar resultado com valores nulos ao invés de fallback
            return {
                'xgh': None,
                'xga': None,
                'dxg': None,
                'odd_home_calc': None,
                'odd_away_calc': None,
                'cfxgh': None,
                'cfxga': None,
                'mcgh': None,
                'mvgh': None,
                'mcga': None,
                'mvga': None,
                'erro': 'Dados insuficientes no range ±7% de probabilidade'
            }
        
        # Usar fórmula completa com MCGH, MVGH, MCGA, MVGA
        # xGH = (1 + MCGH * MVGH * oddH * oddA) / (2 * MCGH * oddH)
        xgh = (1 + mcgh * mvgh * odd_h * odd_a) / (2 * mcgh * odd_h)
        
        # xGA = (1 + MCGA * MVGA * oddH * oddA) / (2 * MCGA * oddA)
        xga = (1 + mcga * mvga * odd_h * odd_a) / (2 * mcga * odd_a)
        
        # Calcular coeficientes de confiança (CF)
        cfxgh = None
        cfxga = None
        
        if std_mcgh is not None and std_mvgh is not None and mcgh > 0 and mvgh > 0:
            try:
                import numpy as np
                cv_cgh = std_mcgh / mcgh
                cv_vgh = std_mvgh / mvgh
                cfxgh = 1 / (1 + np.sqrt(cv_cgh**2 + cv_vgh**2))
            except:
                pass
        
        if std_mcga is not None and std_mvga is not None and mcga > 0 and mvga > 0:
            try:
                import numpy as np
                cv_cga = std_mcga / mcga
                cv_vga = std_mvga / mvga
                cfxga = 1 / (1 + np.sqrt(cv_cga**2 + cv_vga**2))
            except:
                pass
        
        # Calcular DxG
        diff = xgh - xga
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
        
        # Calcular odds esperadas usando distribuição de Poisson
        from scipy.stats import poisson
        
        # Probabilidade de vitória da casa
        prob_home = 0
        for h in range(0, 6):
            for a in range(0, 6):
                if h > a:
                    prob_home += poisson.pmf(h, xgh) * poisson.pmf(a, xga)
        
        # Probabilidade de vitória visitante
        prob_away = 0
        for h in range(0, 6):
            for a in range(0, 6):
                if a > h:
                    prob_away += poisson.pmf(h, xgh) * poisson.pmf(a, xga)
        
        # Probabilidade de empate
        prob_draw = 1 - prob_home - prob_away
        
        # Converter para odds (com margem de segurança)
        odd_home_calc = 1 / prob_home if prob_home > 0.05 else 20
        odd_away_calc = 1 / prob_away if prob_away > 0.05 else 20
        
        return {
            'xgh': round(xgh, 2),
            'xga': round(xga, 2),
            'dxg': dxg,
            'odd_home_calc': round(odd_home_calc, 2),
            'odd_away_calc': round(odd_away_calc, 2),
            'cfxgh': round(cfxgh, 4) if cfxgh is not None else None,
            'cfxga': round(cfxga, 4) if cfxga is not None else None,
            'mcgh': round(mcgh, 2) if mcgh is not None else None,
            'mvgh': round(mvgh, 2) if mvgh is not None else None,
            'mcga': round(mcga, 2) if mcga is not None else None,
            'mvga': round(mvga, 2) if mvga is not None else None
        }
    
    def identificar_value_bets(self, rodada_jogos):
        """
        Identifica value bets na rodada
        Lógica de entrada (mesmo modelo que analisar_proxima_rodada.py):
        - Regra 1: Se B365H > (ODD_H_CALC * 1.1) → HOME
        - Regra 2: Se B365A > (ODD_A_CALC * 1.1) → AWAY
        - Regra 3: Se DxG = EQ → comparar odds reais (B365)
        """
        value_bets = []
        
        for jogo in rodada_jogos:
            home = jogo[self.coluna_home]
            away = jogo[self.coluna_away]
            b365h = jogo[self.coluna_odds_home]
            b365a = jogo[self.coluna_odds_away]
            
            # Calcular xG e odds esperadas (passando as odds reais para filtro)
            calc = self.calcular_xg_e_odds(home, away, odd_h=b365h, odd_a=b365a)
            
            # Pular jogo se não houver dados suficientes
            if calc['xgh'] is None or calc['xga'] is None:
                continue
            
            dxg = calc['dxg']
            odd_h_calc = calc['odd_home_calc']
            odd_a_calc = calc['odd_away_calc']
            
            entrada = None
            
            # Regra 1: Se CASA > (ODD_H_CALC * 1.1) → HOME
            if b365h > (odd_h_calc * 1.1) and odd_h_calc > 0:
                entrada = 'HOME'
            # Regra 2: Se VISITANTE > (ODD_A_CALC * 1.1) → AWAY
            elif b365a > (odd_a_calc * 1.1) and odd_a_calc > 0:
                entrada = 'AWAY'
            # Regra 3: Se DxG = EQ
            elif dxg == 'EQ':
                # Se CASA < VISITANTE → HOME
                if b365h < b365a:
                    entrada = 'HOME'
                # Se CASA > VISITANTE → AWAY
                elif b365h > b365a:
                    entrada = 'AWAY'
            
            if entrada:
                value_bets.append({
                    'home': home,
                    'away': away,
                    'b365h': b365h,
                    'b365a': b365a,
                    'xgh': calc['xgh'],
                    'xga': calc['xga'],
                    'dxg': calc['dxg'],
                    'odd_home_calc': calc['odd_home_calc'],
                    'odd_away_calc': calc['odd_away_calc'],
                    'entrada': entrada,
                    'fthg': jogo[self.coluna_gols_home],
                    'ftag': jogo[self.coluna_gols_away]
                })
        
        return value_bets
    
    def processar_rodada(self):
        """Processa a próxima rodada do backtest"""
        rodada_num, rodada_jogos = self.obter_proxima_rodada()
        
        if rodada_jogos is None:
            self.resultados['completo'] = True
            self._salvar_resultados()
            return None  # Backtest completo
        
        # Identificar value bets
        value_bets = self.identificar_value_bets(rodada_jogos)
        
        # Calcular resultados das entradas
        for vb in value_bets:
            gh = vb['fthg']
            ga = vb['ftag']
            entrada = vb['entrada']
            
            lp = -1  # padrão: perda
            
            if entrada == 'HOME':
                if gh > ga:
                    lp = vb['b365h'] - 1  # Lucro sem desconto (desconto aplicado na exibição)
                else:
                    lp = -1
            elif entrada == 'AWAY':
                if ga > gh:
                    lp = vb['b365a'] - 1  # Lucro sem desconto (desconto aplicado na exibição)
                else:
                    lp = -1
            
            vb['lp'] = round(lp, 2)
            
            # Atualizar estatísticas
            self.resultados['entradas'].append(vb)
            self.resultados['lucro_total'] += lp
            
            if lp > 0:
                self.resultados['acertos'] += 1
            else:
                self.resultados['erros'] += 1
        
        # Atualizar dados de treino com os jogos da rodada processada
        # (adicionar os resultados reais ao arquivo de treino)
        for jogo in rodada_jogos:
            self.df_treino = pd.concat([self.df_treino, pd.DataFrame([jogo])], ignore_index=True)
        
        # Salvar arquivo de treino atualizado
        self.df_treino.to_csv(self.arquivo_treino, index=False)
        
        # Atualizar estado
        self.resultados['jogos_processados'] += len(rodada_jogos)
        self.resultados['rodada_atual'] += 1
        
        self._salvar_resultados()
        
        return {
            'rodada': rodada_num,
            'jogos_rodada': len(rodada_jogos),
            'value_bets': value_bets,
            'lucro_rodada': sum([vb['lp'] for vb in value_bets])
        }
    
    def obter_status(self):
        """Retorna status atual do backtest"""
        total_entradas = len(self.resultados['entradas'])
        winrate = (self.resultados['acertos'] / total_entradas * 100) if total_entradas > 0 else 0
        roi = (self.resultados['lucro_total'] / total_entradas * 100) if total_entradas > 0 else 0
        
        return {
            'rodada_atual': self.resultados['rodada_atual'],
            'jogos_processados': self.resultados['jogos_processados'],
            'total_jogos': len(self.df_teste),
            'total_entradas': total_entradas,
            'acertos': self.resultados['acertos'],
            'erros': self.resultados['erros'],
            'lucro_total': round(self.resultados['lucro_total'], 2),
            'winrate': round(winrate, 1),
            'roi': round(roi, 1),
            'completo': self.resultados['jogos_processados'] >= len(self.df_teste)
        }
    
    def resetar(self):
        """Reseta o backtest"""
        if self.arquivo_resultados.exists():
            self.arquivo_resultados.unlink()
        
        # Recriar arquivo de treino
        df_original = pd.read_csv(self.arquivo_original)
        df_treino = df_original[~df_original['Season'].isin(['2024/2025', '2025/2026'])].copy()
        df_treino.to_csv(self.arquivo_treino, index=False)
        
        self.resultados = self._carregar_resultados()
        return {'sucesso': True, 'mensagem': 'Backtest resetado com sucesso'}

if __name__ == '__main__':
    engine = BacktestEngine()
    print(f"Status: {engine.obter_status()}")
