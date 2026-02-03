#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para preparar arquivos de treinamento para todas as ligas
Cria cópias dos dados originais filtrados até 2023/2024
"""

import os
import pandas as pd
from pathlib import Path

# Dicionário com as ligas e suas informações
LIGAS = {
    # Ligas da Europa (dados_ligas)
    'B1': {'nome': 'Bélgica - Primeira Divisão', 'pasta': 'dados_ligas'},
    'D1': {'nome': 'Alemanha - Bundesliga', 'pasta': 'dados_ligas'},
    'D2': {'nome': 'Alemanha - Segunda Divisão', 'pasta': 'dados_ligas'},
    'E0': {'nome': 'Inglaterra - Premier League', 'pasta': 'dados_ligas'},
    'E1': {'nome': 'Inglaterra - Championship', 'pasta': 'dados_ligas'},
    'F1': {'nome': 'França - Ligue 1', 'pasta': 'dados_ligas'},
    'F2': {'nome': 'França - Ligue 2', 'pasta': 'dados_ligas'},
    'G1': {'nome': 'Grécia - Super League', 'pasta': 'dados_ligas'},
    'I1': {'nome': 'Itália - Serie A', 'pasta': 'dados_ligas'},
    'I2': {'nome': 'Itália - Serie B', 'pasta': 'dados_ligas'},
    'N1': {'nome': 'Holanda - Eredivisie', 'pasta': 'dados_ligas'},
    'P1': {'nome': 'Portugal - Primeira Liga', 'pasta': 'dados_ligas'},
    'SP1': {'nome': 'Espanha - La Liga', 'pasta': 'dados_ligas'},
    'SP2': {'nome': 'Espanha - Segunda Divisão', 'pasta': 'dados_ligas'},
    'T1': {'nome': 'Turquia - Super Lig', 'pasta': 'dados_ligas'},
    # Ligas dos outros países (dados_ligas_new)
    'ARG': {'nome': 'Argentina - Super Liga', 'pasta': 'dados_ligas_new'},
    'AUT': {'nome': 'Áustria - Bundesliga', 'pasta': 'dados_ligas_new'},
    'BRA': {'nome': 'Brasil - Serie A', 'pasta': 'dados_ligas_new'},
    'CHN': {'nome': 'China - Super League', 'pasta': 'dados_ligas_new'},
    'DNK': {'nome': 'Dinamarca - Superligaen', 'pasta': 'dados_ligas_new'},
    'FIN': {'nome': 'Finlândia - Veikkausliiga', 'pasta': 'dados_ligas_new'},
    'IRL': {'nome': 'Irlanda - Premier Division', 'pasta': 'dados_ligas_new'},
    'JPN': {'nome': 'Japão - J-League', 'pasta': 'dados_ligas_new'},
    'MEX': {'nome': 'México - Liga MX', 'pasta': 'dados_ligas_new'},
    'NOR': {'nome': 'Noruega - Eliteserien', 'pasta': 'dados_ligas_new'},
    'POL': {'nome': 'Polônia - Ekstraklasa', 'pasta': 'dados_ligas_new'},
    'ROU': {'nome': 'Romênia - Liga I', 'pasta': 'dados_ligas_new'},
    'RUS': {'nome': 'Rússia - RPL', 'pasta': 'dados_ligas_new'},
    'SWE': {'nome': 'Suécia - Allsvenskan', 'pasta': 'dados_ligas_new'},
    'SWZ': {'nome': 'Suíça - Super Liga', 'pasta': 'dados_ligas_new'},
    'USA': {'nome': 'EUA - MLS', 'pasta': 'dados_ligas_new'},
}

def preparar_dados_liga(codigo_liga, pasta_origem):
    """
    Prepara os dados de uma liga para o backtest
    - Copia arquivo original
    - Cria arquivo de treino com dados até 2023/2024
    """
    
    # Caminho dos arquivos
    projeto_root = Path(__file__).parent.parent
    
    # Tentar com sufixo _completo primeiro, depois sem
    arquivo_original = projeto_root / pasta_origem / f"{codigo_liga}_completo.csv"
    if not arquivo_original.exists():
        arquivo_original = projeto_root / pasta_origem / f"{codigo_liga}.csv"
    
    arquivo_treino = Path(__file__).parent / f"{codigo_liga}_treino.csv"
    
    if not arquivo_original.exists():
        print(f"⚠️  {codigo_liga}: Arquivo original não encontrado: {arquivo_original}")
        return False
    
    try:
        # Ler dados originais
        df = pd.read_csv(arquivo_original)
        
        # Converter coluna de data para datetime
        # Tentar diferentes formatos de data
        data_coluna = None
        for col in df.columns:
            if 'date' in col.lower():
                data_coluna = col
                break
        
        if data_coluna is None:
            print(f"⚠️  {codigo_liga}: Coluna de data não encontrada")
            return False
        
        # Converter para datetime
        df[data_coluna] = pd.to_datetime(df[data_coluna], errors='coerce')
        
        # Filtrar dados até 2023/2024
        # Considerar que temporadas vão de agosto a julho
        # Então até 2024 significa até julho de 2024
        df_treino = df[df[data_coluna] <= '2024-07-31'].copy()
        
        # Ordenar por data
        df_treino = df_treino.sort_values(data_coluna)
        
        # Salvar arquivo de treino
        df_treino.to_csv(arquivo_treino, index=False)
        
        print(f"✓ {codigo_liga}: {len(df_treino)} registros de treino")
        return True
        
    except Exception as e:
        print(f"❌ {codigo_liga}: Erro ao processar - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Preparando dados de todas as ligas para backtest")
    print("=" * 60)
    
    sucesso = 0
    falha = 0
    
    for codigo_liga, info in LIGAS.items():
        if preparar_dados_liga(codigo_liga, info['pasta']):
            sucesso += 1
        else:
            falha += 1
    
    print("\n" + "=" * 60)
    print(f"Resultado: {sucesso} ligas preparadas com sucesso, {falha} falharam")
    print("=" * 60)

if __name__ == '__main__':
    main()
