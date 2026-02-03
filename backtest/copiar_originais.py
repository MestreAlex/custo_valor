#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para copiar arquivos de dados originais para a pasta backtest
com nomes padronizados para facilitar a lógica do BacktestEngine
"""

import os
import shutil
from pathlib import Path

def copiar_arquivo_original(codigo_liga, pasta_origem):
    """
    Copia o arquivo original de uma liga para a pasta backtest
    """
    
    projeto_root = Path(__file__).parent.parent
    pasta_backtest = Path(__file__).parent
    
    # Encontrar arquivo original
    arquivo_origem = projeto_root / pasta_origem / f"{codigo_liga}_completo.csv"
    if not arquivo_origem.exists():
        arquivo_origem = projeto_root / pasta_origem / f"{codigo_liga}.csv"
    
    arquivo_destino = pasta_backtest / f"{codigo_liga}_completo_original.csv"
    
    if not arquivo_origem.exists():
        print(f"⚠️  {codigo_liga}: Arquivo original não encontrado")
        return False
    
    try:
        shutil.copy(arquivo_origem, arquivo_destino)
        print(f"✓ {codigo_liga}: Cópia realizada com sucesso")
        return True
    except Exception as e:
        print(f"❌ {codigo_liga}: Erro ao copiar - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Copiando arquivos originais para a pasta backtest")
    print("=" * 60)
    
    LIGAS = {
        'B1': 'dados_ligas',
        'D1': 'dados_ligas',
        'D2': 'dados_ligas',
        'E0': 'dados_ligas',
        'E1': 'dados_ligas',
        'F1': 'dados_ligas',
        'F2': 'dados_ligas',
        'G1': 'dados_ligas',
        'I1': 'dados_ligas',
        'I2': 'dados_ligas',
        'N1': 'dados_ligas',
        'P1': 'dados_ligas',
        'SP1': 'dados_ligas',
        'SP2': 'dados_ligas',
        'T1': 'dados_ligas',
        'ARG': 'dados_ligas_new',
        'AUT': 'dados_ligas_new',
        'BRA': 'dados_ligas_new',
        'CHN': 'dados_ligas_new',
        'DNK': 'dados_ligas_new',
        'FIN': 'dados_ligas_new',
        'IRL': 'dados_ligas_new',
        'JPN': 'dados_ligas_new',
        'MEX': 'dados_ligas_new',
        'NOR': 'dados_ligas_new',
        'POL': 'dados_ligas_new',
        'ROU': 'dados_ligas_new',
        'RUS': 'dados_ligas_new',
        'SWE': 'dados_ligas_new',
        'SWZ': 'dados_ligas_new',
        'USA': 'dados_ligas_new',
    }
    
    sucesso = 0
    
    for codigo_liga, pasta in LIGAS.items():
        if copiar_arquivo_original(codigo_liga, pasta):
            sucesso += 1
    
    print("\n" + "=" * 60)
    print(f"Resultado: {sucesso}/{len(LIGAS)} ligas copiadas com sucesso")
    print("=" * 60)

if __name__ == '__main__':
    main()
